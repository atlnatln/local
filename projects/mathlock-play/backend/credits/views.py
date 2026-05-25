import json
import logging
import random
import re
import subprocess
import threading
import uuid
import tempfile
import shutil
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from .models import (ChildProfile, CreditBalance, CrashReport,
                     Device, GenerationJob, LevelSet, PurchaseRecord, Question, QuestionSet,
                     PuzzleSet, PuzzleProgress,
                     RenewalLock, UserQuestionProgress)
from .authentication import DeviceTokenSigner
from .google_play import verify_purchase
from .tasks import generate_level_set, generate_question_set, generate_puzzle_set

logger = logging.getLogger(__name__)

# Procedural motor anahtarı — settings.py'den override edilebilir
USE_PROCEDURAL = getattr(settings, 'USE_PROCEDURAL', True)



# ─── Input Sanitization ─────────────────────────────────────────────────────

_SAFE_NAME_RE = re.compile(r'[^\w\s\-]', re.UNICODE)


def _sanitize_child_name(name: str) -> str:
    """Çocuk adını sanitize et — max 100 karakter, zararlı karakter temizle."""
    name = str(name).strip()[:100]
    name = _SAFE_NAME_RE.sub('', name)
    return name or _('default_child_name')


# ─── Soru Üretimi (kimi-cli + AGENTS.md) ──────────────────────────────────

# Proje dizini: backend/ → üst dizin = mathlock-play/
# NOT: Container'da BASE_DIR=/app olduğunda parent=/ olur.
# Mount yapısına göre adaptif: önce parent dizini dene (lokal), yoksa BASE_DIR (container).
_PROJECT_DIR = Path(settings.BASE_DIR).parent
if not (_PROJECT_DIR / 'procedural-questions-v2.py').exists():
    _PROJECT_DIR = Path(settings.BASE_DIR)

_DATA_DIR = _PROJECT_DIR / 'data'
if not _DATA_DIR.exists():
    _DATA_DIR = Path(settings.BASE_DIR) / 'data'

_GENERATE_TIMEOUT = 120  # saniye — procedural üretim çok hızlı

_LEVELS_COUNT = 12  # Her sette 12 seviye

# Yenileme kilidi TTL: 20 dakika (procedural üretim + tampon)
_RENEWAL_LOCK_TTL = 20 * 60  # saniye

# Satın alma doğrulama: test token prefix (sadece DEBUG=True iken geçerli)
DEBUG_TOKEN_PREFIX = "DEBUG_TEST_TOKEN_"

# Dönem bazlı soru sayıları
_QUESTION_COUNTS = {
    'okul_oncesi': 30,
    'sinif_1': 40,
    'sinif_2': 50,
    'sinif_3': 50,
    'sinif_4': 50,
}

_VALID_EDUCATION_PERIODS = set(_QUESTION_COUNTS.keys())


def _generate_questions_procedural(child_stats: dict, education_period: str = 'sinif_2') -> list:
    """
    procedural-questions-v2.py ile prosedürel soru üret.

    Her çocuk için izole geçici dizin kullanır — eşzamanlı üretimlerde dosya çakışması olmaz.

    Akış:
      1. Geçici dizin oluştur (/tmp/mathlock-gen-<uuid>/)
      2. child_stats → tmpdir/stats.json yaz
      3. procedural-questions-v2.py --stats ... --period ... çalıştır
      4. tmpdir/questions.json oku
      5. Geçici dizini temizle

    Hata durumunda RuntimeError fırlatır (use_credit krediyi iade eder).
    """
    if education_period not in _VALID_EDUCATION_PERIODS:
        education_period = 'sinif_2'

    expected_count = _QUESTION_COUNTS[education_period]
    script = _PROJECT_DIR / 'procedural-questions-v2.py'

    tmpdir = Path(tempfile.mkdtemp(prefix='mathlock-gen-'))
    try:
        (tmpdir / 'stats.json').write_text(
            json.dumps(child_stats, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        if not script.exists():
            raise RuntimeError(_('procedural_script_not_found'))

        try:
            result = subprocess.run(
                ['python3', str(script),
                 '--stats', str(tmpdir / 'stats.json'),
                 '--output', str(tmpdir / 'questions.json'),
                 '--period', education_period,
                 '--seed', str(random.randint(0, 999999))],
                capture_output=True, text=True,
                timeout=_GENERATE_TIMEOUT,
                cwd=str(_PROJECT_DIR),
            )
        except subprocess.TimeoutExpired:
            logger.error("procedural-questions-v2.py %d saniye zaman aşımı", _GENERATE_TIMEOUT)
            raise RuntimeError(_('question_generation_timeout'))

        if result.returncode != 0:
            logger.error("procedural-questions-v2.py başarısız (rc=%d): %s",
                         result.returncode, result.stderr[-500:] if result.stderr else "")
            raise RuntimeError(_('question_generation_failed'))

        questions_file = tmpdir / 'questions.json'
        if not questions_file.exists():
            raise RuntimeError(_('questions_json_not_generated'))

        data = json.loads(questions_file.read_text(encoding='utf-8'))
        questions = data.get('questions', [])

        if len(questions) < expected_count:
            raise RuntimeError(_('insufficient_questions').format(got=len(questions), expected=expected_count))

        logger.info(
            "Procedural soru üretimi başarılı: v%s, %d soru, dönem=%s",
            data.get('version', '?'), len(questions), education_period
        )

        return [
            {
                'text': q['text'],
                'answer': q['answer'],
                'type': q.get('type', ''),
                'difficulty': q.get('difficulty', 1),
                'hint': q.get('hint', ''),
            }
            for q in questions[:expected_count]
        ]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ─── Otomatik Yenileme Yardımcıları ─────────────────────────────────────────

def _build_child_stats(child) -> dict:
    """
    Çocuğa özel üretim için DB + Android stats'ı birleştir.
    AI bu dict'i okuyarak çocuğun güçlü/zayıf yönlerine göre soru üretir.
    """
    from datetime import date as _date

    # Android'den gelen tip/zorluk detayları (temel)
    stats = dict(child.stats_json or {})

    # Backend DB'den yetkili alanlar (override)
    stats['childName'] = child.name
    stats['educationPeriod'] = child.education_period
    stats['totalCorrect'] = child.total_correct
    stats['totalShown'] = child.total_shown
    stats['accuracy'] = round(child.accuracy, 3)
    stats['currentDifficulty'] = child.current_difficulty
    stats['totalTimeSeconds'] = child.total_time_seconds

    # Son 7 günlük performans özeti
    if child.daily_stats:
        last7 = dict(sorted(child.daily_stats.items())[-7:])
        stats['last7DaysStats'] = last7

    # AI soru setlerindeki çözülme durumu
    ai_sets_summary = []
    for qs in QuestionSet.objects.filter(child=child).order_by('-version')[:5]:
        ai_sets_summary.append({
            'version': qs.version,
            'total': len(qs.questions_json or []),
            'solved': len(qs.solved_ids or []),
        })
    if ai_sets_summary:
        stats['aiSetsSummary'] = ai_sets_summary

    return stats


def _build_level_stats(child) -> dict:
    """Çocuğa özel seviye üretimi için DB'den level istatistiklerini topla."""
    stats: dict = {
        'childName': child.name,
        'educationPeriod': child.education_period,
        'questionAccuracy': round(child.accuracy, 3),
        'currentDifficulty': child.current_difficulty,
    }

    # Soru performansından güçlü/zayıf konular
    by_type = (child.stats_json or {}).get('byType', {})
    strong, weak = [], []
    for tip, data in by_type.items():
        shown = data.get('shown', 0)
        correct = data.get('correct', 0)
        if shown >= 5:
            acc = correct / shown * 100
            if acc >= 80:
                strong.append(tip)
            elif acc < 50:
                weak.append(tip)
    if strong:
        stats['strongTopics'] = strong
    if weak:
        stats['weakTopics'] = weak

    latest_ls = LevelSet.objects.filter(child=child).order_by('-version').first()
    if latest_ls:
        levels = latest_ls.levels_json or []
        stats['completedLevelIds'] = latest_ls.completed_level_ids or []
        stats['totalCompleted'] = len(latest_ls.completed_level_ids or [])
        stats['totalLevels'] = len(levels)
        stats['lastVersion'] = latest_ls.version

        # Difficulty continuity: previous set's difficulty profile
        if levels:
            diffs = [lv.get('difficulty', 1) for lv in levels]
            stats['lastSetEndDifficulty'] = levels[-1].get('difficulty', 1)
            stats['lastSetMaxDifficulty'] = max(diffs)
            stats['lastSetAvgDifficulty'] = round(sum(diffs) / len(diffs), 1)
            completed = set(latest_ls.completed_level_ids or [])
            stats['completionRate'] = len(completed) / len(levels) if levels else 0
            stats['lastSetCompletionRate'] = stats['completionRate']

        # Cross-set duplicate prevention data
        previous_sets = LevelSet.objects.filter(
            child=child
        ).order_by('-version')[:2]
        stats['previousSets'] = []
        for ls in previous_sets:
            pls = ls.levels_json or []
            stats['previousSets'].append({
                'version': ls.version,
                'titles': [lv.get('title', '') for lv in pls],
                'mechanics': [_summarize_mechanics(lv) for lv in pls],
            })
    return stats


def _build_puzzle_stats(child) -> dict:
    """Çocuğa özel bulmaca üretimi için DB'den puzzle istatistiklerini topla."""
    stats: dict = {
        'childName': child.name,
        'educationPeriod': child.education_period,
        'questionAccuracy': round(child.accuracy, 3),
        'currentDifficulty': child.current_difficulty,
    }

    # Soru performansından güçlü/zayıf konular (level stats ile aynı)
    by_type = (child.stats_json or {}).get('byType', {})
    strong, weak = [], []
    for tip, data in by_type.items():
        shown = data.get('shown', 0)
        correct = data.get('correct', 0)
        if shown >= 5:
            acc = correct / shown * 100
            if acc >= 80:
                strong.append(tip)
            elif acc < 50:
                weak.append(tip)
    if strong:
        stats['strongTopics'] = strong
    if weak:
        stats['weakTopics'] = weak

    # Puzzle ilerleme istatistikleri
    progress_qs = PuzzleProgress.objects.filter(child=child)
    total_completed = progress_qs.filter(completed=True).count()
    total_attempted = progress_qs.count()
    avg_stars = 0.0
    if total_attempted > 0:
        stars_sum = sum(p.stars for p in progress_qs)
        avg_stars = round(stars_sum / total_attempted, 2)

    stats['totalCompleted'] = total_completed
    stats['totalAttempted'] = total_attempted
    stats['averageStars'] = avg_stars
    stats['completionRate'] = round(total_completed / total_attempted, 2) if total_attempted > 0 else 0.0

    # Son puzzle set bilgisi
    latest_ps = PuzzleSet.objects.filter(child=child).order_by('-version').first()
    if latest_ps:
        puzzles = latest_ps.puzzles_json or []
        stats['lastVersion'] = latest_ps.version
        stats['totalLevels'] = len(puzzles)

        # Difficulty continuity
        if puzzles:
            diffs = [pz.get('difficulty', 1) for pz in puzzles]
            stats['lastSetEndDifficulty'] = puzzles[-1].get('difficulty', 1)
            stats['lastSetMaxDifficulty'] = max(diffs)
            stats['lastSetAvgDifficulty'] = round(sum(diffs) / len(diffs), 1)

        # Önceki setlerden duplicate prevention
        previous_sets = PuzzleSet.objects.filter(
            child=child
        ).order_by('-version')[:2]
        stats['previousSets'] = []
        for ps in previous_sets:
            pps = ps.puzzles_json or []
            stats['previousSets'].append({
                'version': ps.version,
                'titles': [pz.get('title', '') for pz in pps],
                'mechanics': [_summarize_mechanics(pz) for pz in pps],
            })
    return stats


def _summarize_mechanics(level: dict) -> str:
    """Generate a short mechanic fingerprint for duplicate detection."""
    fp = level.get('fingerprint')
    if isinstance(fp, dict):
        return (
            f"grid={fp.get('grid', '?x?')}|"
            f"pathShape={fp.get('pathShape', '?')}|"
            f"branching={fp.get('branching', '?')}|"
            f"wallTopology={fp.get('wallTopology', '?')}|"
            f"valuePlanning={fp.get('valuePlanning', '?')}|"
            f"ops={fp.get('ops', '?')}"
        )
    # Fallback to legacy format for backward compatibility
    cmds = ','.join(sorted(level.get('commands', [])))
    has_ops = 'yes' if level.get('ops') else 'no'
    has_walls = 'yes' if level.get('walls') else 'no'
    has_target_val = 'yes' if level.get('targetVal') is not None else 'no'
    grid = f"{level.get('cols', 0)}x{level.get('rows', 0)}"
    return f"cmds={cmds}|ops={has_ops}|walls={has_walls}|targetVal={has_target_val}|grid={grid}"


def _refund_credit(credit_balance_pk: int, is_free: bool):
    """Hata durumunda krediyi iade et (background thread'den güvenli çağrılır)."""
    try:
        with transaction.atomic():
            cb = CreditBalance.objects.select_for_update().get(pk=credit_balance_pk)
            if is_free:
                cb.free_set_used = False
                cb.save(update_fields=['free_set_used', 'updated_at'])
            else:
                cb.balance += 1
                cb.total_used -= 1
                cb.save(update_fields=['balance', 'total_used', 'updated_at'])
    except Exception as e:
        logger.error("Kredi iadesi başarısız (pk=%d): %s", credit_balance_pk, e)


def _refresh_weekly_report(child) -> None:
    """
    Son 7 günün DB istatistiklerinden haftalık gelişim raporunu hesapla ve kaydet.
    upload_stats sonrası çağrılır — ağır işlem yok, sadece DB verisinden özet üretir.
    """
    from datetime import date as _date, timedelta as _td
    try:
        daily = child.daily_stats or {}
        today = _date.today()
        week_start = (today - _td(days=6)).isoformat()
        week_days = {
            (today - _td(days=i)).isoformat(): {}
            for i in range(6, -1, -1)
        }
        total_solved = total_correct = total_time = 0
        for day_str in week_days:
            entry = daily.get(day_str, {})
            total_solved += entry.get('solved', 0)
            total_correct += entry.get('correct', 0)
            total_time += entry.get('time_seconds', 0)
            week_days[day_str] = entry

        weekly_acc = round(total_correct / total_solved * 100, 1) if total_solved > 0 else 0

        # Tip bazlı güçlü/zayıf alan analizi
        by_type = child.stats_json.get('byType', {}) if child.stats_json else {}
        strong, weak = [], []
        for tip, data in by_type.items():
            shown = data.get('shown', 0)
            correct = data.get('correct', 0)
            if shown >= 5:
                acc = correct / shown * 100
                if acc >= 80:
                    strong.append(tip)
                elif acc < 50:
                    weak.append(tip)

        # Seviye ilerleme özeti
        level_summary: dict = {}
        ls = LevelSet.objects.filter(child=child).order_by('-version').first()
        if ls:
            done = len(ls.completed_level_ids or [])
            total = len(ls.levels_json or [])
            level_summary = {'completed': done, 'total': total, 'version': ls.version}

        # Aktif gün sayısı: solved > 0 olan günler
        active_days = sum(1 for d in week_days.values() if d.get('solved', 0) > 0)
        avg_daily_minutes = round(total_time / 60 / active_days, 1) if active_days > 0 else 0.0

        report = {
            'generatedAt': today.isoformat(),
            'period': 'last_7_days',
            'totalSolved': total_solved,
            'totalCorrect': total_correct,
            'accuracy': weekly_acc,
            'totalTimeMinutes': round(total_time / 60, 1),
            'avgDailyMinutes': avg_daily_minutes,
            'currentDifficulty': child.current_difficulty,
            'strongTopics': strong,
            'weakTopics': weak,
            'levelProgress': level_summary,
            'dailyBreakdown': week_days,
        }
        child.weekly_report_json = report
        child.save(update_fields=['weekly_report_json'])
    except Exception as e:
        logger.warning("Haftalık rapor güncellenemedi (child=%s): %s", child.name, e)


def _run_in_background(fn, *args, **kwargs):
    """Django ORM ile güvenli daemon thread başlat."""
    def wrapper():
        fn(*args, **kwargs)
    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    return t


def _release_renewal_lock(child_pk: int, content_type: str):
    """Yenileme kilidini serbest bırak. Hata olursa logla, sessizce devam et."""
    try:
        RenewalLock.objects.filter(child_id=child_pk, content_type=content_type).delete()
    except Exception as e:
        logger.warning(
            "Kilit serbest bırakılamadı (child_pk=%d, type=%s): %s",
            child_pk, content_type, e,
        )


def _deduct_credit_and_lock(child_pk: int, device, content_type: str) -> tuple:
    """
    Tek atomic işlem: yenileme kilidi al + kredi düş.
    Döndürür: (success, is_free, credit_balance_pk, credits_remaining)

    success=False durumları:
      - Aynı çocuk için bu content_type zaten kilitli (yenileme devam ediyor)
      - Kredi yok

    Kilit, arka plan thread'i tamamlanınca _release_renewal_lock ile serbest bırakılır.
    Sunucu çökerse _RENEWAL_LOCK_TTL (20 dk) sonra otomatik geçersiz sayılır.
    """
    now = timezone.now()
    expires_at = now + timedelta(seconds=_RENEWAL_LOCK_TTL)

    with transaction.atomic():
        # ChildProfile satırını kilitle — aynı çocuk için tüm yenileme işlemlerini serialize et
        try:
            ChildProfile.objects.select_for_update(nowait=True).get(pk=child_pk)
        except ChildProfile.DoesNotExist:
            return False, False, 0, 0
        except Exception:
            # nowait: satır başka transaction'da kilitliyse hemen dön
            logger.info(
                "Yenileme: çocuk satırı kilitli, atlanıyor (child_pk=%d, type=%s)",
                child_pk, content_type,
            )
            return False, False, 0, 0

        # 1. Çok eski (2×TTL) kilidi temizle — saat senkronizasyonu sorunlarına karşı güvenlik
        very_old = now - timedelta(seconds=_RENEWAL_LOCK_TTL * 2)
        RenewalLock.objects.filter(
            child_id=child_pk, content_type=content_type, created_at__lt=very_old
        ).delete()

        # 2. Süresi dolmuş kilidi temizle
        RenewalLock.objects.filter(
            child_id=child_pk, content_type=content_type, expires_at__lt=now
        ).delete()

        # 3. Kilit var mı? (double-check: gerçekten aktif mi)
        lock = RenewalLock.objects.filter(child_id=child_pk, content_type=content_type).first()
        if lock:
            if lock.expires_at > now:
                logger.info(
                    "Yenileme zaten devam ediyor, atlandı: child_pk=%d, type=%s, expires=%s",
                    child_pk, content_type, lock.expires_at.isoformat(),
                )
                return False, False, 0, 0
            else:
                # Stale lock (race condition sonrası), sil ve devam et
                lock.delete()
                logger.info(
                    "Stale kilit silindi, devam ediliyor: child_pk=%d, type=%s",
                    child_pk, content_type,
                )

        # Kilidi oluştur
        RenewalLock.objects.create(
            child_id=child_pk,
            content_type=content_type,
            expires_at=expires_at,
        )

        # Kredi düş
        cb = CreditBalance.objects.select_for_update().get_or_create(device=device)[0]
        is_free = not cb.free_set_used

        if is_free:
            cb.free_set_used = True
            cb.save(update_fields=['free_set_used', 'updated_at'])
            return True, True, cb.pk, cb.balance
        elif cb.balance > 0:
            cb.balance -= 1
            cb.total_used += 1
            cb.save(update_fields=['balance', 'total_used', 'updated_at'])
            return True, False, cb.pk, cb.balance
        else:
            # Kredi yok — kilidi geri al (transaction rollback yöntemi: kilidi sil)
            RenewalLock.objects.filter(
                child_id=child_pk, content_type=content_type
            ).delete()
            return False, False, cb.pk, 0


def _check_and_auto_renew_after_purchase(device_pk: int):
    """
    Satın alma sonrası otomatik yenileme — background thread'de çalışır.

    Önce her çocuk için matematik soruları tükendi mi kontrol eder (öncelik 1),
    ardından bulmaca seviyeleri tükendi mi kontrol eder (öncelik 2).
    Her tükenmiş içerik için 1 kredi düşer ve arka planda üretim başlatır.
    Krediler yetmediğinde durur.
    """
    from django.db import connection as _conn
    try:
        device = Device.objects.get(pk=device_pk)
        children = list(device.children.filter(is_active=True))

        for child in children:
            # ── 1. Öncelik: Matematik soruları ──────────────────────────────
            total_free = Question.objects.filter(batch_number=0).count()
            free_solved = UserQuestionProgress.objects.filter(
                device=device, solved=True, child=child
            ).count()
            total_ai = 0
            ai_solved = 0
            for qs in QuestionSet.objects.filter(child=child):
                total_ai += len(qs.questions_json or [])
                ai_solved += len(qs.solved_ids or [])

            total_q = total_free + total_ai
            solved_q = free_solved + ai_solved
            if total_q > 0 and solved_q >= total_q:
                success, is_free, cb_pk, _remaining = _deduct_credit_and_lock(child.pk, device, 'questions')
                if success:
                    task = generate_question_set.delay(child.pk, cb_pk, is_free)
                    logger.info(
                        "Satın alma sonrası matematik yenileme başlatıldı (Celery): child=%s, is_free=%s, job=%s",
                        child.name, is_free, task.id,
                    )
                else:
                    logger.info("Satın alma sonrası yenileme: kredi yetmedi veya kilitli (child=%s)", child.name)

            # ── 2. Öncelik: Bulmaca seviyeleri ──────────────────────────────
            latest_ls = LevelSet.objects.filter(child=child).order_by('-version').first()
            if latest_ls:
                total_lvl = len(latest_ls.levels_json or [])
                done_lvl = len(latest_ls.completed_level_ids or [])
                if total_lvl > 0 and done_lvl >= total_lvl:
                    success, is_free, cb_pk, _remaining = _deduct_credit_and_lock(child.pk, device, 'levels')
                    if success:
                        task = generate_level_set.delay(child.pk, cb_pk, is_free, _build_level_stats(child), child.education_period)
                        logger.info(
                            "Satın alma sonrası seviye yenileme başlatıldı (Celery): child=%s, is_free=%s, job=%s",
                            child.name, is_free, task.id,
                        )
                    else:
                        logger.info(
                            "Satın alma sonrası seviye yenileme: kredi yetmedi veya kilitli (child=%s)",
                            child.name,
                        )

    except Exception as exc:
        logger.error("Satın alma sonrası otomatik yenileme hatası (device_pk=%d): %s", device_pk, exc)
    finally:
        _conn.close()


# ─── Scope-based Throttles ──────────────────────────────────────────────────

class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class PurchaseThrottle(AnonRateThrottle):
    scope = 'purchase'


class CrashReportThrottle(AnonRateThrottle):
    scope = 'crash_report'


# ─── Cihaz Kayıt ────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def register_device(request):
    """
    Cihaz kaydı oluştur veya mevcut cihazı döndür.

    POST /api/mathlock/register/
    Body: { "installation_id": "abc123..." }
    Response: { "device_token": "uuid", "credits": 0, "free_set_used": false }
    """
    installation_id = request.data.get('installation_id')
    if not installation_id or not isinstance(installation_id, str):
        return Response({'error': _('installation_id_required')}, status=status.HTTP_400_BAD_REQUEST)

    # Sanitize
    installation_id = installation_id.strip()[:255]

    device, created = Device.objects.get_or_create(
        installation_id=installation_id,
        defaults={'device_token': uuid.uuid4()}
    )

    # Cihaz locale'ini al (Android'den gelir)
    device_locale = str(request.data.get('locale', 'tr')).strip().lower()[:10]
    if device_locale not in ('tr', 'en', 'de', 'fr', 'es'):
        device_locale = 'tr'

    # Yeni cihaz için kredi bakiyesi ve çocuk profili oluştur
    credit_balance, _created = CreditBalance.objects.get_or_create(device=device)
    child, _created = ChildProfile.objects.get_or_create(
        device=device, name="Çocuk",
        defaults={'locale': device_locale}
    )
    # Locale güncelle (varsa)
    if child.locale != device_locale:
        child.locale = device_locale
        child.save(update_fields=['locale'])

    if not created:
        device.save(update_fields=['last_seen'])

    signer = DeviceTokenSigner()
    access_token = signer.sign(str(device.device_token))

    return Response({
        'device_token': str(device.device_token),
        'access_token': access_token,
        'credits': credit_balance.balance,
        'free_set_used': credit_balance.free_set_used,
        'child_name': child.name,
        'education_period': child.education_period,
        'locale': child.locale,
        'children': [
            {
                'id': c.id,
                'name': c.name,
                'education_period': c.education_period,
                'is_active': c.is_active,
            }
            for c in device.children.all()
        ],
    })


# ─── Satın Alma Doğrulama ───────────────────────────────────────────────────

@api_view(['POST'])
@throttle_classes([PurchaseThrottle])
def verify_purchase_view(request):
    """
    Google Play satın almasını doğrula ve kredi ekle.

    POST /api/mathlock/purchase/verify/
    Body: {
        "device_token": "uuid",
        "purchase_token": "...",
        "product_id": "kredi_10"
    }
    Response: { "success": true, "credits_added": 10, "total_credits": 10 }
    """
    device = request.user
    purchase_token = request.data.get('purchase_token')
    product_id = request.data.get('product_id')

    if not all([purchase_token, product_id]):
        return Response(
            {'error': _('purchase_fields_required')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Ürün ID → kredi miktarı (erken kontrol — DB'ye gitmeden önce geçersiz ürünü reddet)
    credits_map = getattr(settings, 'CREDITS_PER_PURCHASE', {})
    credits_to_add = credits_map.get(product_id, 0)
    if credits_to_add == 0:
        return Response({'error': _('invalid_product_id').format(product_id=product_id)}, status=status.HTTP_400_BAD_REQUEST)

    # ─── Tek atomic blok: race condition'ı önler ──────────────────────────
    # select_for_update(): aynı token'ın eşzamanlı işlenmesini DB seviyesinde kilitler.
    # IntegrityError: "select" ile "create" arasındaki nadir race için son savunma hattı.
    try:
        with transaction.atomic():
            existing = PurchaseRecord.objects.select_for_update().filter(
                purchase_token=purchase_token
            ).first()

            if existing:
                # Güvenlik: token başka cihaza aitse reddet
                if existing.device_id != device.pk:
                    return Response(
                        {'error': _('purchase_token_invalid')},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if existing.verified:
                    _check_refunded_purchases(device)
                    credit_balance, _created = CreditBalance.objects.get_or_create(device=device)
                    return Response({
                        'success': True,
                        'credits_added': existing.credits_added,
                        'total_credits': credit_balance.balance,
                        'message': _('purchase_already_processed'),
                    })

                # Pending veya eski başarısız kayıt: tekrar doğrula
                needs_retry = (
                    existing.purchase_state == 2
                    or existing.last_verified_at is None
                    or (timezone.now() - existing.last_verified_at) > timedelta(hours=24)
                )
                if not needs_retry:
                    return Response(
                        {'error': _('purchase_token_pending')},
                        status=status.HTTP_409_CONFLICT,
                    )

                # Tekrar doğrula ve kaydı güncelle
                verification = verify_purchase(purchase_token, product_id)
                existing.verification_response = verification.get('raw_response', {})
                existing.purchase_state = verification.get('purchase_state', -1)
                existing.last_verified_at = timezone.now()

                if not verification.get('valid'):
                    error_msg = verification.get('error', _('verification_failed'))
                    existing.save()
                    return Response({'success': False, 'error': error_msg},
                                    status=status.HTTP_402_PAYMENT_REQUIRED)

                if existing.purchase_state == 0:
                    existing.verified = True
                    existing.credits_added = credits_to_add
                    existing.order_id = verification.get('order_id', '')
                    existing.save()
                    credit_balance, _created = CreditBalance.objects.get_or_create(device=device)
                    credit_balance.add_credits(credits_to_add)
                    _run_in_background(_check_and_auto_renew_after_purchase, device.pk)
                    return Response({
                        'success': True,
                        'credits_added': credits_to_add,
                        'total_credits': credit_balance.balance,
                    })

                existing.save()
                if existing.purchase_state == 2:
                    return Response(
                        {'error': _('purchase_token_pending')},
                        status=status.HTTP_409_CONFLICT,
                    )
                return Response(
                    {'error': _('purchase_canceled')},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            # DEBUG token bypass — yalnızca settings.DEBUG=True devrede iken
            if purchase_token.startswith(DEBUG_TOKEN_PREFIX):
                if not settings.DEBUG:
                    logger.warning("Üretim ortamında debug token reddedildi: %s", purchase_token[:30])
                    return Response({'error': _('debug_token_not_allowed')}, status=status.HTTP_403_FORBIDDEN)
                logger.info("DEV DEBUG: Test token kabul edildi: %s", purchase_token[:40])
                PurchaseRecord.objects.create(
                    device=device,
                    purchase_token=purchase_token,
                    product_id=product_id,
                    order_id=f"DEBUG_{purchase_token[:40]}",
                    credits_added=credits_to_add,
                    verified=True,
                    purchase_state=0,
                    last_verified_at=timezone.now(),
                    verification_response={"debug": True},
                )
                credit_balance, _created = CreditBalance.objects.get_or_create(device=device)
                credit_balance.add_credits(credits_to_add)
                _run_in_background(_check_and_auto_renew_after_purchase, device.pk)
                return Response({
                    'success': True,
                    'credits_added': credits_to_add,
                    'total_credits': credit_balance.balance,
                    'auto_renewal_queued': True,
                    'debug': True,
                })

            # Google Play API ile doğrula
            record = PurchaseRecord.objects.create(
                device=device,
                purchase_token=purchase_token,
                product_id=product_id,
            )

            verification = verify_purchase(purchase_token, product_id)
            record.verification_response = verification.get('raw_response', {})
            record.purchase_state = verification.get('purchase_state', -1)
            record.last_verified_at = timezone.now()

            if not verification.get('valid'):
                error_msg = verification.get('error', _('verification_failed'))
                logger.warning("Satın alma doğrulanamadı: device=%s, product=%s, error=%s, purchase_state=%s",
                               device.installation_id[:12], product_id, error_msg, record.purchase_state)
                record.save()
                return Response({'success': False, 'error': error_msg},
                                status=status.HTTP_402_PAYMENT_REQUIRED)

            if record.purchase_state == 0:
                record.verified = True
                record.order_id = verification.get('order_id', '')
                record.credits_added = credits_to_add
                record.save()

                credit_balance, _created = CreditBalance.objects.get_or_create(device=device)
                credit_balance.add_credits(credits_to_add)

                logger.info("Satın alma doğrulandı: device=%s, product=%s, credits=%d",
                            device.installation_id[:12], product_id, credits_to_add)

                _run_in_background(_check_and_auto_renew_after_purchase, device.pk)

                return Response({
                    'success': True,
                    'credits_added': credits_to_add,
                    'total_credits': credit_balance.balance,
                    'auto_renewal_queued': True,
                })
            else:
                record.save()
                state_map = {1: _('purchase_refunded_or_cancelled'), 2: _('purchase_pending')}
                error_msg = state_map.get(record.purchase_state, _('purchase_invalid_state').format(state=record.purchase_state))
                logger.warning("Satın alma reddedildi: device=%s, product=%s, state=%s",
                               device.installation_id[:12], product_id, record.purchase_state)
                return Response({'success': False, 'error': error_msg},
                                status=status.HTTP_402_PAYMENT_REQUIRED)

    except IntegrityError:
        # İki eşzamanlı istek aynı anda "existing yok" gördüyse DB unique constraint devreye girer
        logger.warning("Race condition yakalandı — aynı purchase_token eşzamanlı işlendi: %s",
                       purchase_token[:40])
        return Response(
            {'error': _('concurrent_purchase_conflict')},
            status=status.HTTP_409_CONFLICT,
        )


# ─── İade Kontrolü (Yardımcı Fonksiyon) ─────────────────────────────────────

def _check_refunded_purchases(device):
    """
    Google Play'den iade edilmiş satın almaları kontrol et ve krediyi düşür.

    Çalışma mantığı:
      - verified=True olan PurchaseRecord'ları al
      - purchase_state=-1 veya last_verified_at 24 saatten eskiyse tekrar doğrula
      - purchase_state=1 (canceled) ise krediyi düşür, verified=False yap
    """
    from django.db import models
    needs_check_q = (
        models.Q(purchase_state=-1)
        | models.Q(last_verified_at__isnull=True)
        | models.Q(last_verified_at__lt=timezone.now() - timedelta(hours=24))
    )
    for record in device.purchases.filter(verified=True).filter(needs_check_q):
        try:
            verification = verify_purchase(record.purchase_token, record.product_id)
            record.purchase_state = verification.get('purchase_state', -1)
            record.last_verified_at = timezone.now()

            if record.purchase_state == 1:  # canceled = iade edilmiş
                with transaction.atomic():
                    credit_balance = CreditBalance.objects.select_for_update().filter(device=device).first()
                    if credit_balance and record.credits_added > 0:
                        credit_balance.balance = max(0, credit_balance.balance - record.credits_added)
                        credit_balance.total_purchased = max(0, credit_balance.total_purchased - record.credits_added)
                        credit_balance.save()
                        logger.warning(
                            "Satın alma iade edildi, kredi düşürüldü: device=%s, order=%s, credits=%d",
                            device.installation_id[:12], record.order_id, record.credits_added
                        )
                    record.verified = False
                    record.save()
            else:
                record.save()
        except Exception as e:
            logger.error("İade kontrolü hatası: device=%s, error=%s",
                         device.installation_id[:12], str(e))


# ─── Kredi Sorgulama ────────────────────────────────────────────────────────

@api_view(['GET'])
def get_credits(request):
    """
    Kredi bakiyesini sorgula.

    GET /api/mathlock/credits/
    Response: { "credits": 10, "total_purchased": 10, "total_used": 0, "free_set_used": false }
    """
    device = request.user

    credit_balance, _created = CreditBalance.objects.get_or_create(device=device)

    # İade kontrolünü en fazla 24 saatte bir yap (Google API rate limit koruması)
    now = timezone.now()
    if (credit_balance.last_refund_check_at is None or
            (now - credit_balance.last_refund_check_at) > timedelta(hours=24)):
        _check_refunded_purchases(device)
        credit_balance.last_refund_check_at = now
        credit_balance.save(update_fields=['last_refund_check_at'])

    return Response({
        'credits': credit_balance.balance,
        'total_purchased': credit_balance.total_purchased,
        'total_used': credit_balance.total_used,
        'free_set_used': credit_balance.free_set_used,
    })


# ─── Kredi Kullanma ──────────────────────────────────────────────────────────

@api_view(['POST'])
def use_credit(request):
    """
    1 kredi kullan → AI ile 50 kişisel soru üret → QuestionSet'e kaydet.

    POST /api/mathlock/credits/use/
    Body: { "device_token": "uuid", "child_name": "Çocuk", "stats": {...} }
    Response: {
        "success": true,
        "credits_remaining": 9,
        "is_free": false,
        "questions_generated": 50,
        "set_version": 2
    }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))
    stats = request.data.get('stats', {})

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    # İstatistikleri güncelle
    if stats:
        child.total_correct = stats.get('totalCorrect', child.total_correct)
        child.total_shown = stats.get('totalShown', child.total_shown)
        child.stats_json = stats
        child.save(update_fields=['total_correct', 'total_shown', 'stats_json', 'updated_at'])

    # ─── Kredi kontrolü: atomic + select_for_update ───────────────────────
    with transaction.atomic():
        credit_balance = CreditBalance.objects.select_for_update().get_or_create(device=device)[0]
        is_free = not credit_balance.free_set_used

        if is_free:
            credit_balance.free_set_used = True
            credit_balance.save(update_fields=['free_set_used', 'updated_at'])
        else:
            if credit_balance.balance > 0:
                credit_balance.balance -= 1
                credit_balance.total_used += 1
                credit_balance.save(update_fields=['balance', 'total_used', 'updated_at'])
            else:
                return Response({
                    'error': _('no_credits'),
                    'credits_remaining': 0,
                }, status=status.HTTP_402_PAYMENT_REQUIRED)

    # ─── Procedural ile kişiye özel soru üret ────────────────────────────
    try:
        questions = _generate_questions_procedural(child.stats_json or {}, child.education_period)
    except Exception as exc:
        logger.error("Soru üretimi hatası: %s", exc)
        # Krediyi iade et
        with transaction.atomic():
            cb = CreditBalance.objects.select_for_update().get(device=device)
            if is_free:
                cb.free_set_used = False
                cb.save(update_fields=['free_set_used', 'updated_at'])
            else:
                cb.balance += 1
                cb.total_used -= 1
                cb.save(update_fields=['balance', 'total_used', 'updated_at'])
        return Response(
            {'error': _('question_generation_failed'), 'credits_refunded': True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # QuestionSet version: mevcut en yüksek + 1
    latest = QuestionSet.objects.filter(child=child).order_by('-version').first()
    next_version = (latest.version + 1) if latest else 1

    try:
        question_set = QuestionSet.objects.create(
            child=child,
            version=next_version,
            questions_json=questions,
            is_ai_generated=False,
            credit_used=not is_free,
        )
    except Exception as exc:
        logger.error("QuestionSet kayıt hatası: %s", exc)
        # Krediyi iade et
        with transaction.atomic():
            cb = CreditBalance.objects.select_for_update().get(device=device)
            if is_free:
                cb.free_set_used = False
                cb.save(update_fields=['free_set_used', 'updated_at'])
            else:
                cb.balance += 1
                cb.total_used -= 1
                cb.save(update_fields=['balance', 'total_used', 'updated_at'])
        return Response(
            {'error': _('question_set_save_failed'), 'credits_refunded': True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    logger.info(
        "Procedural soru seti: child=%s, v%d, %d soru, is_free=%s",
        child.name, next_version, len(questions), is_free
    )

    return Response({
        'success': True,
        'credits_remaining': credit_balance.balance,
        'is_free': is_free,
        'questions_generated': len(questions),
        'set_version': next_version,
        'child_id': child.id,
    })


# ─── İstatistik Yükleme ─────────────────────────────────────────────────────

@api_view(['POST'])
def upload_stats(request):
    """
    Çocuğun soru performans istatistiklerini kaydet.

    POST /api/mathlock/stats/
    Body: {
        "child_name": "Çocuk",
        "question_version": 1,
        "stats": { ... StatsTracker formatında ... }
    }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))
    stats = request.data.get('stats', {})
    question_version = request.data.get('question_version', 0)

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    # Idempotency: aynı session tekrar gönderilirse verileri katlama
    session_id = request.data.get('session_id')
    if session_id and child.last_sync_session_id == session_id:
        return Response({
            'success': True,
            'difficulty': child.current_difficulty,
            'total_correct': child.total_correct,
            'total_shown': child.total_shown,
        })

    # Kümülatif istatistik güncelle
    total_correct = stats.get('totalCorrect', 0)
    total_shown = stats.get('totalShown', 0)
    child.total_correct += total_correct
    child.total_shown += total_shown

    # Oturum süresi güncelle (delta: bu oturumdaki artış)
    session_time = int(request.data.get('session_time_seconds', 0))
    if session_time > 0:
        child.total_time_seconds += session_time

    # Günlük istatistik güncelle (daily_stats)
    from datetime import date as _date, timedelta as _td
    today_str = _date.today().isoformat()
    daily = child.daily_stats or {}
    today_entry = daily.get(today_str, {'solved': 0, 'correct': 0, 'time_seconds': 0})
    today_entry['solved'] = today_entry.get('solved', 0) + total_shown
    today_entry['correct'] = today_entry.get('correct', 0) + total_correct
    today_entry['time_seconds'] = today_entry.get('time_seconds', 0) + session_time
    daily[today_str] = today_entry
    # Son 90 günü tut
    cutoff = (_date.today() - _td(days=90)).isoformat()
    child.daily_stats = {k: v for k, v in daily.items() if k >= cutoff}

    # Zorluk seviyesi ayarla (doğruluk oranına göre)
    if child.total_shown >= 10:
        accuracy = child.total_correct / child.total_shown
        if accuracy >= 0.85 and child.current_difficulty < 5:
            child.current_difficulty += 1
        elif accuracy < 0.5 and child.current_difficulty > 1:
            child.current_difficulty -= 1

    child.stats_json = stats
    if session_id:
        child.last_sync_session_id = session_id
    child.save()

    # Haftalık gelişim raporunu DB istatistiklerinden güncelle
    _refresh_weekly_report(child)

    logger.info("Stats kaydedildi: child=%s, correct=%d/%d, difficulty=%d",
                child.name, total_correct, total_shown, child.current_difficulty)

    return Response({
        'success': True,
        'difficulty': child.current_difficulty,
        'total_correct': child.total_correct,
        'total_shown': child.total_shown,
    })


# ─── Sağlık Kontrolü ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """GET /api/mathlock/health/"""
    return Response({'status': 'ok', 'service': 'mathlock-backend'})


# ─── Email Kayıt ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@throttle_classes([RegisterThrottle])
def register_email(request):
    """
    Cihaza e-posta bağla — kredi satın almak için gerekli.

    POST /api/mathlock/auth/register-email/
    Body: { "email": "user@example.com" }
    Response: { "success": true, "email": "user@example.com" }
    """
    device = request.user
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response({'error': _('email_required')}, status=status.HTTP_400_BAD_REQUEST)

    # Basit email doğrulama
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return Response({'error': _('invalid_email_format')}, status=status.HTTP_400_BAD_REQUEST)
    if len(email) > 254:
        return Response({'error': _('email_too_long')}, status=status.HTTP_400_BAD_REQUEST)

    # Email zaten başka bir cihazda kullanılıyor mu?
    # Eğer varsa → veriyi eski cihazdan yeni cihaza transfer et (hesap kurtarma)
    old_device = Device.objects.filter(email=email).exclude(pk=device.pk).first()

    recovered = False
    if old_device:
        with transaction.atomic():
            # ChildProfile'ları transfer et (isim çakışmasını kontrol et)
            for child in old_device.children.all():
                existing_child = ChildProfile.objects.filter(
                    device=device, name=child.name
                ).first()
                if existing_child:
                    # Yeni cihazda aynı isimde çocuk varsa — istatistikleri birleştir
                    existing_child.total_correct += child.total_correct
                    existing_child.total_shown += child.total_shown
                    existing_child.current_difficulty = max(
                        existing_child.current_difficulty, child.current_difficulty
                    )
                    # stats_json: eski veriyi koru (daha zengin olan)
                    if child.stats_json and not existing_child.stats_json:
                        existing_child.stats_json = child.stats_json
                    existing_child.save()
                    # Eski çocuğun QuestionSet'lerini yeni çocuğa taşı
                    child.question_sets.update(child=existing_child)
                    child.level_sets.update(child=existing_child)
                    child.delete()
                else:
                    child.device = device
                    child.save(update_fields=['device'])

            # CreditBalance transfer: bakiyeleri birleştir
            old_credits = CreditBalance.objects.filter(device=old_device).first()
            if old_credits:
                new_credits, _created = CreditBalance.objects.get_or_create(device=device)
                new_credits.balance += old_credits.balance
                new_credits.total_purchased += old_credits.total_purchased
                new_credits.total_used += old_credits.total_used
                if old_credits.free_set_used:
                    new_credits.free_set_used = True
                new_credits.save()
                old_credits.delete()

            # PurchaseRecord'ları transfer et
            old_device.purchases.update(device=device)

            # UserQuestionProgress transfer et (çakışma varsa atla)
            for progress in old_device.question_progress.all():
                if not UserQuestionProgress.objects.filter(
                    device=device, question=progress.question, child=progress.child
                ).exists():
                    progress.device = device
                    progress.save(update_fields=['device'])
                else:
                    progress.delete()

            # AiQueryRecord transfer et
            old_device.ai_queries.update(device=device)

            # Eski cihazdan email'i temizle
            old_device.email = None
            old_device.save(update_fields=['email'])

            recovered = True
            logger.info(
                "Hesap kurtarma: email=%s, old_device=%s → new_device=%s",
                email, old_device.installation_id[:12], device.installation_id[:12]
            )

            # Transfer sonrası boş varsayılan "Çocuk" profilini temizle
            transferred_children = device.children.exclude(name="Çocuk")
            if transferred_children.exists():
                empty_default = device.children.filter(
                    name="Çocuk", total_shown=0, total_correct=0
                ).first()
                if empty_default:
                    empty_default.delete()
                    logger.info("Boş varsayılan profil temizlendi: device=%s",
                                device.installation_id[:12])

            device.email = email
            device.save(update_fields=['email', 'last_seen'])
    else:
        device.email = email
        device.save(update_fields=['email', 'last_seen'])

    # Transfer sonrası güncel bakiyeyi döndür
    credit_balance, _created = CreditBalance.objects.get_or_create(device=device)

    logger.info("Email kaydedildi: device=%s, email=%s, recovered=%s",
                device.installation_id[:12], email[:3] + "***@" + email.split("@")[-1], recovered)
    return Response({
        'success': True,
        'email': email,
        'recovered': recovered,
        'credits': credit_balance.balance,
    })


# ─── Soru Sync ────────────────────────────────────────────────────────────────

# Global ID şeması:
#   Batch 0 (ücretsiz): question_id direkt (1-50)
#   AI set (QuestionSet pk=N): N * 1000 + soru_index (1001-1050, 2001-2050, ...)

_AI_SET_ID_OFFSET = 1000


def _global_id_for_ai(set_pk: int, index: int) -> int:
    """QuestionSet.pk ve soru index'inden global ID hesapla."""
    return set_pk * _AI_SET_ID_OFFSET + index + 1


def _parse_ai_global_id(global_id: int) -> tuple:
    """Global ID'den (set_pk, question_index) çıkar. None ise batch 0 sorusu."""
    set_pk = global_id // _AI_SET_ID_OFFSET
    if set_pk == 0:
        return None, global_id  # batch 0
    index = (global_id % _AI_SET_ID_OFFSET) - 1
    return set_pk, index


@api_view(['GET'])
def get_questions(request):
    """
    Cihazın erişebildiği soruları döndür: ücretsiz batch 0 + AI per-user setleri.

    GET /api/mathlock/questions/
    Response: {
        "questions": [ { id, text, answer, type, difficulty, hint, batch, solved, source } ],
        "total_questions": 100,
        "solved_count": 35,
        "unsolved_count": 65,
        "ai_sets": 2
    }
    """
    device = request.user

    question_list = []

    # Aktif çocuğu belirle (tüm sorgularda kullanılacak)
    child_id = request.query_params.get('child_id')
    if child_id:
        try:
            child = device.children.get(id=child_id)
        except ChildProfile.DoesNotExist:
            return Response({'error': _('child_not_found')}, status=status.HTTP_404_NOT_FOUND)
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    # ── 1. Ücretsiz batch 0 soruları (Question model) ────────────────────
    period = child.education_period if child else 'sinif_2'
    free_questions = Question.objects.filter(batch_number=0)
    if period:
        period_questions = free_questions.filter(education_period=period)
        if period_questions.exists():
            free_questions = period_questions
    free_questions = free_questions.order_by('question_id')

    # Çocuğa özel çözülen soru ID'leri
    free_solved_ids = set(
        UserQuestionProgress.objects.filter(
            device=device, solved=True, child=child
        ).values_list('question__question_id', flat=True)
    )

    for q in free_questions:
        question_list.append({
            'id': q.question_id,
            'text': q.text,
            'answer': q.answer,
            'type': q.question_type,
            'difficulty': q.difficulty,
            'hint': q.hint,
            'batch': 0,
            'solved': q.question_id in free_solved_ids,
            'source': 'free',
        })

    # ── 2. AI per-user soruları (QuestionSet) ─────────────────────────────
    ai_set_count = 0

    if child:
        ai_sets = QuestionSet.objects.filter(child=child).order_by('version')
        ai_set_count = ai_sets.count()

        for qs in ai_sets:
            solved_ids_in_set = set(qs.solved_ids or [])
            questions_data = qs.questions_json or []

            for i, q in enumerate(questions_data):
                global_id = _global_id_for_ai(qs.pk, i)
                question_list.append({
                    'id': global_id,
                    'text': q.get('text', ''),
                    'answer': q.get('answer', 0),
                    'type': q.get('type', ''),
                    'difficulty': q.get('difficulty', 1),
                    'hint': q.get('hint', ''),
                    'batch': qs.version,  # Yüksek batch = yeni set → rotasyonda önce
                    'solved': global_id in solved_ids_in_set,
                    'source': 'ai',
                })

    solved_count = sum(1 for q in question_list if q['solved'])

    return Response({
        'questions': question_list,
        'total_questions': len(question_list),
        'solved_count': solved_count,
        'unsolved_count': len(question_list) - solved_count,
        'ai_sets': ai_set_count,
    })


# ─── İlerleme Güncelleme ─────────────────────────────────────────────────────

@api_view(['POST'])
def update_progress(request):
    """
    Çözülen soruları raporla. Global ID'ler hem batch 0 hem AI setleri kapsar.

    POST /api/mathlock/questions/progress/
    Body: {
        "solved_questions": [1, 3, 7, 1002, 1005],  // global ID'ler
        "reset_rotation": false
    }
    """
    device = request.user
    solved_ids = request.data.get('solved_questions', [])
    reset_rotation = request.data.get('reset_rotation', False)

    if not isinstance(solved_ids, list):
        return Response({'error': _('solved_questions_must_be_list')}, status=status.HTTP_400_BAD_REQUEST)

    try:
        solved_ids = [int(qid) for qid in solved_ids[:500]]
    except (ValueError, TypeError):
        return Response({'error': _('invalid_solved_questions')}, status=status.HTTP_400_BAD_REQUEST)

    # child_id varsa onu kullan, yoksa aktif profili bul
    child_id_param = request.data.get('child_id')
    if child_id_param:
        try:
            _target_child = device.children.get(id=child_id_param)
        except ChildProfile.DoesNotExist:
            return Response({'error': _('child_not_found')}, status=status.HTTP_404_NOT_FOUND)
    else:
        _target_child = device.children.filter(is_active=True).first() or device.children.first()

    if reset_rotation:
        # Batch 0 ilerlemeyi sıfırla (çocuğa özel)
        UserQuestionProgress.objects.filter(
            device=device, child=_target_child
        ).update(solved=False)
        # AI set ilerlemeyi sıfırla
        if _target_child:
            QuestionSet.objects.filter(child=_target_child).update(solved_ids=[])
        logger.info("Rotasyon sıfırlandı: device=%s", device.installation_id[:12])

    updated = 0

    # Batch 0 soruları (global ID < _AI_SET_ID_OFFSET)
    free_ids = [qid for qid in solved_ids if qid < _AI_SET_ID_OFFSET]
    if free_ids:
        free_question_map = {
            q.question_id: q
            for q in Question.objects.filter(batch_number=0, question_id__in=free_ids)
        }
        for qid in free_ids:
            question = free_question_map.get(qid)
            if not question:
                continue
            progress, created = UserQuestionProgress.objects.get_or_create(
                device=device, question=question, child=_target_child
            )
            if not progress.solved or created:
                progress.solved = True
                progress.solve_count += 1
                progress.save()
                updated += 1

    # AI set soruları (global ID >= _AI_SET_ID_OFFSET)
    ai_ids = [qid for qid in solved_ids if qid >= _AI_SET_ID_OFFSET]
    if ai_ids:
        child = _target_child
        if child:
            # Hangi set'lere ait olduklarını grupla
            sets_to_update = {}  # set_pk → [global_id, ...]
            for gid in ai_ids:
                set_pk, _ignored = _parse_ai_global_id(gid)
                if set_pk:
                    sets_to_update.setdefault(set_pk, []).append(gid)

            for set_pk, gids in sets_to_update.items():
                try:
                    qs = QuestionSet.objects.get(pk=set_pk, child=child)
                    existing = set(qs.solved_ids or [])
                    new_ids = set(gids) - existing
                    if new_ids:
                        qs.solved_ids = list(existing | new_ids)
                        qs.save(update_fields=['solved_ids'])
                        updated += len(new_ids)
                except QuestionSet.DoesNotExist:
                    pass

    # Toplam ilerleme hesapla (çocuğa özel)
    total_free = Question.objects.filter(batch_number=0).count()
    free_solved = UserQuestionProgress.objects.filter(
        device=device, solved=True, child=_target_child
    ).count()

    total_ai = 0
    ai_solved = 0
    if _target_child:
        for qs in QuestionSet.objects.filter(child=_target_child):
            total_ai += len(qs.questions_json or [])
            ai_solved += len(qs.solved_ids or [])

    # ── Otomatik matematik sorusu yenileme ───────────────────────────────────
    # Kural: Bu istekte yeni çözüm yapıldı + tüm sorular çözüldü + kredi var → auto-renew
    auto_renewal_started = False
    credits_remaining = None

    if updated > 0 and _target_child and (total_free + total_ai) > 0:
        all_solved = (free_solved + ai_solved) >= (total_free + total_ai)
        if all_solved:
            success, is_free, cb_pk, credits_remaining = _deduct_credit_and_lock(
                _target_child.pk, device, 'questions'
            )
            if success:
                auto_renewal_started = True
                task = generate_question_set.delay(_target_child.pk, cb_pk, is_free)
                logger.info(
                    "Otomatik matematik yenileme başlatıldı (Celery): child=%s, is_free=%s, job=%s",
                    _target_child.name, is_free, task.id
                )
                return Response({
                    'success': True,
                    'updated': updated,
                    'total_solved': free_solved + ai_solved,
                    'total_accessible': total_free + total_ai,
                    'auto_renewal_started': True,
                    'job_id': task.id,
                    'credits_remaining': credits_remaining or 0,
                })

    return Response({
        'success': True,
        'updated': updated,
        'total_solved': free_solved + ai_solved,
        'total_accessible': total_free + total_ai,
        'auto_renewal_started': auto_renewal_started,
        **(({'credits_remaining': credits_remaining}) if auto_renewal_started else {}),
    })


# ─── Çocuk Profili Yönetimi ──────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def children_list(request):
    """
    GET  /api/mathlock/children/
         Cihaza bağlı tüm çocuk profillerini listele.

    POST /api/mathlock/children/
         Yeni çocuk profili oluştur.
         Body: { "name": "Ali", "education_period": "sinif_1" }
    """
    device = request.user

    if request.method == 'GET':
        children = device.children.all().order_by('-is_active', 'name')
        return Response({
            'children': [
                {
                    'id': c.id,
                    'name': c.name,
                    'education_period': c.education_period,
                    'education_period_display': c.get_education_period_display(),
                    'is_active': c.is_active,
                    'total_correct': c.total_correct,
                    'total_shown': c.total_shown,
                    'total_time_seconds': c.total_time_seconds,
                    'accuracy': round(c.accuracy * 100, 1),
                    'current_difficulty': c.current_difficulty,
                    'question_count': c.question_count,
                    'created_at': c.created_at.isoformat(),
                }
                for c in children
            ],
        })

    # POST — yeni profil oluştur
    name = _sanitize_child_name(request.data.get('name', ''))
    education_period = request.data.get('education_period', 'sinif_2')

    if education_period not in _VALID_EDUCATION_PERIODS:
        return Response(
            {'error': _('invalid_education_period').format(valid=sorted(_VALID_EDUCATION_PERIODS))},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            # Max 5 çocuk profili (race condition koruması için transaction içinde)
            if device.children.count() >= 5:
                return Response({'error': _('max_children_reached')},
                                status=status.HTTP_400_BAD_REQUEST)

            child = ChildProfile.objects.create(
                device=device, name=name, education_period=education_period, is_active=False,
            )
    except IntegrityError:
        return Response({'error': _('profile_name_exists').format(name=name)},
                        status=status.HTTP_409_CONFLICT)

    return Response({
        'success': True,
        'child': {
            'id': child.id,
            'name': child.name,
            'education_period': child.education_period,
            'is_active': child.is_active,
        },
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def children_detail(request):
    """
    PUT  /api/mathlock/children/detail/
         Çocuk profilini güncelle (isim, dönem, aktif profil seç).
         Body: { "name": "Ali",
                 "new_name": "Veli", "education_period": "sinif_3", "set_active": true }

    DELETE /api/mathlock/children/detail/
         Çocuk profilini sil.
         Body: { "name": "Ali" }
    """
    device = request.user
    child_id = request.query_params.get('child_id') or request.data.get('child_id')

    if not child_id:
        return Response({'error': _('child_id_required')}, status=status.HTTP_400_BAD_REQUEST)

    try:
        child = ChildProfile.objects.get(device=device, id=child_id)
    except (ChildProfile.DoesNotExist, ValueError):
        return Response({'error': _('profile_not_found')}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        # Son profil silinemez
        if device.children.count() <= 1:
            return Response({'error': _('cannot_delete_last_profile')}, status=status.HTTP_400_BAD_REQUEST)
        was_active = child.is_active
        child.delete()
        # Silinen aktifse başkasını aktif yap
        if was_active:
            first = device.children.first()
            if first:
                first.is_active = True
                first.save(update_fields=['is_active'])
        return Response({'success': True})

    # PUT — güncelle
    update_fields = ['updated_at']

    new_name = request.data.get('new_name') or request.data.get('name')
    if new_name:
        new_name = _sanitize_child_name(new_name)
        if ChildProfile.objects.filter(device=device, name=new_name).exclude(pk=child.pk).exists():
            return Response({'error': _('profile_name_in_use').format(name=new_name)},
                            status=status.HTTP_409_CONFLICT)
        child.name = new_name
        update_fields.append('name')

    new_period = request.data.get('education_period')
    if new_period:
        if new_period not in _VALID_EDUCATION_PERIODS:
            return Response({'error': 'Geçersiz education_period'},
                            status=status.HTTP_400_BAD_REQUEST)
        child.education_period = new_period
        update_fields.append('education_period')

    set_active = request.data.get('set_active')
    if set_active:
        # Diğerlerini deaktif et
        device.children.exclude(pk=child.pk).update(is_active=False)
        child.is_active = True
        update_fields.append('is_active')

    child.save(update_fields=update_fields)

    return Response({
        'success': True,
        'child': {
            'name': child.name,
            'education_period': child.education_period,
            'is_active': child.is_active,
        },
    })


# ─── Çocuk Rapor ve İstatistik ──────────────────────────────────────────────

@api_view(['GET'])
def child_report(request):
    """
    Çocuğun performans raporunu döndür.

    GET /api/mathlock/children/report/?child_name=Ali
    Response: {
        "child": { name, education_period, accuracy, ... },
        "summary": { ... },
        "by_type": { ... },
        "weekly_report": { ... },
        "daily_history": [ ... ]
    }
    """
    device = request.user
    child_name = request.query_params.get('child_name', _('default_child_name'))

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    # Tip bazlı istatistik analizi
    by_type = {}
    stats = child.stats_json or {}
    by_type_raw = stats.get('byType', {})

    for tip, data in by_type_raw.items():
        shown = data.get('shown', 0)
        correct = data.get('correct', 0)
        accuracy = (correct / shown * 100) if shown > 0 else 0

        # Kategori belirle
        avg_time_str = str(data.get('avgTime', '0')).replace(',', '.')
        try:
            avg_time = float(avg_time_str)
        except ValueError:
            avg_time = 0.0

        if accuracy >= 85 and avg_time < 5:
            category = _('category_master')
        elif accuracy >= 85:
            category = _('category_secure')
        elif accuracy >= 60:
            category = _('category_developing')
        elif accuracy >= 40:
            category = _('category_challenging')
        else:
            category = _('category_critical')

        by_type[tip] = {
            'shown': shown,
            'correct': correct,
            'accuracy': round(accuracy, 1),
            'avgTime': round(avg_time, 1),
            'hintUsed': data.get('hintUsed', 0),
            'topicUsed': data.get('topicUsed', 0),
            'category': category,
        }

    # Toplam set sayısı
    set_count = QuestionSet.objects.filter(child=child).count()

    return Response({
        'child': {
            'name': child.name,
            'education_period': child.education_period,
            'education_period_display': child.get_education_period_display(),
            'accuracy': round(child.accuracy * 100, 1),
            'total_correct': child.total_correct,
            'total_shown': child.total_shown,
            'total_time_seconds': child.total_time_seconds,
            'current_difficulty': child.current_difficulty,
            'question_count': child.question_count,
            'sets_completed': set_count,
            'created_at': child.created_at.isoformat(),
        },
        'by_type': by_type,
        'weekly_report': child.weekly_report_json or {},
        'daily_history': child.daily_stats or {},
    })


# ─── İstatistik Geçmişi (Dashboard Grafikleri İçin) ─────────────────────────

@api_view(['GET'])
def stats_history(request):
    """
    Çocuğun günlük/haftalık istatistik geçmişini döndür (grafik verisi).

    GET /api/mathlock/children/stats-history/?child_name=Ali
    """
    device = request.user
    child_name = request.query_params.get('child_name', _('default_child_name'))

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    # Günlük istatistikler
    daily_stats = child.daily_stats or {}

    # Tip bazlı istatistikler
    stats = child.stats_json or {}
    by_type_raw = stats.get('byType', {})
    by_type = {}
    for tip, data in by_type_raw.items():
        shown = data.get('shown', 0)
        correct = data.get('correct', 0)
        by_type[tip] = {
            'total': shown,
            'correct': correct,
            'accuracy': round((correct / shown * 100) if shown > 0 else 0, 1),
        }

    # Seri (streak) hesaplama — ardışık gün sayısı
    from datetime import date, timedelta
    streak = 0
    check_date = date.today()
    for __ in range(365):
        date_str = check_date.isoformat()
        day_data = daily_stats.get(date_str, {})
        if isinstance(day_data, dict) and day_data.get('solved', 0) > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return Response({
        'daily': daily_stats,
        'by_type': by_type,
        'streak_days': streak,
        'total_time_minutes': round(child.total_time_seconds / 60, 1),
        'total_correct': child.total_correct,
        'total_shown': child.total_shown,
        'accuracy': round(child.accuracy * 100, 1),
    })


# ─── Bulmaca Seviye Endpoint'leri ────────────────────────────────────────────

@api_view(['GET'])
def get_levels(request):
    """
    Çocuğun mevcut bulmaca seviye setini döndür.
    İlk istekte static levels.json'dan kişisel LevelSet oluşturulur.

    GET /api/mathlock/levels/[?child_id=N]
    Response: {
        "levels": [...],
        "version": 1,
        "set_id": 5,
        "completed_level_ids": [1, 2, 3],
        "total_levels": 12,
        "completed_count": 3
    }
    """
    device = request.user

    child_id = request.query_params.get('child_id')
    if child_id:
        child = ChildProfile.objects.filter(device=device, id=child_id).first()
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    if not child:
        return Response({'error': _('profile_not_found')}, status=status.HTTP_404_NOT_FOUND)

    level_set = LevelSet.objects.filter(child=child).order_by('-version').first()

    # Locale'e göre fallback levels dosyasını seç
    locale = request.query_params.get('locale', child.locale)[:10]
    if locale not in ('tr', 'en', 'de', 'fr', 'es'):
        locale = 'tr'
    fallback_locale_file = _DATA_DIR / f'fallback-levels.{locale}.json'
    if not fallback_locale_file.exists():
        fallback_locale_file = _DATA_DIR / 'fallback-levels.tr.json'

    if not level_set:
        # İlk erişim: locale'e özgü fallback levels'dan kişisel set oluştur
        try:
            if fallback_locale_file.exists():
                data = json.loads(fallback_locale_file.read_text(encoding='utf-8'))
                levels = data.get('levels', [])[:_LEVELS_COUNT]
            else:
                levels = []
        except Exception as e:
            logger.error("fallback levels okunamadı (%s): %s", fallback_locale_file.name, e)
            levels = []

        if not levels:
            return Response(
                {'error': _('levels_not_found')},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            level_set = LevelSet.objects.create(
                child=child,
                version=1,
                levels_json=levels,
                is_ai_generated=False,
                credit_used=False,
            )
        except IntegrityError:
            # Race condition: başka istek aynı anda oluşturdu
            level_set = LevelSet.objects.filter(child=child).order_by('-version').first()
        logger.info("İlk seviye seti oluşturuldu: child=%s", child.name)

    if not level_set:
        return Response(
            {'error': _('levels_not_found')},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    completed = level_set.completed_level_ids or []

    # Aktif generation job var mı? (client "hazırlanıyor" ekranı göstersin)
    generation_in_progress = GenerationJob.objects.filter(
        child=child, content_type='levels', status='running'
    ).exists()

    return Response({
        'levels': level_set.levels_json,
        'version': level_set.version,
        'set_id': level_set.pk,
        'completed_level_ids': completed,
        'total_levels': len(level_set.levels_json or []),
        'completed_count': len(completed),
        'locale': child.locale,
        'generation_in_progress': generation_in_progress,
    })


@api_view(['POST'])
def update_level_progress(request):
    """
    Tamamlanan bulmaca seviyelerini raporla.
    Tüm seviyeler biterse + kredi varsa → otomatik kredi düş + yeni set üret.

    POST /api/mathlock/levels/progress/
    Body: {
        "child_id": 1,
        "set_id": 5,
        "completed_level_ids": [1, 2, ..., 12],
        "level_stats": { "totalCompleted": 12, "totalStars": 28, ... }
    }
    Response: {
        "success": true,
        "completed_count": 12,
        "total_levels": 12,
        "all_completed": true,
        "auto_renewal_started": true,
        "credits_remaining": 4
    }
    """
    device = request.user

    child_id = request.data.get('child_id')
    if child_id:
        child = ChildProfile.objects.filter(device=device, id=child_id).first()
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    if not child:
        return Response({'error': _('profile_not_found')}, status=status.HTTP_404_NOT_FOUND)

    # İlerleme verilerini al
    set_id = request.data.get('set_id')
    completed_ids_raw = request.data.get('completed_level_ids', [])
    level_stats = request.data.get('level_stats', {})

    if not isinstance(completed_ids_raw, list):
        return Response({'error': _('completed_level_ids_must_be_list')}, status=status.HTTP_400_BAD_REQUEST)

    try:
        completed_ids = [int(lid) for lid in completed_ids_raw[:50]]
    except (ValueError, TypeError):
        return Response({'error': _('invalid_completed_level_ids')}, status=status.HTTP_400_BAD_REQUEST)

    # Level set'i bul, yoksa oluştur
    if set_id:
        level_set = LevelSet.objects.filter(pk=set_id, child=child).first()
    else:
        level_set = LevelSet.objects.filter(child=child).order_by('-version').first()

    if not level_set:
        # İlk erişim: locale'e özgü fallback levels'dan kişisel set oluştur
        locale = request.data.get('locale', child.locale)[:10]
        if locale not in ('tr', 'en', 'de', 'fr', 'es'):
            locale = 'tr'
        fallback_locale_file = _DATA_DIR / f'fallback-levels.{locale}.json'
        if not fallback_locale_file.exists():
            fallback_locale_file = _DATA_DIR / 'fallback-levels.tr.json'

        try:
            if fallback_locale_file.exists():
                data = json.loads(fallback_locale_file.read_text(encoding='utf-8'))
                levels = data.get('levels', [])[:_LEVELS_COUNT]
            else:
                levels = []
        except Exception as e:
            logger.error("fallback levels okunamadı (%s): %s", fallback_locale_file.name, e)
            levels = []

        if not levels:
            return Response(
                {'error': _('levels_not_found')},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            level_set = LevelSet.objects.create(
                child=child,
                version=1,
                levels_json=levels,
                is_ai_generated=False,
                credit_used=False,
            )
        except IntegrityError:
            # Race condition: başka istek aynı anda oluşturdu
            level_set = LevelSet.objects.filter(child=child).order_by('-version').first()
        logger.info("İlk seviye seti oluşturuldu (update_progress): child=%s, locale=%s", child.name, locale)

    if not level_set:
        return Response(
            {'error': _('levels_not_found')},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # İlerlemeyi güncelle
    existing = set(level_set.completed_level_ids or [])
    new_completed = set(completed_ids) - existing
    level_set.completed_level_ids = list(existing | set(completed_ids))
    level_set.save(update_fields=['completed_level_ids'])

    total_levels = len(level_set.levels_json or [])
    completed_count = len(level_set.completed_level_ids)
    all_completed = completed_count >= total_levels > 0

    auto_renewal_started = False
    credits_remaining = None

    # Yeni ilerleme + tüm bitti → otomatik yenile
    # NOT: len(new_completed)>0 kontrolü kaldırıldı.
    # Sebep: ilk yenileme başarısız olursa (örn. AI hata verirse) çocuk tekrar
    # aynı seti bitirdiğinde new_completed boş kalıyor ve yenileme hiçbir
    # zaman tekrar denenmiyordu (deadlock).
    # Yerine: daha yüksek versiyonlu set var mı + kilit var mı kontrolü eklendi.
    if all_completed:
        has_newer = LevelSet.objects.filter(child=child, version__gt=level_set.version).exists()
        # Süresi dolmuş ve çok eski kilitleri temizle (saat senkronizasyonu sorunlarına karşı)
        now = timezone.now()
        very_old = now - timedelta(seconds=_RENEWAL_LOCK_TTL * 2)
        RenewalLock.objects.filter(
            child_id=child.pk, content_type='levels',
            expires_at__lt=now
        ).delete()
        RenewalLock.objects.filter(
            child_id=child.pk, content_type='levels',
            created_at__lt=very_old
        ).delete()
        lock_exists = RenewalLock.objects.filter(child_id=child.pk, content_type='levels').exists()

        if has_newer:
            logger.info(
                "Seviye seti tamamlandı ama daha yeni set zaten mevcut: "
                "child=%s, version=%d",
                child.name, level_set.version
            )
            return Response({
                'success': True,
                'completed_count': completed_count,
                'total_levels': total_levels,
                'all_completed': all_completed,
                'auto_renewal_started': True,
                'credits_remaining': device.credits.balance,
            })
        elif lock_exists:
            logger.info(
                "Seviye seti tamamlandı ama yenileme zaten devam ediyor: "
                "child=%s, version=%d",
                child.name, level_set.version
            )
            return Response({
                'success': True,
                'completed_count': completed_count,
                'total_levels': total_levels,
                'all_completed': all_completed,
                'auto_renewal_started': True,
                'credits_remaining': device.credits.balance,
            })
        else:
            # Önce kredi düşmeyi dene (kredi varsa)
            success, is_free, cb_pk, credits_remaining = _deduct_credit_and_lock(
                child.pk, device, 'levels'
            )
            if success:
                auto_renewal_started = True
                task = generate_level_set.delay(
                    child.pk, cb_pk, is_free, _build_level_stats(child), child.education_period
                )
                logger.info(
                    "Otomatik seviye yenileme başlatıldı (Celery): "
                    "child=%s, is_free=%s, version=%d → %d, job=%s",
                    child.name, is_free, level_set.version, level_set.version + 1, task.id
                )
                return Response({
                    'success': True,
                    'completed_count': completed_count,
                    'total_levels': total_levels,
                    'all_completed': all_completed,
                    'auto_renewal_started': True,
                    'job_id': task.id,
                    'credits_remaining': credits_remaining or 0,
                })
            else:
                # Kredi yoksa bile ücretsiz yenile — Sayı Yolculuğu her zaman devam edebilmeli
                auto_renewal_started = True
                credits_remaining = credits_remaining or 0
                task = generate_level_set.delay(
                    child.pk, 0, True, _build_level_stats(child), child.education_period
                )
                logger.info(
                    "Otomatik seviye yenileme başlatıldı (Celery ücretsiz): "
                    "child=%s, version=%d → %d, job=%s",
                    child.name, level_set.version, level_set.version + 1, task.id
                )
                return Response({
                    'success': True,
                    'completed_count': completed_count,
                    'total_levels': total_levels,
                    'all_completed': all_completed,
                    'auto_renewal_started': True,
                    'job_id': task.id,
                    'credits_remaining': 0,
                })

    return Response({
        'success': True,
        'completed_count': completed_count,
        'total_levels': total_levels,
        'all_completed': all_completed,
        'auto_renewal_started': auto_renewal_started,
        **(({'credits_remaining': credits_remaining}) if auto_renewal_started else {}),
    })


# ─── Sayı Yolculuğu (Puzzle) API ────────────────────────────────────────────

@api_view(['POST'])
def get_puzzles(request):
    """
    Sayı Yolculuğu bulmaca setlerini listele.
    PuzzleSet yoksa otomatik üretim başlatır (async Celery).

    POST /api/mathlock/puzzles/
    Body: { "child_name": "Çocuk" }
    Response:
      - Varset: { "puzzle_sets": [...], "progress": {...}, "child_id": ... }
      - Yoksa: { "generation_in_progress": true, "job_id": "..." }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    sets = PuzzleSet.objects.filter(child=child).order_by('-version')

    if not sets.exists():
        # Halihazırda running bir puzzle generation job var mı?
        from .models import GenerationJob
        running_job = GenerationJob.objects.filter(
            child=child, content_type='puzzles', status='running'
        ).first()
        if running_job:
            return Response({
                'generation_in_progress': True,
                'job_id': str(running_job.pk),
            })

        # Yeni puzzle seti üret
        puzzle_stats = _build_puzzle_stats(child)
        task = generate_puzzle_set.delay(
            child.pk, 0, True, puzzle_stats, child.education_period
        )
        return Response({
            'generation_in_progress': True,
            'job_id': task.id,
        })

    # Progress bilgisini de ekle
    progress_map = {}
    for p in PuzzleProgress.objects.filter(child=child):
        v = str(p.puzzle_set_version)
        if v not in progress_map:
            progress_map[v] = {}
        progress_map[v][str(p.level_index)] = {
            'completed': p.completed,
            'stars': p.stars,
            'attempts': p.attempts,
            'best_cmd_count': p.best_cmd_count,
        }

    return Response({
        'puzzle_sets': [
            {
                'version': s.version,
                'puzzles': s.puzzles_json,
                'is_procedural': s.is_procedural,
                'generated_by': s.generated_by,
                'created_at': s.created_at.isoformat(),
            }
            for s in sets
        ],
        'progress': progress_map,
        'child_id': child.id,
    })


@api_view(['POST'])
def save_puzzle_progress(request):
    """
    Tek bir bulmaca seviyesinin ilerlemesini kaydet.

    POST /api/mathlock/puzzles/progress/
    Body: {
        "child_name": "Çocuk",
        "puzzle_set_version": 1,
        "level_index": 0,
        "completed": true,
        "stars": 3,
        "cmd_count": 4
    }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))
    data = request.data

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    version = data.get('puzzle_set_version', 1)
    level_index = data.get('level_index', 0)
    completed = bool(data.get('completed', False))
    stars = min(int(data.get('stars', 0)), 3)
    cmd_count = data.get('cmd_count')

    progress, created = PuzzleProgress.objects.get_or_create(
        child=child,
        puzzle_set_version=version,
        level_index=level_index,
        defaults={
            'completed': completed,
            'stars': stars,
            'best_cmd_count': cmd_count,
            'completed_at': timezone.now() if completed else None,
        }
    )

    if not created:
        # Conflict: sunucu kazansın ama stars maksimumu koru
        progress.stars = max(progress.stars, stars)
        progress.attempts += 1
        if completed and not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
        if cmd_count is not None:
            if progress.best_cmd_count is None or cmd_count < progress.best_cmd_count:
                progress.best_cmd_count = cmd_count
        progress.save(update_fields=['stars', 'attempts', 'completed', 'completed_at', 'best_cmd_count', 'updated_at'])
    else:
        if not completed:
            progress.attempts = 1
            progress.save(update_fields=['attempts'])

    return Response({
        'success': True,
        'progress': {
            'level_index': progress.level_index,
            'completed': progress.completed,
            'stars': progress.stars,
            'attempts': progress.attempts,
            'best_cmd_count': progress.best_cmd_count,
        },
    })


@api_view(['POST'])
def sync_puzzle_progress(request):
    """
    Cihazdaki tüm ilerlemeyi sunucuya senkronize et.

    POST /api/mathlock/puzzles/progress/sync/
    Body: {
        "child_name": "Çocuk",
        "progress": {
            "1": {  // puzzle_set_version
                "0": {"completed": true, "stars": 3},
                "1": {"completed": true, "stars": 2}
            }
        }
    }
    Response: { "synced": 5, "conflicts": 2, "server_progress": {...} }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))
    client_progress = request.data.get('progress', {})

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    synced = 0
    conflicts = 0

    with transaction.atomic():
        for version_str, levels in client_progress.items():
            version = int(version_str)
            for level_index_str, lvl_data in levels.items():
                level_index = int(level_index_str)
                completed = bool(lvl_data.get('completed', False))
                stars = min(int(lvl_data.get('stars', 0)), 3)
                cmd_count = lvl_data.get('cmd_count')

                progress, created = PuzzleProgress.objects.get_or_create(
                    child=child,
                    puzzle_set_version=version,
                    level_index=level_index,
                    defaults={
                        'completed': completed,
                        'stars': stars,
                        'best_cmd_count': cmd_count,
                        'completed_at': timezone.now() if completed else None,
                    }
                )

                if not created:
                    if stars > progress.stars or completed != progress.completed:
                        conflicts += 1
                    progress.stars = max(progress.stars, stars)
                    progress.attempts += 1
                    if completed and not progress.completed:
                        progress.completed = True
                        progress.completed_at = timezone.now()
                    if cmd_count is not None:
                        if progress.best_cmd_count is None or cmd_count < progress.best_cmd_count:
                            progress.best_cmd_count = cmd_count
                    progress.save(update_fields=['stars', 'attempts', 'completed', 'completed_at', 'best_cmd_count', 'updated_at'])
                else:
                    if not completed:
                        progress.attempts = 1
                        progress.save(update_fields=['attempts'])

                synced += 1

    # Tüm sunucu ilerlemesini döndür
    server_progress = {}
    for p in PuzzleProgress.objects.filter(child=child):
        v = str(p.puzzle_set_version)
        if v not in server_progress:
            server_progress[v] = {}
        server_progress[v][str(p.level_index)] = {
            'completed': p.completed,
            'stars': p.stars,
            'attempts': p.attempts,
            'best_cmd_count': p.best_cmd_count,
        }

    return Response({
        'success': True,
        'synced': synced,
        'conflicts': conflicts,
        'server_progress': server_progress,
    })


@api_view(['POST'])
def upload_puzzle_analytics(request):
    """
    Batch puzzle analytics olaylarını al ve kaydet.

    POST /api/mathlock/puzzles/analytics/
    Body: {
        "child_name": "Çocuk",
        "events": [
            {"event_type": "level_start", "payload": {"level_index": 0}, "timestamp": "..."}
        ]
    }
    """
    device = request.user
    child_name = _sanitize_child_name(request.data.get('child_name', _('default_child_name')))
    events = request.data.get('events', [])

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': _('child_profile_not_found').format(child_name=child_name)},
                        status=status.HTTP_404_NOT_FOUND)

    created = []
    for ev in events:
        payload = ev.get('payload', {})
        if 'timestamp' in ev:
            payload['client_timestamp'] = ev['timestamp']
        created.append(PuzzleAnalyticsEvent(
            device=device,
            child=child,
            event_type=ev.get('event_type', 'unknown')[:30],
            payload_json=payload,
        ))

    if created:
        PuzzleAnalyticsEvent.objects.bulk_create(created)

    return Response({
        'success': True,
        'saved': len(created),
    })


@api_view(['POST'])
def get_daily_challenge(request):
    """
    Günlük challenge bulmacası üret.
    Aynı gün herkes aynı seed'ten aynı seviyeyi görür.

    POST /api/mathlock/puzzles/daily/
    Body: { "date": "2026-05-24" }  // opsiyonel, varsayılan bugün
    """
    request_date = request.data.get('date')
    if request_date:
        try:
            year, month, day = request_date.split('-')
            challenge_date = date(int(year), int(month), int(day))
        except (ValueError, TypeError):
            return Response({'error': 'invalid_date_format'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        challenge_date = date.today()

    seed = int(challenge_date.strftime('%Y%m%d'))

    # Procedural üret — seed sabit olduğu için aynı gün aynı puzzle döner
    import subprocess as sp
    import tempfile as tf
    from pathlib import Path

    tmpdir = Path(tf.mkdtemp(prefix='mathlock-daily-'))
    script = Path(__file__).resolve().parent.parent.parent / 'procedural-puzzles.py'
    puzzle = None
    try:
        result = sp.run(
            ['python3', str(script),
             '--output', str(tmpdir / 'puzzles.json'),
             '--version', str(seed),
             '--seed', str(seed),
             '--count', '1'],
            capture_output=True, text=True, timeout=30,
            cwd=str(Path(__file__).resolve().parent.parent.parent),
        )
        if result.returncode == 0:
            data = json.loads((tmpdir / 'puzzles.json').read_text(encoding='utf-8'))
            puzzles = data.get('puzzles', [])
            if puzzles:
                puzzle = puzzles[0]
    except Exception as exc:
        logger.error("Daily challenge generation failed: %s", exc)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if puzzle is None:
        return Response({'error': 'generation_failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'date': challenge_date.isoformat(),
        'seed': seed,
        'puzzle': puzzle,
    })


@api_view(['GET'])
def get_leaderboard(request):
    """
    Skor tablosu.

    GET /api/mathlock/puzzles/leaderboard/?period=daily|weekly|all
    """
    period = request.query_params.get('period', 'all')
    from django.utils import timezone

    if period == 'daily':
        since = timezone.now() - timedelta(days=1)
    elif period == 'weekly':
        since = timezone.now() - timedelta(weeks=1)
    else:
        since = None

    qs = PuzzleProgress.objects.all()
    if since:
        qs = qs.filter(updated_at__gte=since)

    # Her çocuk için toplam skor hesapla
    scores = {}
    for p in qs.select_related('child'):
        child = p.child
        if child is None:
            continue
        cid = child.id
        if cid not in scores:
            scores[cid] = {
                'child_name': child.name,
                'total_stars': 0,
                'total_completed': 0,
                'best_cmd_sum': 0,
            }
        scores[cid]['total_stars'] += p.stars
        if p.completed:
            scores[cid]['total_completed'] += 1
        if p.best_cmd_count:
            scores[cid]['best_cmd_sum'] += p.best_cmd_count

    entries = []
    for cid, data in scores.items():
        # Skor formülü: stars * 100 + completed * 50
        score = data['total_stars'] * 100 + data['total_completed'] * 50
        entries.append({
            'child_name': data['child_name'],
            'total_stars': data['total_stars'],
            'total_completed': data['total_completed'],
            'score': score,
        })

    entries.sort(key=lambda x: x['score'], reverse=True)

    return Response({
        'period': period,
        'entries': entries[:50],  # İlk 50
    })



# ─── Crash Report (ACRA) ────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([CrashReportThrottle])
@csrf_exempt
def report_crash(request):
    """
    ACRA'dan gelen çökme raporlarını kaydet.

    POST /api/mathlock/crash-reports/
    Body: ACRA JSON report
    Response: { "success": true, "id": 123 }
    """
    data = request.data

    # ACRA'nın standart alanlarını maple
    device_id = data.get('CUSTOM_DATA', {}).get('device_id_hash', '')
    if not device_id:
        device_id = data.get('INSTALLATION_ID', '')

    crash_type = data.get('EXCEPTION_CLASSNAME', '')
    stack_trace = data.get('STACK_TRACE', '')

    # Aynı crash_type + device_id + stack_trace fingerprint varsa occurrence_count artır
    # (Basit grouping: son 24 saat içinde aynı crash_type + device_id varsa count artır)
    from django.utils import timezone
    from datetime import timedelta

    existing = CrashReport.objects.filter(
        crash_type=crash_type,
        device_id=device_id,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).first()

    if existing:
        existing.occurrence_count += 1
        existing.save(update_fields=['occurrence_count'])
        return Response({'success': True, 'id': existing.id, 'grouped': True})

    report = CrashReport.objects.create(
        device_id=device_id,
        device_fingerprint=data.get('DEVICE_ID', ''),
        app_version_code=int(data.get('APP_VERSION_CODE', 0)),
        app_version_name=data.get('APP_VERSION_NAME', ''),
        android_version=data.get('ANDROID_VERSION', ''),
        sdk_version=int(data.get('SDK_VERSION', 0)),
        device_model=data.get('PHONE_MODEL', ''),
        device_manufacturer=data.get('BRAND', ''),
        stack_trace=stack_trace,
        crash_type=crash_type,
        crash_message=data.get('EXCEPTION_MESSAGE', ''),
        thread_name=data.get('THREAD_DETAILS', ''),
        custom_data=data.get('CUSTOM_DATA', {}),
    )

    logger.info("Crash report received: %s on %s v%s",
                crash_type, report.device_model, report.app_version_name)

    return Response({'success': True, 'id': report.id})

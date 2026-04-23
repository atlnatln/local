import json
import logging
import re
import subprocess
import threading
import uuid
import tempfile
import shutil
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import (ChildProfile, CreditBalance, CreditPackage,
                     Device, LevelSet, PurchaseRecord, Question, QuestionSet,
                     RenewalLock, UserQuestionProgress)
from .google_play import verify_purchase

logger = logging.getLogger(__name__)

# ─── Input Sanitization ─────────────────────────────────────────────────────

_SAFE_NAME_RE = re.compile(r'[^\w\s\-]', re.UNICODE)


def _sanitize_child_name(name: str) -> str:
    """Çocuk adını sanitize et — max 100 karakter, zararlı karakter temizle."""
    name = str(name).strip()[:100]
    name = _SAFE_NAME_RE.sub('', name)
    return name or 'Çocuk'


# ─── Soru Üretimi (kimi-cli + AGENTS.md) ──────────────────────────────────

# Proje dizini: backend/ → üst dizin = mathlock-play/
_PROJECT_DIR = Path(settings.BASE_DIR).parent
_DATA_DIR = _PROJECT_DIR / 'data'
_GENERATE_SCRIPT = _PROJECT_DIR / 'ai-generate.sh'
_GENERATE_TIMEOUT = 180  # saniye

# Bulmaca seviye scripti
_GENERATE_LEVELS_SCRIPT = _PROJECT_DIR / 'ai-generate-levels.sh'
_LEVELS_FILE = _DATA_DIR / 'levels.json'
_LEVELS_COUNT = 12  # Her sette 12 seviye

# Yenileme kilidi TTL: 15 dakika (generation timeout 3 dk + tampon)
_RENEWAL_LOCK_TTL = 15 * 60  # saniye

# Dönem bazlı soru sayıları
_QUESTION_COUNTS = {
    'okul_oncesi': 30,
    'sinif_1': 40,
    'sinif_2': 50,
    'sinif_3': 50,
    'sinif_4': 50,
}

_VALID_EDUCATION_PERIODS = set(_QUESTION_COUNTS.keys())


def _generate_via_kimi(child_stats: dict, education_period: str = 'sinif_2') -> list:
    """
    ai-generate.sh + AGENTS.md ile kimi-cli kullanarak soru üret.

    Her çocuk için izole geçici dizin kullanır — eşzamanlı üretimlerde dosya çakışması olmaz.

    Akış:
      1. Geçici dizin oluştur (/tmp/mathlock-gen-<uuid>/)
      2. child_stats → tmpdir/stats.json yaz
      3. ai-generate.sh --vps-mode --skip-sync --period <dönem> --data-dir tmpdir çalıştır
      4. tmpdir/questions.json oku
      5. Geçici dizini temizle

    Hata durumunda RuntimeError fırlatır (use_credit krediyi iade eder).
    """
    if education_period not in _VALID_EDUCATION_PERIODS:
        education_period = 'sinif_2'

    expected_count = _QUESTION_COUNTS[education_period]

    tmpdir = Path(tempfile.mkdtemp(prefix='mathlock-gen-'))
    try:
        # Stats'ı geçici dizine yaz (ai-generate.sh bunu okur)
        (tmpdir / 'stats.json').write_text(
            json.dumps(child_stats, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # ai-generate.sh çalıştır
        if not _GENERATE_SCRIPT.exists():
            raise RuntimeError("ai-generate.sh bulunamadı")

        try:
            result = subprocess.run(
                ['bash', str(_GENERATE_SCRIPT), '--vps-mode', '--skip-sync',
                 '--period', education_period, '--data-dir', str(tmpdir)],
                capture_output=True, text=True,
                timeout=_GENERATE_TIMEOUT,
                cwd=str(_PROJECT_DIR),
            )
        except subprocess.TimeoutExpired:
            logger.error("ai-generate.sh %d saniye zaman aşımı", _GENERATE_TIMEOUT)
            raise RuntimeError("Soru üretimi zaman aşımına uğradı")

        if result.returncode != 0:
            logger.error("ai-generate.sh başarısız (rc=%d): %s",
                         result.returncode, result.stderr[-500:] if result.stderr else "")
            raise RuntimeError("Soru üretimi başarısız")

        # Üretilen soruları oku
        questions_file = tmpdir / 'questions.json'
        if not questions_file.exists():
            raise RuntimeError("questions.json üretilmedi")

        data = json.loads(questions_file.read_text(encoding='utf-8'))
        questions = data.get('questions', [])

        if len(questions) < expected_count:
            raise RuntimeError(f"Yetersiz soru: {len(questions)}/{expected_count}")

        logger.info(
            "kimi-cli soru üretimi başarılı: v%s, %d soru, dönem=%s",
            data.get('version', '?'), len(questions), education_period
        )

        # AGENTS.md formatından QuestionSet formatına dönüştür
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


# ─── Seviye Üretimi (ai-generate-levels.sh) ──────────────────────────────────

def _generate_levels_via_kimi(level_stats: dict = None, education_period: str = 'sinif_2') -> list:
    """
    ai-generate-levels.sh --vps-mode --period <dönem> ile 12 yeni bulmaca seviyesi üret.

    Her çocuk için izole geçici dizin kullanır — eşzamanlı üretimlerde dosya çakışması olmaz.

    Akış:
      1. Geçici dizin oluştur
      2. level_stats → tmpdir/level-stats.json yaz
      3. ai-generate-levels.sh --vps-mode --period <dönem> --data-dir tmpdir çalıştır
      4. tmpdir/levels.json oku → seviyeleri döndür
      5. Geçici dizini temizle

    Hata durumunda RuntimeError fırlatır.
    """
    if education_period not in _VALID_EDUCATION_PERIODS:
        education_period = 'sinif_2'

    if not _GENERATE_LEVELS_SCRIPT.exists():
        raise RuntimeError("ai-generate-levels.sh bulunamadı")

    tmpdir = Path(tempfile.mkdtemp(prefix='mathlock-levels-gen-'))
    try:
        # Stats'ı geçici dizine yaz (script okuyacak)
        if level_stats:
            (tmpdir / 'level-stats.json').write_text(
                json.dumps(level_stats, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )

        try:
            result = subprocess.run(
                ['bash', str(_GENERATE_LEVELS_SCRIPT), '--vps-mode',
                 '--period', education_period, '--data-dir', str(tmpdir)],
                capture_output=True, text=True,
                timeout=_GENERATE_TIMEOUT,
                cwd=str(_PROJECT_DIR),
            )
        except subprocess.TimeoutExpired:
            logger.error("ai-generate-levels.sh %d saniye zaman aşımı", _GENERATE_TIMEOUT)
            raise RuntimeError("Seviye üretimi zaman aşımına uğradı")

        if result.returncode != 0:
            logger.error("ai-generate-levels.sh başarısız (rc=%d): %s",
                         result.returncode, result.stderr[-500:] if result.stderr else "")
            raise RuntimeError("Seviye üretimi başarısız")

        levels_file = tmpdir / 'levels.json'
        if not levels_file.exists():
            raise RuntimeError("levels.json üretilmedi")

        data = json.loads(levels_file.read_text(encoding='utf-8'))
        levels = data.get('levels', [])

        if len(levels) < _LEVELS_COUNT:
            raise RuntimeError(f"Yetersiz seviye: {len(levels)}/{_LEVELS_COUNT}")

        logger.info(
            "Seviye üretimi başarılı: v%s, %d seviye", data.get('version', '?'), len(levels)
        )
        return levels[:_LEVELS_COUNT]
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
    }
    latest_ls = LevelSet.objects.filter(child=child).order_by('-version').first()
    if latest_ls:
        stats['completedLevelIds'] = latest_ls.completed_level_ids or []
        stats['totalCompleted'] = len(latest_ls.completed_level_ids or [])
        stats['totalLevels'] = len(latest_ls.levels_json or [])
        stats['lastVersion'] = latest_ls.version
    return stats


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

        report = {
            'generatedAt': today.isoformat(),
            'period': 'last_7_days',
            'totalSolved': total_solved,
            'totalCorrect': total_correct,
            'accuracy': weekly_acc,
            'totalTimeMinutes': round(total_time / 60, 1),
            'avgDailyMinutes': round(total_time / 60 / 7, 1),
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


def _auto_renew_questions(child_pk: int, credit_balance_pk: int, is_free: bool):
    """Background thread: matematik soru seti yenile."""
    from django.db import connection
    try:
        child = ChildProfile.objects.get(pk=child_pk)
        child_stats = _build_child_stats(child)
        questions = _generate_via_kimi(child_stats, child.education_period)

        latest = QuestionSet.objects.filter(child=child).order_by('-version').first()
        next_version = (latest.version + 1) if latest else 1

        QuestionSet.objects.create(
            child=child,
            version=next_version,
            questions_json=questions,
            is_ai_generated=True,
            credit_used=not is_free,
        )
        logger.info(
            "Otomatik soru yenileme başarılı: child=%s, v%d, %d soru",
            child.name, next_version, len(questions)
        )
    except Exception as exc:
        logger.error("Otomatik soru yenileme hatası: %s", exc)
        _refund_credit(credit_balance_pk, is_free)
    finally:
        _release_renewal_lock(child_pk, 'questions')
        from django.db import connection as _conn
        _conn.close()


def _auto_renew_levels(child_pk: int, credit_balance_pk: int, is_free: bool, level_stats: dict):
    """Background thread: bulmaca seviye seti yenile."""
    try:
        child = ChildProfile.objects.get(pk=child_pk)
        levels = _generate_levels_via_kimi(level_stats, child.education_period)

        latest = LevelSet.objects.filter(child=child).order_by('-version').first()
        next_version = (latest.version + 1) if latest else 1

        LevelSet.objects.create(
            child=child,
            version=next_version,
            levels_json=levels,
            is_ai_generated=True,
            credit_used=not is_free,
        )
        logger.info(
            "Otomatik seviye yenileme başarılı: child=%s, v%d, %d seviye",
            child.name, next_version, len(levels)
        )
    except Exception as exc:
        logger.error("Otomatik seviye yenileme hatası: %s", exc)
        _refund_credit(credit_balance_pk, is_free)
    finally:
        _release_renewal_lock(child_pk, 'levels')
        from django.db import connection as _conn
        _conn.close()


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
    Sunucu çökerse _RENEWAL_LOCK_TTL (15 dk) sonra otomatik geçersiz sayılır.
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

        # Süresi dolmuş kilidi temizle
        RenewalLock.objects.filter(
            child_id=child_pk, content_type=content_type, expires_at__lt=now
        ).delete()

        # Kilit var mı?
        if RenewalLock.objects.filter(child_id=child_pk, content_type=content_type).exists():
            logger.info(
                "Yenileme zaten devam ediyor, atlandı: child_pk=%d, type=%s",
                child_pk, content_type,
            )
            return False, False, 0, 0

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
                success, is_free, cb_pk, _ = _deduct_credit_and_lock(child.pk, device, 'questions')
                if success:
                    _run_in_background(_auto_renew_questions, child.pk, cb_pk, is_free)
                    logger.info(
                        "Satın alma sonrası matematik yenileme başlatıldı: child=%s, is_free=%s",
                        child.name, is_free,
                    )
                else:
                    logger.info("Satın alma sonrası yenileme: kredi yetmedi veya kilitli (child=%s)", child.name)

            # ── 2. Öncelik: Bulmaca seviyeleri ──────────────────────────────
            latest_ls = LevelSet.objects.filter(child=child).order_by('-version').first()
            if latest_ls:
                total_lvl = len(latest_ls.levels_json or [])
                done_lvl = len(latest_ls.completed_level_ids or [])
                if total_lvl > 0 and done_lvl >= total_lvl:
                    success, is_free, cb_pk, _ = _deduct_credit_and_lock(child.pk, device, 'levels')
                    if success:
                        _run_in_background(_auto_renew_levels, child.pk, cb_pk, is_free, _build_level_stats(child))
                        logger.info(
                            "Satın alma sonrası seviye yenileme başlatıldı: child=%s, is_free=%s",
                            child.name, is_free,
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


# ─── Cihaz Kayıt ────────────────────────────────────────────────────────────

@api_view(['POST'])
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
        return Response({'error': 'installation_id gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    # Sanitize
    installation_id = installation_id.strip()[:255]

    device, created = Device.objects.get_or_create(
        installation_id=installation_id,
        defaults={'device_token': uuid.uuid4()}
    )

    # Yeni cihaz için kredi bakiyesi ve çocuk profili oluştur
    credit_balance, _ = CreditBalance.objects.get_or_create(device=device)
    child, _ = ChildProfile.objects.get_or_create(device=device, name="Çocuk")

    if not created:
        device.save(update_fields=['last_seen'])

    return Response({
        'device_token': str(device.device_token),
        'credits': credit_balance.balance,
        'free_set_used': credit_balance.free_set_used,
        'child_name': child.name,
        'education_period': child.education_period,
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
    device_token = request.data.get('device_token')
    purchase_token = request.data.get('purchase_token')
    product_id = request.data.get('product_id')

    if not all([device_token, purchase_token, product_id]):
        return Response(
            {'error': 'device_token, purchase_token ve product_id gerekli'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cihaz doğrulama
    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    # Ürün ID → kredi miktarı (erken kontrol — DB'ye gitmeden önce geçersiz ürünü reddet)
    credits_map = getattr(settings, 'CREDITS_PER_PURCHASE', {})
    credits_to_add = credits_map.get(product_id, 0)
    if credits_to_add == 0:
        return Response({'error': f'Geçersiz product_id: {product_id}'}, status=status.HTTP_400_BAD_REQUEST)

    DEBUG_TOKEN_PREFIX = "DEBUG_TEST_TOKEN_"

    # ─── Tek atomic blok: race condition'ı önler ──────────────────────────
    # select_for_update(): aynı token'ın eşzamanlı işlenmesini DB seviyesinde kilitler.
    # IntegrityError: "select" ile "create" arasındaki nadir race için son savunma hattı.
    try:
        with transaction.atomic():
            existing = PurchaseRecord.objects.select_for_update().filter(
                purchase_token=purchase_token
            ).first()

            if existing:
                if existing.verified:
                    credit_balance, _ = CreditBalance.objects.get_or_create(device=device)
                    return Response({
                        'success': True,
                        'credits_added': existing.credits_added,
                        'total_credits': credit_balance.balance,
                        'message': 'Bu satın alma zaten işlendi',
                    })
                return Response(
                    {'error': 'Bu purchase_token zaten kayıtlı ama doğrulanmamış'},
                    status=status.HTTP_409_CONFLICT,
                )

            # DEBUG token bypass — yalnızca settings.DEBUG=True devrede iken
            if purchase_token.startswith(DEBUG_TOKEN_PREFIX):
                if not settings.DEBUG:
                    logger.warning("Üretim ortamında debug token reddedildi: %s", purchase_token[:30])
                    return Response({'error': 'Debug token üretimde geçersiz'}, status=status.HTTP_403_FORBIDDEN)
                logger.info("DEV DEBUG: Test token kabul edildi: %s", purchase_token[:40])
                PurchaseRecord.objects.create(
                    device=device,
                    purchase_token=purchase_token,
                    product_id=product_id,
                    order_id=f"DEBUG_{purchase_token[:40]}",
                    credits_added=credits_to_add,
                    verified=True,
                    verification_response={"debug": True},
                )
                credit_balance, _ = CreditBalance.objects.get_or_create(device=device)
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

            if verification.get('valid'):
                record.verified = True
                record.order_id = verification.get('order_id', '')
                record.credits_added = credits_to_add
                record.save()

                credit_balance, _ = CreditBalance.objects.get_or_create(device=device)
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
                error_msg = verification.get('error', 'Doğrulama başarısız')
                logger.warning("Satın alma doğrulanamadı: device=%s, error=%s",
                               device.installation_id[:12], error_msg)
                return Response({'success': False, 'error': error_msg},
                                status=status.HTTP_402_PAYMENT_REQUIRED)

    except IntegrityError:
        # İki eşzamanlı istek aynı anda "existing yok" gördüyse DB unique constraint devreye girer
        logger.warning("Race condition yakalandı — aynı purchase_token eşzamanlı işlendi: %s",
                       purchase_token[:40])
        return Response(
            {'error': 'Bu token eşzamanlı başka bir istek tarafından işlendi, lütfen bakiyenizi kontrol edin'},
            status=status.HTTP_409_CONFLICT,
        )


# ─── Kredi Sorgulama ────────────────────────────────────────────────────────

@api_view(['GET'])
def get_credits(request):
    """
    Kredi bakiyesini sorgula.

    GET /api/mathlock/credits/?device_token=uuid
    Response: { "credits": 10, "total_purchased": 10, "total_used": 0, "free_set_used": false }
    """
    device_token = request.query_params.get('device_token')
    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    credit_balance, _ = CreditBalance.objects.get_or_create(device=device)

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
    device_token = request.data.get('device_token')
    child_name = _sanitize_child_name(request.data.get('child_name', 'Çocuk'))
    stats = request.data.get('stats', {})

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': f'"{child_name}" isimli profil bulunamadı'},
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
                    'error': 'Kredi yok',
                    'credits_remaining': 0,
                }, status=status.HTTP_402_PAYMENT_REQUIRED)

    # ─── kimi-cli + AGENTS.md ile kişiye özel soru üret ──────────────────
    try:
        questions = _generate_via_kimi(child.stats_json or {}, child.education_period)
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
            {'error': f'Soru üretimi başarısız: {exc}', 'credits_refunded': True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # QuestionSet version: mevcut en yüksek + 1
    latest = QuestionSet.objects.filter(child=child).order_by('-version').first()
    next_version = (latest.version + 1) if latest else 1

    question_set = QuestionSet.objects.create(
        child=child,
        version=next_version,
        questions_json=questions,
        is_ai_generated=True,
        credit_used=not is_free,
    )

    logger.info(
        "kimi-cli soru seti: child=%s, v%d, %d soru, is_free=%s",
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
        "device_token": "uuid",
        "child_name": "Çocuk",
        "question_version": 1,
        "stats": { ... StatsTracker formatında ... }
    }
    """
    device_token = request.data.get('device_token')
    child_name = _sanitize_child_name(request.data.get('child_name', 'Çocuk'))
    stats = request.data.get('stats', {})
    question_version = request.data.get('question_version', 0)

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': f'"{child_name}" isimli profil bulunamadı'},
                        status=status.HTTP_404_NOT_FOUND)

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
def health(request):
    """GET /api/mathlock/health/"""
    return Response({'status': 'ok', 'service': 'mathlock-backend'})


# ─── Dinamik Paket Listesi ───────────────────────────────────────────────────

@api_view(['GET'])
def get_packages(request):
    """
    Güncel kredi paket listesini döndür.
    Önce DB'ye bakar (admin panelinden yönetilebilir), DB boşsa settings.py'den okur.

    GET /api/mathlock/packages/
    Response: {
        "packages": [
            { "product_id": "kredi_1",  "display_name": "Başlangıç", "credits": 1,  "questions_count": 50 },
            { "product_id": "kredi_5",  "display_name": "Standart",  "credits": 5,  "questions_count": 250 },
            { "product_id": "kredi_10", "display_name": "Süper",     "credits": 10, "questions_count": 500 }
        ],
        "source": "db" | "settings"
    }
    """
    db_packages = CreditPackage.objects.filter(is_active=True)

    if db_packages.exists():
        data = [
            {
                'product_id': p.product_id,
                'display_name': p.display_name,
                'credits': p.credits,
                'questions_count': p.questions_count,
                'description': p.description,
                'sort_order': p.sort_order,
            }
            for p in db_packages
        ]
        return Response({'packages': data, 'source': 'db'})

    # Fallback: settings.py'deki statik tanım
    credits_map = getattr(settings, 'CREDITS_PER_PURCHASE', {})
    questions_per_credit = getattr(settings, 'QUESTIONS_PER_CREDIT', 50)

    # Makul bir görüntü adı üret
    display_names = {
        'kredi_1': 'Başlangıç Paketi',
        'kredi_5': 'Standart Paket',
        'kredi_10': 'Süper Paket',
    }

    data = sorted(
        [
            {
                'product_id': pid,
                'display_name': display_names.get(pid, pid),
                'credits': credits,
                'questions_count': credits * questions_per_credit,
                'description': '',
                'sort_order': i,
            }
            for i, (pid, credits) in enumerate(credits_map.items())
        ],
        key=lambda x: x['credits'],
    )
    return Response({'packages': data, 'source': 'settings'})


# ─── Email Kayıt ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@throttle_classes([RegisterThrottle])
def register_email(request):
    """
    Cihaza e-posta bağla — kredi satın almak için gerekli.

    POST /api/mathlock/auth/register-email/
    Body: { "device_token": "uuid", "email": "user@example.com" }
    Response: { "success": true, "email": "user@example.com" }
    """
    device_token = request.data.get('device_token')
    email = request.data.get('email', '').strip().lower()

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)
    if not email:
        return Response({'error': 'email gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    # Basit email doğrulama
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return Response({'error': 'Geçersiz email formatı'}, status=status.HTTP_400_BAD_REQUEST)
    if len(email) > 254:
        return Response({'error': 'Email çok uzun'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

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
                    child.delete()
                else:
                    child.device = device
                    child.save(update_fields=['device'])

            # CreditBalance transfer: bakiyeleri birleştir
            old_credits = CreditBalance.objects.filter(device=old_device).first()
            if old_credits:
                new_credits, _ = CreditBalance.objects.get_or_create(device=device)
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

    # Transfer sonrası güncel bakiyeyi döndür
    credit_balance, _ = CreditBalance.objects.get_or_create(device=device)

    logger.info("Email kaydedildi: device=%s, email=%s, recovered=%s",
                device.installation_id[:12], email, recovered)
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

    GET /api/mathlock/questions/?device_token=uuid
    Response: {
        "questions": [ { id, text, answer, type, difficulty, hint, batch, solved, source } ],
        "total_questions": 100,
        "solved_count": 35,
        "unsolved_count": 65,
        "ai_sets": 2
    }
    """
    device_token = request.query_params.get('device_token')
    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    question_list = []

    # Aktif çocuğu belirle (tüm sorgularda kullanılacak)
    child_id = request.query_params.get('child_id')
    if child_id:
        child = ChildProfile.objects.filter(device=device, id=child_id).first()
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    # ── 1. Ücretsiz batch 0 soruları (Question model) ────────────────────
    free_questions = Question.objects.filter(batch_number=0).order_by('question_id')

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
        "device_token": "uuid",
        "solved_questions": [1, 3, 7, 1002, 1005],  // global ID'ler
        "reset_rotation": false
    }
    """
    device_token = request.data.get('device_token')
    solved_ids = request.data.get('solved_questions', [])
    reset_rotation = request.data.get('reset_rotation', False)

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(solved_ids, list):
        return Response({'error': 'solved_questions liste olmalı'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        solved_ids = [int(qid) for qid in solved_ids[:500]]
    except (ValueError, TypeError):
        return Response({'error': 'solved_questions geçersiz'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    # child_id varsa onu kullan, yoksa aktif profili bul
    child_id_param = request.data.get('child_id')
    if child_id_param:
        _target_child = ChildProfile.objects.filter(device=device, id=child_id_param).first()
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
                set_pk, _ = _parse_ai_global_id(gid)
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
                _run_in_background(_auto_renew_questions, _target_child.pk, cb_pk, is_free)
                logger.info(
                    "Otomatik matematik yenileme başlatıldı: child=%s, is_free=%s",
                    _target_child.name, is_free
                )

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
    GET  /api/mathlock/children/?device_token=uuid
         Cihaza bağlı tüm çocuk profillerini listele.

    POST /api/mathlock/children/
         Yeni çocuk profili oluştur.
         Body: { "device_token": "uuid", "name": "Ali", "education_period": "sinif_1" }
    """
    device_token = request.data.get('device_token') or request.query_params.get('device_token')
    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

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
            {'error': f'Geçersiz education_period. Geçerli: {sorted(_VALID_EDUCATION_PERIODS)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Max 5 çocuk profili
    if device.children.count() >= 5:
        return Response({'error': 'Maksimum 5 çocuk profili oluşturulabilir'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        child = ChildProfile.objects.create(
            device=device, name=name, education_period=education_period, is_active=False,
        )
    except IntegrityError:
        return Response({'error': f'"{name}" isimli profil zaten mevcut'},
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
         Body: { "device_token": "uuid", "name": "Ali",
                 "new_name": "Veli", "education_period": "sinif_3", "set_active": true }

    DELETE /api/mathlock/children/detail/
         Çocuk profilini sil.
         Body: { "device_token": "uuid", "name": "Ali" }
    """
    device_token = request.data.get('device_token') or request.query_params.get('device_token')
    child_id = request.query_params.get('child_id') or request.data.get('child_id')

    if not device_token or not child_id:
        return Response({'error': 'device_token ve child_id gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    try:
        child = ChildProfile.objects.get(device=device, id=child_id)
    except (ChildProfile.DoesNotExist, ValueError):
        return Response({'error': 'Profil bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        # Son profil silinemez
        if device.children.count() <= 1:
            return Response({'error': 'Son profil silinemez'}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'error': f'"{new_name}" ismi zaten kullanılıyor'},
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

    GET /api/mathlock/children/report/?device_token=uuid&child_name=Ali
    Response: {
        "child": { name, education_period, accuracy, ... },
        "summary": { ... },
        "by_type": { ... },
        "weekly_report": { ... },
        "daily_history": [ ... ]
    }
    """
    device_token = request.query_params.get('device_token')
    child_name = request.query_params.get('child_name', 'Çocuk')

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': f'"{child_name}" isimli profil bulunamadı'},
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
            category = 'USTA'
        elif accuracy >= 85:
            category = 'GÜVENLİ'
        elif accuracy >= 60:
            category = 'GELİŞEN'
        elif accuracy >= 40:
            category = 'ZORLU'
        else:
            category = 'KRİTİK'

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

    GET /api/mathlock/children/stats-history/?device_token=uuid&child_name=Ali
    """
    device_token = request.query_params.get('device_token')
    child_name = request.query_params.get('child_name', 'Çocuk')

    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    try:
        child = ChildProfile.objects.get(device=device, name=child_name)
    except ChildProfile.DoesNotExist:
        return Response({'error': f'"{child_name}" isimli profil bulunamadı'},
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
    for _ in range(365):
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

    GET /api/mathlock/levels/?device_token=uuid[&child_id=N]
    Response: {
        "levels": [...],
        "version": 1,
        "set_id": 5,
        "completed_level_ids": [1, 2, 3],
        "total_levels": 12,
        "completed_count": 3
    }
    """
    device_token = request.query_params.get('device_token')
    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    child_id = request.query_params.get('child_id')
    if child_id:
        child = ChildProfile.objects.filter(device=device, id=child_id).first()
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    if not child:
        return Response({'error': 'Profil bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    level_set = LevelSet.objects.filter(child=child).order_by('-version').first()

    if not level_set:
        # İlk erişim: static levels.json'dan kişisel set oluştur
        try:
            if _LEVELS_FILE.exists():
                data = json.loads(_LEVELS_FILE.read_text(encoding='utf-8'))
                levels = data.get('levels', [])[:_LEVELS_COUNT]
            else:
                levels = []
        except Exception as e:
            logger.error("levels.json okunamadı: %s", e)
            levels = []

        if not levels:
            return Response(
                {'error': 'Seviye verisi bulunamadı'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        level_set = LevelSet.objects.create(
            child=child,
            version=1,
            levels_json=levels,
            is_ai_generated=False,
            credit_used=False,
        )
        logger.info("İlk seviye seti oluşturuldu: child=%s", child.name)

    completed = level_set.completed_level_ids or []

    return Response({
        'levels': level_set.levels_json,
        'version': level_set.version,
        'set_id': level_set.pk,
        'completed_level_ids': completed,
        'total_levels': len(level_set.levels_json or []),
        'completed_count': len(completed),
    })


@api_view(['POST'])
def update_level_progress(request):
    """
    Tamamlanan bulmaca seviyelerini raporla.
    Tüm seviyeler biterse + kredi varsa → otomatik kredi düş + yeni set üret.

    POST /api/mathlock/levels/progress/
    Body: {
        "device_token": "uuid",
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
    device_token = request.data.get('device_token')
    if not device_token:
        return Response({'error': 'device_token gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    child_id = request.data.get('child_id')
    if child_id:
        child = ChildProfile.objects.filter(device=device, id=child_id).first()
    else:
        child = device.children.filter(is_active=True).first() or device.children.first()

    if not child:
        return Response({'error': 'Profil bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    # İlerleme verilerini al
    set_id = request.data.get('set_id')
    completed_ids_raw = request.data.get('completed_level_ids', [])
    level_stats = request.data.get('level_stats', {})

    if not isinstance(completed_ids_raw, list):
        return Response({'error': 'completed_level_ids liste olmalı'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        completed_ids = [int(lid) for lid in completed_ids_raw[:50]]
    except (ValueError, TypeError):
        return Response({'error': 'completed_level_ids geçersiz'}, status=status.HTTP_400_BAD_REQUEST)

    # Level set'i bul
    if set_id:
        level_set = LevelSet.objects.filter(pk=set_id, child=child).first()
    else:
        level_set = LevelSet.objects.filter(child=child).order_by('-version').first()

    if not level_set:
        return Response({'error': 'Seviye seti bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

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

    # Yeni ilerleme + tüm bitti + kredi var → otomatik yenile
    if all_completed and len(new_completed) > 0:
        success, is_free, cb_pk, credits_remaining = _deduct_credit_and_lock(
            child.pk, device, 'levels'
        )
        if success:
            auto_renewal_started = True
            _run_in_background(_auto_renew_levels, child.pk, cb_pk, is_free, _build_level_stats(child))
            logger.info(
                "Otomatik seviye yenileme başlatıldı: child=%s, is_free=%s",
                child.name, is_free
            )

    return Response({
        'success': True,
        'completed_count': completed_count,
        'total_levels': total_levels,
        'all_completed': all_completed,
        'auto_renewal_started': auto_renewal_started,
        **(({'credits_remaining': credits_remaining}) if auto_renewal_started else {}),
    })


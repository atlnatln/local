import json
import logging
import re
import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import (ChildProfile, CreditBalance, CreditPackage,
                     Device, PurchaseRecord, Question, QuestionSet, UserQuestionProgress)
from .google_play import verify_purchase

logger = logging.getLogger(__name__)

# ─── Input Sanitization ─────────────────────────────────────────────────────

_SAFE_NAME_RE = re.compile(r'[^\w\s\-]', re.UNICODE)


def _sanitize_child_name(name: str) -> str:
    """Çocuk adını sanitize et — max 100 karakter, zararlı karakter temizle."""
    name = str(name).strip()[:100]
    name = _SAFE_NAME_RE.sub('', name)
    return name or 'Çocuk'


# ─── Soru Üretimi (Copilot CLI + AGENTS.md) ─────────────────────────────────

# Proje dizini: backend/ → üst dizin = mathlock-play/
_PROJECT_DIR = Path(settings.BASE_DIR).parent
_DATA_DIR = _PROJECT_DIR / 'data'
_GENERATE_SCRIPT = _PROJECT_DIR / 'ai-generate.sh'
_GENERATE_TIMEOUT = 180  # saniye


def _generate_via_copilot(child_stats: dict) -> list:
    """
    ai-generate.sh + AGENTS.md ile Copilot CLI kullanarak 50 soru üret.

    Akış:
      1. child_stats → data/stats.json yaz
      2. ai-generate.sh --vps-mode --skip-sync çalıştır
      3. data/questions.json oku
      4. 50 soruyu döndür

    Hata durumunda RuntimeError fırlatır (use_credit krediyi iade eder).
    """
    _DATA_DIR.mkdir(exist_ok=True)

    # Stats'ı data/stats.json'a yaz (ai-generate.sh bunu okur)
    stats_file = _DATA_DIR / 'stats.json'
    stats_file.write_text(
        json.dumps(child_stats, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    # ai-generate.sh çalıştır
    if not _GENERATE_SCRIPT.exists():
        raise RuntimeError("ai-generate.sh bulunamadı")

    try:
        result = subprocess.run(
            ['bash', str(_GENERATE_SCRIPT), '--vps-mode', '--skip-sync'],
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
    questions_file = _DATA_DIR / 'questions.json'
    if not questions_file.exists():
        raise RuntimeError("questions.json üretilmedi")

    data = json.loads(questions_file.read_text(encoding='utf-8'))
    questions = data.get('questions', [])

    if len(questions) < 50:
        raise RuntimeError(f"Yetersiz soru: {len(questions)}/50")

    logger.info(
        "Copilot CLI soru üretimi başarılı: v%s, %d soru",
        data.get('version', '?'), len(questions)
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
        for q in questions[:50]
    ]


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
                return Response({
                    'success': True,
                    'credits_added': credits_to_add,
                    'total_credits': credit_balance.balance,
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

                return Response({
                    'success': True,
                    'credits_added': credits_to_add,
                    'total_credits': credit_balance.balance,
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

    child, _ = ChildProfile.objects.get_or_create(device=device, name=child_name)

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

    # ─── Copilot CLI + AGENTS.md ile kişiye özel 50 soru üret ─────────────
    try:
        questions = _generate_via_copilot(child.stats_json or {})
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
        "Copilot CLI soru seti: child=%s, v%d, %d soru, is_free=%s",
        child.name, next_version, len(questions), is_free
    )

    return Response({
        'success': True,
        'credits_remaining': credit_balance.balance,
        'is_free': is_free,
        'questions_generated': len(questions),
        'set_version': next_version,
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

    child, _ = ChildProfile.objects.get_or_create(device=device, name=child_name)

    # Kümülatif istatistik güncelle
    total_correct = stats.get('totalCorrect', 0)
    total_shown = stats.get('totalShown', 0)
    child.total_correct += total_correct
    child.total_shown += total_shown

    # Zorluk seviyesi ayarla (doğruluk oranına göre)
    if child.total_shown >= 10:
        accuracy = child.total_correct / child.total_shown
        if accuracy >= 0.85 and child.current_difficulty < 5:
            child.current_difficulty += 1
        elif accuracy < 0.5 and child.current_difficulty > 1:
            child.current_difficulty -= 1

    child.stats_json = stats
    child.save()

    # ai-generate.sh için stats dosyasını da güncelle
    try:
        stats_path = _DATA_DIR / 'stats.json'
        _DATA_DIR.mkdir(exist_ok=True)
        stats_path.write_text(
            json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8'
        )
    except Exception as e:
        logger.warning("data/stats.json yazılamadı: %s", e)

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
                    device=device, question=progress.question
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

    # ── 1. Ücretsiz batch 0 soruları (Question model) ────────────────────
    free_questions = Question.objects.filter(batch_number=0).order_by('question_id')
    free_solved_ids = set(
        UserQuestionProgress.objects.filter(
            device=device, solved=True
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
    child = ChildProfile.objects.filter(device=device).first()
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
        return Response({'error': 'solved_questions geçerli ID listesi olmalı'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(device_token=device_token)
    except (Device.DoesNotExist, ValidationError):
        return Response({'error': 'Geçersiz device_token'}, status=status.HTTP_404_NOT_FOUND)

    if reset_rotation:
        # Batch 0 ilerlemeyi sıfırla
        UserQuestionProgress.objects.filter(device=device).update(solved=False)
        # AI set ilerlemeyi sıfırla
        child = ChildProfile.objects.filter(device=device).first()
        if child:
            QuestionSet.objects.filter(child=child).update(solved_ids=[])
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
                device=device, question=question
            )
            if not progress.solved or created:
                progress.solved = True
                progress.solve_count += 1
                progress.save()
                updated += 1

    # AI set soruları (global ID >= _AI_SET_ID_OFFSET)
    ai_ids = [qid for qid in solved_ids if qid >= _AI_SET_ID_OFFSET]
    if ai_ids:
        child = ChildProfile.objects.filter(device=device).first()
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

    # Toplam ilerleme hesapla
    total_free = Question.objects.filter(batch_number=0).count()
    free_solved = UserQuestionProgress.objects.filter(device=device, solved=True).count()

    total_ai = 0
    ai_solved = 0
    child = ChildProfile.objects.filter(device=device).first()
    if child:
        for qs in QuestionSet.objects.filter(child=child):
            total_ai += len(qs.questions_json or [])
            ai_solved += len(qs.solved_ids or [])

    return Response({
        'success': True,
        'updated': updated,
        'total_solved': free_solved + ai_solved,
        'total_accessible': total_free + total_ai,
    })

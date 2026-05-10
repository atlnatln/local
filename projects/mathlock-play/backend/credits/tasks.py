import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from celery import shared_task
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)

# Proje dizini — backend/ üst dizini
_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
_GENERATE_SCRIPT = _PROJECT_DIR / 'ai-generate.sh'
_GENERATE_LEVELS_SCRIPT = _PROJECT_DIR / 'ai-generate-levels.sh'


def _refund_credit(credit_balance_pk: int, is_free: bool):
    """Kredi iadesi — lazy import circular dependency önlemek için."""
    from django.db import transaction
    from .models import CreditBalance
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


def _release_renewal_lock(child_pk: int, content_type: str):
    """Yenileme kilidini serbest bırak."""
    from .models import RenewalLock
    try:
        RenewalLock.objects.filter(child_id=child_pk, content_type=content_type).delete()
    except Exception as e:
        logger.warning("Kilit serbest bırakılamadı (child_pk=%d, type=%s): %s", child_pk, content_type, e)


@shared_task(bind=True, max_retries=0, queue='levels')
def generate_level_set(self, child_pk, credit_balance_pk, is_free, level_stats, education_period='sinif_2', use_procedural=False):
    """
    Celery task: AI seviye üretimi LAUNCHER.

    Subprocess'i başlatır, PID kaydeder, hemen döner.
    Arka plan poller (poll_generation_jobs) tamamlandığında output'u okur.
    """
    from .models import ChildProfile, GenerationJob

    try:
        child = ChildProfile.objects.get(pk=child_pk)
    except ChildProfile.DoesNotExist:
        logger.error("generate_level_set: child bulunamadı pk=%d", child_pk)
        return {'success': False, 'error': 'child_not_found'}

    # Önceki başarısuz/pending job'ları temizle
    GenerationJob.objects.filter(
        child=child, content_type='levels', status__in=['pending', 'failed']
    ).delete()

    # Geçici dizin oluştur
    tmpdir = Path(tempfile.mkdtemp(prefix='mathlock-levels-gen-'))

    # Stats yaz (script okuyacak)
    if level_stats:
        (tmpdir / 'level-stats.json').write_text(
            json.dumps(level_stats, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    # Scripti NON-blocking başlat
    if not _GENERATE_LEVELS_SCRIPT.exists():
        _release_renewal_lock(child_pk, 'levels')
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        return {'success': False, 'error': 'script_not_found'}

    try:
        cmd = ['bash', str(_GENERATE_LEVELS_SCRIPT), '--vps-mode',
               '--period', education_period, '--data-dir', str(tmpdir)]
        if use_procedural:
            cmd.append('--procedural')
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(_PROJECT_DIR),
        )
    except Exception as exc:
        logger.error("Subprocess başlatılamadı: %s", exc)
        _release_renewal_lock(child_pk, 'levels')
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {'success': False, 'error': str(exc)}

    # Job kaydet
    job = GenerationJob.objects.create(
        child=child,
        content_type='levels',
        status='running',
        pid=process.pid,
        temp_dir=str(tmpdir),
        credit_balance_pk=credit_balance_pk,
        is_free=is_free,
        level_stats=level_stats or {},
        education_period=education_period,
    )

    logger.info(
        "Level generation launched: child=%s, pid=%d, job=%d, tmpdir=%s",
        child.name, process.pid, job.pk, tmpdir
    )
    return {'success': True, 'job_id': job.pk, 'pid': process.pid}


@shared_task(bind=True, max_retries=0, queue='questions')
def generate_question_set(self, child_pk, credit_balance_pk, is_free):
    """
    Celery task: AI soru üretimi LAUNCHER.

    Subprocess'i başlatır, PID kaydeder, hemen döner.
    """
    from .models import ChildProfile, GenerationJob
    # Lazy import — circular dependency önlemek için
    from .views import _build_child_stats

    try:
        child = ChildProfile.objects.get(pk=child_pk)
    except ChildProfile.DoesNotExist:
        logger.error("generate_question_set: child bulunamadı pk=%d", child_pk)
        return {'success': False, 'error': 'child_not_found'}

    GenerationJob.objects.filter(
        child=child, content_type='questions', status__in=['pending', 'failed']
    ).delete()

    tmpdir = Path(tempfile.mkdtemp(prefix='mathlock-questions-gen-'))
    child_stats = _build_child_stats(child)

    if not _GENERATE_SCRIPT.exists():
        _release_renewal_lock(child_pk, 'questions')
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        return {'success': False, 'error': 'script_not_found'}

    try:
        (tmpdir / 'stats.json').write_text(
            json.dumps(child_stats, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        process = subprocess.Popen(
            ['bash', str(_GENERATE_SCRIPT), '--vps-mode', '--skip-sync',
             '--period', child.education_period, '--data-dir', str(tmpdir)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(_PROJECT_DIR),
        )
    except Exception as exc:
        logger.error("Subprocess başlatılamadı: %s", exc)
        _release_renewal_lock(child_pk, 'questions')
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {'success': False, 'error': str(exc)}

    job = GenerationJob.objects.create(
        child=child,
        content_type='questions',
        status='running',
        pid=process.pid,
        temp_dir=str(tmpdir),
        credit_balance_pk=credit_balance_pk,
        is_free=is_free,
        education_period=child.education_period,
    )

    logger.info(
        "Question generation launched: child=%s, pid=%d, job=%d, tmpdir=%s",
        child.name, process.pid, job.pk, tmpdir
    )
    return {'success': True, 'job_id': job.pk, 'pid': process.pid}


@shared_task(queue='levels')
def poll_generation_jobs():
    """
    Periodic task: çalışan generation job'larını kontrol et.

    Her 30 saniyede bir çalışır (CELERY_BEAT_SCHEDULE).
    Subprocess bitmişse output'u okur, DB'ye kaydeder.
    """
    from .models import GenerationJob, LevelSet, QuestionSet

    running_jobs = GenerationJob.objects.filter(status='running')
    if not running_jobs.exists():
        return

    logger.debug("poll_generation_jobs: %d running job", running_jobs.count())

    for job in running_jobs:
        _process_single_job(job)

    connection.close()


def _process_single_job(job):
    """Tek bir generation job'u işle — subprocess bitti mi kontrol et."""
    from .models import LevelSet, QuestionSet

    # 1. PID hâlâ çalışıyor mu?
    # NOT: os.kill(pid, 0) zombie process'lerde başarılı olur!
    # /proc/<pid>/status üzerinden State kontrolü yapmalıyız.
    try:
        with open(f'/proc/{job.pid}/status') as f:
            for line in f:
                if line.startswith('State:'):
                    state = line.split()[1]
                    if state in ('Z', 'X', 'x'):
                        # Zombie / dead — process bitmiş, parent wait etmemiş
                        # Temizlik için waitpid dene
                        try:
                            os.waitpid(job.pid, os.WNOHANG)
                        except ChildProcessError:
                            pass
                        break
                    else:
                        # R, S, D, T, t, W, P — hâlâ "yaşıyor"
                        return
    except (FileNotFoundError, ProcessLookupError):
        # /proc/<pid> yok — process tamamen bitmiş ve temizlenmiş
        pass
    except Exception as exc:
        logger.warning("PID kontrolü hatası (job=%d, pid=%d): %s", job.pk, job.pid, exc)
        # Devam et — belki process zaten bitmiştir

    # 2. Output'u oku
    tmpdir = Path(job.temp_dir)
    success = False
    error_msg = ""

    # Validator path (one dir up from backend/)
    validator_path = Path(__file__).resolve().parent.parent.parent / 'validate-levels.py'

    try:
        if job.content_type == 'levels':
            levels_file = tmpdir / 'levels.json'
            if not levels_file.exists():
                raise RuntimeError("levels.json not generated")

            # Run validation before saving
            if validator_path.exists():
                val_result = subprocess.run(
                    [sys.executable, str(validator_path), '--file', str(levels_file), '--stats-file', str(tmpdir / 'level-stats.json')],
                    capture_output=True, text=True
                )
                if val_result.returncode != 0:
                    raise RuntimeError(f"Validation failed:\n{val_result.stdout}")

            data = json.loads(levels_file.read_text(encoding='utf-8'))
            levels = data.get('levels', [])

            if len(levels) < 12:
                raise RuntimeError(f"Insufficient levels: {len(levels)} < 12")

            latest = LevelSet.objects.filter(child=job.child).order_by('-version').first()
            next_version = (latest.version + 1) if latest else 1

            LevelSet.objects.create(
                child=job.child,
                version=next_version,
                levels_json=levels[:12],
                is_ai_generated=True,
                credit_used=not job.is_free,
            )
            logger.info(
                "Level generation completed: child=%s, v%d, job=%d",
                job.child.name, next_version, job.pk
            )
            success = True

        else:  # questions
            questions_file = tmpdir / 'questions.json'
            if not questions_file.exists():
                raise RuntimeError("questions.json not generated")

            data = json.loads(questions_file.read_text(encoding='utf-8'))
            questions = data.get('questions', [])

            # Döneme göre beklenen soru sayısı
            expected = {'okul_oncesi': 30, 'sinif_1': 40}.get(job.education_period, 50)
            if len(questions) < expected:
                raise RuntimeError(f"Insufficient questions: {len(questions)} < {expected}")

            latest = QuestionSet.objects.filter(child=job.child).order_by('-version').first()
            next_version = (latest.version + 1) if latest else 1

            # AGENTS.md formatından QuestionSet formatına dönüştür
            normalized = [
                {
                    'text': q['text'],
                    'answer': q['answer'],
                    'type': q.get('type', ''),
                    'difficulty': q.get('difficulty', 1),
                    'hint': q.get('hint', ''),
                }
                for q in questions[:expected]
            ]

            QuestionSet.objects.create(
                child=job.child,
                version=next_version,
                questions_json=normalized,
                is_ai_generated=True,
                credit_used=not job.is_free,
            )
            logger.info(
                "Question generation completed: child=%s, v%d, job=%d",
                job.child.name, next_version, job.pk
            )
            success = True

    except Exception as exc:
        error_msg = str(exc)[:500]
        logger.error("Job %d failed: %s", job.pk, exc)

    # 3. Durum güncelle ve temizlik
    if success:
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'completed_at', 'updated_at'])
        _release_renewal_lock(job.child.pk, job.content_type)
    else:
        job.status = 'failed'
        job.error_message = error_msg
        job.save(update_fields=['status', 'error_message', 'updated_at'])
        if job.credit_balance_pk:
            _refund_credit(job.credit_balance_pk, job.is_free)
        _release_renewal_lock(job.child.pk, job.content_type)

    # Geçici dizini temizle
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception as exc:
        logger.warning("Temp dir temizlenemedi (%s): %s", tmpdir, exc)

    connection.close()

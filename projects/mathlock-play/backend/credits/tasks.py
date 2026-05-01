import logging
from celery import shared_task
from django.db import connection

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue='levels')
def generate_level_set(self, child_pk, credit_balance_pk, is_free, level_stats, education_period='sinif_2'):
    """Celery task: AI seviye üretimi."""
    # Lazy import circular dependency önlemek için
    from .models import ChildProfile, LevelSet
    from .views import _generate_levels_via_kimi, _release_renewal_lock, _refund_credit

    try:
        child = ChildProfile.objects.get(pk=child_pk)
        levels = _generate_levels_via_kimi(level_stats, child.education_period)

        latest = LevelSet.objects.filter(child=child).order_by('-version').first()
        next_version = (latest.version + 1) if latest else 1

        level_set = LevelSet.objects.create(
            child=child,
            version=next_version,
            levels_json=levels,
            is_ai_generated=True,
            credit_used=not is_free,
        )
        logger.info(
            "Celery seviye üretimi başarılı: child=%s, v%d, %d seviye",
            child.name, next_version, len(levels)
        )
        _release_renewal_lock(child.pk, 'levels')
        return {'success': True, 'level_set_id': level_set.pk}
    except Exception as exc:
        logger.error("Celery seviye üretimi hatası: %s", exc)
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        _release_renewal_lock(child_pk, 'levels')
        raise self.retry(exc=exc, countdown=60)
    finally:
        connection.close()


@shared_task(bind=True, max_retries=3, queue='questions')
def generate_question_set(self, child_pk, credit_balance_pk, is_free):
    """Celery task: AI soru üretimi."""
    # Lazy import circular dependency önlemek için
    from .models import ChildProfile, QuestionSet
    from .views import _generate_via_kimi, _build_child_stats, _release_renewal_lock, _refund_credit

    try:
        child = ChildProfile.objects.get(pk=child_pk)
        child_stats = _build_child_stats(child)
        questions = _generate_via_kimi(child_stats, child.education_period)

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
            "Celery soru üretimi başarılı: child=%s, v%d, %d soru",
            child.name, next_version, len(questions)
        )
        _release_renewal_lock(child.pk, 'questions')
        return {'success': True, 'question_set_id': question_set.pk}
    except Exception as exc:
        logger.error("Celery soru üretimi hatası: %s", exc)
        if credit_balance_pk:
            _refund_credit(credit_balance_pk, is_free)
        _release_renewal_lock(child_pk, 'questions')
        raise self.retry(exc=exc, countdown=60)
    finally:
        connection.close()

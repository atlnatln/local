"""
Mevcut Question kayıtlarına question_code alanını doldurur.

Format: {Yıl}G{Sınıf}-B{Batch}-{SıraNo}
Örnek: 2025G2-B0-3001

Kullanım:
    python manage.py backfill_question_codes --dry-run
    python manage.py backfill_question_codes
"""
from django.core.management.base import BaseCommand
from credits.models import Question


class Command(BaseCommand):
    help = 'Mevcut sorulara question_code üret'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Değişiklik yapmadan rapor ver'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Eğitim dönemi → sınıf numarası
        period_map = {
            'okul_oncesi': '0',
            'sinif_1': '1',
            'sinif_2': '2',
            'sinif_3': '3',
            'sinif_4': '4',
        }

        questions = Question.objects.filter(
            question_code__isnull=True
        ) | Question.objects.filter(question_code='')

        total = questions.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Tüm soruların question_code alanı dolu.'))
            return

        self.stdout.write(f'İşlenecek soru sayısı: {total}')
        updated = 0
        skipped = 0

        for q in questions:
            grade = period_map.get(q.education_period, 'X')
            year = q.created_at.year if q.created_at else 2025
            batch = q.batch_number
            seq = q.question_id

            code = f"{year}G{grade}-B{batch}-{seq}"

            # unique constraint kontrolü
            if Question.objects.filter(question_code=code).exclude(pk=q.pk).exists():
                self.stderr.write(
                    self.style.WARNING(f'Çakışma: Q{q.question_id} için {code} zaten var — atlanıyor')
                )
                skipped += 1
                continue

            if not dry_run:
                q.question_code = code
                q.save(update_fields=['question_code'])

            updated += 1
            if updated <= 5 or updated % 100 == 0:
                self.stdout.write(f'  {code} ← Q{q.question_id} ({q.education_period}, batch={batch})')

        action = 'Rapor' if dry_run else 'Güncelleme'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} tamamlandı: {updated} güncellendi, {skipped} atlandı (toplam {total})'
            )
        )

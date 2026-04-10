"""
Master soru bankasını JSON dosyalarından DB'ye yükler.

Kullanım:
    python manage.py load_questions                          # data/questions.json batch=0
    python manage.py load_questions --file extra.json --batch 1
    python manage.py load_questions --clear                  # Tüm soruları sil ve yeniden yükle
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from credits.models import Question


class Command(BaseCommand):
    help = 'Master soru bankasını JSON dosyasından yükle'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', type=str, default=None,
            help='JSON dosya yolu (varsayılan: data/questions.json)'
        )
        parser.add_argument(
            '--batch', type=int, default=0,
            help='Batch numarası (0=ücretsiz, 1+=kredi ile)'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Yüklemeden önce mevcut soruları sil'
        )

    def handle(self, *args, **options):
        batch = options['batch']
        clear = options['clear']

        # Dosya yolu
        if options['file']:
            json_path = Path(options['file'])
        else:
            json_path = Path(__file__).resolve().parents[4] / 'data' / 'questions.json'

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'Dosya bulunamadı: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = data.get('questions', [])
        if not questions:
            self.stderr.write(self.style.ERROR('JSON dosyasında soru bulunamadı'))
            return

        if clear:
            deleted, _ = Question.objects.filter(batch_number=batch).delete()
            self.stdout.write(f'Batch {batch}: {deleted} soru silindi')

        created = 0
        updated = 0
        for q in questions:
            _, was_created = Question.objects.update_or_create(
                question_id=q['id'],
                defaults={
                    'text': q['text'],
                    'answer': q['answer'],
                    'question_type': q.get('type', ''),
                    'difficulty': q.get('difficulty', 1),
                    'hint': q.get('hint', ''),
                    'batch_number': batch,
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Batch {batch}: {created} yeni, {updated} güncellendi (toplam {len(questions)} soru)'
        ))

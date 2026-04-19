from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0003_questionset_solved_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='childprofile',
            name='education_period',
            field=models.CharField(
                choices=[
                    ('okul_oncesi', 'Okul Öncesi (5-6 yaş)'),
                    ('sinif_1', '1. Sınıf (6-7 yaş)'),
                    ('sinif_2', '2. Sınıf (7-8 yaş)'),
                    ('sinif_3', '3. Sınıf (8-9 yaş)'),
                    ('sinif_4', '4. Sınıf (9-10 yaş)'),
                ],
                default='sinif_2',
                help_text='Eğitim dönemi — soru üretimi bu döneme göre yapılır',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Cihazda aktif seçili profil',
            ),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='total_time_seconds',
            field=models.IntegerField(
                default=0,
                help_text='Toplam çözüm süresi (saniye)',
            ),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='daily_stats',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Günlük performans özeti: {tarih: {correct, shown, time_seconds}}',
            ),
        ),
        migrations.AddField(
            model_name='childprofile',
            name='weekly_report_json',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='AI tarafından üretilen haftalık performans raporu',
            ),
        ),
    ]

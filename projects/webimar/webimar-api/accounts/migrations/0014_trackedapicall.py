from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_analyticsevent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackedApiCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Session ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')),
                ('method', models.CharField(db_index=True, max_length=10, verbose_name='HTTP Metodu')),
                ('path', models.CharField(db_index=True, max_length=512, verbose_name='Path')),
                ('query_params', models.JSONField(blank=True, null=True, verbose_name='Query Parametreleri')),
                ('request_body', models.JSONField(blank=True, null=True, verbose_name='Request JSON')),
                ('response_status', models.PositiveSmallIntegerField(verbose_name='Response Status')),
                ('response_body', models.JSONField(blank=True, null=True, verbose_name='Response JSON')),
                ('duration_ms', models.PositiveIntegerField(blank=True, null=True, verbose_name='Süre (ms)')),
                ('calculation_type', models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Hesaplama Türü')),
                ('dimensions', models.JSONField(blank=True, null=True, verbose_name='Boyutlar (il/ilçe/yapı türü vb.)')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')),
                (
                    'user',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='tracked_api_calls',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Kullanıcı',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Tracked API Call',
                'verbose_name_plural': 'Tracked API Calls',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='trackedapicall',
            index=models.Index(fields=['ip_address', 'created_at'], name='acc_trk_ip_created_idx'),
        ),
        migrations.AddIndex(
            model_name='trackedapicall',
            index=models.Index(fields=['session_id', 'created_at'], name='acc_trk_session_created_idx'),
        ),
        migrations.AddIndex(
            model_name='trackedapicall',
            index=models.Index(fields=['path', 'created_at'], name='acc_trk_path_created_idx'),
        ),
        migrations.AddIndex(
            model_name='trackedapicall',
            index=models.Index(fields=['calculation_type', 'created_at'], name='acc_trk_calc_created_idx'),
        ),
    ]

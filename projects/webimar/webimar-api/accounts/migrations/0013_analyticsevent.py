from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_add_unique_email_constraint'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=64, verbose_name='Session ID')),
                ('page_id', models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Page ID')),
                ('event_type', models.CharField(choices=[('page_view', 'Sayfa Görüntüleme'), ('page_leave', 'Sayfadan Ayrılma'), ('calculation', 'Hesaplama')], db_index=True, max_length=20, verbose_name='Event Türü')),
                ('path', models.CharField(db_index=True, max_length=512, verbose_name='Path')),
                ('referrer', models.CharField(blank=True, max_length=512, null=True, verbose_name='Referrer')),
                ('duration_ms', models.PositiveIntegerField(blank=True, null=True, verbose_name='Süre (ms)')),
                ('calculation_type', models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Hesaplama Türü')),
                ('metadata', models.JSONField(blank=True, null=True, verbose_name='Ek Veriler')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_events', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Analytics Event',
                'verbose_name_plural': 'Analytics Eventleri',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='analyticsevent',
            index=models.Index(fields=['session_id', 'created_at'], name='accounts_an_session__b7e4df_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsevent',
            index=models.Index(fields=['event_type', 'created_at'], name='accounts_an_event_t_6c9a3f_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsevent',
            index=models.Index(fields=['path', 'created_at'], name='accounts_an_path_4e0c2c_idx'),
        ),
    ]

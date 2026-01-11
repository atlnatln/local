# Generated manually for PageView and UserInteraction models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calculations', '0008_alter_calculationhistory_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=100, verbose_name='Oturum ID')),
                ('ip_address', models.GenericIPAddressField(db_index=True, verbose_name='IP Adresi')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('device_fingerprint', models.CharField(blank=True, max_length=255, null=True, verbose_name='Cihaz Parmak İzi')),
                ('path', models.CharField(db_index=True, max_length=500, verbose_name='URL Path')),
                ('full_url', models.CharField(blank=True, max_length=1000, verbose_name='Tam URL')),
                ('page_title', models.CharField(blank=True, max_length=500, verbose_name='Sayfa Başlığı')),
                ('referrer', models.CharField(blank=True, max_length=1000, verbose_name='Referrer')),
                ('platform', models.CharField(blank=True, max_length=50, verbose_name='Platform')),
                ('browser', models.CharField(blank=True, max_length=100, verbose_name='Tarayıcı')),
                ('os', models.CharField(blank=True, max_length=100, verbose_name='İşletim Sistemi')),
                ('load_time', models.FloatField(blank=True, null=True, verbose_name='Yüklenme Süresi (ms)')),
                ('time_on_page', models.IntegerField(blank=True, null=True, verbose_name='Sayfada Geçirilen Süre (sn)')),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='Ülke')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Şehir')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_views', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Sayfa Görüntüleme',
                'verbose_name_plural': 'Sayfa Görüntülemeleri',
                'db_table': 'page_views',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=100, verbose_name='Oturum ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Adresi')),
                ('interaction_type', models.CharField(choices=[('click', 'Tıklama'), ('form_submit', 'Form Gönderimi'), ('scroll', 'Scroll'), ('download', 'İndirme'), ('search', 'Arama'), ('filter', 'Filtreleme'), ('tab_change', 'Sekme Değişimi'), ('modal_open', 'Modal Açma'), ('video_play', 'Video Oynatma'), ('share', 'Paylaşma'), ('other', 'Diğer')], db_index=True, max_length=20, verbose_name='Etkileşim Türü')),
                ('element_id', models.CharField(blank=True, max_length=200, verbose_name='Element ID')),
                ('element_class', models.CharField(blank=True, max_length=200, verbose_name='Element Class')),
                ('element_text', models.CharField(blank=True, max_length=500, verbose_name='Element Metni')),
                ('page_path', models.CharField(db_index=True, max_length=500, verbose_name='Sayfa Path')),
                ('page_title', models.CharField(blank=True, max_length=500, verbose_name='Sayfa Başlığı')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Metadata')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interactions', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Kullanıcı Etkileşimi',
                'verbose_name_plural': 'Kullanıcı Etkileşimleri',
                'db_table': 'user_interactions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['created_at', 'path'], name='page_views_created_4b0e98_idx'),
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['session_id', 'created_at'], name='page_views_session_b9c6e5_idx'),
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['ip_address', 'created_at'], name='page_views_ip_addr_1f76ab_idx'),
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['user', 'created_at'], name='page_views_user_id_0e0c88_idx'),
        ),
        migrations.AddIndex(
            model_name='userinteraction',
            index=models.Index(fields=['created_at', 'interaction_type'], name='user_intera_created_e6b5a9_idx'),
        ),
        migrations.AddIndex(
            model_name='userinteraction',
            index=models.Index(fields=['session_id', 'created_at'], name='user_intera_session_bde0c6_idx'),
        ),
        migrations.AddIndex(
            model_name='userinteraction',
            index=models.Index(fields=['page_path', 'created_at'], name='user_intera_page_pa_a72b5f_idx'),
        ),
    ]

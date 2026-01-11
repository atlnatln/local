from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Kullanıcı profil bilgileri"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='Son Giriş IP')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='Son Giriş Zamanı')
    last_password_reset_email = models.DateTimeField(blank=True, null=True, verbose_name='Son Şifre Sıfırlama Maili')
    
    # Günlük şifre sıfırlama limit alanları
    password_reset_count_today = models.PositiveIntegerField(default=0, verbose_name='Bugünkü Şifre Sıfırlama Sayısı')
    password_reset_date = models.DateField(blank=True, null=True, verbose_name='Şifre Sıfırlama Tarihi')
    
    is_active_profile = models.BooleanField(default=True, verbose_name='Aktif Profil')
    
    # Admin mail takip field'ları
    awaiting_activation = models.BooleanField(default=False, verbose_name='Aktivasyon Bekliyor')
    awaiting_password_reset = models.BooleanField(default=False, verbose_name='Şifre Sıfırlama Bekliyor')
    activation_mail_sent = models.BooleanField(default=False, verbose_name='Aktivasyon Maili Gönderildi')
    password_reset_mail_sent = models.BooleanField(default=False, verbose_name='Şifre Sıfırlama Maili Gönderildi')
    activation_mail_sent_at = models.DateTimeField(blank=True, null=True, verbose_name='Aktivasyon Maili Gönderim Zamanı')
    password_reset_mail_sent_at = models.DateTimeField(blank=True, null=True, verbose_name='Şifre Sıfırlama Maili Gönderim Zamanı')
    
    # Şifre bilgisi
    password_self_chosen = models.BooleanField(default=False, verbose_name='Kullanıcı Şifresini Kendisi Belirledi')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='Admin Notları')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')

    class Meta:
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'

    def __str__(self):
        return f'{self.user.username} - Profil'
    
    @property
    def mail_action_status(self):
        """Mail işlem durumunu döndürür"""
        if self.awaiting_activation and not self.activation_mail_sent:
            if self.password_self_chosen:
                return 'Kullanıcı şifresini belirledi, aktivasyon bekliyor'
            else:
                return 'Aktivasyon ve şifre gönderilmesi bekliyor'
        elif self.awaiting_password_reset and not self.password_reset_mail_sent:
            return 'Şifre sıfırlama maili bekliyor'
        elif self.activation_mail_sent and not self.user.is_active:
            return 'Aktivasyon maili gönderildi'
        elif self.password_reset_mail_sent:
            return 'Şifre sıfırlama maili gönderildi'
        return 'İşlem beklenmiyor'
    
    @property
    def needs_admin_action(self):
        """Admin işlemi gerekip gerekmediğini kontrol eder"""
        return (self.awaiting_activation and not self.activation_mail_sent) or \
               (self.awaiting_password_reset and not self.password_reset_mail_sent)

class UserSession(models.Model):
    """Kullanıcı oturum bilgileri"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    device_info = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    login_time = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Kullanıcı Oturumu'
        verbose_name_plural = 'Kullanıcı Oturumları'
        ordering = ['-last_activity']

    def __str__(self):
        return f'{self.user.username} - {self.ip_address} - {self.login_time}'

class UserActivity(models.Model):
    """Kullanıcı aktivite takip modeli"""
    ACTIVITY_TYPES = [
        ('login', 'Giriş Yaptı'),
        ('logout', 'Çıkış Yaptı'),
        ('calculation', 'Hesaplama Yaptı'),
        ('map_point', 'Harita Noktası İşaretledi'),
        ('profile_update', 'Profil Güncelledi'),
        ('password_change', 'Şifre Değiştirdi'),
        ('file_upload', 'Dosya Yükledi'),
        ('data_export', 'Veri İndirdi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='Aktivite Türü')
    description = models.TextField(verbose_name='Açıklama')
    ip_address = models.GenericIPAddressField(verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')
    location_data = models.JSONField(blank=True, null=True, verbose_name='Konum Bilgisi')
    calculation_data = models.JSONField(blank=True, null=True, verbose_name='Hesaplama Verileri')
    result_data = models.JSONField(blank=True, null=True, verbose_name='Sonuç Verileri')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    
    class Meta:
        verbose_name = 'Kullanıcı Aktivitesi'
        verbose_name_plural = 'Kullanıcı Aktiviteleri'
        ordering = ['-created_at']
    
    def __str__(self):
        user_name = self.user.username if self.user else "Anonim"
        return f'{user_name} - {self.get_activity_type_display()} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Kullanıcı oluşturulduğunda otomatik profil oluştur, güncellemede profili kaydet
    Google gibi doğrulanmış kaynaklardan gelen aktif kullanıcılar için profil flag'leri False başlatılır.
    """
    if created:
        # Varsayılan profil oluştur
        profile = UserProfile.objects.create(user=instance)
        # Kullanıcı aktifse (ör. Google OAuth) herhangi bir aktivasyon bekleme süreci yok
        if instance.is_active:
            profile.awaiting_activation = False
            profile.activation_mail_sent = False
            profile.awaiting_password_reset = False
            profile.password_reset_mail_sent = False
            profile.save()
        else:
            # Admin onaylı akış için pasif kullanıcılar
            profile.awaiting_activation = True
            profile.activation_mail_sent = False
            profile.save()
    else:
        # Kullanıcı güncellendiğinde, profil varsa kaydet
        if hasattr(instance, 'profile'):
            instance.profile.save()

class SecurityEvent(models.Model):
    """Güvenlik olaylarını takip eden model"""
    EVENT_TYPES = [
        ('failed_login', 'Başarısız Giriş'),
        ('failed_register', 'Başarısız Kayıt'),
        ('rate_limit_exceeded', 'Rate Limit Aşıldı'),
        ('suspicious_activity', 'Şüpheli Aktivite'),
        ('password_change', 'Şifre Değiştirildi'),
        ('account_deleted', 'Hesap Silindi'),
        ('failed_account_deletion', 'Başarısız Hesap Silme'),
        ('multiple_failed_attempts', 'Çoklu Başarısız Deneme'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Kritik'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name='Olay Türü')
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium', verbose_name='Önem Derecesi')
    ip_address = models.GenericIPAddressField(verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_events', verbose_name='Kullanıcı')
    username_attempted = models.CharField(max_length=150, blank=True, null=True, verbose_name='Denenen Kullanıcı Adı')
    email_attempted = models.EmailField(blank=True, null=True, verbose_name='Denenen E-posta')
    description = models.TextField(verbose_name='Açıklama')
    metadata = models.JSONField(blank=True, null=True, verbose_name='Ek Veriler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    
    class Meta:
        verbose_name = 'Güvenlik Olayı'
        verbose_name_plural = 'Güvenlik Olayları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.get_event_type_display()} - {self.ip_address} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class AnalyticsEvent(models.Model):
    """Ziyaretçi/kullanıcı davranış eventleri (page view, navigation, duration, calculation)."""

    EVENT_TYPES = [
        ('page_view', 'Sayfa Görüntüleme'),
        ('page_leave', 'Sayfadan Ayrılma'),
        ('calculation', 'Hesaplama'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_events',
        verbose_name='Kullanıcı',
    )

    session_id = models.CharField(max_length=64, db_index=True, verbose_name='Session ID')
    page_id = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name='Page ID')

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True, verbose_name='Event Türü')
    path = models.CharField(max_length=512, db_index=True, verbose_name='Path')
    referrer = models.CharField(max_length=512, blank=True, null=True, verbose_name='Referrer')

    duration_ms = models.PositiveIntegerField(blank=True, null=True, verbose_name='Süre (ms)')
    calculation_type = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name='Hesaplama Türü')

    metadata = models.JSONField(blank=True, null=True, verbose_name='Ek Veriler')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')

    class Meta:
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Eventleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['path', 'created_at']),
        ]

    def __str__(self):
        user_name = self.user.username if self.user else 'Anonim'
        return f'{user_name} - {self.event_type} - {self.path} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class TrackedApiCall(models.Model):
    """API çağrılarını ve hesaplama istek/yanıtlarını raporlama için saklar."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracked_api_calls',
        verbose_name='Kullanıcı',
    )

    session_id = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name='Session ID')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, null=True, verbose_name='Tarayıcı Bilgisi')

    method = models.CharField(max_length=10, db_index=True, verbose_name='HTTP Metodu')
    path = models.CharField(max_length=512, db_index=True, verbose_name='Path')

    query_params = models.JSONField(blank=True, null=True, verbose_name='Query Parametreleri')
    request_body = models.JSONField(blank=True, null=True, verbose_name='Request JSON')

    response_status = models.PositiveSmallIntegerField(verbose_name='Response Status')
    response_body = models.JSONField(blank=True, null=True, verbose_name='Response JSON')

    duration_ms = models.PositiveIntegerField(blank=True, null=True, verbose_name='Süre (ms)')

    calculation_type = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name='Hesaplama Türü')
    dimensions = models.JSONField(blank=True, null=True, verbose_name='Boyutlar (il/ilçe/yapı türü vb.)')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')

    class Meta:
        verbose_name = 'Tracked API Call'
        verbose_name_plural = 'Tracked API Calls'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['path', 'created_at']),
            models.Index(fields=['calculation_type', 'created_at']),
        ]

    def __str__(self):
        who = self.user.username if self.user else (self.ip_address or 'Anonim')
        return f'{who} - {self.method} {self.path} - {self.response_status} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

from django.db import IntegrityError, models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
import json
import hashlib

User = get_user_model()

class CalculationHistory(models.Model):
    """Hesaplama geçmişi modeli"""
    CALCULATION_TYPES = [
        ('arazi_alani', 'Arazi Alanı Hesaplama'),
        ('dikili_alan', 'Dikili Alan Hesaplama'),
        ('bag-evi', 'Bağ Evi Hesaplama'),
        ('yapilasma', 'Yapılaşma Hesaplama'),
        ('mesafe', 'Mesafe Hesaplama'),
        ('sera', 'Sera Hesaplaması'),
        ('aricilik', 'Arıcılık Tesisi Hesaplaması'),
        ('mantar-tesisi', 'Mantar Tesisi Hesaplaması'),
        ('solucan-tesisi', 'Solucan Tesisi Hesaplaması'),
        ('buyukbas', 'Büyükbaş Hayvancılık Hesaplaması'),
        ('kucukbas', 'Küçükbaş Hayvancılık Hesaplaması'),
        ('kanatli', 'Kanatlı Hayvancılık Hesaplaması'),
        ('hara', 'Hara Tesisi Hesaplaması'),
        ('tarimsal-depo', 'Tarımsal Depo Hesaplaması'),
        ('tarimsal-amacli-depo', 'Tarımsal Amaçlı Depo Hesaplaması'),
        ('lisansli-depo', 'Lisanslı Depo Hesaplaması'),
        ('hububat-silo', 'Hububat Silo Hesaplaması'),
        ('yikama-tesisi', 'Yıkama Tesisi Hesaplaması'),
        ('kurutma-tesisi', 'Kurutma Tesisi Hesaplaması'),
        ('soguk-hava-deposu', 'Soğuk Hava Deposu Hesaplaması'),
        ('zeytinyagi-fabrikasi', 'Zeytinyağı Fabrikası Hesaplaması'),
        ('su-depolama', 'Su Depolama Tesisi Hesaplaması'),
        ('su-kuyulari', 'Su Kuyuları Hesaplaması'),
        ('evcil-hayvan', 'Evcil Hayvan Bakımevi Hesaplaması'),
        ('sut-sigirciligi', 'Süt Sığırcılığı Hesaplaması'),
        ('besi-sigirciligi', 'Besi Sığırcılığı Hesaplaması'),
        ('agil-kucukbas', 'Ağıl (Küçükbaş) Hesaplaması'),
        ('kumes-yumurtaci', 'Kümes (Yumurtacı) Hesaplaması'),
        ('kumes-etci', 'Kümes (Etçi) Hesaplaması'),
        ('kumes-gezen', 'Kümes (Gezen) Hesaplaması'),
        ('kumes-hindi', 'Kümes (Hindi) Hesaplaması'),
        ('kaz-ordek', 'Kaz-Ördek Hesaplaması'),
        ('ipek-bocekciligi', 'İpek Böcekçiliği Hesaplaması'),
        ('zeytinyagi-uretim-tesisi', 'Zeytinyağı Üretim Tesisi Hesaplaması'),
        ('meyve-sebze-kurutma', 'Meyve-Sebze Kurutma Tesisi Hesaplaması'),
        ('other', 'Diğer Hesaplama'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='calculation_histories')
    calculation_type = models.CharField(max_length=50, choices=CALCULATION_TYPES, verbose_name='Hesaplama Türü')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name='Başlık')
    description = models.TextField(blank=True, null=True, verbose_name='Açıklama')
    parameters = models.JSONField(verbose_name='Parametreler')
    result = models.JSONField(null=True, blank=True, verbose_name='Sonuç')
    map_coordinates = models.JSONField(blank=True, null=True, verbose_name='Harita Koordinatları')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Zamanı')
    is_successful = models.BooleanField(default=True, verbose_name='Başarılı mı?')
    error_message = models.TextField(blank=True, null=True, verbose_name='Hata Mesajı')

    class Meta:
        verbose_name = 'Hesaplama Geçmişi'
        verbose_name_plural = 'Hesaplama Geçmişleri'
        ordering = ['-created_at']
        # Duplicate kayıt önleme - aynı kullanıcı, tip ve başlıkta tekrar önleme
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'calculation_type', 'title'],
                name='unique_calculation_per_user_type_title'
            )
        ]

    def __str__(self):
        user_name = self.user.username if self.user else "Anonim"
        return f"{user_name} - {self.get_calculation_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class MapInteraction(models.Model):
    """Harita etkileşim modeli"""
    INTERACTION_TYPES = [
        ('point_mark', 'Nokta İşaretleme'),
        ('area_draw', 'Alan Çizme'),
        ('line_draw', 'Çizgi Çizme'),
        ('polygon_draw', 'Poligon Çizme'),
        ('marker_place', 'İşaretçi Yerleştirme'),
        ('zoom', 'Yakınlaştırma'),
        ('pan', 'Kaydırma'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='map_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name='Etkileşim Türü')
    coordinates = models.JSONField(verbose_name='Koordinatlar')
    zoom_level = models.IntegerField(blank=True, null=True, verbose_name='Yakınlaştırma Seviyesi')
    map_layer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Harita Katmanı')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Adresi')
    session_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Oturum ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    
    class Meta:
        verbose_name = 'Harita Etkileşimi'
        verbose_name_plural = 'Harita Etkileşimleri'
        ordering = ['-created_at']
    
    def __str__(self):
        user_name = self.user.username if self.user else "Anonim"
        return f"{user_name} - {self.get_interaction_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class DailyCalculationLimit(models.Model):
    """Günlük hesaplama limiti takip tablosu"""
    # IP bazlı takip için (kayıtsız kullanıcılar)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True, verbose_name='IP Adresi')
    device_fingerprint = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name='Cihaz Parmak İzi')
    
    # Kayıtlı kullanıcılar için
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True, verbose_name='Kullanıcı')
    
    # Limit bilgileri
    calculation_count = models.IntegerField(default=0, verbose_name='Hesaplama Sayısı')
    limit_exceeded = models.BooleanField(default=False, verbose_name='Limit Aşıldı mı?')
    limit_exceeded_at = models.DateTimeField(null=True, blank=True, verbose_name='Limit Aşılma Zamanı')
    
    # Tarih takibi
    date = models.DateField(default=timezone.now, db_index=True, verbose_name='Tarih')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Zamanı')
    
    class Meta:
        db_table = 'daily_calculation_limits'
        verbose_name = 'Günlük Hesaplama Limiti'
        verbose_name_plural = 'Günlük Hesaplama Limitleri'
        unique_together = [
            ['ip_address', 'device_fingerprint', 'date'],  # Kayıtsız kullanıcılar için
            ['user', 'date']  # Kayıtlı kullanıcılar için
        ]
        indexes = [
            models.Index(fields=['date', 'ip_address']),
            models.Index(fields=['date', 'user']),
        ]
    
    @property
    def user_type(self):
        return 'registered' if self.user else 'anonymous'
    
    @property
    def current_limit(self):
        """Mevcut kullanıcı tipine göre limit döndürür"""
        if self.user and self.user.is_superuser:
            return float('inf')  # Süper kullanıcılar için limitsiz
        elif self.user and self.user.is_active:
            return 10  # Kayıtlı kullanıcılar için limit
        return 5  # Kayıtsız kullanıcılar için limit
    
    @property
    def remaining_calculations(self):
        """Kalan hesaplama hakkı"""
        if self.user and self.user.is_superuser:
            return "Limitsiz"
        if self.current_limit == float('inf'):
            return "Limitsiz"
        remaining = self.current_limit - self.calculation_count
        return max(0, int(remaining))
    
    @property
    def is_limit_reached(self):
        """Limit doldu mu?"""
        if self.user and self.user.is_superuser:
            return False
        if self.current_limit == float('inf'):
            return False
        return self.calculation_count >= self.current_limit
    
    def increment_count(self):
        """Hesaplama sayısını artır"""
        # Yük altında (aynı IP/user için paralel istekler) count güncellemesi
        # yarışa girip yanlış sayım/duplicate key zinciri tetikleyebilir.
        # Row-level lock ile güvenli artır.
        with transaction.atomic():
            locked = type(self).objects.select_for_update().get(pk=self.pk)
            locked.calculation_count += 1

            # Süper kullanıcılar için limit kontrolü yapmıyoruz
            if not (locked.user and locked.user.is_superuser) and locked.current_limit != float('inf'):
                if locked.calculation_count >= locked.current_limit:
                    locked.limit_exceeded = True
                    if not locked.limit_exceeded_at:
                        locked.limit_exceeded_at = timezone.now()

            locked.save()

            # Çağıran kodun elindeki instance'ı da güncelle
            self.calculation_count = locked.calculation_count
            self.limit_exceeded = locked.limit_exceeded
            self.limit_exceeded_at = locked.limit_exceeded_at
            self.updated_at = locked.updated_at

        return self
    
    @classmethod
    def get_cache_key(cls, user=None, ip_address=None, device_fingerprint=None):
        """Cache key oluştur"""
        today = timezone.now().date().isoformat()
        if user and user.is_authenticated:
            return f"calc_limit:user:{user.id}:{today}"
        else:
            fingerprint = device_fingerprint or 'unknown'
            # IP ve fingerprint hash'le
            hash_input = f"{ip_address}:{fingerprint}".encode('utf-8')
            hash_key = hashlib.md5(hash_input).hexdigest()[:12]
            return f"calc_limit:anon:{hash_key}:{today}"
    
    @classmethod
    def get_or_create_limit(cls, user=None, ip_address=None, device_fingerprint=None):
        """Limit objesi oluştur veya getir"""
        today = timezone.now().date()

        # Cache devre dışı - direkt DB'den al
        # Not: get_or_create paralel isteklerde IntegrityError (duplicate key) üretebilir.
        # Bu durumda ikinci bir fetch ile toparlıyoruz.
        try:
            with transaction.atomic():
                if user and user.is_authenticated:
                    limit_obj, created = cls.objects.get_or_create(
                        user=user,
                        date=today,
                        defaults={'ip_address': ip_address, 'device_fingerprint': device_fingerprint},
                    )
                else:
                    limit_obj, created = cls.objects.get_or_create(
                        ip_address=ip_address,
                        device_fingerprint=device_fingerprint,
                        date=today,
                        defaults={'user': None},
                    )
                return limit_obj, created
        except IntegrityError:
            # Race: başka bir worker kaydı oluşturdu
            if user and user.is_authenticated:
                return cls.objects.get(user=user, date=today), False
            return cls.objects.get(ip_address=ip_address, device_fingerprint=device_fingerprint, date=today), False
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.date}: {self.calculation_count}/{self.current_limit}"
        return f"IP:{self.ip_address} - {self.date}: {self.calculation_count}/{self.current_limit}"

class CalculationLog(models.Model):
    """Hesaplama işlem logları (güvenlik ve analiz için)"""
    LOG_TYPES = [
        ('calculation', 'Hesaplama'),
        ('limit_check', 'Limit Kontrolü'),
        ('limit_exceeded', 'Limit Aşımı'),
        ('error', 'Hata'),
        ('security', 'Güvenlik'),
    ]
    
    # Kullanıcı bilgileri
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Kullanıcı')
    ip_address = models.GenericIPAddressField(db_index=True, verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    device_fingerprint = models.CharField(max_length=255, null=True, blank=True, verbose_name='Cihaz Parmak İzi')
    
    # İşlem bilgileri
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='calculation', verbose_name='Log Tipi')
    calculation_type = models.CharField(max_length=100, db_index=True, verbose_name='Hesaplama Türü')
    calculation_data = models.JSONField(default=dict, verbose_name='Hesaplama Verisi')
    result_data = models.JSONField(default=dict, verbose_name='Sonuç Verisi')
    
    # Status bilgileri
    is_successful = models.BooleanField(default=True, verbose_name='Başarılı mı?')
    error_message = models.TextField(blank=True, null=True, verbose_name='Hata Mesajı')
    limit_exceeded = models.BooleanField(default=False, verbose_name='Limit Aşıldı mı?')
    current_count = models.IntegerField(null=True, blank=True, verbose_name='Mevcut Sayı')
    current_limit = models.IntegerField(null=True, blank=True, verbose_name='Mevcut Limit')
    
    # Lokasyon bilgileri (eğer varsa)
    location_data = models.JSONField(default=dict, blank=True, verbose_name='Lokasyon Verisi')
    
    # Tarih bilgileri
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Oluşturulma Zamanı')
    
    class Meta:
        db_table = 'calculation_logs'
        verbose_name = 'Hesaplama Logu'
        verbose_name_plural = 'Hesaplama Logları'
        indexes = [
            models.Index(fields=['created_at', 'ip_address']),
            models.Index(fields=['created_at', 'user']),
            models.Index(fields=['calculation_type', 'created_at']),
            models.Index(fields=['log_type', 'created_at']),
        ]
        ordering = ['-created_at']
    
    @classmethod
    def log_calculation(cls, user=None, ip_address=None, calculation_type=None, 
                       calculation_data=None, result_data=None, user_agent='', 
                       device_fingerprint=None, location_data=None, is_successful=True, 
                       error_message=None, limit_exceeded=False, current_count=None, 
                       current_limit=None):
        """Hesaplama logla"""
        log_type = 'limit_exceeded' if limit_exceeded else 'calculation'
        if not is_successful:
            log_type = 'error'
            
        return cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            log_type=log_type,
            calculation_type=calculation_type or 'unknown',
            calculation_data=calculation_data or {},
            result_data=result_data or {},
            is_successful=is_successful,
            error_message=error_message,
            limit_exceeded=limit_exceeded,
            current_count=current_count,
            current_limit=current_limit,
            location_data=location_data or {}
        )
    
    def __str__(self):
        user_info = self.user.username if self.user else f"IP:{self.ip_address}"
        status = "✅" if self.is_successful else "❌"
        limit_info = f"[{self.current_count}/{self.current_limit}]" if self.current_count is not None else ""
        return f"{status} {user_info} - {self.calculation_type} {limit_info} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

import uuid
from django.db import models
from django.utils import timezone


class Device(models.Model):
    """Cihaz kaydı — installation-scoped benzersiz kimlik."""
    device_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    installation_id = models.CharField(max_length=255, unique=True,
                                       help_text="Android tarafından gönderilen installation ID")
    email = models.EmailField(blank=True, null=True, unique=True,
                              help_text="Kredi satın alma için gerekli e-posta adresi")
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device {self.installation_id[:12]}..."


class ChildProfile(models.Model):
    """Çocuk profili — cihaz başına performans verileri."""

    EDUCATION_PERIOD_CHOICES = [
        ('okul_oncesi', 'Okul Öncesi (5-6 yaş)'),
        ('sinif_1', '1. Sınıf (6-7 yaş)'),
        ('sinif_2', '2. Sınıf (7-8 yaş)'),
        ('sinif_3', '3. Sınıf (8-9 yaş)'),
        ('sinif_4', '4. Sınıf (9-10 yaş)'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, default="Çocuk")
    education_period = models.CharField(
        max_length=20, choices=EDUCATION_PERIOD_CHOICES, default='sinif_2',
        help_text="Eğitim dönemi — soru üretimi bu döneme göre yapılır"
    )
    is_active = models.BooleanField(
        default=True, help_text="Cihazda aktif seçili profil"
    )
    total_correct = models.IntegerField(default=0)
    total_shown = models.IntegerField(default=0)
    total_time_seconds = models.IntegerField(
        default=0, help_text="Toplam çözüm süresi (saniye)"
    )
    current_difficulty = models.IntegerField(default=1)
    stats_json = models.JSONField(default=dict, blank=True,
                                  help_text="Tip/zorluk bazlı detaylı istatistikler")
    daily_stats = models.JSONField(
        default=dict, blank=True,
        help_text="Günlük performans özeti: {tarih: {correct, shown, time_seconds}}"
    )
    weekly_report_json = models.JSONField(
        default=dict, blank=True,
        help_text="AI tarafından üretilen haftalık performans raporu"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _VALID_EDUCATION_PERIODS = {'okul_oncesi', 'sinif_1', 'sinif_2', 'sinif_3', 'sinif_4'}

    class Meta:
        unique_together = ('device', 'name')

    def save(self, *args, **kwargs):
        if self.education_period not in self._VALID_EDUCATION_PERIODS:
            self.education_period = 'sinif_2'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.get_education_period_display()}] ({self.device})"

    @property
    def accuracy(self):
        if self.total_shown == 0:
            return 0.0
        return self.total_correct / self.total_shown

    @property
    def question_count(self):
        """Bu dönem için soru sayısı."""
        counts = {'okul_oncesi': 30, 'sinif_1': 40}
        return counts.get(self.education_period, 50)


class CreditBalance(models.Model):
    """Cihaz başına kredi bakiyesi."""
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='credits')
    balance = models.IntegerField(default=0, help_text="Kalan kredi (her biri 50 soru)")
    total_purchased = models.IntegerField(default=0, help_text="Toplam satın alınan kredi")
    total_used = models.IntegerField(default=0, help_text="Toplam kullanılan kredi")
    free_set_used = models.BooleanField(default=False, help_text="Ücretsiz 50 soru kullanıldı mı")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credits: {self.balance} (device={self.device})"

    def add_credits(self, amount):
        self.balance += amount
        self.total_purchased += amount
        self.save(update_fields=['balance', 'total_purchased', 'updated_at'])

    def use_credit(self):
        """1 kredi kullan. Başarılıysa True döner."""
        if self.balance <= 0:
            return False
        self.balance -= 1
        self.total_used += 1
        self.save(update_fields=['balance', 'total_used', 'updated_at'])
        return True


class PurchaseRecord(models.Model):
    """Google Play satın alma kaydı."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='purchases')
    purchase_token = models.TextField(unique=True)
    product_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=255, blank=True, default='')
    credits_added = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    consumed = models.BooleanField(default=False)
    verification_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "✅" if self.verified else "❌"
        return f"{status} {self.product_id} → {self.credits_added} kredi"


class QuestionSet(models.Model):
    """Çocuk için AI tarafından üretilen kişisel soru seti."""
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='question_sets')
    version = models.IntegerField()
    questions_json = models.JSONField(help_text="50 sorudan oluşan set")
    is_ai_generated = models.BooleanField(default=False)
    credit_used = models.BooleanField(default=False, help_text="Bu set için kredi harcandı mı")
    solved_ids = models.JSONField(default=list, blank=True,
                                  help_text="Çözülen soru global ID'leri")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version']
        unique_together = ('child', 'version')

    def __str__(self):
        ai = "🤖" if self.is_ai_generated else "📦"
        return f"{ai} v{self.version} ({self.child.name})"


class CreditPackage(models.Model):
    """
    Satın alınabilir kredi paketleri.
    Backend'den dinamik çekilir; Play Console'daki product_id ile eşleşmeli.
    """
    product_id = models.CharField(max_length=100, unique=True,
                                  help_text="Google Play product ID (ör: kredi_5)")
    display_name = models.CharField(max_length=200, help_text="Kullanıcıya gösterilen ad")
    credits = models.IntegerField(help_text="Bu paketle eklenen kredi sayısı")
    questions_count = models.IntegerField(
        help_text="credits × QUESTIONS_PER_CREDIT — bilgi amaçlı gösterim için"
    )
    description = models.CharField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'credits']

    def __str__(self):
        return f"{self.display_name} ({self.product_id}) — {self.credits} kredi"


class LevelSet(models.Model):
    """Çocuk için AI tarafından üretilen kişisel seviye seti (12 bulmaca)."""
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='level_sets')
    version = models.IntegerField()
    levels_json = models.JSONField(help_text="12 seviyeden oluşan set")
    is_ai_generated = models.BooleanField(default=False)
    credit_used = models.BooleanField(default=False, help_text="Bu set için kredi harcandı mı")
    completed_level_ids = models.JSONField(
        default=list, blank=True,
        help_text="Tamamlanan seviye ID'leri"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version']
        unique_together = ('child', 'version')

    def __str__(self):
        ai = "🤖" if self.is_ai_generated else "📦"
        completed = len(self.completed_level_ids or [])
        total = len(self.levels_json or [])
        return f"{ai} v{self.version} ({self.child.name}) — {completed}/{total}"


class RenewalLock(models.Model):
    """
    Otomatik içerik yenileme kilidi — idempotency garantisi.

    Aynı çocuk için eşzamanlı yenileme başlatma riskini ortadan kaldırır.
    Örnek: kullanıcı "tüm seviyeler bitti" + "kredi yükledi" sinyalleri aynı anda geldiğinde
    yalnızca biri kredi düşer, diğeri kilitli görüp gerisiz döner.

    content_type: 'questions' | 'levels'
    TTL: 15 dakika (generation timeout'dan fazla) — sunucu çökerse otomatik temizlenir.
    """
    child = models.ForeignKey(
        ChildProfile, on_delete=models.CASCADE, related_name='renewal_locks'
    )
    content_type = models.CharField(max_length=20)
    expires_at = models.DateTimeField(help_text="Bu süre geçince kilit geçersiz sayılır")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('child', 'content_type')
        indexes = [models.Index(fields=['expires_at'])]

    def __str__(self):
        return f"RenewalLock({self.content_type}) — {self.child.name} until {self.expires_at}"


class AiQueryRecord(models.Model):
    """Her AI sorgu isteği için kayıt — denetim ve analiz için."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='ai_queries')
    child = models.ForeignKey(ChildProfile, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='ai_queries')
    prompt = models.TextField()
    response = models.TextField(blank=True)
    provider = models.CharField(max_length=50, default='simulate')
    credit_cost = models.IntegerField(default=1)
    success = models.BooleanField(default=False)
    error_message = models.CharField(max_length=500, blank=True)
    response_time_ms = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        mark = "✅" if self.success else "❌"
        return f"{mark} {self.provider} — {self.prompt[:50]}"


class Question(models.Model):
    """Master soru bankası — tüm sorular burada tutulur."""
    question_id = models.IntegerField(unique=True, help_text="Global benzersiz soru ID'si")
    text = models.CharField(max_length=500)
    answer = models.IntegerField()
    question_type = models.CharField(max_length=50, help_text="toplama, cikarma, carpma, bolme")
    difficulty = models.IntegerField(default=1)
    hint = models.CharField(max_length=500, blank=True)
    batch_number = models.IntegerField(default=0, db_index=True,
                                       help_text="0=ücretsiz set, 1+=kredi ile açılan set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['batch_number', 'question_id']

    def __str__(self):
        return f"Q{self.question_id} [{self.question_type}] batch={self.batch_number}"


class UserQuestionProgress(models.Model):
    """Çocuk profili başına soru çözme ilerlemesi."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='question_progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_progress')
    child = models.ForeignKey(
        'ChildProfile', on_delete=models.CASCADE,
        related_name='question_progress', null=True, blank=True,
    )
    solved = models.BooleanField(default=False)
    solve_count = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('device', 'question', 'child')

    def __str__(self):
        status = "✅" if self.solved else "⬜"
        child_name = self.child.name if self.child else "?"
        return f"{status} Q{self.question.question_id} — {child_name}"

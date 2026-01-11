from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, UserSession, UserActivity, SecurityEvent
from utils.email_service import EmailService
import secrets
from django.contrib import messages
import json

# Admin onaylı kayıt için yardımcı fonksiyonlar
def activate_user_and_send_password(user):
    """Kullanıcıyı aktif yapar ve şifre gönderir"""
    try:
        # Rastgele şifre oluştur
        password = secrets.token_urlsafe(8)
        user.set_password(password)
        user.is_active = True
        user.save()
        
        # Kullanıcıya şifre gönder
        message = f"""
Merhaba {user.username},

Admin onayından geçtiniz! Hesabınız aktif edildi.

Giriş Bilgileriniz:
- Kullanıcı Adı: {user.username}
- Şifre: {password}

Giriş yapmak için: https://tarimimar.com.tr/login

İlk girişinizden sonra şifrenizi değiştirebilirsiniz.

İyi çalışmalar!
        """
        
        EmailService.send_simple_email(
            to_email=user.email,
            subject="Hesabınız Aktif Edildi",
            message=message
        )
        
        return True, f"Kullanıcı {user.username} aktif edildi ve şifre gönderildi."
        
    except Exception as e:
        return False, f"Hata: {str(e)}"

def send_password_reset_to_user(user):
    """Kullanıcıya yeni şifre oluştur ve gönder"""
    try:
        # Rastgele şifre oluştur
        password = secrets.token_urlsafe(8)
        user.set_password(password)
        user.save()
        
        # Kullanıcıya yeni şifre gönder
        message = f"""
Merhaba {user.username},

Şifre sıfırlama talebiniz admin tarafından onaylandı.

Yeni Giriş Bilgileriniz:
- Kullanıcı Adı: {user.username}
- Yeni Şifre: {password}

Giriş yapmak için: https://tarimimar.com.tr/login

Güvenlik için ilk girişinizden sonra şifrenizi değiştirmenizi öneririz.

İyi çalışmalar!
        """
        
        EmailService.send_simple_email(
            to_email=user.email,
            subject="Şifreniz Sıfırlandı",
            message=message
        )
        
        return True, f"Kullanıcı {user.username} için yeni şifre oluşturuldu ve gönderildi."
        
    except Exception as e:
        return False, f"Hata: {str(e)}"

def send_admin_registration_notification(user):
    """Admin'e yeni kayıt bildirimi gönder"""
    try:
        message = f"""
Yeni Kayıt Talebi

Kullanıcı Adı: {user.username}
E-posta: {user.email}
Kayıt Tarihi: {user.date_joined}

Bu kullanıcıyı aktif etmek için admin panele giriş yapın.
        """
        
        EmailService.send_simple_email(
            to_email='info@tarimimar.com.tr',  # Admin email
            subject="Yeni Kayıt Talebi",
            message=message
        )
        return True
    except Exception as e:
        return False

# User admin'ini genişlet
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Bilgileri'
    extra = 0
    readonly_fields = ('last_login_ip', 'last_login_time', 'last_password_reset_email', 'created_at', 'updated_at')

# Admin Dashboard View
@staff_member_required
def admin_dashboard_view(request):
    """Gelişmiş Admin Gösterge Paneli"""
    
    # Temel istatistikler
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Kullanıcı istatistikleri
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    pending_users = User.objects.filter(is_active=False, is_staff=False).count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # Güvenlik istatistikleri
    security_events_today = SecurityEvent.objects.filter(created_at__date=today).count()
    failed_logins_today = SecurityEvent.objects.filter(
        event_type='failed_login', 
        created_at__date=today
    ).count()
    
    # En son aktiviteler
    recent_registrations = User.objects.filter(is_active=False, is_staff=False).order_by('-date_joined')[:10]
    recent_security_events = SecurityEvent.objects.filter(severity__in=['high', 'critical']).order_by('-created_at')[:10]
    recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:20]
    
    # En aktif kullanıcılar (son 30 gün)
    active_users_stats = UserActivity.objects.filter(
        created_at__gte=month_ago
    ).values(
        'user__username', 'user__email'
    ).annotate(
        activity_count=Count('id')
    ).order_by('-activity_count')[:10]
    
    # IP bazlı şüpheli aktiviteler
    suspicious_ips = SecurityEvent.objects.filter(
        created_at__gte=week_ago
    ).values('ip_address').annotate(
        event_count=Count('id')
    ).filter(event_count__gte=5).order_by('-event_count')[:10]
    
    context = {
        'title': 'Kullanıcı Yönetimi Gösterge Paneli',
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'pending_users': pending_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'new_users_month': new_users_month,
            'security_events_today': security_events_today,
            'failed_logins_today': failed_logins_today,
        },
        'recent_registrations': recent_registrations,
        'recent_security_events': recent_security_events,
        'recent_activities': recent_activities,
        'active_users_stats': active_users_stats,
        'suspicious_ips': suspicious_ips,
    }
    
    return render(request, 'admin/accounts/dashboard.html', context)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined_formatted', 'last_login_formatted', 'activation_status', 'quick_actions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    actions = [
        'activate_users_and_send_passwords', 
        'reset_passwords_and_send', 
        'deactivate_users',
        'send_welcome_email',
        'bulk_password_reset'
    ]
    
    # URL'leri genişlet
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', admin_dashboard_view, name='accounts_dashboard'),
            path('<int:user_id>/quick-activate/', self.quick_activate_view, name='accounts_quick_activate'),
            path('<int:user_id>/quick-reset/', self.quick_reset_view, name='accounts_quick_reset'),
        ]
        return custom_urls + urls
    
    def date_joined_formatted(self, obj):
        return obj.date_joined.strftime("%d.%m.%Y %H:%M") if obj.date_joined else "-"
    date_joined_formatted.short_description = "Kayıt Tarihi"
    
    def last_login_formatted(self, obj):
        return obj.last_login.strftime("%d.%m.%Y %H:%M") if obj.last_login else "Hiç giriş yapmadı"
    last_login_formatted.short_description = "Son Giriş"
    
    def activation_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Aktif</span>')
        else:
            return format_html('<span style="color: red;">❌ Pasif (Onay Bekliyor)</span>')
    activation_status.short_description = "Durum"
    
    def quick_actions(self, obj):
        """Hızlı işlem butonları"""
        buttons = []
        
        if not obj.is_active and not obj.is_staff:
            # Pasif kullanıcılar için aktifleştirme butonu
            activate_url = reverse('admin:accounts_quick_activate', args=[obj.pk])
            buttons.append(f'<a href="{activate_url}" class="button" style="background: #28a745; color: white; padding: 3px 8px; text-decoration: none; border-radius: 4px; font-size: 11px;">⚡ Aktifleştir</a>')
        
        if obj.is_active:
            # Aktif kullanıcılar için şifre sıfırlama butonu
            reset_url = reverse('admin:accounts_quick_reset', args=[obj.pk])
            buttons.append(f'<a href="{reset_url}" class="button" style="background: #ffc107; color: black; padding: 3px 8px; text-decoration: none; border-radius: 4px; font-size: 11px;">🔑 Şifre Sıfırla</a>')
        
        return format_html(' '.join(buttons)) if buttons else '-'
    quick_actions.short_description = "Hızlı İşlemler"
    
    def quick_activate_view(self, request, user_id):
        """Tek tıklamayla kullanıcı aktifleştirme"""
        user = User.objects.get(pk=user_id)
        success, message = activate_user_and_send_password(user)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def quick_reset_view(self, request, user_id):
        """Tek tıklamayla şifre sıfırlama"""
        user = User.objects.get(pk=user_id)
        success, message = send_password_reset_to_user(user)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def activate_users_and_send_passwords(self, request, queryset):
        """Seçilen pasif kullanıcıları aktif et ve şifre gönder"""
        success_count = 0
        error_messages = []
        
        for user in queryset.filter(is_active=False, is_staff=False):
            success, message = activate_user_and_send_password(user)
            if success:
                success_count += 1
            else:
                error_messages.append(message)
        
        if success_count > 0:
            messages.success(request, f"✅ {success_count} kullanıcı başarıyla aktif edildi ve şifre gönderildi.")
        
        if error_messages:
            for error in error_messages[:5]:  # İlk 5 hatayı göster
                messages.error(request, error)
    
    activate_users_and_send_passwords.short_description = "🟢 Seçilen kullanıcıları aktif et ve şifre gönder"
    
    def reset_passwords_and_send(self, request, queryset):
        """Seçilen kullanıcıların şifrelerini sıfırla ve gönder"""
        success_count = 0
        error_messages = []
        
        for user in queryset.filter(is_active=True):
            success, message = send_password_reset_to_user(user)
            if success:
                success_count += 1
            else:
                error_messages.append(message)
        
        if success_count > 0:
            messages.success(request, f"🔑 {success_count} kullanıcının şifresi sıfırlandı ve gönderildi.")
        
        if error_messages:
            for error in error_messages[:5]:
                messages.error(request, error)
    
    reset_passwords_and_send.short_description = "🔑 Seçilen kullanıcıların şifrelerini sıfırla ve gönder"
    
    def deactivate_users(self, request, queryset):
        """Seçilen kullanıcıları pasifleştir"""
        count = 0
        for user in queryset.filter(is_active=True, is_staff=False):
            user.is_active = False
            user.save()
            count += 1
        
        if count > 0:
            messages.success(request, f"❌ {count} kullanıcı pasifleştirildi.")
    
    deactivate_users.short_description = "❌ Seçilen kullanıcıları pasifleştir"
    
    def send_welcome_email(self, request, queryset):
        """Hoş geldiniz e-postası gönder"""
        success_count = 0
        
        for user in queryset.filter(is_active=True):
            try:
                message = f"""
Merhaba {user.first_name or user.username},

Tarım İmar hesaplama sistemimize hoş geldiniz!

Giriş yapmak için: https://tarimimar.com.tr/login
- Kullanıcı Adı: {user.username}
- E-posta: {user.email}

Sistemimizde yapabilecekleriniz:
• Tarımsal yapı hesaplamaları
• Harita üzerinde alan belirleme
• Hesaplama geçmişi saklama
• PDF raporlar oluşturma

Herhangi bir sorunuz olursa info@tarimimar.com.tr adresinden bize ulaşabilirsiniz.

İyi çalışmalar!
                """
                
                EmailService.send_simple_email(
                    to_email=user.email,
                    subject="Tarım İmar'a Hoş Geldiniz!",
                    message=message
                )
                success_count += 1
                
            except Exception:
                pass
        
        if success_count > 0:
            messages.success(request, f"📧 {success_count} kullanıcıya hoş geldiniz e-postası gönderildi.")
    
    send_welcome_email.short_description = "📧 Hoş geldiniz e-postası gönder"
    
    def bulk_password_reset(self, request, queryset):
        """Toplu şifre sıfırlama - Güçlü şifreler"""
        success_count = 0
        failed_users = []
        
        for user in queryset.filter(is_active=True):
            try:
                # Daha güçlü şifre üret
                password = secrets.token_urlsafe(12)  # 12 karakter
                user.set_password(password)
                user.save()
                
                # Kullanıcıya bildir
                message = f"""
Merhaba {user.username},

Admin tarafından güvenlik amacıyla şifreniz yenilendi.

Yeni Giriş Bilgileriniz:
- Kullanıcı Adı: {user.username}
- Yeni Şifre: {password}

🔐 Güvenlik Önerileri:
• Şifrenizi kimseyle paylaşmayın
• İlk girişinizde şifrenizi değiştirin
• Güçlü ve benzersiz şifreler kullanın

Giriş: https://tarimimar.com.tr/login
                """
                
                EmailService.send_simple_email(
                    to_email=user.email,
                    subject="🔐 Şifreniz Güvenlik Amacıyla Yenilendi",
                    message=message
                )
                
                success_count += 1
                
            except Exception as e:
                failed_users.append(f"{user.username}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"🔐 {success_count} kullanıcının şifresi güvenli şekilde yenilendi.")
        
        if failed_users:
            for error in failed_users[:3]:  # İlk 3 hatayı göster
                messages.error(request, f"Hata: {error}")
    
    bulk_password_reset.short_description = "🔐 Toplu güvenli şifre yenileme"

# User admin'ini yeniden kaydet
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login_time', 'created_at')
    list_filter = ('is_active_profile', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Sistem Bilgileri', {'fields': ('last_login_ip', 'last_login_time', 'is_active_profile')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device_info', 'login_time', 'last_activity', 'is_active')
    list_filter = ('is_active', 'login_time', 'last_activity')
    search_fields = ('user__username', 'ip_address', 'device_info')
    readonly_fields = ('session_key', 'login_time', 'last_activity')
    date_hierarchy = 'login_time'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Genel Bilgiler', {'fields': ('user', 'activity_type', 'description')}),
        ('Teknik Bilgiler', {'fields': ('ip_address', 'user_agent')}),
        ('Veri', {'fields': ('location_data', 'calculation_data', 'result_data')}),
        ('Zaman', {'fields': ('created_at',)}),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'severity', 'ip_address', 'user', 'username_attempted', 'created_at')
    list_filter = ('event_type', 'severity', 'created_at')
    search_fields = ('ip_address', 'user__username', 'username_attempted', 'email_attempted', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Olay Bilgileri', {
            'fields': ('event_type', 'severity', 'description')
        }),
        ('Güvenlik Bilgileri', {
            'fields': ('ip_address', 'user_agent', 'user')
        }),
        ('Deneme Bilgileri', {
            'fields': ('username_attempted', 'email_attempted')
        }),
        ('Ek Bilgiler', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Zaman', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    # Özel actions
    actions = ['mark_as_reviewed', 'export_security_report']
    
    def mark_as_reviewed(self, request, queryset):
        # Gelecekte incelendi olarak işaretleme için
        queryset.update(metadata={'reviewed': True, 'reviewed_by': request.user.username, 'reviewed_at': timezone.now().isoformat()})
        messages.success(request, f"{queryset.count()} güvenlik olayı incelendi olarak işaretlendi.")
    mark_as_reviewed.short_description = "✅ Seçilen olayları incelendi olarak işaretle"
    
    def export_security_report(self, request, queryset):
        """Güvenlik raporunu JSON olarak export et"""
        import json
        from django.http import HttpResponse
        
        data = []
        for event in queryset:
            data.append({
                'event_type': event.get_event_type_display(),
                'severity': event.get_severity_display(),
                'ip_address': event.ip_address,
                'user': event.user.username if event.user else None,
                'username_attempted': event.username_attempted,
                'email_attempted': event.email_attempted,
                'description': event.description,
                'created_at': event.created_at.isoformat(),
                'metadata': event.metadata,
            })
        
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="security_report_{timezone.now().strftime("%Y%m%d_%H%M")}.json"'
        return response
    export_security_report.short_description = "📋 Güvenlik raporu export et"

from django.contrib.admin import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils.safestring import mark_safe

# Admin site özelleştirmeleri
admin.site.site_header = "🌾 Tarım İmar Yönetim Paneli"
admin.site.site_title = "Tarım İmar Admin"
admin.site.index_title = "Yönetim Paneli"

class CustomAdminSite(AdminSite):
    """Özelleştirilmiş Admin Site"""
    
    def index(self, request, extra_context=None):
        """Ana admin sayfasını özelleştir"""
        extra_context = extra_context or {}
        
        # Kullanıcı istatistikleri
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        
        # Email doğrulaması olan kullanıcılar
        verified_users = 0
        unverified_users = 0
        if hasattr(User.objects.first(), 'email_verified'):
            verified_users = User.objects.filter(email_verified=True).count()
            unverified_users = User.objects.filter(email_verified=False).count()
        
        extra_context['user_stats'] = {
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superuser_count': superuser_count,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'inactive_users': total_users - active_users,
        }
        
        return super().index(request, extra_context)

# Custom admin site kullan
# admin_site = CustomAdminSite(name='custom_admin')

@staff_member_required
def admin_dashboard_view(request):
    """Admin Dashboard View"""
    from django.shortcuts import render
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    
    User = get_user_model()
    
    # İstatistikler
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superuser_count = User.objects.filter(is_superuser=True).count()
    
    # Son 30 günde kaydolan kullanıcılar
    last_30_days = timezone.now() - timedelta(days=30)
    recent_signups = User.objects.filter(date_joined__gte=last_30_days).count()
    
    # Son 7 günde aktif olan kullanıcılar
    last_7_days = timezone.now() - timedelta(days=7)
    recent_active = User.objects.filter(last_login__gte=last_7_days).count() if User.objects.first() and hasattr(User.objects.first(), 'last_login') else 0
    
    # Email doğrulaması
    verified_users = 0
    unverified_users = 0
    if hasattr(User.objects.first(), 'email_verified'):
        verified_users = User.objects.filter(email_verified=True).count()
        unverified_users = User.objects.filter(email_verified=False).count()
    
    # Son kullanıcılar (10 kişi)
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Güvenlik olayları
    security_events = []
    if SecurityEvent.objects.exists():
        security_events = SecurityEvent.objects.filter(
            created_at__gte=last_7_days
        ).order_by('-created_at')[:10]
    
    # Hesaplama aktiviteleri (eğer varsa)
    calculation_stats = {}
    try:
        from calculations.models import Calculation
        calculation_stats = {
            'total_calculations': Calculation.objects.count(),
            'recent_calculations': Calculation.objects.filter(
                created_at__gte=last_7_days
            ).count() if hasattr(Calculation, 'created_at') else 0,
        }
    except ImportError:
        pass
    
    context = {
        'title': 'Kullanıcı Yönetimi Dashboard',
        'user_stats': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'staff_users': staff_users,
            'superuser_count': superuser_count,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'recent_signups': recent_signups,
            'recent_active': recent_active,
        },
        'recent_users': recent_users,
        'security_events': security_events,
        'calculation_stats': calculation_stats,
        'dashboard_url': reverse('accounts:accounts_dashboard'),
    }
    
    return render(request, 'admin/accounts/dashboard.html', context)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import UserProfile, UserSession, UserActivity, SecurityEvent
from utils.email_service import EmailService
import secrets
import string
import json

# Admin onaylı kayıt için yardımcı fonksiyonlar
def activate_user_and_send_password(user):
    """Kullanıcıyı aktif yapar ve durum bilgisini admin'e iletir"""
    try:
        profile = getattr(user, 'profile', None)
        password = None
        
        if profile and profile.password_self_chosen:
            # Kullanıcı şifresini kendisi belirlemiş, şifre değiştirmeye gerek yok
            user.is_active = True
            user.save()
            
            # Admin'e bilgi maili gönder
            message = f"""
Kullanıcı aktifleştirildi (Şifresini kendisi belirlemiş).
- Kullanıcı Adı: {user.username}
- Email: {user.email}
- Şifre Durumu: Kullanıcı tarafından belirlenmiş (değiştirilmedi)
- Admin işlem zamanı: {timezone.now().strftime('%Y-%m-%d %H:%M')}
            """
            password_message = "Kullanıcı şifresini kendisi belirlemiş"
        else:
            # Admin şifre belirleyecek
            password = secrets.token_urlsafe(8)
            user.set_password(password)
            user.is_active = True
            user.save()
            
            # Admin'e bilgi maili gönder
            message = f"""
Kullanıcı aktifleştirildi ve yeni şifre atandı.
- Kullanıcı Adı: {user.username}
- Email: {user.email}
- Geçici Şifre: {password}
- Admin işlem zamanı: {timezone.now().strftime('%Y-%m-%d %H:%M')}
            """
            password_message = password
        
        EmailService.send_simple_email(
            to_email=settings.ADMIN_NOTIFICATION_EMAIL,
            subject="Kullanıcı Aktifleştirildi",
            message=message,
            force_admin=True
        )
        
        # Profile güncelle
        if profile:
            profile.awaiting_activation = False
            profile.activation_mail_sent = True
            profile.activation_mail_sent_at = timezone.now()
            profile.save()
        
        return True, password_message
    except Exception as e:
        print(f"Kullanıcı aktifleştirme hatası: {e}")
        return False, None

def reset_user_password_and_send(user):
    """Kullanıcı şifresini sıfırlar ve bilgiyi admin’e iletir (kullanıcıya mail yok)"""
    try:
        # Rastgele şifre oluştur
        password = secrets.token_urlsafe(8)
        user.set_password(password)
        user.save()
        
        # Admin’e bilgi maili gönder
        message = f"""
Kullanıcı şifresi sıfırlandı.
- Kullanıcı Adı: {user.username}
- Email: {user.email}
- Yeni Geçici Şifre: {password}
- İşlem zamanı: {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        EmailService.send_simple_email(
            to_email=settings.ADMIN_NOTIFICATION_EMAIL,
            subject="Kullanıcı Şifresi Sıfırlandı",
            message=message,
            force_admin=True
        )
        
        return True, password
    except Exception as e:
        print(f"Şifre sıfırlama hatası: {e}")
        return False, None

def send_admin_registration_notification(user):
    """Yeni kullanıcı kaydı için admin'e bildirim e-postası gönder"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Admin bildirim e-postası gönderiliyor: {user.email}")
        
        # E-posta içeriği
        subject = f"Yeni Kullanıcı Kayıt Başvurusu - {user.get_full_name()}"
        message = f"""
Merhaba,

Sitenizde yeni bir kullanıcı kayıt başvurusu yapıldı:

Kullanıcı Bilgileri:
- Ad Soyad: {user.get_full_name()}
- E-posta: {user.email}
- Kullanıcı Adı: {user.username}
- Kayıt Tarihi: {user.date_joined.strftime('%d/%m/%Y %H:%M')}

Admin panelinden kullanıcıyı onaylamak için:
http://tarimimar.com.tr/admin/auth/user/{user.id}/change/

Bu e-posta otomatik olarak gönderilmiştir.

Saygılarla,
Tarımimar Sistemi
"""
        
        logger.info(f"E-posta içeriği hazırlandı. Konu: {subject}")
        
        # Admin'e e-posta gönder
        result = EmailService.send_simple_email(
            to_email='info@tarimimar.com.tr',
            subject=subject,
            message=message
        )
        
        logger.info(f"E-posta gönderim sonucu: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Admin bildirim e-postası gönderiminde hata: {e}")
        print(f"Admin bildirim e-postası gönderiminde hata: {e}")
        return False

class CustomUserAdmin(UserAdmin):
    """Gelişmiş User Admin Panel"""
    
    # Admin listesi görünümü
    list_display = ['id', 'username', 'email', 'user_status', 'password_status', 'mail_action_status', 'date_joined', 'last_login_display', 'admin_actions']
    list_filter = ['is_active', 'is_staff', 'date_joined', 'last_login', 'profile__awaiting_activation', 'profile__awaiting_password_reset', 'profile__activation_mail_sent', 'profile__password_reset_mail_sent', 'profile__password_self_chosen']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    
    # Listeleme ayarları
    list_per_page = 25
    list_max_show_all = 100
    
    # Toplu işlemler
    actions = [
        'activate_users', 'deactivate_users', 'send_bulk_password_reset',
        'export_user_report', 'mark_users_for_review', 'delete_inactive_users',
        'send_welcome_emails', 'generate_user_statistics',
        'mark_awaiting_activation', 'mark_awaiting_password_reset',
        'send_activation_mail_to_admin', 'send_password_reset_mail_to_admin',
        'clear_mail_flags'
    ]
    
    def user_status(self, obj):
        """Kullanıcı durumunu renkli göster"""
        if obj.is_superuser:
            return format_html('<span style="color: #d63384; font-weight: bold;">🛡️ Süper Admin</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #0d6efd; font-weight: bold;">👤 Personel</span>')
        elif obj.is_active:
            return format_html('<span style="color: #198754;">✅ Aktif</span>')
        else:
            return format_html('<span style="color: #dc3545;">❌ Pasif</span>')
    user_status.short_description = "Durum"
    
    def password_status(self, obj):
        """Şifre durumunu göster"""
        if not hasattr(obj, 'profile'):
            return format_html('<span style="color: gray;">-</span>')
        
        profile = obj.profile
        if profile.password_self_chosen:
            return format_html('<span style="color: #198754;">🔑 Kullanıcı belirledi</span>')
        else:
            return format_html('<span style="color: #6c757d;">🔧 Admin belirleyecek</span>')
    password_status.short_description = "Şifre Durumu"
    
    def last_login_display(self, obj):
        """Son giriş tarihini güzel formatta göster"""
        if obj.last_login:
            now = timezone.now()
            diff = now - obj.last_login
            
            if diff.days > 30:
                return format_html('<span style="color: #dc3545;">🔴 {}+ gün önce</span>', diff.days)
            elif diff.days > 7:
                return format_html('<span style="color: #ffc107;">🟡 {} gün önce</span>', diff.days)
            elif diff.days > 0:
                return format_html('<span style="color: #198754;">🟢 {} gün önce</span>', diff.days)
            else:
                hours = diff.seconds // 3600
                return format_html('<span style="color: #198754;">🟢 {} saat önce</span>', hours)
        return format_html('<span style="color: #6c757d;">Hiç giriş yapmamış</span>')
    last_login_display.short_description = "Son Giriş"
    
    def mail_action_status(self, obj):
        """Mail işlem durumunu ikon ile gösterir"""
        if not hasattr(obj, 'profile'):
            return format_html('<span style="color: gray;">-</span>')
        
        profile = obj.profile
        status_parts = []
        
        if profile.awaiting_activation and not profile.activation_mail_sent:
            if profile.password_self_chosen:
                status_parts.append('<span style="color: #ff6600; font-weight: bold;">🔑 Kullanıcı şifresini belirledi - Aktivasyon bekliyor</span>')
            else:
                status_parts.append('<span style="color: orange; font-weight: bold;">📬 Aktivasyon ve şifre belirlenmesi bekliyor</span>')
        elif profile.awaiting_activation and profile.activation_mail_sent:
            status_parts.append('<span style="color: green;">✅ Aktivasyon maili gönderildi</span>')
        
        if profile.awaiting_password_reset and not profile.password_reset_mail_sent:
            status_parts.append('<span style="color: blue; font-weight: bold;">🔑 Şifre reset bekliyor</span>')
        elif profile.awaiting_password_reset and profile.password_reset_mail_sent:
            status_parts.append('<span style="color: green;">✅ Şifre reset maili gönderildi</span>')
        
        if not status_parts:
            return format_html('<span style="color: gray;">-</span>')
        
        return format_html('<br>'.join(status_parts))
    mail_action_status.short_description = "Mail Durumu"
    
    def admin_actions(self, obj):
        """Hızlı admin işlemleri"""
        try:
            activate_url = reverse('admin:quick_activate_user', args=[obj.pk])
            reset_url = reverse('admin:quick_reset_password', args=[obj.pk])
            
            actions = []
            
            if not obj.is_active:
                actions.append(f'<a href="{activate_url}" style="color: #198754; text-decoration: none;">✅ Aktif Et</a>')
            
            actions.append(f'<a href="{reset_url}" style="color: #0d6efd; text-decoration: none;">🔑 Şifre Sıfırla</a>')
            
            return format_html(' | '.join(actions))
        except:
            return "N/A"
    admin_actions.short_description = "Hızlı İşlemler"
    
    def get_urls(self):
        """Özel admin URL'leri ekle"""
        urls = super().get_urls()
        custom_urls = [
            path('quick-activate/<int:user_id>/', self.admin_site.admin_view(self.quick_activate_user), name='quick_activate_user'),
            path('quick-reset/<int:user_id>/', self.admin_site.admin_view(self.quick_reset_password), name='quick_reset_password'),
            path('bulk-operations/', self.admin_site.admin_view(self.bulk_operations_view), name='bulk_operations'),
            path('<int:object_id>/activate-user/', self.admin_site.admin_view(self.activate_user_from_detail), name='activate_user_from_detail'),
        ]
        return custom_urls + urls
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Kullanıcı detay sayfasında aktivasyon butonu göster"""
        extra_context = extra_context or {}
        
        try:
            user = User.objects.get(pk=object_id)
            profile = getattr(user, 'profile', None)
            
            # Aktivasyon butonu gösterme koşulları
            if not user.is_active and profile and profile.awaiting_activation:
                extra_context['show_activate_button'] = True
                
                # Şifre durumuna göre buton metni
                if profile.password_self_chosen:
                    extra_context['activate_button_text'] = '🔑 Kullanıcıyı Aktif Et (Şifre Korunsun)'
                    extra_context['activate_button_class'] = 'btn-success'
                else:
                    extra_context['activate_button_text'] = '🔑 Kullanıcıyı Aktif Et ve Şifre Gönder'
                    extra_context['activate_button_class'] = 'btn-warning'
                    
                extra_context['activate_url'] = f'{object_id}/activate-user/'
        except User.DoesNotExist:
            pass
            
        return super().change_view(request, object_id, form_url, extra_context)
    
    def quick_activate_user(self, request, user_id):
        """Hızlı kullanıcı aktifleştirme"""
        try:
            user = User.objects.get(pk=user_id)
            success, password = activate_user_and_send_password(user)
            
            if success:
                messages.success(request, f"✅ {user.username} aktif edildi ve şifre gönderildi: {password}")
            else:
                messages.error(request, f"❌ {user.username} aktifleştirilirken hata oluştu")
                
        except User.DoesNotExist:
            messages.error(request, "Kullanıcı bulunamadı")
        
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def activate_user_from_detail(self, request, object_id):
        """Kullanıcı detay sayfasından aktivasyon"""
        try:
            user = User.objects.get(pk=object_id)
            success, message = activate_user_and_send_password(user)
            
            if success:
                messages.success(request, f"✅ {user.username} başarıyla aktif edildi! {message}")
            else:
                messages.error(request, f"❌ {user.username} aktifleştirilirken hata oluştu: {message}")
                
        except User.DoesNotExist:
            messages.error(request, "Kullanıcı bulunamadı")
        
        return HttpResponseRedirect(reverse('admin:auth_user_change', args=[object_id]))
    
    def quick_reset_password(self, request, user_id):
        """Hızlı şifre sıfırlama"""
        try:
            user = User.objects.get(pk=user_id)
            success, password = reset_user_password_and_send(user)
            
            if success:
                messages.success(request, f"🔑 {user.username} şifresi sıfırlandı ve gönderildi: {password}")
            else:
                messages.error(request, f"❌ {user.username} şifresi sıfırlanırken hata oluştu")
                
        except User.DoesNotExist:
            messages.error(request, "Kullanıcı bulunamadı")
        
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def bulk_operations_view(self, request):
        """Toplu işlemler sayfası"""
        if request.method == 'POST':
            operation = request.POST.get('operation')
            user_ids = request.POST.getlist('user_ids')
            
            if operation == 'activate_all':
                count = 0
                for user_id in user_ids:
                    try:
                        user = User.objects.get(pk=user_id)
                        success, _ = activate_user_and_send_password(user)
                        if success:
                            count += 1
                    except User.DoesNotExist:
                        pass
                messages.success(request, f"{count} kullanıcı aktif edildi")
            
        users = User.objects.filter(is_active=False)[:50]  # İlk 50 pasif kullanıcı
        context = {'users': users, 'title': 'Toplu Kullanıcı İşlemleri'}
        return render(request, 'admin/accounts/bulk_operations.html', context)
    
    # Toplu işlem metodları
    def activate_users(self, request, queryset):
        """Seçili kullanıcıları aktif et ve şifre gönder"""
        count = 0
        for user in queryset.filter(is_active=False):
            success, password = activate_user_and_send_password(user)
            if success:
                count += 1
        
        self.message_user(request, f"✅ {count} kullanıcı aktif edildi ve şifreleri gönderildi.")
    activate_users.short_description = "✅ Seçili kullanıcıları aktif et ve şifre gönder"
    
    def deactivate_users(self, request, queryset):
        """Seçili kullanıcıları pasif et"""
        count = queryset.filter(is_active=True, is_staff=False).update(is_active=False)
        self.message_user(request, f"❌ {count} kullanıcı pasif edildi.")
    deactivate_users.short_description = "❌ Seçili kullanıcıları pasif et"
    
    def send_bulk_password_reset(self, request, queryset):
        """Toplu şifre sıfırlama"""
        count = 0
        for user in queryset.filter(is_active=True):
            success, _ = reset_user_password_and_send(user)
            if success:
                count += 1
        
        self.message_user(request, f"🔑 {count} kullanıcının şifresi sıfırlandı.")
    send_bulk_password_reset.short_description = "🔑 Toplu şifre sıfırlama"
    
    def export_user_report(self, request, queryset):
        """Kullanıcı raporunu export et"""
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_report_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Kullanıcı Adı', 'Email', 'Ad Soyad', 'Aktif', 'Personel', 'Kayıt Tarihi', 'Son Giriş'])
        
        for user in queryset:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                f"{user.first_name} {user.last_name}".strip(),
                "Evet" if user.is_active else "Hayır",
                "Evet" if user.is_staff else "Hayır",
                user.date_joined.strftime("%Y-%m-%d %H:%M"),
                user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Hiç"
            ])
        
        return response
    export_user_report.short_description = "📊 Kullanıcı raporu export et"
    
    def mark_users_for_review(self, request, queryset):
        """Kullanıcıları inceleme için işaretle"""
        count = queryset.count()
        self.message_user(request, f"👀 {count} kullanıcı inceleme için işaretlendi.")
    mark_users_for_review.short_description = "👀 İnceleme için işaretle"
    
    def delete_inactive_users(self, request, queryset):
        """30+ gündür pasif olan kullanıcıları sil"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        inactive_users = queryset.filter(
            is_active=False,
            last_login__lt=thirty_days_ago,
            is_staff=False
        )
        count = inactive_users.count()
        inactive_users.delete()
        
        self.message_user(request, f"🗑️ {count} uzun süre pasif olan kullanıcı silindi.")
    delete_inactive_users.short_description = "🗑️ Uzun süre pasif olanları sil"
    
    def send_welcome_emails(self, request, queryset):
        """Hoşgeldin e-postası gönder"""
        count = 0
        for user in queryset.filter(is_active=True):
            try:
                message = f"""
Merhaba {user.username},

Tarım İmar platformuna hoş geldiniz! 

Hesap bilgileriniz:
- Kullanıcı Adı: {user.username}
- Email: {user.email}

Platform üzerinden tarımsal hesaplamalar yapabilir, projelerinizi yönetebilirsiniz.

İyi çalışmalar!
                """
                
                EmailService.send_simple_email(
                    to_email=user.email,
                    subject="Tarım İmar'a Hoş Geldiniz!",
                    message=message
                )
                count += 1
            except Exception as e:
                print(f"Email gönderim hatası {user.email}: {e}")
        
        self.message_user(request, f"📧 {count} kullanıcıya hoşgeldin e-postası gönderildi.")
    send_welcome_emails.short_description = "📧 Hoşgeldin e-postası gönder"
    
    def generate_user_statistics(self, request, queryset):
        """Kullanıcı istatistikleri oluştur"""
        total = queryset.count()
        active = queryset.filter(is_active=True).count()
        staff = queryset.filter(is_staff=True).count()
        recent = queryset.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
        
        message = f"""
📊 Kullanıcı İstatistikleri:
- Toplam: {total}
- Aktif: {active}
- Personel: {staff}
- Son 7 gün: {recent}
        """
        
        self.message_user(request, message)
    generate_user_statistics.short_description = "📊 İstatistik oluştur"
    
    # Mail takip action'ları
    def mark_awaiting_activation(self, request, queryset):
        """Kullanıcıları aktivasyon bekliyor olarak işaretle"""
        count = 0
        for user in queryset:
            profile = getattr(user, 'profile', None)
            if profile:
                profile.awaiting_activation = True
                profile.activation_mail_sent = False
                profile.save()
                count += 1
        
        self.message_user(request, f"📬 {count} kullanıcı aktivasyon bekliyor olarak işaretlendi.")
    mark_awaiting_activation.short_description = "📬 Aktivasyon bekliyor işaretle"
    
    def mark_awaiting_password_reset(self, request, queryset):
        """Kullanıcıları şifre sıfırlama bekliyor olarak işaretle"""
        count = 0
        for user in queryset:
            profile = getattr(user, 'profile', None)
            if profile:
                profile.awaiting_password_reset = True
                profile.password_reset_mail_sent = False
                profile.save()
                count += 1
        
        self.message_user(request, f"🔑 {count} kullanıcı şifre sıfırlama bekliyor olarak işaretlendi.")
    mark_awaiting_password_reset.short_description = "🔑 Şifre reset bekliyor işaretle"
    
    def send_activation_mail_to_admin(self, request, queryset):
        """Aktivasyon maillerini sadece admin'e gönder"""
        count = 0
        admin_mails = []
        
        for user in queryset.filter(profile__awaiting_activation=True):
            profile = user.profile
            
            # Rastgele şifre oluştur
            password = secrets.token_urlsafe(8)
            user.set_password(password)
            user.is_active = True
            user.save()
            
            admin_mails.append(f"""
Kullanıcı: {user.username} ({user.email})
Ad Soyad: {user.first_name} {user.last_name}
Yeni Şifre: {password}
Aktivasyon Tarihi: {timezone.now().strftime('%Y-%m-%d %H:%M')}
            """)
            
            # Profile güncelle
            profile.activation_mail_sent = True
            profile.activation_mail_sent_at = timezone.now()
            profile.awaiting_activation = False
            profile.save()
            count += 1
        
        if admin_mails:
            # Admin'e toplu mail gönder
            admin_message = f"""
KULLANICI AKTİVASYON BİLGİLERİ

{len(admin_mails)} kullanıcı aktif edildi:

{'='*50}
            """ + "\n".join(admin_mails)
            
            try:
                EmailService.send_simple_email(
                    to_email="info@tarimimar.com.tr",
                    subject=f"Kullanıcı Aktivasyonları - {timezone.now().strftime('%Y-%m-%d')}",
                    message=admin_message
                )
            except Exception as e:
                self.message_user(request, f"❌ Email gönderimi başarısız: {e}")
        
        self.message_user(request, f"✅ {count} kullanıcı aktif edildi, bilgiler admin'e gönderildi.")
    send_activation_mail_to_admin.short_description = "✅ Aktif et (admin'e mail gönder)"
    
    def send_password_reset_mail_to_admin(self, request, queryset):
        """Şifre sıfırlama maillerini sadece admin'e gönder"""
        count = 0
        admin_mails = []
        
        for user in queryset.filter(profile__awaiting_password_reset=True):
            profile = user.profile
            
            # Rastgele şifre oluştur
            password = secrets.token_urlsafe(8)
            user.set_password(password)
            user.save()
            
            admin_mails.append(f"""
Kullanıcı: {user.username} ({user.email})
Ad Soyad: {user.first_name} {user.last_name}
Yeni Şifre: {password}
Şifre Reset Tarihi: {timezone.now().strftime('%Y-%m-%d %H:%M')}
            """)
            
            # Profile güncelle
            profile.password_reset_mail_sent = True
            profile.password_reset_mail_sent_at = timezone.now()
            profile.awaiting_password_reset = False
            profile.save()
            count += 1
        
        if admin_mails:
            # Admin'e toplu mail gönder
            admin_message = f"""
ŞİFRE SIFIRLAMA BİLGİLERİ

{len(admin_mails)} kullanıcının şifresi sıfırlandı:

{'='*50}
            """ + "\n".join(admin_mails)
            
            try:
                EmailService.send_simple_email(
                    to_email="info@tarimimar.com.tr",
                    subject=f"Şifre Sıfırlamaları - {timezone.now().strftime('%Y-%m-%d')}",
                    message=admin_message
                )
            except Exception as e:
                self.message_user(request, f"❌ Email gönderimi başarısız: {e}")
        
        self.message_user(request, f"🔑 {count} kullanıcının şifresi sıfırlandı, bilgiler admin'e gönderildi.")
    send_password_reset_mail_to_admin.short_description = "🔑 Şifre sıfırla (admin'e mail gönder)"
    
    def clear_mail_flags(self, request, queryset):
        """Mail flag'lerini temizle"""
        count = 0
        for user in queryset:
            profile = getattr(user, 'profile', None)
            if profile:
                profile.awaiting_activation = False
                profile.awaiting_password_reset = False
                profile.activation_mail_sent = False
                profile.password_reset_mail_sent = False
                profile.save()
                count += 1
        
        self.message_user(request, f"🧹 {count} kullanıcının mail flag'leri temizlendi.")
    clear_mail_flags.short_description = "🧹 Mail flag'lerini temizle"

# User Profile Admin (sadece model varsa kaydet)
try:
    class UserProfileAdmin(admin.ModelAdmin):
        list_display = ['user', 'awaiting_activation', 'awaiting_password_reset', 'activation_mail_sent', 'password_reset_mail_sent', 'password_reset_count_today', 'last_login_ip', 'created_at']
        list_filter = ['awaiting_activation', 'awaiting_password_reset', 'activation_mail_sent', 'password_reset_mail_sent', 'created_at', 'is_active_profile', 'password_reset_date']
        search_fields = ['user__username', 'user__email', 'last_login_ip', 'admin_notes']
        readonly_fields = ['created_at', 'updated_at', 'password_reset_count_today', 'password_reset_date']
        
        fieldsets = (
            ('Kullanıcı Bilgileri', {
                'fields': ('user', 'is_active_profile')
            }),
            ('Mail Takip Durumu', {
                'fields': ('awaiting_activation', 'awaiting_password_reset', 'activation_mail_sent', 'password_reset_mail_sent'),
                'classes': ('wide',)
            }),
            ('Şifre Sıfırlama Limit Kontrolü', {
                'fields': ('password_reset_count_today', 'password_reset_date'),
                'classes': ('wide',),
                'description': 'Günlük şifre sıfırlama limit takibi (maksimum 3/gün)'
            }),
            ('Mail Gönderim Zamanları', {
                'fields': ('activation_mail_sent_at', 'password_reset_mail_sent_at', 'last_password_reset_email'),
                'classes': ('collapse',)
            }),
            ('Admin Notları', {
                'fields': ('admin_notes',),
                'classes': ('wide',)
            }),
            ('Oturum Bilgileri', {
                'fields': ('last_login_ip', 'last_login_time'),
                'classes': ('collapse',)
            }),
            ('Tarihler', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
    
    admin.site.register(UserProfile, UserProfileAdmin)
except:
    pass

# Security Event Admin (sadece model varsa kaydet)
try:
    class SecurityEventAdmin(admin.ModelAdmin):
        list_display = ['event_type', 'severity', 'user', 'ip_address', 'created_at']
        list_filter = ['event_type', 'severity', 'created_at']
        search_fields = ['user__username', 'ip_address', 'username_attempted', 'email_attempted']
        readonly_fields = ['created_at']
        
        def get_actions(self, request):
            """Action'ları tamamen kaldır - action_checkbox hatasını önle"""
            return {}
        
        def mark_as_reviewed(self, request, queryset):
            count = queryset.count()
            messages.success(request, f"{count} güvenlik olayı incelendi olarak işaretlendi.")
        mark_as_reviewed.short_description = "✅ Seçilen olayları incelendi olarak işaretle"
        
        def export_security_report(self, request, queryset):
            """Güvenlik raporunu JSON olarak export et"""
            data = []
            for event in queryset:
                data.append({
                    'event_type': str(event.event_type),
                    'severity': str(event.severity),
                    'ip_address': event.ip_address,
                    'user': event.user.username if event.user else None,
                    'username_attempted': event.username_attempted,
                    'email_attempted': event.email_attempted,
                    'description': event.description,
                    'created_at': event.created_at.isoformat(),
                })
            
            response = HttpResponse(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type='application/json; charset=utf-8'
            )
            response['Content-Disposition'] = f'attachment; filename="security_report_{timezone.now().strftime("%Y%m%d_%H%M")}.json"'
            return response
        export_security_report.short_description = "📋 Güvenlik raporu export et"
    
    admin.site.register(SecurityEvent, SecurityEventAdmin)
except:
    pass

# Admin site özelleştirmeleri
admin.site.site_header = "🌾 Tarım İmar Yönetim Paneli"
admin.site.site_title = "Tarım İmar Admin"
admin.site.index_title = "Yönetim Paneli"

@staff_member_required
def admin_dashboard_view(request):
    """Admin Dashboard View"""
    from django.contrib.auth import get_user_model
    
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
    recent_active = 0
    try:
        recent_active = User.objects.filter(last_login__gte=last_7_days).count()
    except:
        pass
    
    # Son kullanıcılar (10 kişi)
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Güvenlik olayları
    security_events = []
    try:
        if SecurityEvent.objects.exists():
            security_events = SecurityEvent.objects.filter(
                created_at__gte=last_7_days
            ).order_by('-created_at')[:10]
    except:
        pass
    
    # Hesaplama aktiviteleri (eğer varsa)
    calculation_stats = {}
    try:
        from calculations.models import Calculation
        calculation_stats = {
            'total_calculations': Calculation.objects.count(),
            'recent_calculations': Calculation.objects.filter(
                created_at__gte=last_7_days
            ).count(),
        }
    except:
        pass
    
    context = {
        'title': 'Kullanıcı Yönetimi Dashboard',
        'user_stats': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'staff_users': staff_users,
            'superuser_count': superuser_count,
            'verified_users': 0,
            'unverified_users': 0,
            'recent_signups': recent_signups,
            'recent_active': recent_active,
        },
        'recent_users': recent_users,
        'security_events': security_events,
        'calculation_stats': calculation_stats,
    }
    
    return render(request, 'admin/accounts/dashboard.html', context)

# Admin kayıtları
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Diğer modelleri güvenli şekilde kaydet
try:
    class UserActivityAdmin(admin.ModelAdmin):
        list_display = ['user', 'activity_type', 'description', 'ip_address', 'created_at']
        list_filter = ['activity_type', 'created_at', 'user']
        search_fields = ['user__username', 'description', 'ip_address']
        readonly_fields = ['created_at']
        
        def get_actions(self, request):
            """Action'ları tamamen kaldır - action_checkbox hatasını önle"""
            return {}
        
        def has_add_permission(self, request):
            return False  # Sadece görüntüleme için
        
        def has_change_permission(self, request, obj=None):
            return False  # Sadece görüntüleme için
        
        def has_delete_permission(self, request, obj=None):
            return request.user.is_superuser  # Sadece superuser silebilir
    
    admin.site.register(UserActivity, UserActivityAdmin)
except:
    pass

try:
    admin.site.register(UserSession)
except:
    pass

# JWT Token Blacklist Admin (sektör standartlarında token yönetimi)
try:
    from django.contrib.admin import site
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
    from .admin_token_blacklist import OutstandingTokenAdmin, BlacklistedTokenAdmin
    
    # Eğer token_blacklist app'i kendi default admin'iyle register ettiyse önce kaldır
    if OutstandingToken in site._registry:
        site.unregister(OutstandingToken)
    if BlacklistedToken in site._registry:
        site.unregister(BlacklistedToken)
    
    site.register(OutstandingToken, OutstandingTokenAdmin)
    site.register(BlacklistedToken, BlacklistedTokenAdmin)
except Exception:
    pass

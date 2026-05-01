"""
JWT Token Blacklist Admin Integration

Sektör standartlarında token yönetimi:
- OutstandingToken: Aktif (henüz expire olmamış) token'ları görüntüle
- BlacklistedToken: Kullanıcı tarafından invalidate edilmiş token'ları görüntüle
"""

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class OutstandingTokenAdmin(admin.ModelAdmin):
    """Aktif JWT token'larını yönet"""
    
    list_display = [
        'user', 'jti', 'created_at', 'expires_at', 
        'is_expired_display', 'is_blacklisted_display'
    ]
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'jti']
    readonly_fields = ['jti', 'token', 'created_at', 'expires_at', 'user']
    
    def is_blacklisted_display(self, obj):
        """Token blacklist'te mi?"""
        try:
            if hasattr(obj, 'blacklistedtoken'):
                return format_html('<span style="color: #dc3545;">🚫 Blacklisted</span>')
        except:
            pass
        return format_html('<span style="color: #198754;">✅ Aktif</span>')
    is_blacklisted_display.short_description = "Durum"
    
    def is_expired_display(self, obj):
        """Token expire olmuş mu?"""
        from django.utils import timezone
        if obj.expires_at and obj.expires_at < timezone.now():
            return format_html('<span style="color: #6c757d;">⏰ Expired</span>')
        return format_html('<span style="color: #198754;">🟢 Valid</span>')
    is_expired_display.short_description = "Geçerlilik"
    
    def has_add_permission(self, request):
        return False  # Manuel token oluşturulamaz
    
    def has_change_permission(self, request, obj=None):
        return False  # Token'lar değiştirilemez
    
    def has_delete_permission(self, request, obj=None):
        return True  # Superuser token'ları silebilir (revoke)
    
    actions = ['blacklist_selected_tokens', 'delete_expired_tokens']
    
    def blacklist_selected_tokens(self, request, queryset):
        """Seçili token'ları blacklist'e ekle (manuel revoke)"""
        count = 0
        for token in queryset:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
                count += 1
            except Exception:
                pass
        messages.success(request, f"🚫 {count} token blacklist'e eklendi (revoke edildi).")
    blacklist_selected_tokens.short_description = "🚫 Seçili token'ları blacklist et (revoke)"
    
    def delete_expired_tokens(self, request, queryset):
        """Expire olmuş token'ları temizle"""
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        messages.success(request, f"🗑️ {count} expire olmuş token silindi.")
    delete_expired_tokens.short_description = "🗑️ Expire olmuş token'ları temizle"


class BlacklistedTokenAdmin(admin.ModelAdmin):
    """Blacklist'teki token'ları görüntüle"""
    
    list_display = ['token', 'blacklisted_at', 'user_info', 'token_jti']
    list_filter = ['blacklisted_at']
    search_fields = ['token__user__username', 'token__jti']
    readonly_fields = ['token', 'blacklisted_at']
    
    def user_info(self, obj):
        if obj.token and obj.token.user:
            return f"{obj.token.user.username} ({obj.token.user.email})"
        return "-"
    user_info.short_description = "Kullanıcı"
    
    def token_jti(self, obj):
        return obj.token.jti if obj.token else "-"
    token_jti.short_description = "JTI"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Admin'e kaydet
try:
    admin.site.register(OutstandingToken, OutstandingTokenAdmin)
    admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
except admin.sites.AlreadyRegistered:
    pass

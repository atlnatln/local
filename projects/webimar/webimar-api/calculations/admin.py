from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db import models
import json
from .models import CalculationHistory, MapInteraction, DailyCalculationLimit, CalculationLog
from .utils.html_sanitizer import sanitize_html_content

@admin.register(CalculationHistory)
class CalculationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'calculation_type', 'title', 'coordinates_summary', 'is_successful', 'ip_address', 'created_at')
    list_filter = ('calculation_type', 'is_successful', 'created_at')
    search_fields = ('user__username', 'title', 'description', 'ip_address')
    readonly_fields = ('created_at', 'updated_at', 'map_widget', 'formatted_parameters', 'formatted_result')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Genel Bilgiler', {'fields': ('user', 'calculation_type', 'title', 'description')}),
        ('Hesaplama Verileri', {
            'fields': ('formatted_parameters', 'formatted_result'),
            'classes': ('wide',)
        }),
        ('Harita Bilgileri', {
            'fields': ('map_coordinates', 'map_widget'),
            'classes': ('wide',)
        }),
        ('Sistem Bilgileri', {'fields': ('ip_address', 'is_successful', 'error_message')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )

    def get_actions(self, request):
        """Action'ları tamamen kaldır - action_checkbox hatasını önle"""
        return {}
    
    def coordinates_summary(self, obj):
        """Koordinatları özetleyen metod"""
        if obj.map_coordinates:
            coords = obj.map_coordinates
            lat = coords.get('lat') or coords.get('latitude')
            lng = coords.get('lng') or coords.get('longitude')
            if lat and lng:
                return f"📍 {lat:.4f}, {lng:.4f}"
        return "Koordinat yok"
    coordinates_summary.short_description = 'Harita Koordinatları'
    
    def map_widget(self, obj):
        """Koordinat varsa küçük bir harita widget'ı döndürür (readonly)"""
        if obj.map_coordinates:
            coords = obj.map_coordinates
            # Destek: {'lat': ..., 'lng': ...} veya {'latitude': ..., 'longitude': ...}
            lat = coords.get('lat') or coords.get('latitude')
            lng = coords.get('lng') or coords.get('longitude')
            if lat and lng:
                # Leaflet embed (OpenStreetMap) - Daha büyük harita
                iframe_html = format_html(
                    '''
                    <div style="width:100%;max-width:500px;height:300px;border:2px solid #007cba;border-radius:8px;overflow:hidden;">
                        <iframe width="100%" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                                src="https://www.openstreetmap.org/export/embed.html?bbox={}&layer=mapnik&marker={},{}" 
                                style="border:0;">
                        </iframe>
                        <div style="text-align:center; padding:5px; background:#f8f9fa; font-size:12px; color:#666;">
                            📍 Koordinat: {:.6f}, {:.6f}
                        </div>
                    </div>
                    ''',
                    f"{float(lng)-0.005},{float(lat)-0.005},{float(lng)+0.005},{float(lat)+0.005}",
                    lat, lng, lat, lng
                )
                return iframe_html
        return format_html("<span style='color:#888;'>Koordinat yok</span>")
    map_widget.short_description = 'Harita'
    
    def formatted_parameters(self, obj):
        """Parametreleri düzenli HTML formatında göster"""
        if not obj.parameters:
            return "Parametre yok"
        
        html = '<div style="background:#f8f9fa; padding:10px; border-radius:4px; border:1px solid #dee2e6;">'
        html += '<h4 style="margin:0 0 10px 0; color:#495057;">📊 Hesaplama Parametreleri</h4>'
        html += '<table style="width:100%; border-collapse:collapse;">'
        
        for key, value in obj.parameters.items():
            # Anahtar isimlerini Türkçe'ye çevir
            turkish_key = self.translate_key(key)
            html += f'<tr style="border-bottom:1px solid #dee2e6;">'
            html += f'<td style="padding:5px; font-weight:bold; width:40%;">{turkish_key}:</td>'
            html += f'<td style="padding:5px;">{value}</td>'
            html += '</tr>'
        
        html += '</table></div>'
        return mark_safe(html)
    formatted_parameters.short_description = 'Parametreler'

    def formatted_result(self, obj):
        """Sonuçları düzenli HTML formatında göster"""
        if not obj.result:
            return "Sonuç yok"
        
        html = '<div style="background:#e8f5e8; padding:10px; border-radius:4px; border:1px solid #c3e6c3;">'
        html += '<h4 style="margin:0 0 10px 0; color:#155724;">✅ Hesaplama Sonuçları</h4>'
        
        # Ana sonuç verilerini çıkar
        result_data = obj.result
        if isinstance(result_data, dict):
            if 'data' in result_data and isinstance(result_data['data'], dict):
                if 'results' in result_data['data']:
                    results = result_data['data']['results']
                elif 'data' in result_data['data']:
                    results = result_data['data']['data']
                else:
                    results = result_data['data']
            else:
                results = result_data
            
            # İzin durumu
            if 'izin_durumu' in results:
                status_color = '#28a745' if 'YAPILABİLİR' in results['izin_durumu'] else '#dc3545'
                html += f'<div style="background:{status_color}; color:white; padding:8px; border-radius:4px; margin-bottom:10px; text-align:center; font-weight:bold;">'
                html += f'{results["izin_durumu"]}'
                html += '</div>'
            
            # Sonuç tablosu
            html += '<table style="width:100%; border-collapse:collapse; margin-top:10px;">'
            
            key_translations = {
                'arazi_buyuklugu_m2': 'Arazi Büyüklüğü (m²)',
                'maksimum_yapi_alani_m2': 'Maksimum Yapı Alanı (m²)',
                'maksimum_kurutma_alani_m2': 'Maksimum Kurutma Alanı (m²)',
                'emsal_orani': 'Emsal Oranı',
                'maksimum_kumes_alani_m2': 'Maksimum Kümes Alanı (m²)',
                'maksimum_depo_alani_m2': 'Maksimum Depo Alanı (m²)',
                'maksimum_sera_alani_m2': 'Maksimum Sera Alanı (m²)',
                'success': 'Başarı Durumu',
                'message': 'Mesaj'
            }
            
            for key, value in results.items():
                if key in ['html_mesaj', 'success', 'message'] and key != 'success':
                    continue
                    
                turkish_key = key_translations.get(key, key.replace('_', ' ').title())
                
                if key == 'emsal_orani' and isinstance(value, float):
                    value = f"%{int(value * 100)}"
                elif key.endswith('_m2') and isinstance(value, (int, float)):
                    value = f"{value:,.0f} m²"
                elif isinstance(value, bool):
                    value = "✅ Evet" if value else "❌ Hayır"
                
                html += f'<tr style="border-bottom:1px solid #c3e6c3;">'
                html += f'<td style="padding:5px; font-weight:bold; width:40%;">{turkish_key}:</td>'
                html += f'<td style="padding:5px;">{value}</td>'
                html += '</tr>'
            
            html += '</table>'
            
            # HTML mesajı varsa göster (kısaltılmış)
            if 'html_mesaj' in results:
                html += '<details style="margin-top:10px;">'
                html += '<summary style="cursor:pointer; font-weight:bold;">📋 Detaylı Rapor Görüntüle</summary>'
                html += '<div style="margin-top:10px; max-height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px;">'
                # HTML mesajını güvenli şekilde sanitize et
                sanitized_html = sanitize_html_content(results['html_mesaj'])
                html += sanitized_html
                html += '</div></details>'
        
        html += '</div>'
        return mark_safe(html)
    formatted_result.short_description = 'Sonuç'

    def translate_key(self, key):
        """Anahtar isimlerini Türkçe'ye çevir"""
        translations = {
            'alan_m2': 'Alan (m²)',
            'arazi_vasfi': 'Arazi Vasfı',
            'emsal_turu': 'Emsal Türü',
            'hayvan_sayisi': 'Hayvan Sayısı',
            'yapi_turu': 'Yapı Türü',
            'kumes_turu': 'Kümes Türü',
            'depo_turu': 'Depo Türü',
            'sera_turu': 'Sera Türü',
            'coordinates': 'Koordinatlar',
            'lat': 'Enlem',
            'lng': 'Boylam',
            'latitude': 'Enlem',
            'longitude': 'Boylam'
        }
        return translations.get(key, key.replace('_', ' ').title())
    
    def has_add_permission(self, request):
        return False  # Sadece görüntüleme için
    
    def has_change_permission(self, request, obj=None):
        return False  # Sadece görüntüleme için
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Sadece superuser silebilir

@admin.register(MapInteraction)
class MapInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'coordinates_summary', 'zoom_level', 'ip_address', 'created_at')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__username', 'ip_address', 'session_id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Genel Bilgiler', {'fields': ('user', 'interaction_type', 'coordinates')}),
        ('Harita Bilgileri', {'fields': ('zoom_level', 'map_layer')}),
        ('Sistem Bilgileri', {'fields': ('ip_address', 'session_id')}),
        ('Zaman', {'fields': ('created_at',)}),
    )
    
    def get_actions(self, request):
        """Action'ları tamamen kaldır - action_checkbox hatasını önle"""
        return {}
    
    def coordinates_summary(self, obj):
        """Koordinatları özetleyen metod"""
        if obj.coordinates:
            coord_str = str(obj.coordinates)
            return coord_str[:50] + "..." if len(coord_str) > 50 else coord_str
        return "Koordinat yok"
    coordinates_summary.short_description = 'Koordinatlar'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Sadece superuser silebilir

@admin.register(DailyCalculationLimit)
class DailyCalculationLimitAdmin(admin.ModelAdmin):
    """Günlük hesaplama limitleri yönetimi"""
    list_display = ['user_info', 'user_type_display', 'calculation_count', 'get_current_limit_display', 'get_remaining_calculations_display', 'limit_status', 'date', 'updated_at']
    list_filter = ['date', 'limit_exceeded', ('user', admin.RelatedOnlyFieldListFilter)]
    search_fields = ['user__username', 'user__email', 'ip_address', 'device_fingerprint']
    readonly_fields = ['created_at', 'updated_at', 'limit_exceeded_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'ip_address', 'device_fingerprint')
        }),
        ('Limit Bilgileri', {
            'fields': ('calculation_count', 'limit_exceeded', 'limit_exceeded_at'),
        }),
        ('Tarihler', {
            'fields': ('date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['reset_user_daily_limits', 'extend_limits_for_selected_users']
    
    def get_actions(self, request):
        """Django'nun varsayılan 'delete' action'ını tamamen kaldır - güvenlik amacıyla"""
        actions = super().get_actions(request)
        # Tüm delete action'larını kaldır
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        """Delete izinlerini tamamen kaldır - sistem kritik"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Silme iznini kaldır - güvenlik nedeniyle"""
        return False
    
    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email
            )
        return format_html(
            '<em>Kayıtsız Kullanıcı</em><br><small>IP: {}</small>',
            obj.ip_address or 'Bilinmiyor'
        )
    user_info.short_description = 'Kullanıcı'
    
    def user_type_display(self, obj):
        if obj.user and obj.user.is_superuser:
            return format_html('<span style="color: #dc3545; font-weight: bold;">👑 Süper Admin</span>')
        elif obj.user and obj.user.is_active:
            return format_html('<span style="color: #28a745; font-weight: bold;">🏅 Kayıtlı</span>')
        return format_html('<span style="color: #6c757d;">👤 Kayıtsız</span>')
    user_type_display.short_description = 'Tip'
    
    def get_current_limit_display(self, obj):
        """Süper kullanıcılar için 'Limitsiz', diğerleri için sayısal limit göster"""
        if obj.user and obj.user.is_superuser:
            return format_html('<span style="color: #dc3545; font-weight: bold;">♾️ Limitsiz</span>')
        return format_html('<span style="color: #17a2b8; font-weight: bold;">{}</span>', int(obj.current_limit))
    get_current_limit_display.short_description = 'Günlük Limit'
    
    def get_remaining_calculations_display(self, obj):
        """Kalan hesaplama sayısını güvenli şekilde göster"""
        if obj.user and obj.user.is_superuser:
            return format_html('<span style="color: #dc3545; font-weight: bold;">♾️ Limitsiz</span>')
        
        remaining = obj.remaining_calculations
        if isinstance(remaining, str) and remaining == "Limitsiz":
            return format_html('<span style="color: #dc3545; font-weight: bold;">♾️ Limitsiz</span>')
        elif isinstance(remaining, int):
            if remaining <= 2:
                return format_html('<span style="color: #ffc107; font-weight: bold;">⚠️ {}</span>', remaining)
            else:
                return format_html('<span style="color: #28a745; font-weight: bold;">{}</span>', remaining)
        else:
            return format_html('<span style="color: #6c757d;">-</span>')
    get_remaining_calculations_display.short_description = 'Kalan Hesaplama'
    
    def limit_status(self, obj):
        # Süper kullanıcılar için özel durum
        if obj.user and obj.user.is_superuser:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">👑 Limitsiz Erişim</span>'
            )
        
        if obj.is_limit_reached:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🚫 Limit Doldu</span><br>'
                '<small>{}</small>',
                obj.limit_exceeded_at.strftime('%H:%M') if obj.limit_exceeded_at else 'Bilinmiyor'
            )
        
        remaining = obj.remaining_calculations
        # remaining_calculations property'si string veya int olabilir
        if isinstance(remaining, str) and remaining == "Limitsiz":
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">👑 Limitsiz Erişim</span>'
            )
        elif isinstance(remaining, int):
            if remaining <= 2:
                color = '#ffc107'
                icon = '⚠️'
            else:
                color = '#28a745'
                icon = '✅'
            
            return format_html(
                '<span style="color: {};">{} Limit Uygun</span>',
                color, icon
            )
        else:
            return format_html(
                '<span style="color: #28a745;">✅ Limit Uygun</span>'
            )
    limit_status.short_description = 'Durum'
    
    def reset_user_daily_limits(self, request, queryset):
        """Seçili kullanıcıların günlük limitlerini sıfırla"""
        count = 0
        for limit_obj in queryset:
            limit_obj.calculation_count = 0
            limit_obj.limit_exceeded = False
            limit_obj.limit_exceeded_at = None
            limit_obj.save()
            count += 1
        
        self.message_user(
            request,
            f"✅ {count} kullanıcının günlük limiti sıfırlandı."
        )
    reset_user_daily_limits.short_description = "🔄 Seçili kullanıcıların limitlerini sıfırla"
    
    def extend_limits_for_selected_users(self, request, queryset):
        """Seçili kullanıcılar için bugün limitleri genişlet"""
        count = 0
        for limit_obj in queryset:
            # Limiti 5 artır
            limit_obj.calculation_count = max(0, limit_obj.calculation_count - 5)
            limit_obj.limit_exceeded = False
            limit_obj.limit_exceeded_at = None
            limit_obj.save()
            count += 1
        
        self.message_user(
            request,
            f"🎁 {count} kullanıcı için +5 ekstra hesaplama hakkı tanındı."
        )
    extend_limits_for_selected_users.short_description = "🎁 Seçili kullanıcılara +5 Extra hak ver"
    
    def get_queryset(self, request):
        """Son 7 günün verilerini göster"""
        queryset = super().get_queryset(request)
        seven_days_ago = timezone.now().date() - timezone.timedelta(days=7)
        return queryset.filter(date__gte=seven_days_ago)

@admin.register(CalculationLog)
class CalculationLogAdmin(admin.ModelAdmin):
    """Hesaplama logları yönetimi"""
    list_display = ['log_info', 'user_info', 'calculation_type', 'status_display', 'limit_info', 'created_at']
    list_filter = ['log_type', 'is_successful', 'limit_exceeded', 'calculation_type', 'created_at']
    search_fields = ['user__username', 'ip_address', 'calculation_type', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('log_type', 'user', 'ip_address', 'calculation_type')
        }),
        ('İşlem Detayları', {
            'fields': ('is_successful', 'error_message', 'limit_exceeded', 'current_count', 'current_limit'),
        }),
        ('Veri', {
            'fields': ('calculation_data', 'result_data', 'location_data'),
            'classes': ('collapse',)
        }),
        ('Sistem', {
            'fields': ('user_agent', 'device_fingerprint', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['export_logs_csv', 'clear_old_logs']
    
    def log_info(self, obj):
        """Log tipini renkli göster"""
        colors = {
            'calculation': '#28a745',
            'limit_exceeded': '#dc3545',
            'error': '#dc3545',
            'security': '#ffc107',
            'limit_check': '#17a2b8'
        }
        icons = {
            'calculation': '🧮',
            'limit_exceeded': '🚫',
            'error': '❌',
            'security': '🔐',
            'limit_check': '✅'
        }
        
        color = colors.get(obj.log_type, '#6c757d')
        icon = icons.get(obj.log_type, '📝')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_log_type_display()
        )
    log_info.short_description = 'Log Tipi'
    
    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.ip_address
            )
        return format_html(
            '<em>Anonim</em><br><small>{}</small>',
            obj.ip_address
        )
    user_info.short_description = 'Kullanıcı'
    
    def status_display(self, obj):
        if obj.is_successful:
            return format_html('<span style="color: #28a745;">✅ Başarılı</span>')
        return format_html(
            '<span style="color: #dc3545;">❌ Hata</span><br>'
            '<small title="{}">{}</small>',
            obj.error_message or '',
            (obj.error_message or '')[:30] + '...' if len(obj.error_message or '') > 30 else obj.error_message or ''
        )
    status_display.short_description = 'Durum'
    
    def limit_info(self, obj):
        if obj.current_count is not None and obj.current_limit is not None:
            if obj.limit_exceeded:
                return format_html(
                    '<span style="color: #dc3545; font-weight: bold;">{}/{} 🚫</span>',
                    obj.current_count, obj.current_limit
                )
            else:
                return format_html(
                    '<span style="color: #28a745;">{}/{}</span>',
                    obj.current_count, obj.current_limit
                )
        return '-'
    limit_info.short_description = 'Limit'
    
    def export_logs_csv(self, request, queryset):
        """Logları CSV olarak export et"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="calculation_logs_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Zaman', 'Log Tipi', 'Kullanıcı', 'IP', 'Hesaplama Tipi', 
            'Başarılı', 'Limit Aşımı', 'Sayı', 'Limit', 'Hata'
        ])
        
        for log in queryset:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.get_log_type_display(),
                log.user.username if log.user else 'Anonim',
                log.ip_address,
                log.calculation_type,
                'Evet' if log.is_successful else 'Hayır',
                'Evet' if log.limit_exceeded else 'Hayır',
                log.current_count or '',
                log.current_limit or '',
                log.error_message or ''
            ])
        
        return response
    export_logs_csv.short_description = "📊 CSV Export Et"
    
    def clear_old_logs(self, request, queryset):
        """30 günden eski logları temizle"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        old_logs_count = CalculationLog.objects.filter(created_at__lt=thirty_days_ago).count()
        CalculationLog.objects.filter(created_at__lt=thirty_days_ago).delete()
        
        self.message_user(
            request,
            f"🧹 {old_logs_count} adet 30 günden eski log temizlendi."
        )
    clear_old_logs.short_description = "🧹 Eski logları temizle (30+ gün)"
    
    def get_queryset(self, request):
        """Son 7 günün loglarını göster (performans için)"""
        queryset = super().get_queryset(request)
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        return queryset.filter(created_at__gte=seven_days_ago)

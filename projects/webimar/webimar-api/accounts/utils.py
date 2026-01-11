from django.utils import timezone
from .models import UserActivity, UserSession
from calculations.models import CalculationHistory, MapInteraction

def log_user_activity(user, activity_type, description, request, **kwargs):
    """
    Kullanıcı aktivitesini kaydet
    """
    if not user or not user.is_authenticated:
        return None
    
    # IP adresini al
    ip_address = get_client_ip(request)
    
    # User agent bilgisini al
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Aktiviteyi kaydet
    activity = UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        location_data=kwargs.get('location_data'),
        calculation_data=kwargs.get('calculation_data'),
        result_data=kwargs.get('result_data'),
    )
    
    return activity

def log_calculation(user, calculation_type, title, parameters, result, request, map_coordinates=None):
    """
    Hesaplama aktivitesini kaydet
    """
    if not user or not user.is_authenticated:
        return None
    
    # IP adresini al
    ip_address = get_client_ip(request)
    
    # Hesaplamayı kaydet
    calculation = CalculationHistory.objects.create(
        user=user,
        calculation_type=calculation_type,
        title=title,
        parameters=parameters,
        result=result,
        map_coordinates=map_coordinates,
        ip_address=ip_address,
        is_successful=True if result else False,
    )
    
    # Aktivite olarak da kaydet
    log_user_activity(
        user=user,
        activity_type='calculation',
        description=f'{calculation_type} hesaplama yaptı: {title}',
        request=request,
        calculation_data=parameters,
        result_data=result,
        location_data=map_coordinates
    )
    
    return calculation

def log_map_interaction(user, interaction_type, coordinates, request, **kwargs):
    """
    Harita etkileşimini kaydet
    """
    if not user or not user.is_authenticated:
        return None
    
    # IP adresini al
    ip_address = get_client_ip(request)
    
    # Session ID'yi al
    session_id = request.session.session_key
    
    # Etkileşimi kaydet
    interaction = MapInteraction.objects.create(
        user=user,
        interaction_type=interaction_type,
        coordinates=coordinates,
        zoom_level=kwargs.get('zoom_level'),
        map_layer=kwargs.get('map_layer'),
        ip_address=ip_address,
        session_id=session_id,
    )
    
    # Aktivite olarak da kaydet
    log_user_activity(
        user=user,
        activity_type='map_point',
        description=f'{interaction_type} - Harita etkileşimi',
        request=request,
        location_data=coordinates
    )
    
    return interaction

def get_client_ip(request):
    """
    Kullanıcının IP adresini al
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def update_user_session(user, request):
    """
    Kullanıcı oturumunu güncelle veya oluştur
    """
    if not user or not user.is_authenticated:
        return None
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Mevcut oturumu bul veya yeni oluştur
    session, created = UserSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_info': parse_user_agent(user_agent),
            'location': get_location_from_ip(ip_address),
            'is_active': True,
        }
    )
    
    # Oturumu güncelle
    if not created:
        session.last_activity = timezone.now()
        session.save()
    
    return session

def cleanup_expired_sessions():
    """
    Süresi dolmuş oturumları temizle
    JWT token süresi tipik olarak 24 saat, bu fonksiyon günlük çalıştırılabilir
    """
    from datetime import timedelta
    
    # 24 saatten eski ve hala aktif olan oturumları pasifleştir
    expired_time = timezone.now() - timedelta(hours=24)
    
    expired_sessions = UserSession.objects.filter(
        is_active=True,
        last_activity__lt=expired_time
    )
    
    count = expired_sessions.count()
    expired_sessions.update(is_active=False)
    
    return count

def deactivate_user_sessions_on_logout(user, session_key=None):
    """
    Kullanıcı logout yaptığında belirli session'ı veya tüm aktif session'ları pasifleştir
    """
    if session_key:
        # Belirli session'ı pasifleştir
        try:
            session = UserSession.objects.get(
                session_key=session_key,
                user=user,
                is_active=True
            )
            session.is_active = False
            session.save()
            return 1
        except UserSession.DoesNotExist:
            return 0
    else:
        # Kullanıcının tüm aktif session'larını pasifleştir
        active_sessions = UserSession.objects.filter(
            user=user,
            is_active=True
        )
        count = active_sessions.count()
        active_sessions.update(is_active=False)
        return count

def parse_user_agent(user_agent):
    """
    User agent'tan cihaz bilgisini çıkar
    """
    if not user_agent:
        return "Bilinmeyen Cihaz"
    
    user_agent_lower = user_agent.lower()
    
    # Tarayıcı tespiti
    if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
        browser = 'Chrome'
    elif 'firefox' in user_agent_lower:
        browser = 'Firefox'
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        browser = 'Safari'
    elif 'edg' in user_agent_lower:
        browser = 'Edge'
    else:
        browser = 'Diğer'
    
    # İşletim sistemi tespiti
    if 'windows' in user_agent_lower:
        os = 'Windows'
    elif 'mac' in user_agent_lower:
        os = 'macOS'
    elif 'linux' in user_agent_lower:
        os = 'Linux'
    elif 'android' in user_agent_lower:
        os = 'Android'
    elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
        os = 'iOS'
    else:
        os = 'Diğer'
    
    return f"{browser} on {os}"

def get_location_from_ip(ip_address):
    """
    IP adresinden konum bilgisini al (basit versiyon)
    """
    # Gerçek uygulamada GeoIP2 veya başka bir servis kullanılabilir
    if ip_address and ip_address != '127.0.0.1':
        return "Türkiye"  # Varsayılan olarak Türkiye
    return "Yerel"

def log_security_event(event_type, ip_address, description, request, **kwargs):
    """
    Güvenlik olayını kaydet
    """
    from .models import SecurityEvent
    
    # User agent bilgisini al
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
    
    # Önem derecesini belirle
    severity_map = {
        'failed_register': 'medium',
        'failed_login': 'medium', 
        'rate_limit_exceeded': 'high',
        'multiple_failed_attempts': 'high',
        'suspicious_activity': 'critical',
    }
    
    severity = severity_map.get(event_type, 'medium')
    
    # Güvenlik olayını kaydet
    security_event = SecurityEvent.objects.create(
        event_type=event_type,
        severity=severity,
        ip_address=ip_address,
        user_agent=user_agent,
        user=kwargs.get('user'),
        username_attempted=kwargs.get('username_attempted'),
        email_attempted=kwargs.get('email_attempted'),
        description=description,
        metadata=kwargs.get('metadata', {}),
    )
    
    return security_event

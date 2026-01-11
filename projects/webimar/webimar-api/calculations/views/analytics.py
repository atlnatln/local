"""
Analytics tracking endpoints
Tüm ziyaretçiler için sayfa görüntüleme ve etkileşim tracking
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from calculations.models import PageView, UserInteraction
from calculations.middleware import get_client_ip, get_device_fingerprint

logger = logging.getLogger('analytics')


@api_view(['POST'])
def track_page_view(request):
    """Sayfa görüntüleme kaydı - tüm ziyaretçiler için"""
    try:
        data = request.data
        
        # Session ID - frontend'den gelmezse oluştur
        session_id = data.get('session_id') or request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # IP ve fingerprint
        ip_address = get_client_ip(request)
        device_fingerprint = get_device_fingerprint(request)
        
        # Kullanıcı bilgisi
        user = request.user if request.user.is_authenticated else None
        
        # PageView kaydı oluştur
        page_view = PageView.objects.create(
            user=user,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_fingerprint=device_fingerprint,
            path=data.get('path', ''),
            full_url=data.get('full_url', ''),
            page_title=data.get('page_title', ''),
            referrer=data.get('referrer', ''),
            platform=data.get('platform', ''),
            browser=data.get('browser', ''),
            os=data.get('os', ''),
            load_time=data.get('load_time'),
            time_on_page=data.get('time_on_page'),
            country=data.get('country', ''),
            city=data.get('city', ''),
        )
        
        logger.info(f"📊 Page view tracked: {page_view.path} - Session: {session_id[:8]}...")
        
        return Response({
            'success': True,
            'message': 'Page view tracked',
            'session_id': session_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to track page view: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def track_interaction(request):
    """Kullanıcı etkileşimi kaydı - tıklama, form submit vb."""
    try:
        data = request.data
        
        # Session ID
        session_id = data.get('session_id') or request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # IP
        ip_address = get_client_ip(request)
        
        # Kullanıcı bilgisi
        user = request.user if request.user.is_authenticated else None
        
        # UserInteraction kaydı oluştur
        interaction = UserInteraction.objects.create(
            user=user,
            session_id=session_id,
            ip_address=ip_address,
            interaction_type=data.get('interaction_type', 'other'),
            element_id=data.get('element_id', ''),
            element_class=data.get('element_class', ''),
            element_text=data.get('element_text', ''),
            page_path=data.get('page_path', ''),
            page_title=data.get('page_title', ''),
            metadata=data.get('metadata', {}),
        )
        
        logger.info(f"🎯 Interaction tracked: {interaction.interaction_type} on {interaction.page_path}")
        
        return Response({
            'success': True,
            'message': 'Interaction tracked',
            'session_id': session_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to track interaction: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def track_time_on_page(request):
    """Sayfada geçirilen süre güncelleme"""
    try:
        data = request.data
        session_id = data.get('session_id') or request.session.session_key
        path = data.get('path')
        time_on_page = data.get('time_on_page')
        
        if not session_id or not path or time_on_page is None:
            return Response({
                'success': False,
                'error': 'session_id, path, and time_on_page are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Son page view'i bul ve güncelle
        page_view = PageView.objects.filter(
            session_id=session_id,
            path=path
        ).order_by('-created_at').first()
        
        if page_view:
            page_view.time_on_page = time_on_page
            page_view.save(update_fields=['time_on_page'])
            logger.info(f"⏱️ Time on page updated: {path} - {time_on_page}s")
        
        return Response({
            'success': True,
            'message': 'Time on page updated'
        })
        
    except Exception as e:
        logger.error(f"Failed to update time on page: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

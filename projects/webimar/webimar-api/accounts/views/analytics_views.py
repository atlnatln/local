import re
from typing import Any

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from accounts.models import AnalyticsEvent


_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _get_client_ip(request) -> str | None:
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        # XFF: client, proxy1, proxy2
        return xff.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR')


@api_view(['POST'])
@permission_classes([AllowAny])
def analytics_event(request):
    """Frontend'den gelen davranış eventlerini kaydeder.

    Beklenen alanlar:
      - session_id (zorunlu)
      - event_type: page_view | page_leave | calculation (zorunlu)
      - path (zorunlu)
      - referrer (opsiyonel)
      - page_id (opsiyonel)
      - duration_ms (opsiyonel, page_leave için)
      - calculation_type (opsiyonel, calculation için)
      - metadata (opsiyonel)
    """

    data: dict[str, Any] = request.data if isinstance(request.data, dict) else {}

    session_id = (data.get('session_id') or '').strip()
    event_type = (data.get('event_type') or '').strip()
    path = (data.get('path') or '').strip()

    if not session_id or not _SESSION_ID_RE.match(session_id):
        return Response(
            {'uygun': False, 'mesaj': 'Geçersiz session_id', 'detaylar': {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    allowed_types = {'page_view', 'page_leave', 'calculation'}
    if event_type not in allowed_types:
        return Response(
            {'uygun': False, 'mesaj': 'Geçersiz event_type', 'detaylar': {'allowed': sorted(allowed_types)}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not path:
        return Response(
            {'uygun': False, 'mesaj': 'path zorunlu', 'detaylar': {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    duration_ms = data.get('duration_ms')
    if duration_ms is not None:
        try:
            duration_ms = int(duration_ms)
        except Exception:
            return Response(
                {'uygun': False, 'mesaj': 'duration_ms sayı olmalı', 'detaylar': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 0..24saat arası makul limit
        if duration_ms < 0 or duration_ms > 86_400_000:
            return Response(
                {'uygun': False, 'mesaj': 'duration_ms aralığı geçersiz', 'detaylar': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    metadata = data.get('metadata')
    if metadata is not None and not isinstance(metadata, (dict, list, str, int, float, bool)):
        metadata = {'value': str(metadata)}

    referrer_raw = (data.get('referrer') or '').strip()
    referrer = referrer_raw[:512] if referrer_raw else None

    try:
        event = AnalyticsEvent.objects.create(
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            session_id=session_id,
            page_id=(data.get('page_id') or None),
            event_type=event_type,
            path=path[:512],
            referrer=referrer,
            duration_ms=duration_ms,
            calculation_type=(data.get('calculation_type') or None),
            metadata=metadata,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
    except Exception as e:
        # DB constraint hatalarını yakala (varchar overflow, foreign key vb.)
        return Response(
            {'uygun': False, 'mesaj': 'Veri kaydedilemedi', 'detaylar': {'error': str(e)[:200]}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {'uygun': True, 'mesaj': 'Kaydedildi', 'detaylar': {'id': event.id}},
        status=status.HTTP_201_CREATED,
    )

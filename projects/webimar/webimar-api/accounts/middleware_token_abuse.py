"""Token abuse detection middleware.

Tracks per-user API request rates and logs security events when thresholds
are exceeded. This is a passive detector — throttling is handled by DRF.
"""

import time
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Thresholds
RATE_LIMIT_PER_MINUTE = 30      # Same as MeEndpointRateThrottle
ALERT_THRESHOLD_PER_MINUTE = 60  # Double the throttle — active investigation
ALERT_THRESHOLD_PER_HOUR = 500   # Hourly flood indicator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TokenAbuseDetectionMiddleware:
    """Passive token abuse detection — logs but does not block."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._check_for_abuse(request, response)
        return response

    def _check_for_abuse(self, request, response):
        if not request.path.startswith('/api/'):
            return
        if not (request.user and request.user.is_authenticated):
            return
        if request.user.is_superuser:
            return

        user_id = request.user.pk
        ip = get_client_ip(request)
        path = request.path
        now = time.time()

        # Per-user per-minute counter
        minute_key = f"token_abuse_min:{user_id}"
        minute_data = cache.get(minute_key, {"count": 0, "start": now, "paths": []})
        
        if now - minute_data["start"] > 60:
            minute_data = {"count": 0, "start": now, "paths": []}
        
        minute_data["count"] += 1
        minute_data["paths"].append(path)
        cache.set(minute_key, minute_data, timeout=120)

        # Per-user per-hour counter
        hour_key = f"token_abuse_hour:{user_id}"
        hour_data = cache.get(hour_key, {"count": 0, "start": now, "ips": set()})
        
        if now - hour_data["start"] > 3600:
            hour_data = {"count": 0, "start": now, "ips": set()}
        
        hour_data["count"] += 1
        hour_data["ips"].add(ip)
        cache.set(hour_key, hour_data, timeout=3700)

        # Alert if thresholds exceeded (only once per window to avoid spam)
        alert_key = f"token_abuse_alert:{user_id}"
        already_alerted = cache.get(alert_key, False)

        if not already_alerted:
            is_abuse = False
            abuse_reason = ""

            if minute_data["count"] >= ALERT_THRESHOLD_PER_MINUTE:
                is_abuse = True
                abuse_reason = (
                    f"User {user_id} made {minute_data['count']} API requests in 60s "
                    f"from IP {ip} — possible compromised token or automation"
                )
            elif hour_data["count"] >= ALERT_THRESHOLD_PER_HOUR:
                is_abuse = True
                abuse_reason = (
                    f"User {user_id} made {hour_data['count']} API requests in 1h "
                    f"from IPs {hour_data['ips']} — possible token abuse or enumeration"
                )

            if is_abuse:
                cache.set(alert_key, True, timeout=3600)  # Alert once per hour
                self._log_security_event(user_id, ip, path, abuse_reason, minute_data, hour_data)

    def _log_security_event(self, user_id, ip, path, reason, minute_data, hour_data):
        try:
            from accounts.models import SecurityEvent
            from accounts.utils import log_security_event

            log_security_event(
                event_type="token_abuse",
                severity="critical",
                ip_address=ip,
                user_id=user_id,
                description=reason,
                metadata={
                    "path": path,
                    "requests_per_minute": minute_data["count"],
                    "requests_per_hour": hour_data["count"],
                    "unique_ips_in_hour": list(hour_data["ips"]),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log token abuse security event: {e}")

        # Also log to Django logger for immediate visibility
        logger.critical(f"TOKEN_ABUSE: {reason}")

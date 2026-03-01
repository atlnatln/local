"""
HttpOnly cookie-based JWT authentication for Anka Platform.

This module provides:
- CookieJWTAuthentication: reads JWT from HttpOnly cookies (fallback: Authorization header)
- set_jwt_cookies(): sets HttpOnly/Secure/SameSite cookies on a response
- clear_jwt_cookies(): clears JWT cookies on logout

Security rationale (ADR-0007):
  Storing JWT in HttpOnly cookies prevents XSS from stealing tokens.
  SameSite=Lax + Secure flags mitigate CSRF for state-changing requests.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

# Cookie names
ACCESS_COOKIE = "anka_access_token"
REFRESH_COOKIE = "anka_refresh_token"

# Durations (seconds)
ACCESS_MAX_AGE = 15 * 60        # 15 minutes  — matches SIMPLE_JWT ACCESS_TOKEN_LIFETIME
REFRESH_MAX_AGE = 7 * 24 * 3600  # 7 days      — matches SIMPLE_JWT REFRESH_TOKEN_LIFETIME


def _is_secure() -> bool:
    """Return True when the app is running behind HTTPS (production)."""
    return not getattr(settings, "DEBUG", True)


def set_jwt_cookies(response: Response, access: str, refresh: str) -> Response:
    """Attach HttpOnly JWT cookies to *response*."""
    secure = _is_secure()
    samesite = "Lax"

    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access,
        max_age=ACCESS_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh,
        max_age=REFRESH_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/api/auth/",  # covers both /api/auth/refresh/ and /api/auth/logout/
    )
    return response


def clear_jwt_cookies(response: Response) -> Response:
    """Delete JWT cookies from the client."""
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth/")
    return response


# ---------------------------------------------------------------------------
# OpenAPI / drf-spectacular authentication extension
# Tells spectacular how to document CookieJWTAuthentication in the schema.
# ---------------------------------------------------------------------------
try:
    from drf_spectacular.extensions import OpenApiAuthenticationExtension

    class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
        target_class = 'apps.accounts.cookie_auth.CookieJWTAuthentication'
        name = 'ankaJWTAuth'  # Unique name — 'cookieAuth' is reserved by SessionAuthentication

        def get_security_definition(self, auto_schema):
            return {
                'type': 'apiKey',
                'in': 'cookie',
                'name': 'anka_access_token',
                'description': 'HttpOnly cookie tabanlı JWT kimlik doğrulaması (anka_access_token)',
            }
except ImportError:
    pass  # drf_spectacular kurulu değil, API şeması üretilmeyecek


class CookieJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT's JWTAuthentication to also look for the access token in
    an HttpOnly cookie.

    Priority:
      1. Authorization: Bearer <token>  (standard header — useful for Swagger/API clients)
      2. ``anka_access_token`` cookie   (browser sessions)
    """

    def authenticate(self, request: Request) -> Optional[Tuple]:
        # 1. Try standard header first (e.g. Swagger, curl, mobile apps)
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result

        # 2. Fallback: read from cookie
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

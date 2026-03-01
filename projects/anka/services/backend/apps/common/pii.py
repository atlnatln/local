"""
PII (Personally Identifiable Information) masking utilities.

KVKK/GDPR uyumlu loglama için kişisel verileri maskeleme fonksiyonları.
Güvenlik politikası: docs/SECURITY/kvkk-data-compliance.md
"""

import hashlib


def mask_email(email: str) -> str:
    """Email adresini KVKK uyumlu şekilde maskeler.

    Örnekler:
        >>> mask_email("john.doe@example.com")
        'j***@example.com'
        >>> mask_email("a@b.com")
        'a***@b.com'
        >>> mask_email("")
        '***'
    """
    if not email or '@' not in email:
        return '***'
    local, domain = email.split('@', 1)
    return f"{local[0]}***@{domain}"


def hash_pii(value: str) -> str:
    """PII için tek yönlü kısa hash (log correlation amaçlı).

    Örnekler:
        >>> len(hash_pii("test@example.com"))
        12
    """
    if not value:
        return '***'
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def mask_username(username: str) -> str:
    """Kullanıcı adını maskeler.

    Örnekler:
        >>> mask_username("john.doe")
        'jo***'
        >>> mask_username("a")
        'a***'
    """
    if not username:
        return '***'
    visible = min(2, len(username))
    return f"{username[:visible]}***"

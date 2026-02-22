"""
Centralized alarm / alerting utilities for Anka Platform.

Usage:
    from apps.common.alerts import emit_alarm

    emit_alarm(
        code="EXPORT_FAILED",
        message="Export generation failed after max retries",
        metadata={"export_id": "...", "error": "..."},
        level="ERROR",
    )

This module:
- Always writes a structured JSON log entry (captured by Docker json-file driver / log aggregators).
- Optionally sends an email to Django ADMINS when ANKA_ALARM_EMAIL_ENABLED=True and ADMINS is set.
- Never raises exceptions itself — alerting must never crash the caller.
"""

import json
import logging
import os
import traceback
from datetime import datetime, timezone

from django.conf import settings

logger = logging.getLogger("anka.alarms")


# ─── Public API ───────────────────────────────────────────────────────────────

def emit_alarm(
    code: str,
    message: str,
    metadata: dict | None = None,
    level: str = "ERROR",
    exc: BaseException | None = None,
) -> None:
    """
    Emit a platform alarm.

    Args:
        code:     Short uppercase alarm code. e.g. "EXPORT_FAILED", "BATCH_FAILED".
        message:  Human-readable description.
        metadata: Optional dict with additional context (batch_id, export_id, etc.).
        level:    Python logging level string. "WARNING" | "ERROR" | "CRITICAL".
        exc:      Optional exception instance — traceback is captured automatically.
    """
    try:
        _emit(code=code, message=message, metadata=metadata or {}, level=level, exc=exc)
    except Exception:  # noqa: BLE001
        # Swallow — alarms must never crash the caller
        logger.exception("emit_alarm internal error (level=%s code=%s)", level, code)


# ─── Internal implementation ──────────────────────────────────────────────────

def _emit(code: str, message: str, metadata: dict, level: str, exc: BaseException | None) -> None:
    payload = {
        "alarm": True,
        "code": code,
        "message": message,
        "level": level.upper(),
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "metadata": metadata,
    }
    if exc is not None:
        payload["exception"] = {
            "type": type(exc).__name__,
            "value": str(exc),
            "traceback": traceback.format_exc(),
        }

    log_level = getattr(logging, level.upper(), logging.ERROR)
    logger.log(log_level, json.dumps(payload, ensure_ascii=False, default=str))

    _maybe_send_email(code=code, message=message, metadata=metadata, payload=payload, level=level)


def _maybe_send_email(code: str, message: str, metadata: dict, payload: dict, level: str) -> None:
    """Send email to ADMINS if ANKA_ALARM_EMAIL_ENABLED=True and ADMINS is configured."""
    enabled = os.environ.get("ANKA_ALARM_EMAIL_ENABLED", "False").strip().lower() == "true"
    if not enabled:
        return

    admins = getattr(settings, "ADMINS", [])
    if not admins:
        return

    try:
        from django.core.mail import mail_admins  # noqa: PLC0415

        subject = f"[ANKA ALARM] {level.upper()} — {code}"
        body_lines = [
            f"Alarm Code : {code}",
            f"Level      : {level.upper()}",
            f"Message    : {message}",
            "",
            "Metadata:",
            json.dumps(metadata, indent=2, ensure_ascii=False, default=str),
            "",
            "Full payload:",
            json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        ]
        mail_admins(
            subject=subject,
            message="\n".join(body_lines),
            fail_silently=True,
        )
    except Exception:  # noqa: BLE001
        logger.exception("emit_alarm email send failed (code=%s)", code)

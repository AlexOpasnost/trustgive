"""Production settings — for Railway deployment."""
from __future__ import annotations

import logging
import re
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *  # noqa: F401,F403
from .base import (
    APP_VERSION,
    RAILWAY_DEPLOYMENT_ID,
    SENTRY_DSN,
    SENTRY_ENVIRONMENT,
    SENTRY_TRACES_SAMPLE_RATE,
)

DEBUG = False

# --- Security hardening ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# --- Sentry init (per ADR-008) ---
_SENSITIVE_FIELD_RE = re.compile(r"key|secret|token|password|authorization|cookie", re.IGNORECASE)


def _scrub_sensitive_fields(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    """Strip sensitive headers/fields from Sentry events before sending."""
    request = event.get("request") or {}
    headers = request.get("headers") or {}
    for key in list(headers.keys()):
        if _SENSITIVE_FIELD_RE.search(key):
            headers[key] = "[Filtered]"
    if "data" in request and isinstance(request["data"], dict):
        for key in list(request["data"].keys()):
            if _SENSITIVE_FIELD_RE.search(key):
                request["data"][key] = "[Filtered]"
    return event


if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT or "production",
        release=RAILWAY_DEPLOYMENT_ID,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
        before_send=_scrub_sensitive_fields,
    )

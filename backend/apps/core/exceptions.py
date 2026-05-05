"""Custom DRF exception handler emitting the API_SPEC §5 error envelope."""
from __future__ import annotations

import logging
from typing import Any

import sentry_sdk
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler

from apps.core.middleware import get_request_id

logger = logging.getLogger(__name__)


_CODE_MAP = {
    ValidationError: "VALIDATION_ERROR",
    NotFound: "NOT_FOUND",
    PermissionDenied: "PERMISSION_DENIED",
    Throttled: "RATE_LIMITED",
}


def _code_for(exc: Exception) -> str:
    for klass, code in _CODE_MAP.items():
        if isinstance(exc, klass):
            return code
    if isinstance(exc, APIException):
        return getattr(exc, "default_code", "API_ERROR").upper()
    return "INTERNAL_ERROR"


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Emit uniform error envelope: {error: {code, message, details, request_id}}."""
    response = drf_default_exception_handler(exc, context)
    code = _code_for(exc)
    request_id = get_request_id()

    if response is None:
        # Unhandled — capture in Sentry, return 500 envelope
        sentry_id = sentry_sdk.capture_exception(exc)
        logger.exception("Unhandled exception", extra={"sentry_id": sentry_id})
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "details": {"sentry_id": sentry_id} if sentry_id else None,
                    "request_id": request_id,
                }
            },
            status=500,
        )

    # Build envelope from DRF default response
    detail = response.data
    message = "Request failed"
    details: dict[str, Any] | None = None

    if isinstance(detail, dict) and "detail" in detail:
        message = str(detail["detail"])
    elif isinstance(detail, dict):
        message = "Request validation failed"
        details = {k: v for k, v in detail.items() if k != "detail"}
    elif isinstance(detail, list) and detail:
        message = str(detail[0])

    if isinstance(exc, Throttled):
        # Per KB-010: exc.wait can be None
        wait_seconds = int(exc.wait or 0)
        details = {"retry_after_seconds": wait_seconds}
        message = f"Too many requests. Retry after {wait_seconds}s."
        response["Retry-After"] = str(wait_seconds)

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id,
        }
    }
    return response

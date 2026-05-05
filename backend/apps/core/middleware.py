"""Request-ID and Cache-Control middleware (per ADR-007 + ADR-008)."""
from __future__ import annotations

import contextvars
import logging
import time
import uuid
from typing import Any, Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
_charity_slug_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("charity_slug", default="")


def get_request_id() -> str:
    """Return current request_id; '' when outside request scope (per KB-007)."""
    return _request_id_ctx.get()


def set_charity_slug(slug: str) -> None:
    _charity_slug_ctx.set(slug)


class RequestIDMiddleware(MiddlewareMixin):
    """Generate UUID4 per request, attach to context + response header X-Request-ID."""

    def process_request(self, request: HttpRequest) -> None:
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.request_id = rid  # type: ignore[attr-defined]
        request._start_time = time.monotonic()  # type: ignore[attr-defined]
        _request_id_ctx.set(rid)
        _charity_slug_ctx.set("")

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        rid = getattr(request, "request_id", "") or ""
        if rid:
            response["X-Request-ID"] = rid

        start = getattr(request, "_start_time", None)
        if start is not None:
            duration_ms = int((time.monotonic() - start) * 1000)
            logging.getLogger("trustgive.access").info(
                "request_completed",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
        return response


class CacheControlMiddleware(MiddlewareMixin):
    """Apply Cache-Control headers per URL name (per KB-009).

    Uses settings.CACHE_CONTROL_MAP keyed on `request.resolver_match.url_name`.
    """

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        match = getattr(request, "resolver_match", None)
        if match is None:
            return response

        cache_map = getattr(settings, "CACHE_CONTROL_MAP", {})
        directive = cache_map.get(match.url_name)
        if directive and "Cache-Control" not in response:
            response["Cache-Control"] = directive
            response["Vary"] = "Accept-Encoding, Accept-Language"
        return response


class RequestIDLogFilter(logging.Filter):
    """Inject request_id + charity_slug into every log record (for python-json-logger)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = _request_id_ctx.get() or ""
        if not hasattr(record, "charity_slug"):
            record.charity_slug = _charity_slug_ctx.get() or ""
        for attr in ("path", "method", "status_code", "duration_ms"):
            if not hasattr(record, attr):
                setattr(record, attr, "")
        return True

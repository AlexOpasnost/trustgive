"""Health endpoint per ADR-008 + API_SPEC endpoint #1."""
from __future__ import annotations

import logging

import sentry_sdk
from django.conf import settings
from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def _check_db() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:
        logger.exception("Health check: DB ping failed")
        return False


def _check_sentry() -> str:
    if not settings.SENTRY_DSN:
        return "disabled"
    client = sentry_sdk.Hub.current.client
    return "ok" if client is not None else "fail"


class HealthView(APIView):
    """Liveness + DB + Sentry probe. Throttle-exempt so Railway healthcheck never trips."""

    permission_classes = [AllowAny]
    throttle_classes: list = []
    authentication_classes: list = []

    @extend_schema(
        operation_id="getHealth",
        tags=["ops"],
        summary="Liveness + DB + Sentry probe",
        responses={
            200: OpenApiResponse(description="Healthy"),
            503: OpenApiResponse(description="Unhealthy (DB or critical dependency down)"),
        },
    )
    def get(self, request) -> Response:
        db_ok = _check_db()
        sentry_status = _check_sentry()
        status_ok = db_ok
        body = {
            "status": "ok" if status_ok else "fail",
            "db": "ok" if db_ok else "fail",
            "sentry": sentry_status,
            "version": settings.APP_VERSION,
            "timestamp": timezone.now().isoformat(),
        }
        return Response(body, status=200 if status_ok else 503)

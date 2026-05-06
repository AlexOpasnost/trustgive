"""Health endpoint per ADR-008 + API_SPEC endpoint #1."""
from __future__ import annotations

import logging
import os

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
            "commit_sha": _read_commit_sha(),
            "latest_migration": _latest_migration() if db_ok else None,
            "timestamp": timezone.now().isoformat(),
        }
        return Response(body, status=200 if status_ok else 503)


class DebugGiveDirectlyRawView(APIView):
    """Diagnostic only: dumps raw SQL select for the GiveDirectly row.

    Used to debug why migrations 0005/0006 didn't seem to land — distinguishes
    between "UPDATE didn't run" (raw value is empty default) and "UPDATE ran
    but reader strips" (raw value is correct, API serializer returns empty).

    Remove after the data fix is confirmed.
    """

    permission_classes = [AllowAny]
    throttle_classes: list = []
    authentication_classes: list = []

    def get(self, request) -> Response:
        from apps.charities.models import Charity

        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW client_encoding")
                client_encoding = cursor.fetchone()[0]
                cursor.execute("SHOW server_encoding")
                server_encoding = cursor.fetchone()[0]

                # Raw SQL — bypasses LocalizedTextField.from_db_value
                cursor.execute(
                    "SELECT id::text, slug, name::text, name->>'en' AS name_en, "
                    "name->>'ru' AS name_ru, tagline::text, "
                    "description::text, methodology_note::text, donation_url, "
                    "name_trgm, registration_id "
                    "FROM charities_charity WHERE registration_id = %s",
                    ["271661997"],
                )
                row = cursor.fetchone()

            # Same row through the runtime ORM (LocalizedTextField + JSONField path)
            try:
                charity = Charity.objects.get(registration_id="271661997")
                orm_name = charity.name
                orm_tagline_ru = charity.tagline.get("ru", "") if isinstance(charity.tagline, dict) else "(non-dict)"
                orm_name_type = type(charity.name).__name__
            except Exception as e:
                orm_name = f"ERROR: {e}"
                orm_tagline_ru = ""
                orm_name_type = "(error)"
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response(
            {
                "client_encoding": client_encoding,
                "server_encoding": server_encoding,
                "raw_sql": {
                    "id": row[0],
                    "slug": row[1],
                    "name_text": row[2],
                    "name_op_en": row[3],  # via JSONB ->> 'en' operator
                    "name_op_ru": row[4],
                    "tagline_text": row[5],
                    "description_text_first200": row[6][:200] if row[6] else row[6],
                    "methodology_note_text_first200": row[7][:200] if row[7] else row[7],
                    "donation_url": row[8],
                    "name_trgm": row[9],
                    "registration_id": row[10],
                },
                "orm": {
                    "name": orm_name,
                    "name_type": orm_name_type,
                    "tagline_ru": orm_tagline_ru,
                },
            },
            status=200,
        )


def _read_commit_sha() -> str:
    """Read the deploy commit SHA from env (Railway provides RAILWAY_GIT_COMMIT_SHA)."""
    sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "")
    return sha[:7] if sha else "unknown"


def _latest_migration() -> str | None:
    """Return the name of the most-recently-applied migration on charities app.

    Lets ops verify which schema/data version is live without DB access — useful
    for confirming that data migrations like 0005/0006 have run.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM django_migrations WHERE app=%s ORDER BY id DESC LIMIT 1",
                ["charities"],
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception:
        logger.exception("Health check: latest_migration lookup failed")
        return None

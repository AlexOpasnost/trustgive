"""Donation-redirect event endpoint — mirrors to PostHog server-side."""
from __future__ import annotations

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.posthog import capture as posthog_capture
from apps.events.serializers import DonationRedirectEventSerializer
from apps.events.throttling import DonationRedirectThrottle

logger = logging.getLogger(__name__)


class DonationRedirectView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [DonationRedirectThrottle]

    @extend_schema(
        operation_id="logDonationRedirect",
        tags=["events"],
        summary="Fire-and-forget logging for outbound donate clicks",
        request=DonationRedirectEventSerializer,
        responses={
            202: OpenApiResponse(description="Accepted"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = DonationRedirectEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Idempotency: client_event_id is UNIQUE; ignore_duplicate via update_or_create
        from apps.events.models import DonationRedirectEvent

        DonationRedirectEvent.objects.get_or_create(
            client_event_id=validated["client_event_id"],
            defaults={
                "charity_slug": validated["charity_slug"],
                "lang": validated["lang"],
                "source_page": validated.get("source_page", ""),
            },
        )

        # Mirror to PostHog server-side (best-effort, async, ad-block-resistant)
        posthog_capture(
            event="donation_redirect",
            properties={
                "charity_slug": validated["charity_slug"],
                "lang": validated["lang"],
                "source_page": validated.get("source_page", ""),
                "client_event_id": str(validated["client_event_id"]),
            },
        )

        return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)

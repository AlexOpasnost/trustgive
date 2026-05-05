"""ViewSets for charity catalog, detail, source-documents, comparison, causes, RSS feed."""
from __future__ import annotations

import logging
from typing import Any

from django.contrib.syndication.views import Feed
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.charities.filters import CharityFilter
from apps.charities.models import Cause, Charity, CharitySlugAlias
from apps.charities.serializers import (
    CauseSerializer,
    CharityComparisonSerializer,
    CharityDetailSerializer,
    CharitySummarySerializer,
    SourceDocumentSerializer,
)
from apps.core.middleware import set_charity_slug

logger = logging.getLogger(__name__)


SORT_MAP = {
    "most_recent_filing": "-last_filed_date",
    "largest_revenue": "-total_revenue_usd",
    "highest_program_pct": "-program_expense_pct",
    "alphabetical": "slug",
}


def _resolve_slug(slug: str) -> Charity:
    try:
        return Charity.objects.prefetch_related(
            "financial_history",
            "source_documents",
            "news_mentions",
            "charity_badges__badge",
        ).get(slug=slug)
    except Charity.DoesNotExist:
        # Try slug alias → 301 redirect path will be handled by viewset retrieve
        raise


class CharityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Charity.objects.all().prefetch_related("charity_badges__badge")
    serializer_class = CharitySummarySerializer
    filterset_class = CharityFilter
    lookup_field = "slug"
    lookup_value_regex = r"[a-z0-9-]+"

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.query_params.get("sort") or "most_recent_filing"
        order_by = SORT_MAP.get(sort, "-last_filed_date")
        return qs.order_by(order_by, "slug")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CharityDetailSerializer
        return CharitySummarySerializer

    @extend_schema(
        operation_id="listCharities",
        tags=["catalog"],
        summary="Paginated, faceted charity list",
        parameters=[
            OpenApiParameter("cause", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Cause slug(s); repeat for multiple"),
            OpenApiParameter("country", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["US", "GB", "RU"]),
            OpenApiParameter("size", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["small", "medium", "large"]),
            OpenApiParameter("verification_status", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["verified", "listed", "stale"]),
            OpenApiParameter("badges", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Comma-separated badge slugs"),
            OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Free-text search"),
            OpenApiParameter("lang", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["en", "ru"]),
            OpenApiParameter("sort", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=list(SORT_MAP.keys())),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(operation_id="getCharity", tags=["catalog"], summary="Full charity detail")
    def retrieve(self, request: Request, slug: str | None = None, **_: Any) -> Response:
        if slug:
            set_charity_slug(slug)
        try:
            instance = _resolve_slug(slug or "")
        except Charity.DoesNotExist:
            alias = CharitySlugAlias.objects.filter(slug=slug).select_related("charity").first()
            if alias is None:
                raise NotFound(f"No charity with slug '{slug}'")
            return Response(
                {"redirect_to": f"/api/charities/{alias.charity.slug}/"},
                status=status.HTTP_301_MOVED_PERMANENTLY,
                headers={"Location": f"/api/charities/{alias.charity.slug}/"},
            )
        return Response(CharityDetailSerializer(instance).data)

    @extend_schema(
        operation_id="listSourceDocuments",
        tags=["catalog"],
        summary="Source documents for a charity (drawer §6.7)",
    )
    @action(detail=True, methods=["get"], url_path="source-documents", url_name="charity-source-documents")
    def source_documents(self, request: Request, slug: str | None = None) -> Response:
        instance = get_object_or_404(Charity, slug=slug)
        set_charity_slug(slug or "")
        docs = instance.source_documents.all().order_by("-filed_date")
        return Response(SourceDocumentSerializer(docs, many=True).data)

    @extend_schema(
        operation_id="compareCharities",
        tags=["catalog"],
        summary="Side-by-side comparison (max 3)",
        parameters=[
            OpenApiParameter(
                "slugs",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Comma-separated, 2–3 charity slugs",
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="compare", url_name="charity-compare")
    def compare(self, request: Request) -> Response:
        slugs_param = (request.query_params.get("slugs") or "").strip()
        if not slugs_param:
            raise ValidationError({"slugs": "Required"})
        slugs = [s for s in slugs_param.split(",") if s]
        if not (2 <= len(slugs) <= 3):
            raise ValidationError({"slugs": "Must be 2 or 3 slugs"})

        charities = list(
            Charity.objects.filter(slug__in=slugs).prefetch_related(
                "financial_history", "source_documents", "charity_badges__badge"
            )
        )
        found_slugs = {c.slug for c in charities}
        missing = [s for s in slugs if s not in found_slugs]
        if missing:
            raise NotFound({"missing_slugs": missing})

        # Preserve user-supplied order
        ordered = sorted(charities, key=lambda c: slugs.index(c.slug))
        return Response({"charities": CharityComparisonSerializer(ordered, many=True).data})


class CauseListView(viewsets.ReadOnlyModelViewSet):
    """Lightweight list for the taxonomy endpoint (no detail action)."""

    queryset = Cause.objects.filter(parent__isnull=True).order_by("slug")
    serializer_class = CauseSerializer
    pagination_class = None

    @extend_schema(operation_id="listCauses", tags=["taxonomy"], summary="Cause taxonomy tree (EN+RU)")
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)


class NewCharitiesFeed(Feed):
    """RSS 2.0 of newly-added charities (per API_SPEC endpoint #7)."""

    title = "TrustGive — Newly Added Charities"
    link = "/api/feed.rss"
    description = "Verified charities newly added to TrustGive."

    def items(self):
        return Charity.objects.order_by("-created_at")[:50]

    def item_title(self, item: Charity) -> str:
        name = item.name or {}
        return name.get("en") or item.slug

    def item_description(self, item: Charity) -> str:
        tagline = (item.tagline or {}).get("en") or ""
        return tagline

    def item_link(self, item: Charity) -> str:
        return f"/api/charities/{item.slug}/"

    def item_pubdate(self, item: Charity):
        return item.created_at

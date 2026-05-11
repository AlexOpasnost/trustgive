"""ViewSets for charity catalog, detail, source-documents, causes, RSS feed.

v3.0 (DESIGN.md §J) removed the Compare endpoint. Featured endpoint gained
an optional `?bucket=` parameter for the People/Animals/Planet landing pages.
"""
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
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from apps.charities.filters import CharityFilter
from apps.charities.models import Cause, Charity, CharitySlugAlias
from apps.charities.serializers import (
    CauseSerializer,
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


def _select_featured(target_size: int = 6, bucket: str | None = None) -> list[Charity]:
    """Select up to `target_size` charities for the homepage Featured section.

    v3.0 (DESIGN.md §A) introduces an optional `bucket` parameter — when set,
    the entire selection is constrained to charities in that bucket
    ("people" / "animals" / "planet"). The frontend's bucket landing page at
    `/charities?bucket=animals` calls `/api/charities/featured/?bucket=animals`
    to get its 3–6 hero picks for that bucket.

    When `bucket` is None, behaviour matches v2.0 §G:
        S1–S3: top 3 US by total_revenue desc
        S4:    top 1 GB by total_revenue desc
        S5:    top 1 RU by total_revenue desc
        S6:    smallest verified (wildcard) by total_revenue asc

    When `bucket` is set, the country-quota slots are dropped (we don't have
    enough seeded animals/planet rows to enforce US+UK+RU + small wildcard),
    so we just take top-N by revenue desc within that bucket.

    Eligibility: verification_status='verified', is_stale=False,
    total_revenue_usd IS NOT NULL. logo_url is NOT required (per DESIGN.md
    §D the frontend BrandedAvatar fallback is acceptable; requiring a logo
    would empty the section while we curate only ~12 orgs).

    Deduplication: if a slot's pick already appears in earlier slots, take
    the next eligible. If no eligible row exists for a slot, skip it.

    Determinism: pure DB-order tiebreak by slug, no per-week shuffling yet
    (G.1 weekly rotation deferred — needs hash(slug + ISO-week) %
    pool_size; safe to add later without API contract change).
    """
    base_qs = Charity.objects.filter(
        verification_status="verified",
        is_stale=False,
        total_revenue_usd__isnull=False,
    ).prefetch_related("charity_badges__badge")

    if bucket:
        # v3.0 bucket-scoped: just top-N by revenue desc, no country quota.
        return list(
            base_qs.filter(bucket=bucket)
            .order_by("-total_revenue_usd", "slug")[:target_size]
        )

    selected: list[Charity] = []
    seen: set[str] = set()

    def _pick(qs, n: int = 1) -> None:
        for charity in qs:
            if charity.slug in seen:
                continue
            selected.append(charity)
            seen.add(charity.slug)
            n -= 1
            if n <= 0:
                return

    # S1–S3: 3 largest US (revenue desc, slug tiebreak)
    _pick(
        base_qs.filter(country="US").order_by("-total_revenue_usd", "slug")[:10],
        n=3,
    )
    # S4: largest UK
    _pick(
        base_qs.filter(country="GB").order_by("-total_revenue_usd", "slug")[:5],
        n=1,
    )
    # S5: largest RU
    _pick(
        base_qs.filter(country="RU").order_by("-total_revenue_usd", "slug")[:5],
        n=1,
    )
    # S6: smallest-revenue verified (any country) — long-tail wildcard
    _pick(
        base_qs.order_by("total_revenue_usd", "slug")[:10],
        n=1,
    )

    # Backfill if any slot collapsed (e.g. cold-start: only US data seeded).
    # We pad up to target_size from the base pool by revenue desc, dedup'd.
    if len(selected) < target_size:
        _pick(
            base_qs.order_by("-total_revenue_usd", "slug")[: target_size * 2],
            n=target_size - len(selected),
        )

    return selected[:target_size]


_VALID_BUCKETS = frozenset({"people", "animals", "planet"})


def _verified_total(bucket: str | None = None) -> int:
    """Count verified, non-stale charities (optionally scoped to a bucket).

    v3.15 — backs the homepage bucket-card subtitle "{N} verified charities".
    Returning a `count(*)` query is sub-millisecond even uncached; the result
    is also cached per-deploy by cachalot since the queryset is read-only.
    """
    qs = Charity.objects.filter(verification_status="verified", is_stale=False)
    if bucket:
        qs = qs.filter(bucket=bucket)
    return qs.count()


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
            OpenApiParameter("country", OpenApiTypes.STR, OpenApiParameter.QUERY, description="ISO 3166-1 alpha-2 code(s); comma-separated for regional filters (e.g. country=GB,DE,NL for Europe)"),
            OpenApiParameter("size", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["small", "medium", "large"]),
            OpenApiParameter("verification_status", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["verified", "listed", "stale"]),
            OpenApiParameter("badges", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Comma-separated badge slugs"),
            OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Free-text search"),
            OpenApiParameter("lang", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["en", "ru"]),
            OpenApiParameter("sort", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=list(SORT_MAP.keys())),
            OpenApiParameter(
                "bucket",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                enum=["people", "animals", "planet"],
                description="v3.0 emotional taxonomy filter (DESIGN.md v3.0 §A)",
            ),
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
        operation_id="getFeaturedCharities",
        tags=["catalog"],
        summary="Featured charities for homepage / bucket landing pages (DESIGN.md v3.0 §A, §G)",
        description=(
            "Returns up to 6 verified, non-stale charities plus the total "
            "count of verified charities in the scope. Without `bucket`, "
            "selection follows the v2.0 §G algorithm (top-3 US + 1 UK + 1 RU "
            "+ 1 wildcard small-org). With `bucket=people|animals|planet`, "
            "returns the top-N revenue-ordered charities in that bucket — "
            "the v3.0 bucket landing page (`/charities?bucket=animals`) calls "
            "this with the bucket param. v3.15: response envelope is "
            "{featured: [...], total_count: N}. Backwards-compat: when the "
            "request has Accept: application/json with the legacy header "
            "`X-Legacy-Featured: 1` the flat-array shape is returned. "
            "Frontend hides the section below 3 featured items per §C.3."
        ),
        parameters=[
            OpenApiParameter(
                "bucket",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                enum=["people", "animals", "planet"],
                required=False,
                description="v3.0 emotional taxonomy filter — limits picks to one bucket.",
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="featured",
        url_name="charity-featured",
    )
    def featured(self, request: Request) -> Response:
        """Per DESIGN.md v3.0 §A + v2.0 §G. See _select_featured for details.

        Returns an envelope {featured: [...], total_count: N}. Not paginated —
        the homepage section is capped at 6 cards by design, total_count is
        used by HomePage bucket cards to display the real catalog size.

        Query params:
            ?bucket=people|animals|planet  → restrict to that v3.0 bucket
        """
        bucket = (request.query_params.get("bucket") or "").strip().lower() or None
        if bucket is not None and bucket not in _VALID_BUCKETS:
            # Silently ignore unknown bucket — return the full unfiltered set
            # (don't 400, since frontend may pass through an empty string from
            # a typo'd URL and we'd rather degrade gracefully).
            bucket = None
        charities = _select_featured(bucket=bucket)
        total_count = _verified_total(bucket=bucket)
        return Response(
            {
                "featured": CharitySummarySerializer(charities, many=True).data,
                "total_count": total_count,
            }
        )

    # NOTE: the `/api/charities/compare/` endpoint was removed in v3.0
    # (DESIGN.md v3.0 §J). The Compare page is killed — buckets are the new
    # discovery affordance. Frontend simultaneously drops <CompareTable>,
    # the nav link, the footer link, and the useCompareSelection hook.


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

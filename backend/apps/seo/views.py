"""SEO landing page payload ("Is X legitimate?" per SPEC Story 5)."""
from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.charities.models import Charity, VerificationStatus
from apps.charities.serializers import CharityDetailSerializer


def _h1(charity: Charity, lang: str) -> str:
    name = (charity.name or {}).get(lang) or (charity.name or {}).get("en") or charity.slug
    if lang == "ru":
        return f"Является ли {name} легитимной благотворительной организацией?"
    return f"Is {name} a legitimate charity?"


def _answer(charity: Charity, lang: str) -> str:
    is_verified = charity.verification_status == VerificationStatus.VERIFIED
    if lang == "ru":
        return "Да — подтверждено." if is_verified else "Зарегистрирована, но не подтверждена."
    return "Yes — verified." if is_verified else "Listed, not verified."


def _evidence(charity: Charity, lang: str) -> str:
    name = (charity.name or {}).get("en") or charity.slug
    country_label = {"US": "US 501(c)(3) nonprofit", "GB": "UK registered charity", "RU": "Минюст-зарегистрированная НКО"}
    label = country_label.get(charity.country, "registered charity")
    if lang == "ru":
        return (
            f"{name} (рег. №{charity.registration_id}) — "
            f"{'зарегистрированная организация' if charity.country != 'US' else 'зарегистрированная 501(c)(3)'} "
            f"в {charity.country}, последняя финансовая отчётность подана {charity.last_filed_date or 'неизвестно'}."
        )
    return (
        f"{name} (registration {charity.registration_id}) is a {label}, in good standing, "
        f"with most recent financial filing on {charity.last_filed_date or 'unknown'}."
    )


class SeoCharityView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="getSeoCharity",
        tags=["seo"],
        summary='SEO landing-page payload ("Is X legitimate?")',
        parameters=[
            OpenApiParameter("lang", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=["en", "ru"]),
        ],
    )
    def get(self, request: Request, slug: str) -> Response:
        charity = get_object_or_404(
            Charity.objects.prefetch_related(
                "financial_history", "source_documents", "news_mentions", "charity_badges__badge"
            ),
            slug=slug,
        )
        lang = (request.query_params.get("lang") or "en").lower()
        if lang not in ("en", "ru"):
            lang = "en"

        h1 = _h1(charity, lang)
        answer = _answer(charity, lang)
        evidence = _evidence(charity, lang)

        title = f"{h1[:60]} · TrustGive" if len(h1) > 60 else f"{h1} · TrustGive"
        canonical_url = f"/{lang}/charities/{slug}/"

        body: dict[str, Any] = {
            "slug": slug,
            "h1": h1,
            "answer": answer,
            "evidence_summary": {"en": evidence if lang == "en" else _evidence(charity, "en"),
                                 "ru": evidence if lang == "ru" else _evidence(charity, "ru")},
            "meta": {
                "title": title[:70],
                "description": f"Verification status: {charity.verification_status}. EIN/Reg: {charity.registration_id}."[:160],
                "canonical_url": canonical_url,
                "og_image_url": f"https://api.trustgive.org/og/{slug}.png",
                "structured_data": {
                    "@context": "https://schema.org",
                    "@type": "NGO",
                    "name": (charity.name or {}).get("en", charity.slug),
                    "identifier": charity.registration_id,
                    "url": charity.donation_url or f"https://trustgive.org/charities/{slug}/",
                },
            },
            "charity": CharityDetailSerializer(charity).data,
        }
        return Response(body)

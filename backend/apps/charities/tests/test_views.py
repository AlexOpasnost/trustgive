"""DRF API integration tests for charity catalog endpoints."""

from __future__ import annotations

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.charities.models import Charity, Country, IngestionSource, SourceDocument


@pytest.fixture
def charity(db) -> Charity:
    return Charity.objects.create(
        slug="givedirectly",
        country=Country.US,
        registration_id="271661997",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": "GiveDirectly", "ru": "GiveDirectly"},
        tagline={"en": "Cash transfers", "ru": "Денежные переводы"},
        description={"en": "...", "ru": "..."},
        methodology_note={"en": "", "ru": ""},
        cause_tags=["poverty"],
        # Required for /featured/ to surface this row: _verified_total() filters
        # on (verification_status='verified', is_stale=False), _select_featured
        # additionally requires total_revenue_usd IS NOT NULL.
        verification_status="verified",
        is_stale=False,
        total_revenue_usd=1000,
    )


@pytest.mark.django_db
def test_list_charities_returns_paginated_summary(api_client, charity):
    res = api_client.get("/api/charities/")
    assert res.status_code == 200
    body = res.json()
    assert "results" in body
    assert "count" in body
    assert body["count"] >= 1


@pytest.mark.django_db
def test_charity_detail_returns_full_record(api_client, charity):
    res = api_client.get(f"/api/charities/{charity.slug}/")
    assert res.status_code == 200
    body = res.json()
    assert body["slug"] == "givedirectly"
    assert body["name"] == {"en": "GiveDirectly", "ru": "GiveDirectly"}
    assert "source_documents" in body
    assert "financial_history" in body


@pytest.mark.django_db
def test_charity_detail_404_on_unknown_slug(api_client):
    res = api_client.get("/api/charities/non-existent-slug/")
    assert res.status_code == 404
    body = res.json()
    assert body["error"]["code"] == "NOT_FOUND"


# --- v3.22: the catalogue card's source line ------------------------------- #
#
# The card wore a green "Verified" chip without ever saying what it was verified
# against. STRATEGY §2 calls that the missing half of the product, so the summary
# payload now names the document — and these tests hold it to naming a real one.


@pytest.mark.django_db
def test_summary_reports_the_document_backing_the_record(api_client, charity):
    SourceDocument.objects.create(
        charity=charity,
        kind="irs_990",
        label={"en": "IRS Form 990", "ru": "Форма IRS 990"},
        url="https://projects.propublica.org/nonprofits/organizations/271661997",
    )

    body = api_client.get("/api/charities/").json()
    card = next(c for c in body["results"] if c["slug"] == charity.slug)

    assert card["primary_source_kind"] == "irs_990"


@pytest.mark.django_db
def test_summary_reports_null_rather_than_guessing(api_client, charity):
    """No document, no claim. The card then renders no source line at all."""
    body = api_client.get("/api/charities/").json()
    card = next(c for c in body["results"] if c["slug"] == charity.slug)

    assert card["primary_source_kind"] is None


@pytest.mark.django_db
def test_documents_without_a_url_are_not_offered_as_evidence(api_client, charity):
    """A document nobody can open is not evidence, so it must not be named."""
    SourceDocument.objects.create(
        charity=charity,
        kind="annual_report",
        label={"en": "Annual report", "ru": "Годовой отчёт"},
        url="",
    )

    body = api_client.get("/api/charities/").json()
    card = next(c for c in body["results"] if c["slug"] == charity.slug)

    assert card["primary_source_kind"] is None


@pytest.mark.django_db
def test_catalogue_does_not_issue_a_query_per_card(api_client, db):
    """Guards the prefetch that keeps `primary_source_kind` from being an N+1.

    Reading a related document per row would cost one query per card — 60 on a
    catalogue page, 370 across a full crawl of the sitemap. The assertion is a
    ceiling rather than an exact number so unrelated query-count changes don't
    make this brittle; without the prefetch it lands in the twenties.
    """
    for i in range(12):
        row = Charity.objects.create(
            slug=f"org-{i}",
            country=Country.US,
            registration_id=f"reg-{i}",
            ingestion_source=IngestionSource.PROPUBLICA,
            name={"en": f"Org {i}", "ru": f"Org {i}"},
            tagline={"en": "", "ru": ""},
            description={"en": "", "ru": ""},
            methodology_note={"en": "", "ru": ""},
            cause_tags=[],
            verification_status="verified",
        )
        SourceDocument.objects.create(
            charity=row,
            kind="irs_990",
            label={"en": "IRS Form 990", "ru": "Форма IRS 990"},
            url=f"https://projects.propublica.org/nonprofits/organizations/{i}",
        )

    with CaptureQueriesContext(connection) as captured:
        res = api_client.get("/api/charities/?page_size=12")

    assert res.status_code == 200
    assert len(res.json()["results"]) == 12
    assert len(captured) <= 8, [q["sql"][:120] for q in captured]


@pytest.mark.django_db
def test_filter_by_country(api_client, charity):
    res = api_client.get("/api/charities/?country=US")
    assert res.status_code == 200
    body = res.json()
    assert all(r["country"] == "US" for r in body["results"])


@pytest.mark.django_db
def test_compare_endpoint_is_removed_in_v3(api_client, charity):
    """v3.0 (DESIGN.md §J) killed the Compare page entirely."""
    res = api_client.get(f"/api/charities/compare/?slugs={charity.slug}")
    assert res.status_code == 404


@pytest.mark.django_db
def test_filter_by_bucket(api_client, charity):
    """v3.0 catalog filter — bucket is the new primary user-facing taxonomy."""
    res = api_client.get("/api/charities/?bucket=people")
    assert res.status_code == 200
    body = res.json()
    assert all(r["bucket"] == "people" for r in body["results"])


@pytest.mark.django_db
def test_featured_endpoint_accepts_bucket_param(api_client, charity):
    """v3.0 §A — bucket-scoped featured for the bucket landing page.

    v3.15: response envelope is {featured: [...], total_count: N}.
    """
    res = api_client.get("/api/charities/featured/?bucket=animals")
    assert res.status_code == 200
    body = res.json()
    # Empty featured list is fine (no animals seeded in this fixture); the
    # contract is "200 + envelope shape, never 400".
    assert isinstance(body, dict)
    assert "featured" in body and isinstance(body["featured"], list)
    assert "total_count" in body and isinstance(body["total_count"], int)


@pytest.mark.django_db
def test_featured_endpoint_total_count_matches_verified_count(api_client, charity):
    """v3.15 — total_count is the real verified-charity total, not array length."""
    res = api_client.get("/api/charities/featured/")
    assert res.status_code == 200
    body = res.json()
    # The fixture seeds at least one verified charity, so total_count >= 1.
    # The featured array is capped at 6 by _select_featured.
    assert body["total_count"] >= 1
    assert len(body["featured"]) <= 6


@pytest.mark.django_db
def test_response_has_request_id_header(api_client, charity):
    res = api_client.get(f"/api/charities/{charity.slug}/")
    assert "X-Request-ID" in res.headers

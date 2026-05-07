"""DRF API integration tests for charity catalog endpoints."""
from __future__ import annotations

import pytest

from apps.charities.models import Charity, Country, IngestionSource


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
    """v3.0 §A — bucket-scoped featured for the bucket landing page."""
    res = api_client.get("/api/charities/featured/?bucket=animals")
    assert res.status_code == 200
    body = res.json()
    # Empty list is fine (no animals seeded in this fixture); the contract
    # is just "200 + flat list, never 400".
    assert isinstance(body, list)


@pytest.mark.django_db
def test_response_has_request_id_header(api_client, charity):
    res = api_client.get(f"/api/charities/{charity.slug}/")
    assert "X-Request-ID" in res.headers

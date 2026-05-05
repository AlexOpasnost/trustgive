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
def test_compare_endpoint_requires_2_to_3_slugs(api_client, charity):
    res = api_client.get(f"/api/charities/compare/?slugs={charity.slug}")
    assert res.status_code == 400  # only 1 slug
    body = res.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_response_has_request_id_header(api_client, charity):
    res = api_client.get(f"/api/charities/{charity.slug}/")
    assert "X-Request-ID" in res.headers

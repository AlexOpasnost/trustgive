"""The SEO payload and the serializer that documents it must not drift apart.

`SeoCharityView` builds its response as a hand-written dict while
`SeoCharityPayloadSerializer` declares what the OpenAPI schema — and therefore
the frontend's generated types — promises. Nothing forces the two to agree, so
these tests do.

This matters more than a usual docs-drift test. Until 2026-08-01 the view had no
declared response at all, drf-spectacular refused to describe it, and CI's
`spectacular --validate --fail-on-warn` aborted the backend-test job before
pytest ran. A silently-wrong serializer would put the job back in the same place
it just came out of: reporting a schema that doesn't match reality.
"""

from __future__ import annotations

import pytest

from apps.charities.models import Charity, Country, IngestionSource, SourceDocument
from apps.seo.serializers import SeoCharityPayloadSerializer, SeoMetaSerializer

PROPUBLICA = "https://projects.propublica.org/nonprofits/organizations/208625442"


@pytest.fixture
def verified_charity(db) -> Charity:
    charity = Charity.objects.create(
        slug="givewell",
        country=Country.US,
        registration_id="208625442",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": "GiveWell", "ru": "GiveWell"},
        tagline={"en": "", "ru": ""},
        description={"en": "", "ru": ""},
        methodology_note={"en": "", "ru": ""},
        cause_tags=["effective-altruism"],
        verification_status="verified",
        last_filed_date="2023-12-31",
    )
    SourceDocument.objects.create(
        charity=charity,
        kind="irs_990",
        label={"en": "IRS Form 990", "ru": "Форма IRS 990"},
        url=PROPUBLICA,
    )
    return charity


@pytest.mark.django_db
def test_payload_keys_match_serializer(api_client, verified_charity):
    """Every top-level key the view emits is declared, and vice versa."""
    res = api_client.get(f"/api/seo/charities/{verified_charity.slug}/")
    assert res.status_code == 200

    assert set(res.json()) == set(SeoCharityPayloadSerializer().fields)


@pytest.mark.django_db
def test_meta_keys_match_serializer(api_client, verified_charity):
    res = api_client.get(f"/api/seo/charities/{verified_charity.slug}/")

    assert set(res.json()["meta"]) == set(SeoMetaSerializer().fields)


@pytest.mark.django_db
def test_unverified_charity_has_no_landing_page(api_client, verified_charity):
    """A verdict page for an organisation we could not verify would be a lie."""
    verified_charity.verification_status = "listed"
    verified_charity.save(update_fields=["verification_status"])

    res = api_client.get(f"/api/seo/charities/{verified_charity.slug}/")

    assert res.status_code == 404


@pytest.mark.django_db
def test_evidence_summary_carries_both_languages(api_client, verified_charity):
    """The frontend toggles language client-side from one response."""
    res = api_client.get(f"/api/seo/charities/{verified_charity.slug}/?lang=en")

    evidence = res.json()["evidence_summary"]
    assert set(evidence) == {"en", "ru"}
    assert evidence["en"] and evidence["ru"]
    # The registration number is the point of the sentence — assert it survives
    # into both translations rather than only the one that was requested.
    assert verified_charity.registration_id in evidence["en"]
    assert verified_charity.registration_id in evidence["ru"]


@pytest.mark.django_db
def test_seo_endpoint_reaches_the_generated_schema():
    """Guards the specific failure that kept CI red.

    drf-spectacular dropped this endpoint with "unable to guess serializer …
    Ignoring view for now", which `--fail-on-warn` turned into a non-zero exit
    before pytest ever started. A bare command-line exit code says nothing about
    which view was at fault; this names it.
    """
    from drf_spectacular.generators import SchemaGenerator

    schema = SchemaGenerator().get_schema(request=None, public=True)

    paths = schema.get("paths", {})
    assert any("/seo/charities/" in path for path in paths), sorted(paths)
    assert "SeoCharityPayload" in schema["components"]["schemas"]

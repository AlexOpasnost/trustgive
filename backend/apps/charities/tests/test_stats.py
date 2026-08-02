"""Catalogue counts must be derived, never asserted from memory (v3.22).

The defect this guards against shipped and stayed live for weeks: the homepage
said "540+ verified charities across 27 countries" while the catalogue held 370
across 10. Nothing was broken — the numbers were simply typed into markup when
they were true and never revisited. So the test that matters is not "does the
endpoint return 200" but "does the number move when the catalogue moves".
"""

from __future__ import annotations

import pytest

from apps.charities.models import Charity, Country, IngestionSource


def make(slug: str, *, country=Country.US, verified: bool = True) -> Charity:
    return Charity.objects.create(
        slug=slug,
        country=country,
        registration_id=f"reg-{slug}",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": slug, "ru": slug},
        tagline={"en": "", "ru": ""},
        description={"en": "", "ru": ""},
        methodology_note={"en": "", "ru": ""},
        cause_tags=[],
        verification_status="verified" if verified else "listed",
    )


@pytest.mark.django_db
def test_counts_follow_the_catalogue(api_client):
    make("a-us")
    make("b-us")
    make("c-gb", country=Country.GB)

    body = api_client.get("/api/stats/").json()

    assert body["charities"] == 3
    assert body["countries"] == 2


@pytest.mark.django_db
def test_unverified_rows_are_not_counted(api_client):
    """The public claim is about the *published* catalogue, not the database."""
    make("published-one")
    make("hidden-one", verified=False)
    make("hidden-two", country=Country.GB, verified=False)

    body = api_client.get("/api/stats/").json()

    assert body["charities"] == 1
    # The unverified GB row must not add a country to the public count either —
    # that is exactly how "27 countries" outlived the catalogue that had them.
    assert body["countries"] == 1


@pytest.mark.django_db
def test_shrinking_the_catalogue_shrinks_the_numbers(api_client):
    make("a-us")
    gb = make("b-gb", country=Country.GB)

    assert api_client.get("/api/stats/").json() == {
        "charities": 2,
        "countries": 2,
        "last_checked": gb.updated_at.date().isoformat(),
    }

    gb.delete()

    after = api_client.get("/api/stats/").json()
    assert after["charities"] == 1
    assert after["countries"] == 1


@pytest.mark.django_db
def test_empty_catalogue_reports_no_date_rather_than_a_wrong_one(api_client):
    body = api_client.get("/api/stats/").json()

    assert body == {"charities": 0, "countries": 0, "last_checked": None}

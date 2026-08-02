"""Free-text search ranking (v3.21).

The product's dominant arrival is "someone named a charity at me — is it real?".
That makes exactly one thing non-negotiable: the organisation whose name or
registration number IS the query comes first. Everything here defends that,
plus the two defects that broke it in production:

  * `SearchRank("search_vector", …)` re-vectorised the stored tsvector's text
    dump and threw away the A/B/C weights, so charities merely *mentioning*
    GiveWell outranked GiveWell;
  * `TrigramSimilarity` scored the query against the whole EN+RU name blob, so a
    one-letter typo matched nothing despite pg_trgm being enabled.
"""

from __future__ import annotations

import pytest

from apps.charities.models import Charity, Country, IngestionSource


def make(slug: str, name_en: str, *, description: str = "", registration: str = "") -> Charity:
    return Charity.objects.create(
        slug=slug,
        country=Country.US,
        registration_id=registration or f"reg{slug}",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": name_en, "ru": name_en},
        tagline={"en": "", "ru": ""},
        description={"en": description, "ru": description},
        methodology_note={"en": "", "ru": ""},
        cause_tags=[],
        verification_status="verified",
    )


@pytest.fixture
def named(db) -> None:
    """The production shape of the bug: two charities cite a third by name."""
    make("givewell", "GiveWell (The Clear Fund)", registration="208625442")
    make(
        "sightsavers",
        "Sightsavers",
        description="A GiveWell-recommended charity. GiveWell rates it highly.",
    )
    make(
        "brac-usa",
        "BRAC USA",
        description="GiveWell-recommended. Listed by GiveWell for deworming.",
    )


def slugs(api_client, query: str) -> list[str]:
    res = api_client.get("/api/charities/", {"q": query})
    assert res.status_code == 200
    return [r["slug"] for r in res.json()["results"]]


@pytest.mark.django_db
def test_named_charity_outranks_charities_that_merely_mention_it(api_client, named):
    assert slugs(api_client, "givewell")[0] == "givewell"


@pytest.mark.django_db
def test_single_letter_typo_still_finds_the_charity(api_client, named):
    """'givewel' returned nothing before v3.21 — the trigram gate never opened."""
    assert slugs(api_client, "givewel")[0] == "givewell"


@pytest.mark.django_db
def test_registration_number_finds_the_charity(api_client, named):
    assert slugs(api_client, "208625442") == ["givewell"]


@pytest.mark.django_db
def test_registration_number_tolerates_typed_punctuation(api_client, named):
    """People copy an EIN in its printed form."""
    assert slugs(api_client, "20-8625442") == ["givewell"]


@pytest.mark.django_db
def test_exact_name_wins_over_a_stronger_text_match(db, api_client):
    """Identity beats relevance: the charity called X is first for the query X."""
    make("acme", "Acme")
    make("other", "Other Foundation", description="Acme Acme Acme Acme Acme.")
    assert slugs(api_client, "Acme")[0] == "acme"


@pytest.mark.django_db
def test_unknown_name_returns_nothing_rather_than_a_lookalike(db, api_client):
    """An honest empty result beats a plausible wrong one.

    The catalogue publishes only organisations whose filing we could open, so
    "not found" carries real information — the empty state says as much. Handing
    back a same-shaped different charity would undermine that.
    """
    make("american-cancer-society", "American Cancer Society")
    assert slugs(api_client, "amnesty") == []

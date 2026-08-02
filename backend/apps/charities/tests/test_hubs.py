"""Hub sections — /api/hubs/ and the `registry` filter (v3.21).

The behaviour worth protecting here is the threshold. A hub that publishes below
MIN_HUB_SIZE is a thin page: it competes with the catalogue for the same query
and is precisely what Google files under "Discovered — currently not indexed",
which is the problem hubs exist to fix. Equally, an unknown registry slug must
resolve to nothing rather than to the whole catalogue — otherwise
/charities/registry/typo would claim 370 charities were verified by a registry
that never heard of them.
"""

from __future__ import annotations

import pytest

from apps.charities.hubs import MIN_HUB_SIZE, all_hubs
from apps.charities.models import Charity, Country, IngestionSource, SourceDocument

PROPUBLICA = "https://projects.propublica.org/nonprofits/organizations/"


def make_charity(slug: str, *, country=Country.US, causes=None, verified=True) -> Charity:
    return Charity.objects.create(
        slug=slug,
        country=country,
        registration_id=f"reg-{slug}",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": slug, "ru": slug},
        tagline={"en": "", "ru": ""},
        description={"en": "", "ru": ""},
        methodology_note={"en": "", "ru": ""},
        cause_tags=causes if causes is not None else ["global-health"],
        verification_status="verified" if verified else "listed",
    )


@pytest.fixture
def catalogue(db) -> None:
    """Six US charities on `global-health`, plus one UK charity on its own tag."""
    for i in range(MIN_HUB_SIZE + 1):
        charity = make_charity(f"us-{i}", causes=["global-health"])
        SourceDocument.objects.create(
            charity=charity,
            kind="irs_990",
            label={"en": "Form 990", "ru": "Форма 990"},
            url=f"{PROPUBLICA}{i}",
        )
    make_charity("gb-only", country=Country.GB, causes=["rare-cause"])


@pytest.mark.django_db
def test_hub_index_lists_groupings_at_or_above_threshold(api_client, catalogue):
    res = api_client.get("/api/hubs/")
    assert res.status_code == 200
    body = res.json()

    assert body["min_size"] == MIN_HUB_SIZE
    assert [h["slug"] for h in body["countries"]] == ["us"]
    assert [h["slug"] for h in body["causes"]] == ["global-health"]
    assert [h["slug"] for h in body["registries"]] == ["irs-990"]

    us = body["countries"][0]
    assert us["count"] == MIN_HUB_SIZE + 1
    assert us["code"] == "US"
    assert us["path"] == "/charities/country/us"
    assert us["label"]["en"] and us["label"]["ru"]


@pytest.mark.django_db
def test_hub_index_omits_groupings_below_threshold(api_client, catalogue):
    """One UK charity and one `rare-cause` charity get no page of their own."""
    body = api_client.get("/api/hubs/").json()
    assert "gb" not in [h["slug"] for h in body["countries"]]
    assert "rare-cause" not in [h["slug"] for h in body["causes"]]


@pytest.mark.django_db
def test_unverified_charities_do_not_count_towards_a_hub(db):
    """Hubs are counted off the published catalogue, matching views.PUBLISHED."""
    for i in range(MIN_HUB_SIZE + 1):
        make_charity(f"listed-{i}", causes=["hidden-cause"], verified=False)
    hubs = all_hubs()
    assert [h["slug"] for h in hubs["causes"]] == []
    assert [h["slug"] for h in hubs["countries"]] == []


@pytest.mark.django_db
def test_registry_filter_selects_only_that_registry(api_client, catalogue):
    res = api_client.get("/api/charities/?registry=irs-990")
    assert res.status_code == 200
    assert res.json()["count"] == MIN_HUB_SIZE + 1


@pytest.mark.django_db
def test_unknown_registry_slug_returns_nothing_not_everything(api_client, catalogue):
    """A typo'd registry must not silently render as the entire catalogue."""
    res = api_client.get("/api/charities/?registry=not-a-registry")
    assert res.status_code == 200
    assert res.json()["count"] == 0


@pytest.mark.django_db
def test_registry_filter_matches_on_host_not_substring(db):
    """A registry's name inside a path must not put a charity on its page."""
    charity = make_charity("impostor")
    SourceDocument.objects.create(
        charity=charity,
        kind="annual_report",
        label={"en": "Annual report", "ru": "Годовой отчёт"},
        url="https://example.org/mirror/projects.propublica.org/report.pdf",
    )
    res = api_client_get_count()
    assert res == 0


def api_client_get_count() -> int:
    from apps.charities.filters import CharityFilter
    from apps.charities.models import VerificationStatus

    qs = Charity.objects.filter(verification_status=VerificationStatus.VERIFIED)
    return CharityFilter({"registry": "irs-990"}, queryset=qs).qs.count()

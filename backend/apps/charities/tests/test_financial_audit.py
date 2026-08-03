"""The control that watches the money column must itself be watched.

Finding 8 in DATA_INTEGRITY.md happened because nothing checked revenue figures
against the sources they cite. `audit_financial_sources` is that check; these
tests make sure it actually fires, and — just as important — that it stays quiet
on sound data, because a check that cries wolf nightly gets muted and then it is
no check at all.
"""

from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.charities.models import Charity, Country, Financial, IngestionSource


def make_charity(slug: str, *, verified: bool = True, last_filed: str | None = "2023-12-31"):
    return Charity.objects.create(
        slug=slug,
        country=Country.US,
        registration_id=f"reg-{slug}",
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": slug, "ru": slug},
        tagline={"en": "", "ru": ""},
        description={"en": "", "ru": ""},
        methodology_note={"en": "", "ru": ""},
        cause_tags=[],
        verification_status="verified" if verified else "listed",
        last_filed_date=last_filed,
    )


@pytest.mark.django_db
def test_clean_catalogue_passes_strict(capsys):
    charity = make_charity("sound-org")
    Financial.objects.create(
        charity=charity,
        year=2023,
        total_revenue_usd=201181635,  # a real-looking total
        source_url="https://projects.propublica.org/nonprofits/organizations/1",
    )

    call_command("audit_financial_sources", "--strict")

    assert "No unsourced revenue figures found." in capsys.readouterr().out


@pytest.mark.django_db
def test_round_revenue_on_a_published_charity_fails_strict():
    charity = make_charity("round-org")
    Financial.objects.create(
        charity=charity,
        year=2023,
        total_revenue_usd=240000000,  # exact multiple of 10M — the seed signature
        source_url="https://projects.propublica.org/nonprofits/organizations/2",
    )

    with pytest.raises(SystemExit) as exc:
        call_command("audit_financial_sources", "--strict")

    assert exc.value.code == 1


@pytest.mark.django_db
def test_year_ahead_of_the_charitys_own_filing_is_flagged():
    """A figure for a period the cited filing doesn't reach can't come from it."""
    charity = make_charity("ahead-org", last_filed="2019-06-30")
    Financial.objects.create(
        charity=charity,
        year=2023,
        total_revenue_usd=123456789,  # not round — caught by the other rule
        source_url="https://projects.propublica.org/nonprofits/organizations/3",
    )

    with pytest.raises(SystemExit):
        call_command("audit_financial_sources", "--strict")


@pytest.mark.django_db
def test_unpublished_charities_do_not_fail_the_job(capsys):
    """Unverified rows assert nothing publicly, so they must not block the ETL."""
    charity = make_charity("hidden-org", verified=False)
    Financial.objects.create(
        charity=charity,
        year=2023,
        total_revenue_usd=240000000,
        source_url="https://projects.propublica.org/nonprofits/organizations/4",
    )

    call_command("audit_financial_sources", "--strict")

    assert "No unsourced revenue figures found." in capsys.readouterr().out


@pytest.mark.django_db
def test_revenue_with_no_financial_row_behind_it_is_flagged():
    """The other way the money column goes unsourced: a headline with no source."""
    charity = make_charity("orphan-org")
    charity.total_revenue_usd = 123456789
    charity.save(update_fields=["total_revenue_usd"])

    with pytest.raises(SystemExit):
        call_command("audit_financial_sources", "--strict")


@pytest.mark.django_db
def test_without_strict_it_reports_but_does_not_exit(capsys):
    charity = make_charity("round-org-2")
    Financial.objects.create(
        charity=charity,
        year=2023,
        total_revenue_usd=50000000,
        source_url="https://projects.propublica.org/nonprofits/organizations/5",
    )

    call_command("audit_financial_sources")

    assert "unsourced revenue figure" in capsys.readouterr().out

"""What `merge_duplicate_charities` must refuse to do.

It is the only command in this project that deletes a charity row, so its
refusals matter more than its happy path. Each test below is a way the command
could quietly destroy something it was not asked to.
"""

from __future__ import annotations

import json

import pytest
from django.core.management import call_command

from apps.charities.models import (
    Charity,
    Country,
    DocumentKind,
    FileFormat,
    IngestionSource,
    SourceDocument,
    VerificationStatus,
)


def _charity(slug: str, *, reg: str, status: str = VerificationStatus.LISTED, **extra) -> Charity:
    return Charity.objects.create(
        slug=slug,
        country=Country.US,
        registration_id=reg,
        verification_status=status,
        ingestion_source=IngestionSource.PROPUBLICA,
        name={"en": slug, "ru": ""},
        tagline={"en": "", "ru": ""},
        description={"en": "", "ru": ""},
        methodology_note={"en": "", "ru": ""},
        **extra,
    )


@pytest.fixture
def pairs_file(tmp_path):
    def write(keep: str, drop: str):
        path = tmp_path / "pairs.json"
        path.write_text(json.dumps([{"keep": keep, "drop": drop, "why": "test"}]), encoding="utf-8")
        return str(path)

    return write


@pytest.mark.django_db
def test_merges_and_deletes_the_duplicate(pairs_file):
    _charity("keeper", reg="1", status=VerificationStatus.VERIFIED)
    _charity("dupe", reg="2", cause_tags=["oceans"])

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}")

    assert not Charity.objects.filter(slug="dupe").exists()
    assert Charity.objects.get(slug="keeper").cause_tags == ["oceans"]


@pytest.mark.django_db
def test_refuses_to_delete_a_row_that_carries_evidence(pairs_file):
    _charity("keeper", reg="1", status=VerificationStatus.VERIFIED)
    dupe = _charity("dupe", reg="2")
    SourceDocument.objects.create(
        charity=dupe,
        kind=DocumentKind.IRS_990,
        label={"en": "990", "ru": "990"},
        url="https://example.org/990",
        source_label="test",
        file_format=FileFormat.PDF,
    )

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}")

    # A document is the thing this catalogue exists to point at. Nothing that
    # holds one gets deleted by a merge.
    assert Charity.objects.filter(slug="dupe").exists()


@pytest.mark.django_db
def test_refuses_when_the_survivor_is_not_verified(pairs_file):
    # Merging into an unverified row would throw away the pair's only evidence
    # and leave the organisation unpublishable.
    _charity("keeper", reg="1")
    _charity("dupe", reg="2", status=VerificationStatus.VERIFIED)

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}")

    assert Charity.objects.filter(slug="dupe").exists()


@pytest.mark.django_db
def test_refuses_to_delete_a_published_row(pairs_file):
    _charity("keeper", reg="1", status=VerificationStatus.VERIFIED)
    _charity("dupe", reg="2", status=VerificationStatus.VERIFIED)

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}")

    assert Charity.objects.filter(slug="dupe").exists()


@pytest.mark.django_db
def test_never_overwrites_curated_content_on_the_survivor(pairs_file):
    _charity(
        "keeper",
        reg="1",
        status=VerificationStatus.VERIFIED,
        hero_photo_url="https://example.org/keeper.jpg",
        donation_url="https://keeper.org/give",
    )
    _charity(
        "dupe",
        reg="2",
        hero_photo_url="https://example.org/dupe.jpg",
        donation_url="https://dupe.org/give",
    )

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}")

    keep = Charity.objects.get(slug="keeper")
    assert keep.hero_photo_url == "https://example.org/keeper.jpg"
    assert keep.donation_url == "https://keeper.org/give"


@pytest.mark.django_db
def test_dry_run_deletes_nothing(pairs_file):
    _charity("keeper", reg="1", status=VerificationStatus.VERIFIED)
    _charity("dupe", reg="2", cause_tags=["oceans"])

    call_command("merge_duplicate_charities", f"--file={pairs_file('keeper', 'dupe')}", "--dry-run")

    assert Charity.objects.filter(slug="dupe").exists()
    assert Charity.objects.get(slug="keeper").cause_tags == []

"""Tests for Charity model + uniqueness constraints."""
from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.charities.models import (
    Charity,
    Country,
    IngestionSource,
    VerificationStatus,
)


@pytest.fixture
def charity_kwargs() -> dict:
    return {
        "slug": "givedirectly",
        "country": Country.US,
        "registration_id": "271661997",
        "ingestion_source": IngestionSource.PROPUBLICA,
        "name": {"en": "GiveDirectly", "ru": "GiveDirectly"},
        "tagline": {"en": "Cash transfers", "ru": "Денежные переводы"},
        "description": {"en": "...", "ru": "..."},
        "methodology_note": {"en": "", "ru": ""},
    }


@pytest.mark.django_db
def test_charity_creates_with_localized_fields(charity_kwargs):
    charity = Charity.objects.create(**charity_kwargs)
    assert charity.name["en"] == "GiveDirectly"
    assert charity.name["ru"] == "GiveDirectly"
    assert charity.verification_status == VerificationStatus.LISTED  # default


@pytest.mark.django_db
def test_country_registration_id_unique(charity_kwargs):
    Charity.objects.create(**charity_kwargs)
    with pytest.raises(IntegrityError):
        Charity.objects.create(**charity_kwargs)


@pytest.mark.django_db
def test_slug_unique(charity_kwargs):
    Charity.objects.create(**charity_kwargs)
    other = {**charity_kwargs, "registration_id": "999999999"}
    with pytest.raises(IntegrityError):
        Charity.objects.create(**other)


@pytest.mark.django_db
def test_cause_tags_array_field(charity_kwargs):
    charity = Charity.objects.create(**charity_kwargs, cause_tags=["poverty", "cash-transfers"])
    assert charity.cause_tags == ["poverty", "cash-transfers"]
    queried = Charity.objects.filter(cause_tags__overlap=["poverty"]).first()
    assert queried == charity

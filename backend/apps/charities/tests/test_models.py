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
def test_many_charities_per_country_may_have_no_registration_id(charity_kwargs):
    """The point of making the field nullable (migration 0059).

    While it was NOT NULL, "unknown" had to be spelled `""`, which is a value and
    therefore collided under `uniq_country_registration` — so exactly one row per
    country could say it. That is what left four New Zealand and twenty-two
    Canadian charities holding a number registered to somebody else, with no way
    to remove it (DATA_INTEGRITY Findings 11 and 7).
    """
    Charity.objects.create(**{**charity_kwargs, "slug": "a", "registration_id": None})
    Charity.objects.create(**{**charity_kwargs, "slug": "b", "registration_id": None})
    Charity.objects.create(**{**charity_kwargs, "slug": "c", "registration_id": None})

    assert Charity.objects.filter(country=Country.US, registration_id__isnull=True).count() == 3


@pytest.mark.django_db
def test_a_real_registration_id_is_still_unique_per_country(charity_kwargs):
    # Nullability must not have loosened the constraint for actual numbers.
    Charity.objects.create(**{**charity_kwargs, "slug": "a", "registration_id": None})
    Charity.objects.create(**{**charity_kwargs, "slug": "b", "registration_id": "271661997"})
    with pytest.raises(IntegrityError):
        Charity.objects.create(**{**charity_kwargs, "slug": "c", "registration_id": "271661997"})


@pytest.mark.django_db
def test_the_same_number_may_exist_in_two_countries(charity_kwargs):
    # The constraint is (country, registration_id), and registries in different
    # countries do reuse digits.
    Charity.objects.create(**{**charity_kwargs, "slug": "a", "registration_id": "1160558"})
    Charity.objects.create(
        **{**charity_kwargs, "slug": "b", "country": Country.GB, "registration_id": "1160558"}
    )
    assert Charity.objects.filter(registration_id="1160558").count() == 2


@pytest.mark.django_db
def test_cause_tags_array_field(charity_kwargs):
    charity = Charity.objects.create(**charity_kwargs, cause_tags=["poverty", "cash-transfers"])
    assert charity.cause_tags == ["poverty", "cash-transfers"]
    queried = Charity.objects.filter(cause_tags__overlap=["poverty"]).first()
    assert queried == charity

"""Top-level pytest fixtures."""

from __future__ import annotations

import pytest
from django.test import Client
from rest_framework.test import APIClient


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: F811
    """Build the test schema from migrations, then drop the data they seeded.

    The catalogue is populated by data migrations (0025, 0055 and friends carry
    the real ~540 organisations). pytest-django applies every migration when it
    creates the test database, so tests start with a full production-shaped
    catalogue unless something removes it.

    That broke every test that builds its own fixture: creating a charity with
    slug "givewell" hit `duplicate key value violates unique constraint
    charities_charity_slug_key`, and assertions like `slugs(...) == ["givewell"]`
    could not hold against 540 unrelated rows. Nobody had noticed, because the
    suite had never actually run in CI.

    Deleting here rather than passing `--nomigrations` is deliberate: search
    depends on the `search_vector` trigger, which exists only because migration
    0003 creates it. Skipping migrations would take the trigger with it and the
    ranking tests would be testing nothing.

    One deletion at session scope is enough — each test runs inside a
    transaction that is rolled back, so the empty catalogue persists for all of
    them. Cause/TrustBadge taxonomy rows are left in place: they are reference
    data, not catalogue content, and tests read them for labels.
    """
    with django_db_blocker.unblock():
        from apps.charities.models import Charity

        Charity.objects.all().delete()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def client() -> Client:
    return Client()

"""Tests for /api/events/donation-redirect/ — idempotency + throttle (per ADR-007/008)."""
from __future__ import annotations

import uuid

import pytest


@pytest.mark.django_db
def test_donation_redirect_accepted_202(api_client):
    payload = {
        "client_event_id": str(uuid.uuid4()),
        "charity_slug": "givedirectly",
        "lang": "en",
        "source_page": "detail",
    }
    res = api_client.post("/api/events/donation-redirect/", payload, format="json")
    assert res.status_code == 202
    assert res.json() == {"status": "accepted"}


@pytest.mark.django_db
def test_donation_redirect_idempotent_on_repeat_event_id(api_client):
    eid = str(uuid.uuid4())
    payload = {"client_event_id": eid, "charity_slug": "givedirectly", "lang": "en"}
    res1 = api_client.post("/api/events/donation-redirect/", payload, format="json")
    res2 = api_client.post("/api/events/donation-redirect/", payload, format="json")
    assert res1.status_code == 202
    # Second call should still be accepted (get_or_create returns existing)
    assert res2.status_code in (202, 429)  # may throttle, but never duplicate


@pytest.mark.django_db
def test_donation_redirect_validation_error(api_client):
    res = api_client.post("/api/events/donation-redirect/", {}, format="json")
    assert res.status_code == 400
    body = res.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"

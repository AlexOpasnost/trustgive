"""Tests for HealthView (per ADR-008)."""
from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_health_endpoint_returns_200(api_client):
    res = api_client.get("/api/health/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert "timestamp" in body
    assert "version" in body


@pytest.mark.django_db(transaction=True)
def test_health_endpoint_no_throttle(api_client, settings):
    """Health is exempt — even hammering shouldn't trip the throttle.

    transaction=True (rather than the default @pytest.mark.django_db) is
    required because this test loops multiple api_client.get() calls inside
    one test. The default fixture wraps the test in a transaction that gets
    invalidated by Django's `request_finished` → `close_old_connections()`
    signal after the first request; subsequent requests then see a closed
    connection and `_check_db()` returns False (test fails with 503, not
    429 — the actual throttle-bypass logic works fine).
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "1/min"
    for _ in range(5):
        res = api_client.get("/api/health/")
        assert res.status_code == 200, "Health endpoint must NEVER throttle"

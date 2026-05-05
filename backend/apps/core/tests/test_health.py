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


def test_health_endpoint_no_throttle(api_client, settings):
    """Health is exempt — even hammering shouldn't trip the throttle."""
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "1/min"
    for _ in range(5):
        res = api_client.get("/api/health/")
        assert res.status_code == 200, "Health endpoint must NEVER throttle"

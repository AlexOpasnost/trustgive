"""Top-level pytest fixtures."""
from __future__ import annotations

import pytest
from django.test import Client
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def client() -> Client:
    return Client()

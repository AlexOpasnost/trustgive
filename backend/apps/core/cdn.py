"""Cloudflare cache purge helper (per ADR-007).

Gracefully no-ops when CF_API_TOKEN is not configured — useful for local dev.
"""
from __future__ import annotations

import logging
from typing import Iterable

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def purge_charity(slug: str) -> None:
    """Purge per-charity CDN URLs after ingestion update."""
    if not settings.CF_API_TOKEN or not settings.CF_ZONE_ID:
        return

    api_root = "https://api.trustgive.org"
    urls = [
        f"{api_root}/api/charities/{slug}/",
        f"{api_root}/api/charities/{slug}/source-documents/",
        f"{api_root}/api/seo/charities/{slug}/",
    ]
    _purge_files(urls)


def _purge_files(urls: Iterable[str]) -> None:
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{settings.CF_ZONE_ID}/purge_cache"
    headers = {
        "Authorization": f"Bearer {settings.CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(endpoint, headers=headers, json={"files": list(urls)}, timeout=10)
        if resp.status_code >= 400:
            logger.warning("Cloudflare purge failed: %s %s", resp.status_code, resp.text[:200])
    except requests.RequestException:
        logger.exception("Cloudflare purge request failed")

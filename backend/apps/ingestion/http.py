"""ThrottledHTTPClient — politeness throttle + exponential backoff for ETL."""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ThrottledHTTPClient:
    """Wraps `requests` with a per-second rate limit and tenacity retry on 429/5xx."""

    def __init__(self, base_url: str, requests_per_sec: float = 5.0, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self._min_interval = 1.0 / max(requests_per_sec, 0.1)
        self._lock = threading.Lock()
        self._last_request_at = 0.0
        self._timeout = timeout
        self._session = requests.Session()

    def _wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._last_request_at + self._min_interval - now
            if wait > 0:
                time.sleep(wait)
            self._last_request_at = time.monotonic()

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def get(self, path: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        self._wait()
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self._session.get(url, params=params, headers=headers, timeout=self._timeout)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise requests.RequestException(f"Retryable HTTP {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
        return resp.json()

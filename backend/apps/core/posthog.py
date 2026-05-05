"""Server-side PostHog mirror for the donation_redirect event (per ADR-008).

Why server-side: adblocker miss rate on PostHog client SDK is 20-40% for our
privacy-conscious target audience. Donation-redirect is the conversion that
matters most for portfolio narrative — server-side mirror makes it
ad-block-resistant. Keeps API key off the client.
"""
from __future__ import annotations

import logging
import queue
import threading
from typing import Any

from django.conf import settings

try:
    from posthog import Posthog
except ImportError:  # pragma: no cover
    Posthog = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1000)
_worker_started = False
_lock = threading.Lock()


def _client() -> Any:
    if not settings.POSTHOG_SERVER_KEY or Posthog is None:
        return None
    return Posthog(settings.POSTHOG_SERVER_KEY, host=settings.POSTHOG_HOST)


def _worker_loop() -> None:
    client = _client()
    if client is None:
        logger.info("PostHog mirror disabled (POSTHOG_SERVER_KEY not set)")
        return
    while True:
        try:
            item = _queue.get(timeout=60)
        except queue.Empty:
            continue
        try:
            client.capture(
                distinct_id=item.get("distinct_id", "anonymous"),
                event=item["event"],
                properties=item.get("properties", {}),
            )
        except Exception:
            logger.exception("PostHog capture failed")
        finally:
            _queue.task_done()


def _ensure_worker() -> None:
    global _worker_started
    with _lock:
        if _worker_started:
            return
        thread = threading.Thread(target=_worker_loop, name="posthog-mirror", daemon=True)
        thread.start()
        _worker_started = True


def capture(event: str, properties: dict[str, Any], distinct_id: str = "anonymous") -> None:
    """Best-effort capture; never raises. Returns immediately, sends async."""
    if not settings.POSTHOG_SERVER_KEY:
        return
    _ensure_worker()
    try:
        _queue.put_nowait({"event": event, "properties": properties, "distinct_id": distinct_id})
    except queue.Full:
        logger.warning("PostHog mirror queue full; dropping event %s", event)

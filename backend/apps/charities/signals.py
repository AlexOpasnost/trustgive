"""Cache invalidation signals (per ADR-007)."""
from __future__ import annotations

import logging
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.charities.models import Charity
from apps.core.cdn import purge_charity

logger = logging.getLogger(__name__)

# Simple debounce — last purge timestamp per slug to avoid hammering Cloudflare during bulk ETL.
_last_purge_lock = threading.Lock()
_last_purge: dict[str, float] = {}
_DEBOUNCE_SECONDS = 60


@receiver(post_save, sender=Charity)
def purge_on_charity_save(sender, instance: Charity, **kwargs) -> None:
    import time

    now = time.monotonic()
    with _last_purge_lock:
        last = _last_purge.get(instance.slug, 0)
        if now - last < _DEBOUNCE_SECONDS:
            return
        _last_purge[instance.slug] = now

    try:
        purge_charity(instance.slug)
    except Exception:
        logger.exception("Cloudflare purge failed for slug %s", instance.slug)

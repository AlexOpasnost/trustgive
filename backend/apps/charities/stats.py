"""Catalogue-wide counts, read from the catalogue.

Why this exists
---------------
On 2026-08-02 the homepage told visitors "540+ verified charities across 27
countries" in its meta description — the text Google shows in search results —
and "370 organisations across 27 countries" in the hero. The catalogue held 370
organisations across **10** countries. Both numbers were written into the markup
when the catalogue was 541 records spanning 27 countries, and neither was
updated when the July audit removed everything that could not be verified.

For a product whose entire argument is "we don't state what we can't show you",
publishing an unverifiable number about itself is the worst possible defect —
and it is the same failure mode as the counters that under-reported the
catalogue ninefold (STRATEGY §0) and the four charities that carried other
organisations' registration numbers.

So the numbers are derived, never typed. If the catalogue shrinks again, the
homepage shrinks with it.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Max

from apps.charities.models import PUBLISHED, Charity


def catalogue_stats() -> dict[str, Any]:
    """Counts describing the published catalogue.

    `last_checked` is the most recent `updated_at` across published charities,
    which is what the nightly re-check touches — the same value the charity page
    shows as "re-checked". It is a date rather than a timestamp because the
    claim being made is "this catalogue was re-read on this day".
    """
    qs = Charity.objects.filter(**PUBLISHED)
    last_checked = qs.aggregate(latest=Max("updated_at"))["latest"]
    return {
        "charities": qs.count(),
        # `.distinct()` on a single column is a cheap DISTINCT in Postgres, and
        # counts only countries that actually have a published charity — the
        # figure a reader would arrive at by filtering the catalogue themselves.
        "countries": qs.values("country").distinct().count(),
        "last_checked": last_checked.date().isoformat() if last_checked else None,
    }

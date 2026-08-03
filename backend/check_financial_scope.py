"""Scope the round-revenue defect: who is affected and how checkable each case is.

Read-only. Splits the flagged rows by country and by whether the charity has a
filing date at all, because those decide what can be done about them: a US row
citing ProPublica can be checked against ProPublica; a UK row citing the Charity
Commission's accounts page cannot be re-derived automatically, since we never
stored the figure's currency or basis.

    .venv/Scripts/python.exe check_financial_scope.py
"""

from __future__ import annotations

import os
from collections import Counter
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trustgive.settings.development")
django.setup()

from apps.charities.models import Financial  # noqa: E402

ROUND_TO = Decimal("10000000")


def main() -> None:
    flagged = [
        row
        for row in Financial.objects.select_related("charity").all()
        if row.total_revenue_usd
        and row.total_revenue_usd > 0
        and row.total_revenue_usd % ROUND_TO == 0
    ]
    published = [r for r in flagged if r.charity.verification_status == "verified"]

    print(f"rows with round revenue        : {len(flagged)}")
    print(f"  on published charities       : {len(published)}")
    print(f"\nby country: {Counter(r.charity.country for r in published).most_common()}")
    print("by source label:")
    for label, n in Counter(r.source_label for r in published).most_common():
        print(f"   {n:>3}  {label}")
    no_date = [r for r in published if r.charity.last_filed_date is None]
    print(f"\ncharity has no last_filed_date at all : {len(no_date)}")
    for row in sorted(no_date, key=lambda r: r.charity.slug):
        print(f"   {row.charity.slug:<34} FY{row.year}  rev={row.total_revenue_usd}")

    # Does the charity's displayed headline figure equal the flagged row?
    same_as_headline = [r for r in published if r.charity.total_revenue_usd == r.total_revenue_usd]
    print(f"\nflagged figure is the one shown on the card/profile : {len(same_as_headline)}")


if __name__ == "__main__":
    main()

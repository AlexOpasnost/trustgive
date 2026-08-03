"""Is `last_filed_date` really the most recent period we hold?

Written after Compassion International turned up with last_filed_date=2019-06-30
while its financial_history carried a 2023 row — which would make any statement
about "how old the freshest filing is" wrong for that record. Read-only.

    .venv/Scripts/python.exe check_filed_date.py
"""

from __future__ import annotations

import os
from collections import Counter

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trustgive.settings.development")
django.setup()

from apps.charities.models import Charity  # noqa: E402

VERIFIED = "verified"


def main() -> None:
    pub = Charity.objects.filter(verification_status=VERIFIED).prefetch_related("financial_history")

    agree = 0
    disagree = []
    no_financials = 0
    no_date = 0

    for charity in pub:
        years = [f.year for f in charity.financial_history.all() if f.year]
        if charity.last_filed_date is None:
            no_date += 1
            continue
        if not years:
            no_financials += 1
            continue
        newest_year = max(years)
        if newest_year > charity.last_filed_date.year:
            disagree.append((charity.slug, charity.last_filed_date.isoformat(), newest_year))
        else:
            agree += 1

    total = pub.count()
    print(f"published charities            : {total}")
    print(f"  no last_filed_date           : {no_date}")
    print(f"  no financial rows            : {no_financials}")
    print(f"  last_filed_date is newest    : {agree}")
    print(f"  financial history is NEWER   : {len(disagree)}")
    if total:
        share = 100 * len(disagree) / total
        print(f"  → stale last_filed_date      : {share:.1f}% of the catalogue")

    print("\nworst gaps (financial year vs last_filed_date):")
    worst = sorted(disagree, key=lambda r: r[2] - int(r[1][:4]), reverse=True)[:15]
    for slug, filed, year in worst:
        print(f"  {slug:<38} last_filed={filed}  newest financial year={year}")

    print("\ngap size distribution (years):")
    gaps = Counter(row[2] - int(row[1][:4]) for row in disagree)
    for gap, n in sorted(gaps.items()):
        print(f"  +{gap} year(s): {n}")


if __name__ == "__main__":
    main()

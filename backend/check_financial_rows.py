"""Find Financial rows that cite a source which does not support them.

Trigger: compassion-international and donorschoose each carry a row labelled
"IRS Form 990, FY 2023 (ProPublica)" with revenue of exactly 1,100,000,000 and
190,000,000. ProPublica's newest filing with data for those EINs is FY2019 and
FY2022 respectively. A round number wearing a real citation is the signature of
seeded data, and it is the same defect class as the fabricated registration
numbers in DATA_INTEGRITY.md.

Read-only. Two heuristics, deliberately separate so the second doesn't hide
behind the first:

  A. year newer than the charity's own last_filed_date  — the source we cite
     cannot contain that period at all
  B. revenue that is an exact multiple of 10,000,000    — real Form 990 totals
     essentially never land on a round ten million

    .venv/Scripts/python.exe check_financial_rows.py
"""

from __future__ import annotations

import os
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trustgive.settings.development")
django.setup()

from apps.charities.models import Charity, Financial  # noqa: E402

ROUND_TO = Decimal("10000000")


def main() -> None:
    rows = Financial.objects.select_related("charity").all()
    total = rows.count()
    print(f"financial rows in database : {total}")

    newer_than_filing = []
    round_revenue = []

    for row in rows:
        charity: Charity = row.charity
        rev = row.total_revenue_usd
        if charity.last_filed_date and row.year and row.year > charity.last_filed_date.year:
            newer_than_filing.append(row)
        if rev and rev > 0 and rev % ROUND_TO == 0:
            round_revenue.append(row)

    print(f"\nA. year newer than the charity's last_filed_date : {len(newer_than_filing)}")
    for row in sorted(newer_than_filing, key=lambda r: r.charity.slug):
        print(
            f"   {row.charity.slug:<34} FY{row.year}  rev={row.total_revenue_usd}"
            f"  last_filed={row.charity.last_filed_date}"
        )

    print(f"\nB. revenue is an exact multiple of 10,000,000    : {len(round_revenue)}")
    for row in sorted(round_revenue, key=lambda r: -(r.total_revenue_usd or 0))[:40]:
        flag = "  <-- also A" if row in newer_than_filing else ""
        print(
            f"   {row.charity.slug:<34} FY{row.year}  rev={row.total_revenue_usd}"
            f"  status={row.charity.verification_status}{flag}"
        )

    both = {r.id for r in newer_than_filing} & {r.id for r in round_revenue}
    print(f"\nrows matching both heuristics : {len(both)}")

    # How many published charities are affected at all?
    affected = {
        r.charity.slug
        for r in newer_than_filing + round_revenue
        if r.charity.verification_status == "verified"
    }
    print(f"published charities touched   : {len(affected)}")
    for slug in sorted(affected):
        print(f"   {slug}")


if __name__ == "__main__":
    main()

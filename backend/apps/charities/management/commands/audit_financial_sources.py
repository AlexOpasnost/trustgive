"""Detect revenue figures that no cited source supports.

This is the control that Finding 8 (DATA_INTEGRITY.md) proved was missing: every
other check in this project watches identifiers and links, and none watched the
money column. 43 fabricated figures sat on published charities until someone
happened to look while writing something else.

Detection only. It never deletes, and that separation is deliberate — the flag
is a heuristic (an exact multiple of $10,000,000, the shape seeded data takes),
and a genuinely round figure on a newly ingested charity must not be destroyed by
a scheduled job at 02:00. Remediation stays with `strip_unsourced_financials`,
which re-checks each row against its source before touching anything.

Run nightly from the ETL workflow with --strict, so a new occurrence fails the
job loudly instead of accumulating quietly:

    python manage.py audit_financial_sources
    python manage.py audit_financial_sources --strict
"""

from __future__ import annotations

import sys
from collections import Counter
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from apps.charities.models import Charity, Financial, VerificationStatus

# See strip_unsourced_financials for why this shape is the signal.
ROUND_TO = Decimal("10000000")


class Command(BaseCommand):
    help = "Report revenue figures whose shape suggests they were never sourced."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit non-zero when anything is found (for CI / scheduled runs).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        strict: bool = options["strict"]

        rows = Financial.objects.select_related("charity").all()
        round_rows = [
            row
            for row in rows
            if row.total_revenue_usd
            and row.total_revenue_usd > 0
            and row.total_revenue_usd % ROUND_TO == 0
        ]
        # A figure attributed to a period the charity's own newest filing does
        # not reach cannot have come from that filing.
        ahead_of_filing = [
            row
            for row in rows
            if row.charity.last_filed_date
            and row.year
            and row.year > row.charity.last_filed_date.year
        ]

        flagged = {row.id: row for row in round_rows + ahead_of_filing}
        published = [
            row
            for row in flagged.values()
            if row.charity.verification_status == VerificationStatus.VERIFIED
        ]

        self.stdout.write(f"financial rows            : {rows.count()}")
        self.stdout.write(f"  round revenue           : {len(round_rows)}")
        self.stdout.write(f"  year ahead of filing    : {len(ahead_of_filing)}")
        self.stdout.write(f"  distinct flagged rows   : {len(flagged)}")
        self.stdout.write(f"  of those, published     : {len(published)}")

        if published:
            self.stdout.write("\nPublished charities showing an unsourced figure:")
            for row in sorted(published, key=lambda r: r.charity.slug):
                self.stdout.write(
                    f"  {row.charity.slug:<34} FY{row.year}  {row.total_revenue_usd}"
                    f"  ({row.source_label or 'no label'})"
                )
            by_country = Counter(row.charity.country for row in published)
            self.stdout.write(f"\nby country: {by_country.most_common()}")

        # Charities that display a revenue with no financial row behind it at all
        # — a different way for the money column to become unsourced.
        orphaned = [
            charity.slug
            for charity in Charity.objects.filter(
                verification_status=VerificationStatus.VERIFIED,
                total_revenue_usd__isnull=False,
            ).prefetch_related("financial_history")
            if not charity.financial_history.exists()
        ]
        if orphaned:
            self.stdout.write(f"\nRevenue shown with no financial row behind it: {len(orphaned)}")
            for slug in sorted(orphaned)[:20]:
                self.stdout.write(f"  {slug}")

        total_problems = len(published) + len(orphaned)
        if total_problems == 0:
            self.stdout.write(self.style.SUCCESS("\nNo unsourced revenue figures found."))
            return

        message = f"\n{total_problems} unsourced revenue figure(s) on published charities."
        if strict:
            self.stderr.write(self.style.ERROR(message))
            self.stderr.write(
                "Run `manage.py strip_unsourced_financials --dry-run` to see the fix."
            )
            sys.exit(1)
        self.stdout.write(self.style.WARNING(message))

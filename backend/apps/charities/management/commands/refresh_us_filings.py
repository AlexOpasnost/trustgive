"""Refresh US charities against ProPublica: real filing dates + latest financials.

Why this exists
---------------
Two distinct trust defects this fixes:

1. **Fabricated filing dates.** An earlier `fix_us_eins` stored
   `date(tax_prd_yr + 1, 1, 1)` as `last_filed_date`. That is not a filing date —
   it is a synthesised 1 January. 68 charities carried "2024-01-01" (and 3
   "2025-01-01") and the UI rendered it as a factual "Last filed" date. A site
   whose whole premise is "we link you to the real document" must not display a
   date that never happened.

2. **Staleness.** The catalogue was a one-time snapshot. Nothing re-checked it,
   so newly published Form 990s never landed and `is_stale` drifted out of sync
   with reality.

What it does
------------
For every US charity carrying an EIN, re-fetch ProPublica (free, no key) and:
  - set `last_filed_date` to the **real fiscal-period end** derived from the
    filing's `tax_prd` (YYYYMM -> last day of that month);
  - null the date when ProPublica exposes no usable period, instead of inventing
    day precision;
  - recompute `is_stale` honestly (period end older than 24 months);
  - refresh `total_revenue_usd`, `size_bucket` and the latest `Financial` row
    when a newer filing exists.

Curation-safe: never touches name/tagline/description/photo/bucket, and never
promotes verification status (promotion stays with `fix_us_eins`; demotion stays
with `audit_source_links`). Idempotent — safe to run on a schedule.

    python manage.py refresh_us_filings --dry-run
    python manage.py refresh_us_filings --only-fabricated --dry-run
    python manage.py refresh_us_filings
"""

from __future__ import annotations

import calendar
import json
import re
import time
import urllib.request
from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity, Financial

UA = "Mozilla/5.0 (compatible; TrustGiveAudit/1.0; +https://trustgive.org)"
PP_API = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
PP_ORG = "https://projects.propublica.org/nonprofits/organizations/{ein}"
STALE_DAYS = 730  # 24 months, matching the UI's stale-warning copy


def _fetch(ein: str) -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(PP_API.format(ein=ein), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.getcode() != 200:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _latest_filing(filings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Most recent filing that actually carries a revenue figure."""
    usable = [f for f in filings if f.get("totrevenue") or f.get("totrev2")]
    if not usable:
        return None
    return max(usable, key=lambda f: int(f.get("tax_prd_yr") or 0))


def _period_end(filing: dict[str, Any]) -> date | None:
    """Real fiscal-period end from ProPublica's `tax_prd` (YYYYMM).

    202312 -> 2023-12-31. Returns None when the field is absent or malformed —
    callers must leave `last_filed_date` null rather than synthesise one.
    """
    raw = str(filing.get("tax_prd") or "").strip()
    if not re.fullmatch(r"\d{6}", raw):
        return None
    year, month = int(raw[:4]), int(raw[4:])
    if not (1 <= month <= 12) or not (1900 <= year <= 2100):
        return None
    return date(year, month, calendar.monthrange(year, month)[1])


def _bucket_for(revenue: float) -> str:
    if revenue < 100_000:
        return "small"
    if revenue < 1_000_000:
        return "medium"
    return "large"


class Command(BaseCommand):
    help = "Refresh US charities from ProPublica: real filing dates + latest financials."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
        parser.add_argument(
            "--only-fabricated",
            action="store_true",
            help="Only touch rows whose last_filed_date is a synthetic 1-January placeholder.",
        )
        parser.add_argument("--limit", type=int, default=0, help="Process at most N charities.")
        parser.add_argument(
            "--sleep", type=float, default=0.2, help="Delay between ProPublica calls (politeness)."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry: bool = options["dry_run"]
        qs = Charity.objects.filter(country="US").order_by("slug")
        if options["only_fabricated"]:
            qs = qs.filter(last_filed_date__month=1, last_filed_date__day=1)
        if options["limit"]:
            qs = qs[: options["limit"]]

        charities = list(qs)
        self.stdout.write(f"Scanning {len(charities)} US charities ({'dry' if dry else 'apply'})…")

        date_fixed = fin_updated = newer_filing = unresolved = no_period = skipped = 0

        with transaction.atomic():
            for c in charities:
                ein = re.sub(r"\D", "", c.registration_id or "")
                if len(ein) != 9:
                    skipped += 1
                    continue

                payload = _fetch(ein)
                time.sleep(options["sleep"])
                if not payload:
                    unresolved += 1
                    self.stdout.write(f"[MISS]  {c.slug} -- EIN {ein} did not resolve")
                    continue

                filing = _latest_filing(payload.get("filings_with_data", []))
                if not filing:
                    # No filing with data. An invented date is worse than none.
                    if c.last_filed_date is not None:
                        no_period += 1
                        self.stdout.write(
                            f"[NULL]  {c.slug} -- no filing with data; clearing {c.last_filed_date}"
                        )
                        if not dry:
                            c.last_filed_date = None
                            c.is_stale = True
                            c.save(update_fields=["last_filed_date", "is_stale"])
                    continue

                period_end = _period_end(filing)
                year = int(filing.get("tax_prd_yr") or 0)
                revenue = filing.get("totrevenue") or filing.get("totrev2")
                exec_comp = filing.get("compnsatncurrofcr")

                fields: list[str] = []

                if period_end and c.last_filed_date != period_end:
                    was = c.last_filed_date
                    if was and was.month == 1 and was.day == 1:
                        date_fixed += 1
                        tag = "FIXED-FABRICATED"
                    else:
                        newer_filing += 1
                        tag = "NEWER"
                    self.stdout.write(f"[{tag}] {c.slug} -- {was} -> {period_end} (FY{year})")
                    c.last_filed_date = period_end
                    fields += ["last_filed_date"]
                elif not period_end and c.last_filed_date is not None:
                    no_period += 1
                    self.stdout.write(
                        f"[NULL]  {c.slug} -- tax_prd missing; clearing {c.last_filed_date}"
                    )
                    c.last_filed_date = None
                    fields += ["last_filed_date"]

                stale_now = (
                    True
                    if c.last_filed_date is None
                    else (date.today() - c.last_filed_date).days > STALE_DAYS
                )
                if c.is_stale != stale_now:
                    c.is_stale = stale_now
                    fields += ["is_stale"]

                if revenue is not None:
                    rev_dec = Decimal(str(revenue))
                    if c.total_revenue_usd != rev_dec:
                        c.total_revenue_usd = rev_dec
                        c.size_bucket = _bucket_for(float(revenue))
                        fields += ["total_revenue_usd", "size_bucket"]
                        fin_updated += 1

                # `updated_at` is auto_now, but Django does NOT refresh auto_now
                # fields unless they appear in update_fields. Without this the
                # serializer's data_freshness.last_synced_at — rendered in the UI
                # as "Re-checked by TrustGive {date}" — would keep showing the
                # original seed date while the row was in fact re-verified today.
                # A stale freshness stamp is worse than none on a trust site.
                # Bumped on every successful re-check, not just on change: the
                # stamp means "we looked at the registry on this date".
                if not dry:
                    fields.append("updated_at")
                    c.save(update_fields=list(dict.fromkeys(fields)))

                # Keep the Financial row in step with the newest filing.
                if year and revenue is not None and not dry:
                    Financial.objects.update_or_create(
                        charity=c,
                        year=year,
                        defaults={
                            "total_revenue_usd": Decimal(str(revenue)),
                            "top_executive_comp_usd": (
                                Decimal(str(exec_comp)) if exec_comp is not None else None
                            ),
                            "source_url": PP_ORG.format(ein=ein),
                            "source_label": f"IRS Form 990, FY {year} (ProPublica)",
                        },
                    )

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). "
                f"fabricated_dates_fixed={date_fixed} newer_filings={newer_filing} "
                f"financials_updated={fin_updated} cleared_to_null={no_period} "
                f"unresolved={unresolved} skipped_no_ein={skipped}"
            )
        )

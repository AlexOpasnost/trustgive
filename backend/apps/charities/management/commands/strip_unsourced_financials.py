"""Remove revenue figures the cited source does not support.

Why this exists
---------------
On 2026-08-03, 43 of 385 `Financial` rows — every one of them on a *published*
charity — carried a revenue that is an exact multiple of 10,000,000. Real Form
990 and Charity Commission totals essentially never land on a round ten million;
that shape is the signature of hand- or model-authored seed data, the same
defect class as the fabricated registration numbers in DATA_INTEGRITY.md §5.

Four were checked directly against the source they name, and none held up:

  catholic-relief-services   $1,100,000,000 "IRS Form 990, FY 2023 (ProPublica)"
                             → ProPublica has 0 filings with data for that EIN
  catholic-charities-usa     $240,000,000   same label, same result
  compassion-international   FY2023 row     → ProPublica's newest period is FY2019
  donorschoose               FY2023 row     → ProPublica's newest period is FY2022

A money figure that looks like it came from a government filing, cited to that
filing, where the filing does not exist, is the worst thing this catalogue can
publish. It is exactly what the product promises never to do.

What it does
------------
For each flagged row:

  * US charity with an EIN, and ProPublica has a filing for that fiscal year →
    replace the figure with the real one. This is a repair, not a deletion.
  * otherwise → delete the row. UK and self-published figures cannot be
    re-derived: we never stored the currency or the basis of the conversion, so
    there is nothing to check them against and no honest way to keep them.

Then the charity's headline `total_revenue_usd` and `size_bucket` are recomputed
from whatever rows survive, or nulled when none do. A charity is never demoted
here — its *registration* is still verified; only the money is unsourced, which
is precisely the distinction the profile's "What we didn't check" block draws.

    python manage.py strip_unsourced_financials --dry-run
    python manage.py strip_unsourced_financials
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity, Financial

UA = "TrustGive/1.0 (+https://trustgive.org; contact: hello@trustgive.org)"
PP_API = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"

# The fabrication signature. A genuine total landing on an exact ten million is
# possible but vanishingly rare; 43 of them in one catalogue is not.
ROUND_TO = Decimal("10000000")

THROTTLE_SECONDS = 1.0


def _bucket_for(revenue: Decimal) -> str:
    """Matches refresh_us_filings._bucket_for so the two can't disagree."""
    if revenue < 100_000:
        return "small"
    if revenue < 1_000_000:
        return "medium"
    return "large"


def _propublica(ein: str) -> tuple[str, dict[str, Any] | None]:
    """Ask ProPublica about an EIN, distinguishing "absent" from "couldn't ask".

    Returns ("ok", payload), ("missing", None) when ProPublica answers 404, or
    ("error", None) when the request itself failed.

    The distinction decides whether a row is deleted. Collapsing it — as the
    first version of this command did — means a timeout silently downgrades to
    "the source does not support this figure", and a transient network blip
    deletes data that was fine. Two consecutive dry runs disagreed by one row,
    which is how the flaw surfaced.
    """
    request = urllib.request.Request(PP_API.format(ein=ein), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return "ok", json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return ("missing", None) if exc.code == 404 else ("error", None)
    except (urllib.error.URLError, ValueError, TimeoutError):
        return "error", None


def _real_revenue_for_year(payload: dict[str, Any], year: int) -> Decimal | None:
    """ProPublica's own total for that fiscal year, if it has one."""
    for filing in payload.get("filings_with_data") or []:
        if filing.get("tax_prd_yr") == year and filing.get("totrevenue") is not None:
            return Decimal(str(filing["totrevenue"]))
    return None


class Command(BaseCommand):
    help = "Delete or repair revenue figures that the cited source does not support."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]

        flagged = [
            row
            for row in Financial.objects.select_related("charity").all()
            if row.total_revenue_usd
            and row.total_revenue_usd > 0
            and row.total_revenue_usd % ROUND_TO == 0
        ]
        mode = " (dry)" if dry_run else ""
        self.stdout.write(f"Flagged {len(flagged)} round-revenue rows{mode}…")

        repaired = deleted = headline_nulled = headline_updated = skipped = 0
        touched: set[str] = set()
        # Cache per EIN: several rows can belong to one charity.
        seen_ein: dict[str, tuple[str, dict[str, Any] | None]] = {}
        # Rows this run removes. Tracked explicitly because in --dry-run nothing
        # is actually deleted, and the recompute below would otherwise pick the
        # very row it just decided to drop — a preview that disagrees with the
        # real run is worse than no preview.
        dropped_ids: set[int] = set()
        repaired_values: dict[int, Decimal] = {}

        with transaction.atomic():
            for row in flagged:
                charity: Charity = row.charity
                touched.add(charity.slug)
                ein = (charity.registration_id or "").strip()

                real: Decimal | None = None
                unreachable = False
                if charity.country == "US" and ein.isdigit() and row.year:
                    if ein not in seen_ein:
                        seen_ein[ein] = _propublica(ein)
                        time.sleep(THROTTLE_SECONDS)
                    outcome, payload = seen_ein[ein]
                    if outcome == "ok" and payload:
                        real = _real_revenue_for_year(payload, row.year)
                    elif outcome == "error":
                        unreachable = True

                if unreachable:
                    # We could not ask, so we do not know. Leaving the row alone
                    # is the only safe answer: deleting on a failed request would
                    # destroy a figure that may well be sound.
                    self.stdout.write(
                        f"[SKIP]   {charity.slug} FY{row.year}: ProPublica unreachable, "
                        f"left untouched — re-run to resolve"
                    )
                    skipped += 1
                    touched.discard(charity.slug)
                elif real is not None:
                    self.stdout.write(
                        f"[REPAIR] {charity.slug} FY{row.year}: {row.total_revenue_usd} -> {real}"
                    )
                    repaired += 1
                    repaired_values[row.id] = real
                    if not dry_run:
                        row.total_revenue_usd = real
                        row.save(update_fields=["total_revenue_usd"])
                else:
                    self.stdout.write(
                        f"[DROP]   {charity.slug} FY{row.year}: {row.total_revenue_usd} "
                        f"({row.source_label or 'no label'}) — source does not support it"
                    )
                    deleted += 1
                    dropped_ids.add(row.id)
                    if not dry_run:
                        row.delete()

            # Recompute each touched charity's headline figure from what is left.
            for slug in sorted(touched):
                charity = Charity.objects.get(slug=slug)
                candidates = [
                    row
                    for row in Financial.objects.filter(
                        charity=charity, total_revenue_usd__isnull=False
                    ).order_by("-year")
                    if row.id not in dropped_ids
                ]
                for row in candidates:
                    # In --dry-run the repaired value isn't on the row yet.
                    if row.id in repaired_values:
                        row.total_revenue_usd = repaired_values[row.id]
                remaining = candidates[0] if candidates else None
                if remaining is None:
                    if charity.total_revenue_usd is not None:
                        self.stdout.write(f"[NULL]   {slug}: no sourced revenue left")
                        headline_nulled += 1
                        if not dry_run:
                            charity.total_revenue_usd = None
                            charity.size_bucket = ""
                            charity.save(update_fields=["total_revenue_usd", "size_bucket"])
                elif charity.total_revenue_usd != remaining.total_revenue_usd:
                    self.stdout.write(
                        f"[HEAD]   {slug}: {charity.total_revenue_usd} -> "
                        f"{remaining.total_revenue_usd} (FY{remaining.year})"
                    )
                    headline_updated += 1
                    if not dry_run:
                        charity.total_revenue_usd = remaining.total_revenue_usd
                        charity.size_bucket = _bucket_for(remaining.total_revenue_usd)
                        charity.save(update_fields=["total_revenue_usd", "size_bucket"])

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry_run else 'applied'}). "
                f"charities_touched={len(touched)} repaired={repaired} dropped={deleted} "
                f"skipped_unreachable={skipped} "
                f"headline_updated={headline_updated} headline_nulled={headline_nulled}"
            )
        )

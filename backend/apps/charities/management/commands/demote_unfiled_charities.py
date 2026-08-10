"""Remove the badge from charities that are registered but have never filed.

`/methodology` tells the reader that a verified charity "has filed financial
documents in the last 24 months". Four published US charities did not meet that
sentence: their EIN resolves, ProPublica returns the right legal name, and the
linked page opens — but it is a registry record, not a filing. The badge was
resting on the organisation existing.

That is a smaller defect than a wrong identifier and a real one all the same: it
is the site claiming something its own methodology says it does not claim.

What counts as "has filed" here is a filing **with data** — the same test every
other command in this project uses to decide a filing is worth citing. A filing
ProPublica lists without figures cannot support a financial claim, so it does not
lift a charity over the bar either.

Demotion only. Nothing is deleted: the row keeps its name, its prose, its photo
and its registry link, and returns to the catalogue the moment a filing appears
(the nightly `refresh_us_filings` will pick the date up, and promotion stays a
deliberate act as it is everywhere else).

A charity is left completely alone when ProPublica cannot be reached. "We could
not ask" is not "there are no filings" — the rule this project keeps relearning,
most recently in Finding 12.

    python manage.py demote_unfiled_charities --dry-run
    python manage.py demote_unfiled_charities
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity, VerificationStatus

UA = "Mozilla/5.0 (compatible; TrustGiveAudit/1.0; +https://trustgive.org)"
PP_API = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"


def _fetch(ein: str) -> tuple[dict[str, Any] | None, str | None]:
    """Return (payload, error). A transport failure is never reported as 'none'."""
    last: str | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(PP_API.format(ein=ein), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                # The registry answered, and it does not know this EIN at all.
                return None, "not on ProPublica"
            last = f"HTTP {exc.code}"
            time.sleep(2.0 * (attempt + 1))
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2.0 * (attempt + 1))
    return None, last


class Command(BaseCommand):
    help = "Demote published charities whose registry record carries no filing with data."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        dry: bool = options["dry_run"]

        # Candidates: published, and nothing on the row evidences a filing. The
        # date and the financial row are written by different commands, so both
        # have to be empty before the row is even worth a network call.
        candidates = [
            c
            for c in Charity.objects.filter(verification_status=VerificationStatus.VERIFIED)
            .order_by("country", "slug")
            .prefetch_related("financial_history")
            if c.last_filed_date is None and not c.financial_history.exists()
        ]

        non_us = [c for c in candidates if c.country != "US"]
        us = [c for c in candidates if c.country == "US"]

        self.stdout.write(
            f"Published rows with no evidence of a filing: {len(candidates)} "
            f"(US {len(us)}, other {len(non_us)})"
        )
        for c in non_us:
            self.stdout.write(
                f"[LEFT]  {c.slug} ({c.country}) -- no API to re-check this registry from here; "
                f"needs a manual decision"
            )

        demoted = unreachable = kept = 0
        with transaction.atomic():
            for c in us:
                ein = re.sub(r"\D", "", c.registration_id or "")
                if len(ein) != 9:
                    kept += 1
                    self.stdout.write(f"[KEEP]  {c.slug} -- no usable EIN to re-check")
                    continue

                payload, err = _fetch(ein)
                time.sleep(0.4)

                if payload is None and err and err != "not on ProPublica":
                    unreachable += 1
                    self.stdout.write(
                        f"[RETRY] {c.slug} -- could not reach ProPublica ({err}); left verified"
                    )
                    continue

                with_data = len((payload or {}).get("filings_with_data") or [])
                without = len((payload or {}).get("filings_without_data") or [])
                if with_data:
                    kept += 1
                    self.stdout.write(
                        f"[KEEP]  {c.slug} -- {with_data} filing(s) with data after all; "
                        f"run refresh_us_filings to pull the date"
                    )
                    continue

                self.stdout.write(
                    f"[DEMOTE] {c.slug} ({ein}) -- 0 filings with data"
                    + (f", {without} without" if without else ", none of any kind")
                )
                demoted += 1
                if dry:
                    continue
                c.verification_status = VerificationStatus.LISTED
                # auto_now needs naming in update_fields, or the freshness stamp
                # keeps reporting the date before this ran (Finding 2).
                c.save(update_fields=["verification_status", "updated_at"])

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). demoted={demoted} kept={kept} "
                f"unreachable={unreachable} left_for_manual={len(non_us)}"
            )
        )

"""Audit every charity's source-document links and demote the unverifiable ones.

Background (v3.18 data-integrity pass): ~48% of the catalogue was seeded via
hand/AI-authored migrations whose registry identifiers were fabricated — the
"source document" links 404, and the financial figures attached to them are
therefore unverifiable. The brand promise is "every verified claim links to the
regulator's own file", so a charity whose source link is dead must not wear the
`verified` badge or display unverifiable financials.

This command tests each charity's source-document URLs against the live
registry and, per charity:

  * working ≥ 1 (at least one URL returns 200):
        keep the charity as-is; prune only the individual links that return a
        DEFINITIVE dead status (404/410). Ambiguous failures (timeout/5xx) are
        left alone — they may be transient.

  * working == 0, with a definitive 404/410 (proven-fake source):
        demote verification_status → listed, delete the dead SourceDocuments,
        null total_revenue_usd + program_expense_pct, and delete the Financial
        rows (their figures came from the fabricated filing).

  * working == 0, only ambiguous failures (all timeouts/5xx, no 200, no 404):
        demote verification_status → listed (safe, reversible), but DO NOT
        delete anything — flag it [REVIEW] instead, so a transient registry
        outage can never destroy possibly-real data.

The command is data-driven and re-runnable: once a charity is properly
re-sourced (a real working link added), the next run re-promotes nothing
automatically — promotion back to `verified` is left to the ingestion path —
but it will stop demoting it and stop pruning its now-working link.

Usage:
    python manage.py audit_source_links --dry-run            # preview only
    python manage.py audit_source_links                      # apply
    python manage.py audit_source_links --country=CA         # scope to one country
    python manage.py audit_source_links --workers=16 --retries=3
"""
from __future__ import annotations

import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity, SourceDocument, VerificationStatus

UA = "Mozilla/5.0 (compatible; TrustGiveAudit/1.0; +https://trustgive.org)"
DEFINITIVE_DEAD = {404, 410}


def _probe(url: str, *, retries: int, timeout: int) -> int | str:
    """Return the HTTP status of `url`, retrying transient failures.

    A 404/410 short-circuits (no point retrying a definitive miss). Any other
    failure is retried up to `retries` times before giving up as the last
    observed status ('ERR' for a network-level failure / timeout).
    """
    last: int | str = "ERR"
    for _ in range(max(1, retries)):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.getcode()
        except urllib.error.HTTPError as exc:  # noqa: PERF203 — retry loop is intentional
            if exc.code in DEFINITIVE_DEAD:
                return exc.code
            last = exc.code
        except Exception:  # network error / timeout
            last = "ERR"
    return last


class Command(BaseCommand):
    help = "Test charity source-document links; demote and clean the unverifiable ones."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
        parser.add_argument("--country", default="", help="Limit to a 2-letter country code.")
        parser.add_argument("--workers", type=int, default=12, help="Concurrent probe workers.")
        parser.add_argument("--retries", type=int, default=3, help="Retries per URL on transient failure.")
        parser.add_argument("--timeout", type=int, default=20, help="Per-request timeout (s).")

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]
        country: str = options["country"].upper()
        workers: int = options["workers"]
        retries: int = options["retries"]
        timeout: int = options["timeout"]

        qs = Charity.objects.prefetch_related("source_documents", "financial_history")
        if country:
            qs = qs.filter(country=country)
        charities = list(qs)

        # Probe every unique source URL once, concurrently. List (not set) so the
        # zip() below pairs each URL with its own result deterministically.
        urls = list({d.url for c in charities for d in c.source_documents.all() if d.url})
        self.stdout.write(f"Probing {len(urls)} unique source URLs across {len(charities)} charities…")
        status: dict[str, int | str] = {}
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for url, code in zip(
                urls, ex.map(lambda u: _probe(u, retries=retries, timeout=timeout), urls)
            ):
                status[url] = code

        demoted = pruned_docs = cleaned_financials = review = healthy = nodoc = 0

        with transaction.atomic():
            for c in charities:
                docs = list(c.source_documents.all())
                if not docs:
                    nodoc += 1
                    # No source at all → cannot be 'verified'. Demote only.
                    if c.verification_status == VerificationStatus.VERIFIED:
                        demoted += 1
                        if not dry_run:
                            c.verification_status = VerificationStatus.LISTED
                            c.save(update_fields=["verification_status"])
                        self.stdout.write(f"[DEMOTE] {c.slug} ({c.country}) — no source document")
                    continue

                working = [d for d in docs if status.get(d.url) == 200]
                dead = [d for d in docs if status.get(d.url) in DEFINITIVE_DEAD]
                ambiguous = [d for d in docs if d not in working and d not in dead]

                if working:
                    healthy += 1
                    # Prune only individually-dead links; keep working + ambiguous.
                    if dead:
                        pruned_docs += len(dead)
                        self.stdout.write(
                            f"[PRUNE]  {c.slug} ({c.country}) — {len(dead)} dead link(s), "
                            f"{len(working)} still working"
                        )
                        if not dry_run:
                            SourceDocument.objects.filter(id__in=[d.id for d in dead]).delete()
                    continue

                # No working source.
                if dead:
                    # Proven fake → full clean.
                    demoted += 1
                    cleaned_financials += c.financial_history.count()
                    pruned_docs += len(dead) + len(ambiguous)
                    self.stdout.write(
                        f"[CLEAN]  {c.slug} ({c.country}/{c.registration_id}) -- "
                        f"demote to listed, drop {len(docs)} doc(s), null financials"
                    )
                    if not dry_run:
                        c.source_documents.all().delete()
                        c.financial_history.all().delete()
                        c.verification_status = VerificationStatus.LISTED
                        c.total_revenue_usd = None
                        c.program_expense_pct = None
                        # The curated methodology_note typically opens with
                        # "Verified: …" — that contradicts a demoted charity, so
                        # blank it (the detail page hides an empty methodology).
                        c.methodology_note = {"en": "", "ru": ""}
                        c.save(
                            update_fields=[
                                "verification_status",
                                "total_revenue_usd",
                                "program_expense_pct",
                                "methodology_note",
                            ]
                        )
                else:
                    # Only timeouts/5xx — could be a transient registry outage.
                    # Demote the badge (safe) but DESTROY NOTHING.
                    review += 1
                    if c.verification_status == VerificationStatus.VERIFIED:
                        demoted += 1
                        if not dry_run:
                            c.verification_status = VerificationStatus.LISTED
                            c.save(update_fields=["verification_status"])
                    self.stdout.write(
                        f"[REVIEW] {c.slug} ({c.country}) — {len(ambiguous)} link(s) "
                        f"unreachable (not a 404); demoted, kept data for manual check"
                    )

            if dry_run:
                transaction.set_rollback(True)

        verb = "would" if dry_run else "did"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({verb} apply). healthy={healthy} demoted={demoted} "
                f"docs_pruned={pruned_docs} financials_cleaned={cleaned_financials} "
                f"manual_review={review} no_source={nodoc}"
            )
        )

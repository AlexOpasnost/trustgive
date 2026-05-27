"""Re-source US charities with a corrected, human-confirmed EIN.

Companion to `audit_source_links`. The audit demotes charities whose source
link is dead; this command *restores* the ones whose correct EIN we've
confirmed — it swaps in the real EIN and pulls genuine financials + a working
source document straight from ProPublica.

Curation-safe: it touches ONLY the verifiable fields (registration_id, revenue,
size bucket, last-filed date, verification_status, financial history, the IRS
990 source document). It never overwrites the curated name / tagline /
description / hero photo / bucket / cause tags.

Input is a JSON mapping of slug -> corrected EIN. Two shapes are accepted:
    {"hias": "135633307", "first-book": "521779606"}
    {"auto": [["hias", "135633307", "Hias Inc"], ...]}   # from the resolver

Each EIN is re-verified against ProPublica before anything is written — a
mapping row whose EIN doesn't return 200 is skipped, never applied.

Usage:
    python manage.py fix_us_eins --file=us_auto_eins.json --dry-run
    python manage.py fix_us_eins --file=us_auto_eins.json
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities.models import (
    Charity,
    DocumentKind,
    FileFormat,
    Financial,
    SourceDocument,
    VerificationStatus,
)

UA = "Mozilla/5.0 (compatible; TrustGiveAudit/1.0; +https://trustgive.org)"
PP_ORG = "https://projects.propublica.org/nonprofits/organizations/{ein}"
PP_API = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"


def _fetch(ein: str) -> dict[str, Any] | None:
    """Return ProPublica's org payload for `ein`, or None if it doesn't resolve."""
    try:
        req = urllib.request.Request(PP_API.format(ein=ein), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as resp:
            if resp.getcode() != 200:
                return None
            return json.load(resp)
    except Exception:
        return None


def _latest_filing(filings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Most recent filing that actually carries a revenue figure."""
    usable = [f for f in filings if f.get("totrevenue") or f.get("totrev2")]
    if not usable:
        return None
    return max(usable, key=lambda f: int(f.get("tax_prd_yr") or 0))


def _bucket_for(revenue: float) -> str:
    if revenue < 100_000:
        return "small"
    if revenue < 1_000_000:
        return "medium"
    return "large"


def _load_mapping(path: str) -> dict[str, str]:
    raw = json.load(open(path, encoding="utf-8"))
    if isinstance(raw, dict) and "auto" in raw:
        return {row[0]: re.sub(r"\D", "", str(row[1])) for row in raw["auto"]}
    if isinstance(raw, dict):
        return {k: re.sub(r"\D", "", str(v)) for k, v in raw.items()}
    raise CommandError("Mapping file must be a dict {slug: ein} or {'auto': [[slug, ein, ...]]}.")


class Command(BaseCommand):
    help = "Apply confirmed corrected EINs to US charities and re-pull real financials."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True, help="JSON mapping slug -> corrected EIN.")
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        mapping = _load_mapping(options["file"])
        dry_run: bool = options["dry_run"]
        self.stdout.write(f"Loaded {len(mapping)} slug->EIN rows from {options['file']}")

        applied = skipped = no_filing = 0
        with transaction.atomic():
            for slug, ein in mapping.items():
                charity = Charity.objects.filter(slug=slug).first()
                if charity is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such charity")
                    continue

                # Guard: another charity already owns (US, ein) -> would violate
                # the uniq_country_registration constraint. Never merge silently.
                clash = (
                    Charity.objects.filter(country=charity.country, registration_id=ein)
                    .exclude(pk=charity.pk)
                    .first()
                )
                if clash is not None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- EIN {ein} already used by {clash.slug}")
                    continue

                payload = _fetch(ein)
                org = (payload or {}).get("organization") or {}
                if not org:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- EIN {ein} does not resolve on ProPublica")
                    continue

                filing = _latest_filing((payload or {}).get("filings_with_data", []))
                src_url = PP_ORG.format(ein=ein)

                if dry_run:
                    rev = (filing or {}).get("totrevenue") or (filing or {}).get("totrev2")
                    yr = (filing or {}).get("tax_prd_yr")
                    self.stdout.write(
                        f"[APPLY] {slug} -- EIN {charity.registration_id} -> {ein} "
                        f"({org.get('name', '?')}); FY{yr} revenue={rev}"
                    )
                    applied += 1
                    continue

                charity.registration_id = ein
                charity.verification_status = VerificationStatus.VERIFIED

                if filing:
                    year = int(filing.get("tax_prd_yr") or 0)
                    revenue = filing.get("totrevenue") or filing.get("totrev2")
                    exec_comp = filing.get("compnsatncurrofcr")
                    if revenue is not None:
                        charity.total_revenue_usd = Decimal(str(revenue))
                        charity.size_bucket = _bucket_for(float(revenue))
                    # Part IX 3-way split isn't reliable from ProPublica (see
                    # ingest_propublica H-002) -- leave pct NULL, never invent it.
                    charity.program_expense_pct = None
                    if year:
                        try:
                            charity.last_filed_date = date(year + 1, 1, 1)
                            charity.is_stale = (date.today() - charity.last_filed_date).days > 730
                        except ValueError:
                            pass
                    # Rebuild source-of-truth rows for this charity from scratch so
                    # no stale (fabricated-EIN) row survives.
                    charity.financial_history.all().delete()
                    if year:
                        Financial.objects.create(
                            charity=charity,
                            year=year,
                            total_revenue_usd=Decimal(str(revenue)) if revenue is not None else None,
                            top_executive_comp_usd=Decimal(str(exec_comp)) if exec_comp is not None else None,
                            source_url=src_url,
                            source_label=f"IRS Form 990, FY {year} (ProPublica)",
                        )
                    charity.source_documents.all().delete()
                    SourceDocument.objects.create(
                        charity=charity,
                        kind=DocumentKind.IRS_990,
                        filed_date=charity.last_filed_date,
                        label={
                            "en": f"IRS Form 990 ({year})" if year else "IRS Form 990",
                            "ru": f"Налоговая форма IRS 990 ({year})" if year else "Налоговая форма IRS 990",
                        },
                        url=src_url,
                        source_label="ProPublica Nonprofit Explorer",
                        file_format=FileFormat.PDF,
                    )
                else:
                    no_filing += 1
                    self.stdout.write(f"[WARN]  {slug} -- EIN {ein} resolves but has no revenue filing; link fixed, financials left empty")
                    charity.source_documents.all().delete()
                    SourceDocument.objects.create(
                        charity=charity,
                        kind=DocumentKind.IRS_990,
                        label={"en": "IRS Form 990", "ru": "Налоговая форма IRS 990"},
                        url=src_url,
                        source_label="ProPublica Nonprofit Explorer",
                        file_format=FileFormat.PDF,
                    )

                charity.save()
                applied += 1
                self.stdout.write(f"[APPLY] {slug} -- EIN -> {ein} ({org.get('name', '?')})")

            if dry_run:
                transaction.set_rollback(True)

        verb = "would apply" if dry_run else "applied"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {verb}={applied} skipped={skipped} no_filing={no_filing}"
            )
        )

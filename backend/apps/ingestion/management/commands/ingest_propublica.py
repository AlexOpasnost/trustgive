"""Ingest US charities from ProPublica Nonprofit Explorer API v2 (per ADR-004).

Usage:
    python manage.py ingest_propublica --ein=271661997
    python manage.py ingest_propublica --bootstrap --limit=1000
    python manage.py ingest_propublica --since=24h
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import sentry_sdk
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.charities.blocklist import is_blocked
from apps.charities.models import (
    Charity,
    Country,
    DocumentKind,
    FileFormat,
    IngestionSource,
    SizeBucket,
    SourceDocument,
    VerificationStatus,
)
from apps.charities.models import Financial
from apps.ingestion.http import ThrottledHTTPClient
from apps.ingestion.models import IngestionLog, IngestionStatus, SourceMapping

logger = logging.getLogger(__name__)


def _bucket_for(revenue: float | None) -> str:
    if revenue is None:
        return ""
    if revenue < 100_000:
        return SizeBucket.SMALL
    if revenue < 1_000_000:
        return SizeBucket.MEDIUM
    return SizeBucket.LARGE


def _slug_base(name: str, ein: str) -> str:
    base = slugify(name)[:180] or f"charity-{ein}"
    return base


def _hash_record(record: dict[str, Any]) -> bytes:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).digest()


def _filing_for_charity(filings: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not filings:
        return None
    return max(filings, key=lambda f: f.get("tax_prd_yr", 0) or 0)


class Command(BaseCommand):
    help = "Ingest US charities from ProPublica Nonprofit Explorer API v2."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--ein", help="Single EIN to ingest (digits only)")
        parser.add_argument("--bootstrap", action="store_true", help="Initial bulk load")
        parser.add_argument("--limit", type=int, default=1000)
        parser.add_argument(
            "--since",
            help="Window for delta sync, e.g. '24h', '7d'. Ignored with --ein or --bootstrap.",
            default="24h",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        ein = options.get("ein")
        client = ThrottledHTTPClient(settings.PROPUBLICA_API_BASE, requests_per_sec=5)

        log = IngestionLog.objects.create(source=IngestionSource.PROPUBLICA, status=IngestionStatus.RUNNING)

        try:
            if ein:
                self._ingest_one(client, ein, log)
            elif options["bootstrap"]:
                self._ingest_bootstrap(client, options["limit"], log)
            else:
                self._ingest_delta(client, options["since"], log)
        except Exception as exc:
            log.status = IngestionStatus.FAILED
            log.errors.append({"error_class": type(exc).__name__, "message": str(exc)[:500]})
            sentry_sdk.capture_exception(exc)
            log.save(update_fields=["status", "errors"])
            self.stderr.write(self.style.ERROR(f"Ingestion failed: {exc}"))
            raise

        if not log.errors:
            log.status = IngestionStatus.SUCCEEDED
        elif log.records_upserted > 0:
            log.status = IngestionStatus.PARTIAL
            sentry_sdk.add_breadcrumb(category="ingestion", message=f"Partial: {len(log.errors)} errors")
        else:
            log.status = IngestionStatus.FAILED

        log.finished_at = datetime.now(timezone.utc)
        log.save(update_fields=["status", "finished_at", "records_seen", "records_upserted", "records_skipped", "errors"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: status={log.status} seen={log.records_seen} upserted={log.records_upserted} "
                f"skipped={log.records_skipped} errors={len(log.errors)}"
            )
        )

    # --- Modes ---

    def _ingest_one(self, client: ThrottledHTTPClient, ein: str, log: IngestionLog) -> None:
        ein_clean = re.sub(r"\D", "", ein)
        try:
            data = client.get(f"organizations/{ein_clean}.json")
        except Exception as exc:
            log.errors.append({"ein": ein_clean, "error_class": type(exc).__name__, "message": str(exc)[:500]})
            log.records_seen = 1
            return
        log.raw_payload = {"source_url": f"organizations/{ein_clean}.json", "sample": data}
        log.records_seen = 1
        self._process_record(data, log)

    def _ingest_bootstrap(self, client: ThrottledHTTPClient, limit: int, log: IngestionLog) -> None:
        # Bootstrap strategy: paginate the search endpoint sorted by revenue desc.
        # ProPublica's `/search.json` supports `c_code[id]=3` (501c3), `state[id]`, etc.
        # For MVP we just hit the index and process top-N.
        page = 0
        processed = 0
        while processed < limit:
            try:
                data = client.get("search.json", params={"page": page, "c_code[id]": 3})
            except Exception as exc:
                log.errors.append({"page": page, "error_class": type(exc).__name__, "message": str(exc)[:500]})
                break
            orgs = data.get("organizations", [])
            if not orgs:
                break
            for org in orgs:
                if processed >= limit:
                    break
                ein_clean = str(org.get("ein", "")).zfill(9)
                try:
                    detail = client.get(f"organizations/{ein_clean}.json")
                except Exception as exc:
                    log.errors.append({"ein": ein_clean, "error_class": type(exc).__name__, "message": str(exc)[:300]})
                    log.records_skipped += 1
                    continue
                log.records_seen += 1
                processed += 1
                self._process_record(detail, log)
            page += 1

    def _ingest_delta(self, client: ThrottledHTTPClient, since: str, log: IngestionLog) -> None:
        # ProPublica doesn't have an "updated since" param — bootstrap-style hit with smaller limit.
        # In practice nightly delta = re-process top 5K orgs; raw_data_hash short-circuit elides identical re-imports.
        match = re.match(r"^(\d+)([hd])$", since.lower())
        if match:
            window_seconds = int(match.group(1)) * (3600 if match.group(2) == "h" else 86400)
        else:
            window_seconds = 86400
        logger.info("Delta sync window: %ds (note: ProPublica has no updated-since; using hash-shortcircuit)", window_seconds)
        self._ingest_bootstrap(client, limit=5000, log=log)

    # --- Per-record processing ---

    def _process_record(self, data: dict[str, Any], log: IngestionLog) -> None:
        org = data.get("organization") or {}
        if not org:
            log.errors.append({"error_class": "ParseError", "message": "Missing 'organization' key"})
            log.records_skipped += 1
            return

        ein_clean = str(org.get("ein", "")).zfill(9)
        name = (org.get("name") or "").strip()
        if not name or not ein_clean:
            log.errors.append({"ein": ein_clean, "error_class": "ParseError", "message": "Missing name or EIN"})
            log.records_skipped += 1
            return

        # Legal compliance — never ingest blocked records (per blocklist.py)
        block_reason = is_blocked(
            country=Country.US,
            registration_id=ein_clean,
            cause_tags=org.get("category_codes") or [],
            name=name,
            description=(org.get("description") or org.get("mission") or ""),
        )
        if block_reason is not None:
            logger.info("Skipping blocked record EIN=%s reason=%s", ein_clean, block_reason)
            log.records_skipped += 1
            return

        record_hash = _hash_record(org)

        try:
            with transaction.atomic():
                charity = self._find_or_create(name, ein_clean)
                mapping, created = SourceMapping.objects.select_for_update(skip_locked=True).get_or_create(
                    charity=charity,
                    source=IngestionSource.PROPUBLICA,
                    defaults={"source_id": ein_clean, "raw_data_hash": record_hash},
                )
                if not created and bytes(mapping.raw_data_hash) == record_hash:
                    log.records_skipped += 1
                    return  # short-circuit identical
                mapping.source_id = ein_clean
                mapping.raw_data_hash = record_hash
                mapping.save(update_fields=["source_id", "raw_data_hash", "last_synced_at"])

                self._update_charity_fields(charity, org)
                self._upsert_filings(charity, data.get("filings_with_data", []))
                log.records_upserted += 1
        except Exception as exc:
            log.errors.append({"ein": ein_clean, "error_class": type(exc).__name__, "message": str(exc)[:500]})
            log.records_skipped += 1
            logger.exception("Per-record ingestion failed for EIN %s", ein_clean)

    def _find_or_create(self, name: str, ein: str) -> Charity:
        # 1. Hard match
        existing = Charity.objects.filter(country=Country.US, registration_id=ein).first()
        if existing:
            return existing

        # 2. Fuzzy match (per ADR-004 tiered confidence)
        candidates = (
            Charity.objects.annotate(sim=TrigramSimilarity("name_trgm", name))
            .filter(country=Country.US, sim__gte=0.85)
            .order_by("-sim")
        )
        top = candidates.first()
        if top is not None and float(top.sim) >= 0.92:
            logger.info("Auto-merge: '%s' → existing %s (sim=%.3f)", name, top.slug, top.sim)
            return top
        if top is not None:
            logger.info("Flagged for review: '%s' candidate %s (sim=%.3f)", name, top.slug, top.sim)

        # 3. New
        slug = _slug_base(name, ein)
        if Charity.objects.filter(slug=slug).exists():
            slug = f"{slug}-{ein}"
        return Charity.objects.create(
            slug=slug,
            country=Country.US,
            registration_id=ein,
            ingestion_source=IngestionSource.PROPUBLICA,
            name={"en": name, "ru": ""},
            tagline={"en": "", "ru": ""},
            description={"en": "", "ru": ""},
            methodology_note={"en": "", "ru": ""},
        )

    def _update_charity_fields(self, charity: Charity, org: dict[str, Any]) -> None:
        name = (org.get("name") or "").strip()
        if name:
            current = dict(charity.name or {})
            current["en"] = name
            current.setdefault("ru", "")
            charity.name = current

        # Founded year (best-effort — ProPublica field varies)
        founded = org.get("ruling_date") or org.get("inception")
        if founded and isinstance(founded, str):
            try:
                charity.founded_year = int(founded[:4])
            except ValueError:
                pass

        charity.verification_status = VerificationStatus.VERIFIED
        charity.save()

    def _upsert_filings(self, charity: Charity, filings: list[dict[str, Any]]) -> None:
        # TODO H-002: ProPublica's filings_with_data JSON only reliably exposes
        # totrevenue and totfuncexpns at the line-item level. The Form 990 Part
        # IX 3-way split (program / admin / fundraising) requires either:
        #   (a) parsing Schedule O / the Part IX line items from the actual PDF
        #   (b) hitting IRS BMF e-file XML feeds and parsing line 25 columns
        #       (B) Program services, (C) Management & general, (D) Fundraising
        # Both are out of scope for the ProPublica-only ingest command.
        # CURATED charities populate the 3-way split MANUALLY via migration
        # 0008_seed_curated_charities.py — see also REVIEW H-002.
        # Previously this method mapped totasstend → admin and totliabend →
        # fundraising. totasstend is total ASSETS-end-of-year and totliabend is
        # total LIABILITIES-end-of-year — both balance-sheet figures, not Part
        # IX expense-statement figures. That bug shipped to prod (REVIEW H-002)
        # and was the cause of GiveDirectly's 56.8% "fundraising" red flag in
        # screenshots. Cleanup of bad rows handled by migration 0007 + 0008.
        if not filings:
            return
        latest = _filing_for_charity(filings)
        if not latest:
            return

        year = int(latest.get("tax_prd_yr") or latest.get("tax_period") or 0)
        if year == 0:
            return

        # Reliable from ProPublica filings_with_data:
        revenue = latest.get("totrevenue") or latest.get("totrev2")
        # Total functional expenses (program + admin + fundraising combined).
        # Useful for sanity-check and program_expense_pct denominator
        # alternative, but does NOT give us the 3-way split.
        total_expenses = latest.get("totfuncexpns")
        # Executive compensation — ProPublica exposes the Part VII total of
        # current officer/director/key-employee compensation directly:
        exec_comp = latest.get("compnsatncurrofcr")

        Financial.objects.update_or_create(
            charity=charity,
            year=year,
            defaults={
                "total_revenue_usd": Decimal(str(revenue)) if revenue is not None else None,
                # 3-way Part IX split intentionally NULL — see H-002 TODO above.
                # Curated charities (migration 0008) populate these manually.
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": (
                    Decimal(str(exec_comp)) if exec_comp is not None else None
                ),
                "source_url": f"https://projects.propublica.org/nonprofits/organizations/{charity.registration_id}",
                "source_label": f"IRS Form 990, FY {year} (ProPublica)",
            },
        )

        if revenue is not None:
            charity.total_revenue_usd = Decimal(str(revenue))
            charity.size_bucket = _bucket_for(float(revenue))
        # program_expense_pct cannot be derived from ProPublica alone (we'd
        # need the Part IX program-services line, not totfuncexpns). Leave
        # NULL on auto-ingest; curated rows set it explicitly. The frontend
        # CharityCard v2 right-anchor falls back to total_revenue_usd when
        # program_expense_pct is NULL (DESIGN.md v2.0 §A.2 / §F.4).
        charity.program_expense_pct = None

        # Approximate filing date as Jan 1 of year+1 if no specific date present
        try:
            charity.last_filed_date = date(year + 1, 1, 1)
            charity.is_stale = (date.today() - charity.last_filed_date).days > 730
        except ValueError:
            pass
        charity.save()

        # Source document
        SourceDocument.objects.update_or_create(
            charity=charity,
            kind=DocumentKind.IRS_990,
            filed_date=charity.last_filed_date,
            defaults={
                "label": {
                    "en": f"IRS Form 990 ({year})",
                    "ru": f"Налоговая форма IRS 990 ({year})",
                },
                "url": f"https://projects.propublica.org/nonprofits/organizations/{charity.registration_id}",
                "source_label": "ProPublica Nonprofit Explorer",
                "file_format": FileFormat.PDF,
            },
        )

"""Ingest US charities from ProPublica Nonprofit Explorer API v2 (per ADR-004).

Usage:
    python manage.py ingest_propublica --ein=271661997
    python manage.py ingest_propublica --bootstrap --limit=1000
    python manage.py ingest_propublica --since=24h
"""

from __future__ import annotations

import calendar
import hashlib
import json
import logging
import re
from datetime import UTC, date, datetime
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
    Financial,
    IngestionSource,
    SizeBucket,
    SourceDocument,
    VerificationStatus,
)
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


# Words that carry no identifying signal in a charity's legal name. Stripped
# before comparison so "Sea Shepherd Conservation Society" and "Sea Shepherd
# Conservation Society Inc" are the same organisation, while "Chesapeake Climate
# Action Network" and "Climate Action Network" stay different ones.
_NAME_NOISE = frozenset(
    """inc incorporated corp corporation co company the of and for a an in usa us
    america american national foundation fund trust association society institute
    org organization international global charitable charity center centre council
    group ltd llc services service""".split()
)


def _name_tokens(name: str) -> set[str]:
    name = re.sub(r"\(.*?\)", " ", name or "")
    # Apostrophes are deleted, not turned into a separator: registries write
    # "Cure Alzheimers Fund" where the charity writes "Cure Alzheimer's Fund", and
    # splitting on the apostrophe makes those two different words.
    name = name.replace("'", "").replace("’", "")
    name = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return {t for t in name.split() if t and t not in _NAME_NOISE and len(t) > 1}


def _names_match(catalogue_name: str, registry_name: str) -> bool:
    """Do these two names describe the same organisation?

    Equality of the identifying-token sets — not a substring test and not a
    subset test. Both of the looser tests were measured against real ProPublica
    search results on 2026-08-03 and both waved through wrong entities:
    "Chesapeake Climate Action Network" for *Climate Action Network*, and
    "Sickle Cell Disease Association Of America Michigan Chapter Inc" for the
    national body of the same name. An extra identifying word is usually a
    *different* organisation, so any surplus token is disqualifying.

    Returns False when either side has no identifying tokens — an unanswerable
    question is not a yes.

    **Known limit, by construction.** Where two distinct organisations reduce to
    the same identifying tokens ("Climate Action Network" vs "The US Climate
    Action Network"; "NeighborWorks America" vs "National NeighborWorks
    Association") no name comparison can separate them. That is why this gate
    only guards records ingested *from* the registry, whose name comes from the
    registry itself, and why re-pointing an existing curated row at a new
    identifier stays a reviewed step in `fix_us_eins` rather than an automatic
    one. See `apps/ingestion/tests/test_propublica_evidence.py`.
    """
    a, b = _name_tokens(catalogue_name), _name_tokens(registry_name)
    if not a or not b:
        return False
    return a == b


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


def _period_end(filing: dict[str, Any]) -> date | None:
    """Real fiscal-period end from ProPublica's `tax_prd` (YYYYMM).

    202312 -> 2023-12-31. Returns None when the field is missing or malformed, so
    callers store null rather than inventing day precision.

    This mirrors `refresh_us_filings._period_end` deliberately. The two used to
    disagree: this module stored `date(tax_prd_yr + 1, 1, 1)`, which put a
    fabricated "2024-01-01" on 71 charities and rendered it to users as a factual
    "Last filed" date (DATA_INTEGRITY.md Finding 1). That finding was fixed in the
    repair commands but not here, so every fresh ingest re-introduced it.
    """
    raw = str(filing.get("tax_prd") or "").strip()
    if not re.fullmatch(r"\d{6}", raw):
        return None
    year, month = int(raw[:4]), int(raw[4:])
    if not (1 <= month <= 12) or not (1900 <= year <= 2100):
        return None
    return date(year, month, calendar.monthrange(year, month)[1])


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

        log = IngestionLog.objects.create(
            source=IngestionSource.PROPUBLICA, status=IngestionStatus.RUNNING
        )

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
            sentry_sdk.add_breadcrumb(
                category="ingestion", message=f"Partial: {len(log.errors)} errors"
            )
        else:
            log.status = IngestionStatus.FAILED

        log.finished_at = datetime.now(UTC)
        log.save(
            update_fields=[
                "status",
                "finished_at",
                "records_seen",
                "records_upserted",
                "records_skipped",
                "errors",
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: status={log.status} seen={log.records_seen} "
                f"upserted={log.records_upserted} "
                f"skipped={log.records_skipped} errors={len(log.errors)}"
            )
        )

    # --- Modes ---

    def _ingest_one(self, client: ThrottledHTTPClient, ein: str, log: IngestionLog) -> None:
        ein_clean = re.sub(r"\D", "", ein)
        try:
            data = client.get(f"organizations/{ein_clean}.json")
        except Exception as exc:
            log.errors.append(
                {"ein": ein_clean, "error_class": type(exc).__name__, "message": str(exc)[:500]}
            )
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
                log.errors.append(
                    {"page": page, "error_class": type(exc).__name__, "message": str(exc)[:500]}
                )
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
                    log.errors.append(
                        {
                            "ein": ein_clean,
                            "error_class": type(exc).__name__,
                            "message": str(exc)[:300],
                        }
                    )
                    log.records_skipped += 1
                    continue
                log.records_seen += 1
                processed += 1
                self._process_record(detail, log)
            page += 1

    def _ingest_delta(self, client: ThrottledHTTPClient, since: str, log: IngestionLog) -> None:
        # ProPublica has no "updated since" param — this is a bootstrap-style hit
        # with a smaller limit. In practice the nightly delta re-processes the top
        # 5K orgs; the raw_data_hash short-circuit elides identical re-imports.
        match = re.match(r"^(\d+)([hd])$", since.lower())
        if match:
            window_seconds = int(match.group(1)) * (3600 if match.group(2) == "h" else 86400)
        else:
            window_seconds = 86400
        logger.info(
            "Delta sync window: %ds (ProPublica has no updated-since; "
            "relying on the hash short-circuit)",
            window_seconds,
        )
        self._ingest_bootstrap(client, limit=5000, log=log)

    # --- Per-record processing ---

    def _process_record(self, data: dict[str, Any], log: IngestionLog) -> None:
        org = data.get("organization") or {}
        if not org:
            log.errors.append(
                {"error_class": "ParseError", "message": "Missing 'organization' key"}
            )
            log.records_skipped += 1
            return

        ein_clean = str(org.get("ein", "")).zfill(9)
        name = (org.get("name") or "").strip()
        if not name or not ein_clean:
            log.errors.append(
                {"ein": ein_clean, "error_class": "ParseError", "message": "Missing name or EIN"}
            )
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
                mapping, created = SourceMapping.objects.select_for_update(
                    skip_locked=True
                ).get_or_create(
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
                has_evidence = self._upsert_filings(charity, data.get("filings_with_data", []))
                self._set_verification(
                    charity,
                    org_name=name,
                    trade_name=(org.get("sort_name") or "").strip(),
                    has_evidence=has_evidence,
                )
                log.records_upserted += 1
        except Exception as exc:
            log.errors.append(
                {"ein": ein_clean, "error_class": type(exc).__name__, "message": str(exc)[:500]}
            )
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

        charity.save()

    def _set_verification(
        self, charity: Charity, *, org_name: str, trade_name: str, has_evidence: bool
    ) -> None:
        """Promote to verified only when the record can prove itself.

        Two conditions, both required, matching the published methodology:
          * ProPublica exposes a filing with real financial data, and
          * a name it returns describes the charity we are stamping.

        Either of the registry's two names counts. The IRS holds a legal name and
        a trade name, and for a good number of charities the recognisable one is
        the trade name: EIN 03-0355315 is legally "Us Working Group Inc" and
        publicly Forest Stewardship Council US; 52-1886511 is legally "Rape Abuse
        And Incest National Network Inc" and publicly RAINN. Matching only the
        legal name would reject the registry's own answer about its own entity.

        Neither condition is optional. This method used to be a single
        unconditional `verification_status = VERIFIED` executed before the filings
        were even read, so an EIN that merely *resolved* — with zero filings, or
        belonging to a different organisation entirely — earned the badge. That is
        the defect class behind DATA_INTEGRITY.md Findings 3, 6 and 7: a resolving
        identifier is not evidence.

        Demotion is never done here; that stays with `audit_source_links`, which
        can tell a dead link from an unreachable one.
        """
        catalogue_name = (charity.name or {}).get("en") or ""
        name_matches = _names_match(catalogue_name, org_name) or _names_match(
            catalogue_name, trade_name
        )
        if has_evidence and name_matches:
            charity.verification_status = VerificationStatus.VERIFIED
            charity.save(update_fields=["verification_status", "updated_at"])
            return
        if charity.verification_status != VerificationStatus.VERIFIED:
            return
        logger.info(
            "Leaving %s at its existing status: has_evidence=%s name_match=%s (%r vs %r / %r)",
            charity.slug,
            has_evidence,
            name_matches,
            catalogue_name,
            org_name,
            trade_name,
        )

    def _upsert_filings(self, charity: Charity, filings: list[dict[str, Any]]) -> bool:
        """Return True when a filing carrying real financial data was stored."""
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
            return False
        # Only a filing that actually carries a revenue figure can support the
        # badge — "has a filing" and "has a filing with data" are different
        # claims, and the published methodology makes the second one.
        with_data = [f for f in filings if f.get("totrevenue") or f.get("totrev2")]
        if not with_data:
            return False
        latest = _filing_for_charity(with_data)
        if not latest:
            return False

        year = int(latest.get("tax_prd_yr") or latest.get("tax_period") or 0)
        if year == 0:
            return False

        # Reliable from ProPublica filings_with_data:
        revenue = latest.get("totrevenue") or latest.get("totrev2")
        # ProPublica also exposes `totfuncexpns` (program + admin + fundraising
        # combined), but not the 3-way split we'd need to show where the money
        # goes — so it is deliberately not stored rather than read and dropped.
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

        # The real fiscal-period end, read from the filing's `tax_prd`. Null when
        # the source doesn't carry one — see `_period_end` for why this must never
        # be synthesised.
        period_end = _period_end(latest)
        charity.last_filed_date = period_end
        charity.is_stale = True if period_end is None else (date.today() - period_end).days > 730
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
        return True

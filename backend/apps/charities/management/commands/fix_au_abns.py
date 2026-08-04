"""Re-source Australian charities with a confirmed ABN + ACNC/ABR registry link.

Companion to fix_us_eins, for AU. Input: JSON {slug: ABN}. Sets the real ABN as
registration_id, marks verified, and attaches a working ABR (Australian Business
Register) source document. Curation-safe: never touches name/tagline/description/
photo. The ACNC register doesn't expose per-charity revenue, so financials are
left as-is.

What the ABR page has to say before anything is written
-------------------------------------------------------
Three things, read out of the page body:

1. the ABN is in the register at all;
2. one of the names it lists is the charity we are stamping;
3. the entity is **registered as a charity with the ACNC**.

(3) is not redundant with (1): an ABN is issued to any business, so "the ABN
exists" is not the claim the badge makes.

This command used to accept an ABN whenever the ABR page returned HTTP 200.
Measured 2026-08-04: that URL answers **200 for fabricated ABNs too** —
99999999999, 12345678901 and 00000000000 all return an 8,777-byte "not found"
body with status 200. So the check proved nothing, exactly like the CRA check
that Finding 6 disabled, except this one had already promoted 16 live rows. They
were re-audited on content and all 16 held up, but that was luck in the input,
not the check doing its job.

    python manage.py fix_au_abns --file=au_abns.json --dry-run
    python manage.py fix_au_abns --file=au_abns.json
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities.models import (
    Charity,
    DocumentKind,
    FileFormat,
    SourceDocument,
    VerificationStatus,
)

UA = "Mozilla/5.0 (compatible; TrustGiveAudit/1.0; +https://trustgive.org)"
ABR = "https://abr.business.gov.au/ABN/View?abn={abn}"

# Labels the ABR record page puts in front of a name it holds for the entity.
_NAME_LABELS = ("entity name", "business name", "trading name", "main name")

_NAME_NOISE = frozenset(
    """inc incorporated corp ltd limited pty the of and for a an in australia
    australian au national foundation fund trust trustee association society
    institute org organisation organization international global charitable
    charity centre center council services service""".split()
)


def _tokens(name: str) -> set[str]:
    name = re.sub(r"\(.*?\)", " ", name or "")
    name = name.replace("'", "").replace("’", "")
    name = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return {t for t in name.split() if t and t not in _NAME_NOISE and len(t) > 1}


def _names_match(catalogue_name: str, registry_name: str) -> bool:
    """Does this registry name describe the catalogue entry?

    Equality of identifying-token sets, the same rule the US ingest uses. What
    absorbs the Australian legal-entity noise is the stop-word list, not a loose
    threshold: "The Trustee for MATER FOUNDATION" and "Mater Foundation" both
    reduce to {mater}, and "ROYAL FLYING DOCTOR SERVICE OF AUSTRALIA" and "Royal
    Flying Doctor Service" both to {royal, flying, doctor}.

    A partial-overlap threshold was tried first and had to go: at half the
    catalogue's words it accepted "BOWEL CANCER AUSTRALIA" for the Australian
    Cancer Research Foundation, and "THE WALTER & ELIZA HALL CHARITABLE
    FOUNDATION LIMITED" for the Walter and Eliza Hall *Institute* — a real pair of
    distinct entities sharing a benefactor's name. A surplus identifying word
    means a different organisation often enough that it has to disqualify.

    The caller checks every name the register lists for the ABN — entity name,
    business names, trading names — and accepts if any one of them matches, which
    is what lets a familiar trading name stand in for an opaque legal one.
    """
    cat, reg = _tokens(catalogue_name), _tokens(registry_name)
    if not cat or not reg:
        return False
    return cat == reg


def _abr_record(abn: str) -> tuple[list[str], bool, str | None]:
    """Return (names the register lists, is-an-ACNC-charity, error).

    An error means we could not read the page — never that the ABN is absent.
    """
    last: str | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(ABR.format(abn=abn), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as resp:
                html = resp.read().decode("utf-8", "replace")
                break
        except urllib.error.HTTPError as exc:
            return [], False, f"HTTP {exc.code}"
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2.0 * (attempt + 1))
    else:
        return [], False, last

    text = re.sub(r"<[^>]+>", "\n", html)
    text = text.replace("&amp;", "&").replace("&#39;", "'").replace("&nbsp;", " ")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    names: list[str] = []
    for i, line in enumerate(lines):
        if line.lower().rstrip(":").strip() in _NAME_LABELS:
            for nxt in lines[i + 1 : i + 4]:
                if len(nxt) > 2 and not nxt.lower().startswith(("abn", "from", "to ")):
                    names.append(nxt)
                    break
    acnc = "registered as a charity" in " ".join(lines).lower()
    return names, acnc, None


class Command(BaseCommand):
    help = "Apply confirmed AU ABNs + ABR registry source links; mark verified."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        mapping = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(mapping, dict):
            raise CommandError("Mapping file must be {slug: ABN}.")
        dry = options["dry_run"]
        applied = skipped = unreachable = 0
        with transaction.atomic():
            for slug, abn in mapping.items():
                abn = re.sub(r"\D", "", str(abn))
                c = Charity.objects.filter(slug=slug, country="AU").first()
                if c is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such AU charity")
                    continue
                names, acnc, err = _abr_record(abn)
                if err:
                    skipped += 1
                    unreachable += 1
                    self.stdout.write(
                        f"[RETRY] {slug} -- could not read the ABR record for {abn} ({err}); "
                        f"left unchanged, re-run to apply"
                    )
                    continue
                if not names:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- ABN {abn} is not in the register")
                    continue
                catalogue_name = (c.name or {}).get("en") or ""
                matched = next((n for n in names if _names_match(catalogue_name, n)), None)
                if matched is None:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- ABN {abn} belongs to {names!r}, "
                        f"not to {catalogue_name!r}"
                    )
                    continue
                if not acnc:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- {abn} ({matched}) holds an ABN but the register "
                        f"does not show it registered as a charity with the ACNC"
                    )
                    continue
                clash = (
                    Charity.objects.filter(country="AU", registration_id=abn)
                    .exclude(pk=c.pk)
                    .first()
                )
                if clash is not None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- ABN {abn} already used by {clash.slug}")
                    continue
                self.stdout.write(
                    f"[APPLY] {slug} -- ABN -> {abn}, verified against {matched!r} "
                    f"(ACNC-registered), ABR source"
                )
                applied += 1
                if dry:
                    continue
                c.registration_id = abn
                c.verification_status = VerificationStatus.VERIFIED
                c.source_documents.all().delete()
                SourceDocument.objects.create(
                    charity=c,
                    kind=DocumentKind.STATE,
                    label={
                        "en": "ACNC charity register (ABR record)",
                        "ru": "Реестр благотворительных организаций ACNC (запись ABR)",
                    },
                    url=ABR.format(abn=abn),
                    source_label="Australian Business Register / ACNC",
                    file_format=FileFormat.HTML,
                )
                c.save(update_fields=["registration_id", "verification_status"])
            if dry:
                transaction.set_rollback(True)
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). applied={applied} "
                f"skipped={skipped} unreachable={unreachable}"
            )
        )
        if unreachable:
            self.stdout.write(
                self.style.WARNING(
                    f"{unreachable} row(s) were left unchanged because the ABR could not be "
                    f"read, not because their ABN is wrong. Re-run to finish them."
                )
            )

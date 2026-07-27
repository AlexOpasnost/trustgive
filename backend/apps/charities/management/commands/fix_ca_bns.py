"""Re-source Canadian charities with a confirmed CRA Business Number (BN) + registry link.

Companion to fix_us_eins / fix_au_abns, for Canada. Input: JSON {slug: BN}
confirmed against the CRA "List of charities" register. Sets the real BN as
registration_id, marks verified, and attaches a working CRA registry source
document. Curation-safe: never touches name/tagline/description/photo.

CRA's public register exposes a stable per-charity page keyed by the BN
(9 digits + "RR" + 4 digits, e.g. 119304855RR0001) that returns 200:
    https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/rgstrdChrtsInf?charityId={bn}
The command HEAD-checks that URL at apply time and skips any BN that doesn't
resolve — so a mistyped/guessed BN can never land a dead "source" link (the
v3.18 lesson: verify identifiers against the live source at write time).

CRA's T3010 financials aren't exposed on this per-charity URL, so financials are
left as-is (the detail page hides the money section when there's no figure).

    python manage.py fix_ca_bns --file=ca_bns.json --dry-run
    python manage.py fix_ca_bns --file=ca_bns.json
"""
from __future__ import annotations

import json
import re
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
CRA = "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/rgstrdChrtsInf?charityId={bn}"
BN_RE = re.compile(r"^\d{9}RR\d{4}$")


def _normalise_bn(raw: str) -> str:
    """Uppercase + strip spaces/hyphens. CRA BN = 9 digits + 'RR' + 4 digits."""
    return re.sub(r"[\s-]", "", str(raw)).upper()


def _cra_alive(bn: str) -> bool:
    """DISABLED — this check was unsound and is kept only to document why.

    The original implementation accepted any BN whose CRA URL returned HTTP 200.
    Verified 2026-07-27: that URL is an Angular shell which returns an **identical
    200 response (55,230 bytes) for every input**, including deliberately
    fabricated business numbers such as 999999999RR0001. The check therefore
    proved nothing and would have stamped "Verified" on invented identifiers.

    Worse, the same URL renders **HTTP 500 / "We're having a problem with that
    page"** in a real browser, so it is not a usable source document either: the
    charity page would have linked donors to an error screen.

    Canada needs a genuine evidence source before any of this can run — see the
    module docstring. Failing closed until then.
    """
    return False


class Command(BaseCommand):
    help = "Apply confirmed CA Business Numbers + CRA registry source links; mark verified."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        raise CommandError(
            "fix_ca_bns is disabled: its CRA verification was unsound.\n"
            "  * https://apps.cra-arc.gc.ca/.../rgstrdChrtsInf?charityId=<BN> returns an\n"
            "    identical HTTP 200 Angular shell for EVERY input, including fabricated\n"
            "    BNs — so a 200 was never evidence the charity exists.\n"
            "  * The same URL renders HTTP 500 in a browser, so it cannot serve as the\n"
            "    public source document either.\n"
            "Re-enable only after wiring a real evidence source (CRA 'List of charities'\n"
            "open data on open.canada.ca) AND a per-charity URL that actually resolves.\n"
            "See DATA_INTEGRITY.md."
        )
        mapping = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(mapping, dict):
            raise CommandError("Mapping file must be {slug: BN}.")
        dry = options["dry_run"]
        applied = skipped = 0
        with transaction.atomic():
            for slug, raw_bn in mapping.items():
                bn = _normalise_bn(raw_bn)
                if not BN_RE.match(bn):
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- '{raw_bn}' is not a valid CRA BN (9 digits + RRnnnn)")
                    continue
                c = Charity.objects.filter(slug=slug, country="CA").first()
                if c is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such CA charity")
                    continue
                if not _cra_alive(bn):
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- CRA {bn} did not return 200")
                    continue
                clash = (
                    Charity.objects.filter(country="CA", registration_id=bn)
                    .exclude(pk=c.pk).first()
                )
                if clash is not None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- BN {bn} already used by {clash.slug}")
                    continue
                self.stdout.write(f"[APPLY] {slug} -- BN -> {bn}, verified, CRA source")
                applied += 1
                if dry:
                    continue
                c.registration_id = bn
                c.verification_status = VerificationStatus.VERIFIED
                c.source_documents.all().delete()
                SourceDocument.objects.create(
                    charity=c,
                    kind=DocumentKind.STATE,
                    label={
                        "en": "CRA List of charities (registry record)",
                        "ru": "Реестр благотворительных организаций CRA (запись реестра)",
                    },
                    url=CRA.format(bn=bn),
                    source_label="Canada Revenue Agency — List of charities",
                    file_format=FileFormat.HTML,
                )
                c.save(update_fields=["registration_id", "verification_status"])
            if dry:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f"\nDone ({'dry' if dry else 'applied'}). applied={applied} skipped={skipped}"
        ))

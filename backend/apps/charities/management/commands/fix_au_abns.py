"""Re-source Australian charities with a confirmed ABN + ACNC/ABR registry link.

Companion to fix_us_eins, for AU. Input: JSON {slug: ABN} confirmed against the
ACNC Register (matched by website domain). Sets the real ABN as registration_id,
marks verified, and attaches a working ABR (Australian Business Register) source
document. Curation-safe: never touches name/tagline/description/photo. The ACNC
register doesn't expose per-charity revenue, so financials are left as-is.

    python manage.py fix_au_abns --file=au_abns.json --dry-run
    python manage.py fix_au_abns --file=au_abns.json
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
ABR = "https://abr.business.gov.au/ABN/View?abn={abn}"


def _abr_alive(abn: str) -> bool:
    try:
        req = urllib.request.Request(ABR.format(abn=abn), headers={"User-Agent": UA})
        return urllib.request.urlopen(req, timeout=25).getcode() == 200
    except Exception:
        return False


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
        applied = skipped = 0
        with transaction.atomic():
            for slug, abn in mapping.items():
                abn = re.sub(r"\D", "", str(abn))
                c = Charity.objects.filter(slug=slug, country="AU").first()
                if c is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such AU charity")
                    continue
                if not _abr_alive(abn):
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- ABR {abn} did not return 200")
                    continue
                clash = (
                    Charity.objects.filter(country="AU", registration_id=abn)
                    .exclude(pk=c.pk).first()
                )
                if clash is not None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- ABN {abn} already used by {clash.slug}")
                    continue
                self.stdout.write(f"[APPLY] {slug} -- ABN -> {abn}, verified, ABR source")
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
        self.stdout.write(self.style.SUCCESS(
            f"\nDone ({'dry' if dry else 'applied'}). applied={applied} skipped={skipped}"
        ))

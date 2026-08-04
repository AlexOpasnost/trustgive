"""Re-source New Zealand charities with a confirmed CC number + Charities Register link.

Companion to fix_us_eins / fix_au_abns, for NZ. Input: JSON {slug: CC number}.
Sets the number as registration_id, marks verified, and attaches the Charities
Register record as the source document. Curation-safe: never touches name /
tagline / description / photo. The register's per-charity page does not expose a
revenue figure in a form worth storing, so financials are left as-is.

What the register has to say first
----------------------------------
`https://register.charities.govt.nz/Charity/{cc}` returns **HTTP 200 for
anything** — CC99999999, ZZ12345 and a real number all answer 200. So, as with
the CRA (Finding 6) and the ABR (Finding 10), the status code is not evidence.

It is server-rendered, though, and a real record carries three labelled fields
that the not-found body does not. All three are required here:

  * *Legal name of the Charity* — and it has to be this charity;
  * *Registration number* — and it has to be the number we asked for, which is
    what catches a page that quietly fell back to a search form;
  * *Current Status* — and it has to be **Registered**. New Zealand deregisters
    charities that stop filing, and the register keeps serving their page. A
    deregistered record is a real document about a real organisation that is no
    longer a registered charity, which is not what the badge claims.

That last check is not hypothetical: `world-vision-nz` carried CC36358, which the
register answers with a *deregistered* St Vincent de Paul branch.

    python manage.py fix_nz_ccnumbers --file=nz_ccs.json --dry-run
    python manage.py fix_nz_ccnumbers --file=nz_ccs.json
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
REGISTER = "https://register.charities.govt.nz/Charity/{cc}"
CC_RE = re.compile(r"^CC\d{5,8}$")

_NAME_NOISE = frozenset(
    """inc incorporated corp ltd limited the of and for a an in nz zealand new
    aotearoa national foundation fund trust board association society institute
    org organisation organization international global charitable charity centre
    center council services service""".split()
)


def _tokens(name: str) -> set[str]:
    name = name.replace("'", "").replace("’", "").replace("&", " and ")
    name = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return {t for t in name.split() if t and t not in _NAME_NOISE and len(t) > 1}


def _name_forms(catalogue_name: str) -> list[set[str]]:
    """Token sets the catalogue entry may legitimately be known by.

    Catalogue names here often carry the legal name in brackets — "Forest & Bird
    (Royal Forest and Bird Protection Society of NZ)". The short form and the
    bracketed form are both this organisation, and the register holds the long
    one, so both are offered for comparison rather than one being thrown away.
    """
    raw = catalogue_name or ""
    forms = [raw, re.sub(r"\(.*?\)", " ", raw)]
    forms += re.findall(r"\((.*?)\)", raw)
    return [t for t in (_tokens(f) for f in forms) if t]


def _names_match(catalogue_name: str, registry_name: str) -> bool:
    """Equality of identifying-token sets against any form of the catalogue name.

    Same rule as the US and AU gates. Partial overlap is deliberately not
    accepted: the numbers this command exists to replace pointed at *Ashburton
    Seniors Centre Trust* and a St Vincent de Paul branch, and the way to keep
    those out is to require the registry's answer to be this organisation and
    nothing else.
    """
    reg = _tokens(registry_name)
    if not reg:
        return False
    return any(form == reg for form in _name_forms(catalogue_name))


def _register_record(cc: str) -> tuple[dict[str, str], str | None]:
    """Return (fields read off the register page, error).

    An error means the page could not be read — never that the charity is absent.
    """
    last: str | None = None
    html: str | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(REGISTER.format(cc=cc), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                html = resp.read().decode("utf-8", "replace")
                break
        except urllib.error.HTTPError as exc:
            return {}, f"HTTP {exc.code}"
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2.0 * (attempt + 1))
    if html is None:
        return {}, last

    body = re.sub(r"(?s)<script.*?</script>", " ", html)
    body = re.sub(r"(?s)<style.*?</style>", " ", body)
    text = re.sub(r"<[^>]+>", "\n", body)
    text = text.replace("&amp;", "&").replace("&#39;", "'").replace("&nbsp;", " ")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    wanted = {
        "legal name of the charity": "legal_name",
        "registration number": "number",
        "current status": "status",
    }
    found: dict[str, str] = {}
    for i, line in enumerate(lines):
        key = wanted.get(line.lower().rstrip(":").strip())
        if key and key not in found:
            for nxt in lines[i + 1 : i + 3]:
                if len(nxt) > 1:
                    found[key] = nxt
                    break
    return found, None


class Command(BaseCommand):
    help = "Apply confirmed NZ CC numbers + Charities Register source links; mark verified."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True, help="JSON mapping slug -> CC number.")
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        mapping = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(mapping, dict):
            raise CommandError("Mapping file must be {slug: CC number}.")
        dry: bool = options["dry_run"]
        applied = skipped = unreachable = 0

        with transaction.atomic():
            for slug, raw in mapping.items():
                cc = re.sub(r"[\s-]", "", str(raw)).upper()
                if not CC_RE.match(cc):
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- '{raw}' is not a CC number")
                    continue

                charity = Charity.objects.filter(slug=slug, country="NZ").first()
                if charity is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such NZ charity")
                    continue

                record, err = _register_record(cc)
                if err:
                    skipped += 1
                    unreachable += 1
                    self.stdout.write(
                        f"[RETRY] {slug} -- could not read the register for {cc} ({err}); "
                        f"left unchanged, re-run to apply"
                    )
                    continue

                legal = record.get("legal_name")
                if not legal:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {cc} is not in the register")
                    continue
                if (record.get("number") or "").upper() != cc:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- the page for {cc} reports registration number "
                        f"{record.get('number')!r}"
                    )
                    continue

                catalogue_name = (charity.name or {}).get("en") or ""
                if not _names_match(catalogue_name, legal):
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- {cc} is registered to {legal!r}, "
                        f"not to {catalogue_name!r}"
                    )
                    continue

                status = (record.get("status") or "").strip()
                if status.lower() != "registered":
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- {cc} ({legal}) has status {status!r}, not 'Registered'"
                    )
                    continue

                clash = (
                    Charity.objects.filter(country="NZ", registration_id=cc)
                    .exclude(pk=charity.pk)
                    .first()
                )
                if clash is not None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {cc} already used by {clash.slug}")
                    continue

                self.stdout.write(
                    f"[APPLY] {slug} -- {cc}, registered to {legal!r}, status {status}"
                )
                applied += 1
                if dry:
                    continue

                charity.registration_id = cc
                charity.verification_status = VerificationStatus.VERIFIED
                charity.source_documents.all().delete()
                SourceDocument.objects.create(
                    charity=charity,
                    kind=DocumentKind.STATE,
                    label={
                        "en": "Charities Register record (Charities Services)",
                        "ru": "Запись реестра благотворительных организаций (Charities Services)",
                    },
                    url=REGISTER.format(cc=cc),
                    source_label="Charities Services — New Zealand Charities Register",
                    file_format=FileFormat.HTML,
                )
                charity.save(update_fields=["registration_id", "verification_status", "updated_at"])

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
                    f"{unreachable} row(s) were left unchanged because the register could not "
                    f"be read, not because their number is wrong. Re-run to finish them."
                )
            )

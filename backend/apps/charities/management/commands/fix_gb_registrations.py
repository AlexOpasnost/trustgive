"""Repoint or demote a UK charity whose stored registration number is wrong.

Companion to `fix_nz_ccnumbers` / `fix_au_abns` / `fix_us_eins`, for England and
Wales, and the first of them that can also *demote*: three of the five rows it
was written for held another organisation's number while published, and two held
a registration the Commission has since removed.

Every action is stated in the input file together with what the row is expected
to contain now, and the command refuses to act when the database has moved under
the evidence. Both verbs then have to earn their write against the **live**
register (`apps.charities.uk_register`), not against whatever screening produced
the file:

* `repoint` — the new number must come back from the register as that number,
  with status *Registered*, and its name must equal the catalogue name under the
  identifying-token rule. Anything less and the row is left exactly as it is.
* `demote` — the stored number must be confirmed to be *either* another
  organisation's *or* no longer registered, by reading the register for that
  number twice: once in its default scope (registered charities) and once with
  the removed charities included. A number that comes back Registered under this
  charity's own name is not demoted, whatever the file says.

The register being unreachable is reported and never acted on. That distinction
— "the source said no" against "we could not ask" — is the one this project has
had to relearn five times, and a demotion is the most expensive place to get it
wrong.

    python manage.py fix_gb_registrations --file=gb_registration_fixes.json --dry-run
    python manage.py fix_gb_registrations --file=gb_registration_fixes.json
"""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities import uk_register
from apps.charities.models import (
    Charity,
    DocumentKind,
    FileFormat,
    SourceDocument,
    VerificationStatus,
)

ACTIONS = ("repoint", "verify", "demote")


class Command(BaseCommand):
    help = "Correct or demote GB rows whose registration number the register disowns."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True, help="JSON list of intended actions.")
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        rows = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(rows, list):
            raise CommandError("File must be a JSON list of actions.")
        dry: bool = options["dry_run"]
        applied = skipped = unreachable = 0

        with transaction.atomic():
            for row in rows:
                slug = row.get("slug")
                action = row.get("action")
                expect = row.get("expect_current")
                why = row.get("why")
                if not slug or action not in ACTIONS or not expect or not why:
                    raise CommandError(
                        f"Row {row!r} needs slug, action in {ACTIONS}, expect_current and why. "
                        f"The reason is required: changing a published claim has to leave a "
                        f"record of who said so."
                    )

                charity = Charity.objects.filter(slug=slug, country="GB").first()
                if charity is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such GB charity")
                    continue
                if (charity.registration_id or "") != str(expect):
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- stores {charity.registration_id!r}, "
                        f"expected {expect!r}; the evidence is about a different row now"
                    )
                    continue

                catalogue_name = (charity.name or {}).get("en") or ""
                if action == "verify":
                    # Same gate as a repoint, aimed at the number already stored.
                    # This is how a row demoted by a defect that no longer exists
                    # comes back: by passing the check, not by being un-hidden.
                    row = {**row, "new": expect}
                handler = self._demote if action == "demote" else self._repoint
                verdict, write, message = handler(charity, catalogue_name, row)

                if verdict == "unreachable":
                    skipped += 1
                    unreachable += 1
                    self.stdout.write(f"[RETRY] {slug} -- {message}; left unchanged")
                    continue
                if verdict == "skip":
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {message}")
                    continue

                self.stdout.write(f"[{action.upper():7}] {slug} -- {message}")
                applied += 1
                if not dry:
                    write()

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
                    f"be read, not because the evidence failed. Re-run to finish them."
                )
            )

    # ------------------------------------------------------------------ verbs

    def _repoint(self, charity: Charity, catalogue_name: str, row: dict) -> tuple[str, Any, str]:
        new = str(row.get("new") or "").strip()
        if not new.isdigit():
            return "skip", None, f"{new!r} is not a charity number"

        verdict, record, note = uk_register.lookup_number(new)
        if verdict == "unknown":
            return "unreachable", None, f"could not read the register for {new} ({note})"
        if verdict == "absent":
            return "skip", None, note
        if record["status"].strip().lower() != "registered":
            return "skip", None, f"{new} has status {record['status']!r}, not 'Registered'"
        matched = uk_register.names_match(catalogue_name, [record["name"]])
        if not matched:
            return (
                "skip",
                None,
                (f"{new} is registered to {record['name']!r}, not to {catalogue_name!r}"),
            )

        clash = (
            Charity.objects.filter(country="GB", registration_id=new).exclude(pk=charity.pk).first()
        )
        if clash is not None:
            return "skip", None, f"{new} is already used by {clash.slug}"

        def write() -> None:
            charity.registration_id = new
            charity.verification_status = VerificationStatus.VERIFIED
            charity.source_documents.all().delete()
            SourceDocument.objects.create(
                charity=charity,
                kind=DocumentKind.CHARITY_COMMISSION,
                label={
                    "en": "Charity Commission register record",
                    "ru": "Запись реестра Charity Commission",
                },
                url=uk_register.CHARITY_URL.format(number=new),
                source_label="Charity Commission for England and Wales",
                file_format=FileFormat.HTML,
            )
            charity.save(update_fields=["registration_id", "verification_status", "updated_at"])

        moved = "" if str(row.get("expect_current")) == new else f"{row.get('expect_current')} -> "
        return (
            "apply",
            write,
            (
                f"{moved}{new}, registered to {record['name']!r}, "
                f"status {record['status']}, income {record['income']}"
            ),
        )

    def _demote(self, charity: Charity, catalogue_name: str, row: dict) -> tuple[str, Any, str]:
        stored = str(charity.registration_id)

        verdict, current, note = uk_register.lookup_number(stored)
        if verdict == "unknown":
            return "unreachable", None, f"could not read the register for {stored} ({note})"
        if current is not None and current["status"].strip().lower() == "registered":
            if uk_register.names_match(catalogue_name, [current["name"]]):
                # The file says this row is wrong and the register says it is
                # right. The register wins; a demotion needs the source to agree.
                return (
                    "skip",
                    None,
                    (f"{stored} is a live registration of {current['name']!r} — nothing to demote"),
                )
            reason = f"{stored} is registered to {current['name']!r}, not to {catalogue_name!r}"
        else:
            verdict, gone, note = uk_register.lookup_number(stored, status="removed")
            if verdict == "unknown":
                return (
                    "unreachable",
                    None,
                    (f"could not read the removed-charity register for {stored} ({note})"),
                )
            if verdict == "absent":
                return (
                    "skip",
                    None,
                    (
                        f"{note}, and none as removed either — a number the register does not "
                        f"hold is a question about the number, not grounds to unpublish the "
                        f"charity. Clear the number instead."
                    ),
                )
            reason = f"{stored} is {gone['name']!r}, status {gone['status']}"

        if charity.verification_status != VerificationStatus.VERIFIED:
            return "skip", None, f"already unpublished ({charity.verification_status})"

        def write() -> None:
            charity.verification_status = VerificationStatus.LISTED
            charity.save(update_fields=["verification_status", "updated_at"])

        return "apply", write, f"{reason}; {row.get('why')}"

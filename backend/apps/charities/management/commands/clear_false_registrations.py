"""Remove a registration number that the registry says belongs to someone else.

Every other command in this directory *writes* an identifier once it has been
confirmed. This one is the inverse, and it exists because until migration 0059
there was no way to perform it: `registration_id` was NOT NULL inside the
`(country, registration_id)` unique constraint, so "unknown" had to be spelled
`""`, which is a value and collides. Exactly one row per country could hold it.

That is why four New Zealand charities (DATA_INTEGRITY Finding 11) and
twenty-two Canadian ones (Finding 7) were left displaying a government
identifier belonging to a different organisation — the defect was known, written
up, and structurally unfixable.

Input is a JSON list of `{"slug": ..., "country": ..., "expect": ..., "why": ...}`.
`expect` is required and must match what is stored: this command deletes a fact,
so it refuses to act on a row that has already changed under it. Nothing else is
touched — no status change, no document deleted. A charity whose number is
removed is simply one whose registration is unknown, which for these rows is the
true state.

    python manage.py clear_false_registrations --file=nz_false_regs.json --dry-run
    python manage.py clear_false_registrations --file=nz_false_regs.json
"""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities.models import Charity, VerificationStatus


class Command(BaseCommand):
    help = "Clear registration numbers confirmed to belong to another organisation."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True, help="JSON list of rows to clear.")
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        rows = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(rows, list):
            raise CommandError("File must be a JSON list of {slug, country, expect, why}.")
        dry: bool = options["dry_run"]
        cleared = skipped = 0

        with transaction.atomic():
            for row in rows:
                slug = row.get("slug")
                expect = row.get("expect")
                why = row.get("why") or ""
                if not slug or not expect or not why:
                    raise CommandError(
                        f"Row {row!r} needs slug, expect and why. The reason is required: "
                        f"deleting a stored fact has to leave a record of who said so."
                    )

                charity = Charity.objects.filter(slug=slug, country=row.get("country")).first()
                if charity is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no such charity")
                    continue

                if charity.registration_id != expect:
                    # Refuse rather than clear: the row has moved since the
                    # evidence was gathered, so the evidence is about something
                    # else now.
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- stores {charity.registration_id!r}, "
                        f"expected {expect!r}; not clearing"
                    )
                    continue

                if charity.verification_status == VerificationStatus.VERIFIED:
                    # A published charity's badge rests on its document, and its
                    # number is printed beside it. Pulling the number out from
                    # under a live badge is a bigger decision than this command
                    # is allowed to make on its own.
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- is published; demote it first if the number is wrong"
                    )
                    continue

                self.stdout.write(f"[CLEAR] {slug} ({charity.country}) -- {expect!r}: {why}")
                cleared += 1
                if not dry:
                    charity.registration_id = None
                    charity.save(update_fields=["registration_id", "updated_at"])

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). cleared={cleared} skipped={skipped}"
            )
        )

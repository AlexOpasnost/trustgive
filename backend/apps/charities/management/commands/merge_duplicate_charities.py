"""Fold a duplicate catalogue row into the one that carries the evidence.

Four organisations are in the catalogue twice (DATA_INTEGRITY open item 6). Each
pair has the same shape: one row is verified and linked to a working regulator
document, the other is `listed`, holds an EIN that 404s, and has no documents at
all. Because `(country, registration_id)` is unique, the second copy can never be
verified — it would have to claim the identifier the first one already holds — so
it is not an unverified charity waiting to be confirmed. It is the same charity,
twice.

They cost more than tidiness. They inflate the unverified count, and they read as
missed work: a sweep of "hidden US rows that should be recoverable" picks them up
every time, and someone re-derives an EIN that is already in the catalogue.

What this does, per pair:

  * refuses if the row to drop carries any evidence — a source document or a
    financial row. Evidence is never deleted by a convenience command;
  * refuses if the row to drop is published, or if the row to keep is not;
  * copies across only what the surviving row is **missing** (hero photo and its
    credit/licence, logo, founded year, donation URL) and unions the cause tags.
    Curated prose on the survivor is never overwritten — it is what is live and
    what was reviewed;
  * deletes the duplicate.

The organisation stays in the catalogue throughout; only the second copy of it
goes.

    python manage.py merge_duplicate_charities --file=duplicates.json --dry-run
    python manage.py merge_duplicate_charities --file=duplicates.json
"""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities.models import Charity, VerificationStatus

# Fields worth rescuing from the copy being dropped, but only where the survivor
# has nothing. Photo credit and licence travel with the photo — a photo without
# its attribution is a licence breach, not a saving.
PHOTO_FIELDS = ("hero_photo_url", "hero_photo_credit", "hero_photo_license")
FILL_IF_EMPTY = ("logo_url", "donation_url", "founded_year")


class Command(BaseCommand):
    help = "Merge a duplicate charity row into the one holding the evidence, then delete it."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--file", required=True, help="JSON list of {keep, drop, why}.")
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")

    def handle(self, *args: Any, **options: Any) -> None:
        pairs = json.load(open(options["file"], encoding="utf-8"))
        if not isinstance(pairs, list):
            raise CommandError("File must be a JSON list of {keep, drop, why}.")
        dry: bool = options["dry_run"]
        merged = skipped = 0

        with transaction.atomic():
            for pair in pairs:
                keep_slug, drop_slug = pair.get("keep"), pair.get("drop")
                why = pair.get("why") or ""
                if not keep_slug or not drop_slug or not why:
                    raise CommandError(f"Row {pair!r} needs keep, drop and why.")

                keep = Charity.objects.filter(slug=keep_slug).first()
                drop = Charity.objects.filter(slug=drop_slug).first()
                if keep is None or drop is None:
                    skipped += 1
                    missing = keep_slug if keep is None else drop_slug
                    self.stdout.write(
                        f"[SKIP]  {keep_slug} <- {drop_slug} -- no such row: {missing}"
                    )
                    continue

                if keep.verification_status != VerificationStatus.VERIFIED:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {keep_slug} <- {drop_slug} -- the row to keep is not verified; "
                        f"merging into it would lose the pair's only evidence"
                    )
                    continue

                if drop.verification_status == VerificationStatus.VERIFIED:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {drop_slug} is published -- two published copies is a different "
                        f"problem, and not one to resolve by deleting either"
                    )
                    continue

                docs = drop.source_documents.count()
                fins = drop.financial_history.count()
                if docs or fins:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {drop_slug} carries evidence ({docs} document(s), "
                        f"{fins} financial row(s)); not deleting it from here"
                    )
                    continue

                moved: list[str] = []
                if not keep.hero_photo_url and drop.hero_photo_url:
                    for field in PHOTO_FIELDS:
                        setattr(keep, field, getattr(drop, field))
                    moved.append("hero photo (+credit, licence)")
                for field in FILL_IF_EMPTY:
                    if not getattr(keep, field) and getattr(drop, field):
                        setattr(keep, field, getattr(drop, field))
                        moved.append(field)

                added_tags = [
                    t for t in (drop.cause_tags or []) if t not in (keep.cause_tags or [])
                ]
                if added_tags:
                    keep.cause_tags = list(keep.cause_tags or []) + added_tags
                    moved.append(f"cause tags {added_tags}")

                carried = ", ".join(moved) if moved else "nothing (the survivor had it all)"
                self.stdout.write(
                    f"[MERGE] {drop_slug} -> {keep_slug}: {why}\n        carried over: {carried}"
                )
                merged += 1
                if dry:
                    continue

                keep.save()
                drop.delete()

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). merged={merged} skipped={skipped}"
            )
        )

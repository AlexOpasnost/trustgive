"""Apply legal-compliance blocklist to already-loaded Charity records.

This is the cleanup pass — it deletes any record that matches the rules in
`apps/charities/blocklist.py`. ETL itself filters at ingest time so only old
records (pre-blocklist) or records that became blocked after a blocklist
update need this pass.

Usage:
    python manage.py apply_blocklist                # destructive
    python manage.py apply_blocklist --dry-run      # preview
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.blocklist import is_blocked
from apps.charities.models import Charity


class Command(BaseCommand):
    help = "Delete charities matching the legal-compliance blocklist."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without modifying the database.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]
        deleted = 0
        scanned = 0
        reasons: dict[str, int] = {}

        qs = Charity.objects.all().only(
            "id", "slug", "country", "registration_id", "cause_tags", "name", "description"
        )

        with transaction.atomic():
            for charity in qs.iterator(chunk_size=500):
                scanned += 1
                name_en = (charity.name or {}).get("en", "")
                desc_en = (charity.description or {}).get("en", "")
                reason = is_blocked(
                    country=charity.country,
                    registration_id=charity.registration_id,
                    cause_tags=list(charity.cause_tags or []),
                    name=name_en,
                    description=desc_en,
                )
                if reason is None:
                    continue

                deleted += 1
                reasons[reason.rule] = reasons.get(reason.rule, 0) + 1
                if dry_run:
                    self.stdout.write(
                        f"[DRY] would delete {charity.slug} ({charity.country}/{charity.registration_id}) — {reason}"
                    )
                else:
                    self.stdout.write(
                        f"deleting {charity.slug} ({charity.country}/{charity.registration_id}) — {reason}"
                    )
                    charity.delete()

            if dry_run:
                # Roll back the transaction
                transaction.set_rollback(True)

        verb = "would delete" if dry_run else "deleted"
        self.stdout.write(self.style.SUCCESS(
            f"\nScanned {scanned}; {verb} {deleted}. By rule: {reasons or '(none)'}"
        ))

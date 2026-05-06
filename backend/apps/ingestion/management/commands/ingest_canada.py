"""STUB — Canada Revenue Agency (CRA) charities ingestion.

Source: CRA "List of charities" open dataset, https://www.canada.ca/en/revenue-agency/services/charities-giving/list-charities/list-charities-other-qualified-donees.html
Coverage: ~85,000 registered charities. Free, public, no API key.

Full implementation should:
  - Download the CSV/XML registry (refreshed monthly by CRA)
  - For each row: BN (Business Number, 9 digits + RR0001 suffix) → Charity.registration_id
  - Parse charity name, address, fiscal year-end
  - Map "designation" field (Charitable Organization / Public Foundation / Private Foundation)
  - Apply blocklist (apps.charities.blocklist.is_blocked)
  - Use the same tiered fuzzy dedup pattern as ingest_propublica.py
  - Pull most recent T3010 (Registered Charity Information Return) for financials
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "STUB: Canada Revenue Agency charities (full implementation pending)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--bootstrap", action="store_true")
        parser.add_argument("--bn", help="Single BN to ingest (e.g. 119278482RR0001)")

    def handle(self, *args, **options) -> None:
        self.stdout.write(
            self.style.WARNING(
                "STUB — Canada CRA ingestion not yet implemented. "
                "Tracked in BACKEND.md §9 / DEVOPS pre-launch checklist."
            )
        )

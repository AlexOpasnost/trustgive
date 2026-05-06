"""STUB — Australian Charities and Not-for-profits Commission (ACNC) ingestion.

Source: ACNC Register of Charities open data, https://data.gov.au/data/dataset/acnc-register
Coverage: ~60,000 registered Australian charities. Free, CSV download, no API key.

Full implementation should:
  - Download the daily CSV (https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/...)
  - For each row: ABN (Australian Business Number) → Charity.registration_id
  - Parse charity name, charity_size, registration_status
  - Apply blocklist
  - Use tiered fuzzy dedup pattern
  - Pull AIS (Annual Information Statement) for financials
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "STUB: ACNC Australian charities (full implementation pending)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--bootstrap", action="store_true")
        parser.add_argument("--abn", help="Single ABN to ingest (11 digits)")

    def handle(self, *args, **options) -> None:
        self.stdout.write(
            self.style.WARNING(
                "STUB — ACNC ingestion not yet implemented. "
                "Tracked in BACKEND.md §9 / DEVOPS pre-launch checklist."
            )
        )

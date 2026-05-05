"""STUB — Every.org ingestion. Full implementation deferred (per Phase 3 brief).

Will mirror the structure of ingest_propublica.py:
- ThrottledHTTPClient at 1 req/sec
- Tiered dedup via pg_trgm
- Enriches existing Charity records (logos, descriptions, cause_tags from Every.org's 66-tag taxonomy)
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "STUB: Every.org Charity API ingestion (full implementation pending)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--bootstrap", action="store_true")
        parser.add_argument("--since", default="24h")

    def handle(self, *args, **options) -> None:
        self.stdout.write(
            self.style.WARNING(
                "STUB — Every.org ingestion not yet implemented. "
                "Full implementation tracked in BACKEND.md §9."
            )
        )

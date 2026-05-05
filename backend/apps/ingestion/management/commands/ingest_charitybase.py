"""STUB — CharityBase.uk ingestion. Full implementation deferred (per Phase 3 brief)."""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "STUB: CharityBase.uk ingestion (full implementation pending)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--bootstrap", action="store_true")
        parser.add_argument("--since", default="24h")

    def handle(self, *args, **options) -> None:
        self.stdout.write(
            self.style.WARNING(
                "STUB — CharityBase.uk ingestion not yet implemented. "
                "Full implementation tracked in BACKEND.md §9."
            )
        )

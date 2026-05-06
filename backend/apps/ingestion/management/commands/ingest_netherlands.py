"""STUB — Netherlands ANBI register ingestion.

Source: Belastingdienst ANBI register (publieke ANBI gegevens),
        https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/standaard_functies/prive/contact/rss_feeds/anbi
Coverage: ~45,000 ANBI-registered organizations. Free, RSS + bulk download.

Full implementation should:
  - Download the CSV/XML feed (refreshed periodically)
  - For each row: RSIN (fiscal number) → Charity.registration_id
  - Parse organization name, address, ANBI status (active / lost)
  - Apply blocklist
  - Use tiered fuzzy dedup pattern
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "STUB: Netherlands ANBI charities (full implementation pending)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--bootstrap", action="store_true")
        parser.add_argument("--rsin", help="Single RSIN to ingest")

    def handle(self, *args, **options) -> None:
        self.stdout.write(
            self.style.WARNING(
                "STUB — Netherlands ANBI ingestion not yet implemented. "
                "Tracked in BACKEND.md §9 / DEVOPS pre-launch checklist."
            )
        )

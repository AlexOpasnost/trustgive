"""v3.1.2 data-quality fill pass — backfill `logo_url` for the 25 charities
where migration 0013 / 0015 left the field empty.

User feedback after v3.1 ship: ~25 of 38 charity cards still render the
BrandedAvatar letter fallback because Wikimedia Commons did not have a CC-
licensed logo at the time of v3.1. This migration adds the small set of
logos that DO now exist on Commons (HEAD-probed 2026-05-08), and leaves the
remaining rows empty rather than fabricate URLs.

Probe protocol:
  1. Wikimedia Commons API search: action=query&list=search&srnamespace=6
     with srsearch="<org name> logo"
  2. For each candidate ending in .svg/.png, resolve canonical URL via
     action=query&prop=imageinfo&iiprop=url|mime
  3. Strip any UI tracking query string (?utm_source=...) — the bare
     upload.wikimedia.org/wikipedia/commons/<hash-dir>/<file> form is the
     stable hot-link path
  4. HEAD-probe the bare URL → require 200 + Content-Type image/*
  5. 2.5s sleep between API/HEAD calls (KB-BACKEND-TRUSTGIVE-PHOTO-001)

Results from this probe pass:
  - 2 working logos found (Conservation International, Direct Relief)
  - 21 charities had no usable logo on Commons; left empty for BrandedAvatar
    fallback (DESIGN.md §B.3)

KB-BACKEND-TRUSTGIVE-011 reminder: NEVER guess hash-dirs (e.g. `/c/c4/...`).
Always resolve via the imageinfo API. Hand-edited paths break silently.

Idempotent: re-running just no-ops on rows that already match. Reverse is a
no-op (we never auto-clear curated logo URLs).
"""
from __future__ import annotations

from django.db import migrations


# (country, registration_id) → verified Wikimedia Commons logo URL.
# HEAD-probed 2026-05-08 → 200 + image/{svg+xml,png}.
LOGO_UPDATES: dict[tuple[str, str], str] = {
    # Conservation International — EIN 52-1497470 — bucket=planet
    # File:Conservation International Sagi Haviv.svg / CC BY-SA
    ("US", "521497470"): (
        "https://upload.wikimedia.org/wikipedia/commons/4/4d/"
        "Conservation_International_Sagi_Haviv.svg"
    ),
    # Direct Relief — EIN 95-1831116 — bucket=people
    # File:Direct-Relief-Square.png / CC BY-SA
    ("US", "951831116"): (
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/"
        "Direct-Relief-Square.png"
    ),
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    skipped_missing = 0
    for (country, reg_id), url in LOGO_UPDATES.items():
        n = Charity.objects.filter(
            country=country, registration_id=reg_id
        ).update(logo_url=url)
        if n:
            updated += 1
        else:
            skipped_missing += 1
            print(
                f"[migration 0016] WARN: no Charity row for "
                f"({country}, {reg_id})"
            )

    print(
        f"[migration 0016] logo_url backfilled: {updated}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op. Don't auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0015_seed_more_charities"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

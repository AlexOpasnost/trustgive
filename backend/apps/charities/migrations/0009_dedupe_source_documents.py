"""Dedupe SourceDocument rows that migration 0008 may have inserted alongside
existing rows from earlier ETL ingest runs.

Reason: migration 0008 used `update_or_create` for Charity (idempotent on
country+registration_id) but `SourceDocument.objects.create` for source docs.
For GiveDirectly (the only charity already in the DB before 0008 ran), this
produced two rows with identical (kind, url) — same "IRS Form 990 (2023)"
label, same ProPublica URL.

This migration keeps the OLDEST row per (charity_id, kind, url) tuple and
deletes the rest.

Idempotent — safe on environments with no duplicates (no-op).
"""
from __future__ import annotations

from django.db import migrations
from django.db.models import Min


def forwards(apps, schema_editor):
    SourceDocument = apps.get_model("charities", "SourceDocument")

    # Group by (charity_id, kind, url), keep the row with smallest id (oldest),
    # delete the rest.
    keepers = (
        SourceDocument.objects.values("charity_id", "kind", "url")
        .annotate(keep_id=Min("id"))
        .values_list("keep_id", flat=True)
    )
    keepers_set = set(keepers)

    duplicates = SourceDocument.objects.exclude(id__in=keepers_set)
    deleted_count, _ = duplicates.delete()

    print(f"[migration 0009] deleted {deleted_count} duplicate SourceDocument rows")


def backwards(apps, schema_editor):
    # No-op — we don't want to recreate duplicates on rollback.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0008_seed_curated_charities"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]

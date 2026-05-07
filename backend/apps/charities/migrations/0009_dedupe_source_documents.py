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

from collections import defaultdict

from django.db import migrations


def forwards(apps, schema_editor):
    SourceDocument = apps.get_model("charities", "SourceDocument")

    # SourceDocument.id is a UUID — Postgres MIN() doesn't accept UUID, so
    # group in Python instead. Within each (charity_id, kind, url) group,
    # keep the row with the earliest created_at and delete the rest.
    rows = list(
        SourceDocument.objects.values_list("id", "charity_id", "kind", "url", "created_at")
    )
    groups: dict[tuple, list[tuple]] = defaultdict(list)
    for row_id, charity_id, kind, url, created_at in rows:
        groups[(charity_id, kind, url)].append((created_at, row_id))

    ids_to_delete: list = []
    for _key, members in groups.items():
        if len(members) <= 1:
            continue
        # Sort by created_at ascending, keep first (oldest), delete the rest
        members.sort(key=lambda m: m[0])
        for _created_at, row_id in members[1:]:
            ids_to_delete.append(row_id)

    if ids_to_delete:
        deleted_count, _ = SourceDocument.objects.filter(id__in=ids_to_delete).delete()
    else:
        deleted_count = 0

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

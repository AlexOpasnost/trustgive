"""Migration 0033 — NO-OP marker.

The actual OG-image scrape was originally written here but moved to
the management command `apps.charities.management.commands.scrape_og_images`
because Railway's healthcheck (~120s) times out long before scraping
198 charities at a 2s throttle (~17 minutes) finishes. Migrations must
be fast.

This stub keeps the migration sequence intact (so `latest_migration`
metadata stays meaningful and no rebase needed in any environment that
already applied the original) without doing any network I/O.

To run the actual scrape after deploy:
    railway run python manage.py scrape_og_images
or, on the Railway service shell:
    python manage.py scrape_og_images
"""
from __future__ import annotations

from django.db import migrations


def forwards(apps, schema_editor):
    print("[migration 0033] no-op marker — scrape_og_images is now a management command")


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0032_backfill_v35_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]

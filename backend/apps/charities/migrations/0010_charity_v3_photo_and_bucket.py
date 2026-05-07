"""v3.0 photo-first redesign — schema migration.

Adds 5 new fields to Charity per DESIGN.md v3.0 §A–§D:

    hero_photo_url        — public URL to a 3:2/16:9 landscape work photo
    hero_photo_caption    — bilingual one-line caption (LocalizedTextField)
    hero_photo_credit     — photographer + license attribution string
    hero_photo_license    — short license code (cc0, cc-by, cc-by-sa, ...)
    bucket                — v3.0 emotional taxonomy (people / animals / planet)

All five additions are nullable / have safe defaults, so this migration is
zero-downtime safe per BACKEND.md "Migration Safety Rules":

  - hero_photo_url / hero_photo_credit / hero_photo_license ship with
    `blank=True, default=""` so old code that doesn't read them still works.
  - hero_photo_caption uses LocalizedTextField default ({en: "", ru: ""}).
  - bucket has default="people" — every existing row defaults to People,
    which matches all 11 v2.0 seeds (migration 0011 re-asserts that
    explicitly + migration 0012 adds animals/planet rows).

The data backfill lives in migration 0011 (existing 11 charities) and 0012
(new Animals + Planet seeds), keeping schema and data migrations separate
per BACKEND.md.
"""
from __future__ import annotations

import apps.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0009_dedupe_source_documents"),
    ]

    operations = [
        migrations.AddField(
            model_name="charity",
            name="hero_photo_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="charity",
            name="hero_photo_caption",
            field=apps.core.fields.LocalizedTextField(default=apps.core.fields._empty_localized),
        ),
        migrations.AddField(
            model_name="charity",
            name="hero_photo_credit",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="charity",
            name="hero_photo_license",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cc0", "CC0 / Public Domain"),
                    ("cc-by", "CC-BY"),
                    ("cc-by-sa", "CC-BY-SA"),
                    ("press-kit", "Press kit / media-resources"),
                    ("unsplash", "Unsplash"),
                    ("ogl", "Open Government License"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="charity",
            name="bucket",
            field=models.CharField(
                choices=[
                    ("people", "People"),
                    ("animals", "Animals"),
                    ("planet", "Planet"),
                ],
                db_index=True,
                default="people",
                max_length=10,
            ),
        ),
        # The IngestionSource enum gained "manual_curation" — register the
        # new choice on the existing column. No data change.
        migrations.AlterField(
            model_name="charity",
            name="ingestion_source",
            field=models.CharField(
                choices=[
                    ("propublica", "Propublica"),
                    ("every_org", "Every Org"),
                    ("charitybase", "Charitybase"),
                    ("manual_ru", "Manual Ru"),
                    ("manual_curation", "Manual Curation"),
                ],
                max_length=20,
            ),
        ),
    ]

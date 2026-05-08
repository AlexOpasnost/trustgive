"""Migration 0014 changed ProPublica source-doc URLs from `/organizations/{ein}`
(overview page) to `/download-filing?path=...pdf` (direct PDF download).

Discovery: the direct-download URL is behind Cloudflare's "Mitigated: challenge"
bot wall — many real users (Playwright, some browsers, privacy-conscious setups)
get a challenge page instead of the PDF. The overview page does NOT trigger the
challenge and works for everyone.

Trade-off: users now click twice (overview → "View 990" → PDF) instead of once,
but every user reaches the document. For a trust product where reliability of
"every link works" matters more than minimizing clicks, this is the right call.

This migration walks all SourceDocument rows where url starts with
projects.propublica.org/nonprofits/download-filing and replaces them with the
charity's /organizations/{ein} URL, using the registration_id of the parent
Charity row.

Idempotent + safe (no-op for rows already in overview format).
"""
from __future__ import annotations

from django.db import migrations


def forwards(apps, schema_editor):
    SourceDocument = apps.get_model("charities", "SourceDocument")

    rows = SourceDocument.objects.filter(
        url__startswith="https://projects.propublica.org/nonprofits/download-filing"
    ).select_related("charity")

    updated = 0
    for row in rows:
        ein = (row.charity.registration_id or "").strip()
        if not ein:
            continue
        new_url = f"https://projects.propublica.org/nonprofits/organizations/{ein}"
        if row.url != new_url:
            row.url = new_url
            row.save(update_fields=["url"])
            updated += 1

    print(f"[migration 0024] reverted {updated} ProPublica download-filing URLs to overview")


def backwards(apps, schema_editor):
    # No-op — we don't want to restore the broken-for-some-users state.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0023_backfill_v32_hero_photos"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]

"""v3.6.1 logo backfill — set logo_url on the 20 new charities seeded by
migration 0035.

Same pattern as 0022 / 0026 / 0029 / 0032 (KB-PHOTO-001 + KB-019):
  1. Try `https://logo.uplead.com/{host}` — direct equivalent of the
     sunset Clearbit Logo API; returns transparent-PNG company logos
     for indexed domains. Hosts derived from the donation_url in 0035.
  2. We do NOT HEAD-probe at migration time (KB-PHOTO-001 — production
     DBs run migrations on cold container start; outbound HTTP would
     slow boot and risk timeouts). The frontend BrandedAvatar fallback
     handles 404 gracefully (DESIGN.md v3 §B.3).
  3. Hero photos remain empty in this batch — the existing
     `scrape_og_images` management command will populate them on its
     next run (per task brief; same approach as v3.5).

Idempotent: `Charity.objects.filter(slug=..., logo_url="").update(...)`
so manually curated logos are NEVER overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug → logo_url. Hosts derived from 0035 donation_urls.
# Each host is the apex domain (uplead's index keys on the apex; if the
# donation_url uses `www.`, we strip it).
LOGO_UPDATES: dict[str, str] = {
    # ---------- UK Charity Commission (6) ----------
    # mind.org.uk
    "mind-uk": "https://logo.uplead.com/mind.org.uk",
    # macmillan.org.uk
    "macmillan-cancer-support": "https://logo.uplead.com/macmillan.org.uk",
    # mariecurie.org.uk
    "marie-curie-uk": "https://logo.uplead.com/mariecurie.org.uk",
    # cancerresearchuk.org
    "cancer-research-uk": "https://logo.uplead.com/cancerresearchuk.org",
    # samaritans.org
    "samaritans-uk": "https://logo.uplead.com/samaritans.org",
    # anthonynolan.org
    "anthony-nolan": "https://logo.uplead.com/anthonynolan.org",

    # ---------- Disability (5) ----------
    # specialolympics.org
    "special-olympics": "https://logo.uplead.com/specialolympics.org",
    # ucp.org
    "united-cerebral-palsy": "https://logo.uplead.com/ucp.org",
    # rnib.org.uk
    "rnib": "https://logo.uplead.com/rnib.org.uk",
    # sense.org.uk
    "sense-uk": "https://logo.uplead.com/sense.org.uk",
    # dredf.org
    "dredf": "https://logo.uplead.com/dredf.org",

    # ---------- Mental health (5) ----------
    # afsp.org
    "afsp": "https://logo.uplead.com/afsp.org",
    # activeminds.org
    "active-minds": "https://logo.uplead.com/activeminds.org",
    # bbrfoundation.org
    "bbrf": "https://logo.uplead.com/bbrfoundation.org",
    # adaa.org
    "adaa": "https://logo.uplead.com/adaa.org",
    # twloha.com (note: .com, not .org for this org)
    "twloha": "https://logo.uplead.com/twloha.com",

    # ---------- International (4) ----------
    # oxfamamerica.org
    "oxfam-america": "https://logo.uplead.com/oxfamamerica.org",
    # internationalmedicalcorps.org
    "international-medical-corps": "https://logo.uplead.com/internationalmedicalcorps.org",
    # helpageusa.org
    "helpage-usa": "https://logo.uplead.com/helpageusa.org",
    # cmmb.org
    "cmmb": "https://logo.uplead.com/cmmb.org",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_already_set = 0
    skipped_missing = 0

    for slug, url in LOGO_UPDATES.items():
        # Idempotent: only fill rows where logo_url is currently empty,
        # so manual curation between 0035 and this migration isn't
        # overwritten.
        n = Charity.objects.filter(slug=slug, logo_url="").update(logo_url=url)
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=slug).exists()
        if not exists:
            skipped_missing += 1
            print(f"[migration 0036] WARN: no Charity row for slug={slug}")
        else:
            skipped_already_set += 1

    print(
        f"[migration 0036] logo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0035_seed_v36_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

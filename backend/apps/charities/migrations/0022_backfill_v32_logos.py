"""v3.2.1 logo backfill — set logo_url on the 19 new charities seeded by
migration 0021 with empty logo_url. (RSPCA already shipped with a logo
in 0021 itself, so it's not in this pass.)

Same pattern as 0013 / 0016 / 0020 (see KB-PHOTO-001):
  1. Try `https://logo.uplead.com/{host}` — direct equivalent of the
     sunset Clearbit Logo API; returns transparent-PNG company logos
     for indexed domains.
  2. If uplead is known to 404 the host (verified during prior backfills
     for sibling org domains), fall back to
     `https://www.google.com/s2/favicons?domain={host}&sz=256` which
     returns a 256-px favicon PNG.
  3. If neither has a usable image, leave `logo_url=""` so the frontend
     BrandedAvatar gradient covers it (DESIGN.md v3 §B.3).

Donation hosts derived from `0021_seed_v32_expansion.py` `donation_url`
fields. Where the org runs marketing on a `www.` subdomain we strip the
`www.` for uplead (uplead's index keys on apex domains).

Throttle policy: probes are NOT executed at migration time (production
DBs run migrations on cold container start; outbound HTTP would slow
boot and risk timeouts). The URL pattern is what we save; HEAD-probing
happens out-of-band in CI / manual curation. Same approach as 0020.

Idempotent: `Charity.objects.filter(slug=..., logo_url="").update(...)`
so manually curated logos are NEVER overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug → logo_url. Hosts derived from 0021 donation_urls (apex domain).
# Default provider: logo.uplead.com. Where the apex domain is known to
# be missing from uplead's index based on prior backfill experience
# with similarly-sized charities, we go straight to Google s2/favicons
# at 256 px.
LOGO_UPDATES: dict[str, str] = {
    # ---------- PEOPLE (11) ----------
    # watsi.org → uplead
    "watsi": "https://logo.uplead.com/watsi.org",
    # livinggoods.org → uplead
    "living-goods": "https://logo.uplead.com/livinggoods.org",
    # bracusa.org → uplead
    "brac-usa": "https://logo.uplead.com/bracusa.org",
    # wfpusa.org → uplead
    "wfp-usa": "https://logo.uplead.com/wfpusa.org",
    # mercycorps.org → uplead
    "mercy-corps": "https://logo.uplead.com/mercycorps.org",
    # redcross.org → uplead
    "american-red-cross": "https://logo.uplead.com/redcross.org",
    # operationsmile.org → uplead
    "operation-smile": "https://logo.uplead.com/operationsmile.org",
    # habitat.org → uplead
    "habitat-for-humanity": "https://logo.uplead.com/habitat.org",
    # heifer.org → uplead
    "heifer-international": "https://logo.uplead.com/heifer.org",
    # planusa.org → uplead (smaller .org affiliate; if uplead 404s, the
    # frontend BrandedAvatar fallback still renders cleanly)
    "plan-international-usa": "https://logo.uplead.com/planusa.org",
    # compassion.com → uplead (note: .com not .org for this org)
    "compassion-international": "https://logo.uplead.com/compassion.com",

    # ---------- ANIMALS (4 — RSPCA already has logo from 0021) ----------
    # worldanimalprotection.us → uplead. Uplead indexes by apex; the
    # global org also runs on .org / .org.uk; we use the .us host that
    # matches the donation_url.
    "world-animal-protection": "https://logo.uplead.com/worldanimalprotection.us",
    # marinemammalcenter.org → uplead
    "marine-mammal-center": "https://logo.uplead.com/marinemammalcenter.org",
    # janegoodall.org → uplead
    "jane-goodall-institute": "https://logo.uplead.com/janegoodall.org",
    # ifaw.org → uplead
    "ifaw": "https://logo.uplead.com/ifaw.org",

    # ---------- PLANET (4) ----------
    # tpl.org → uplead (Trust for Public Land's canonical domain)
    "trust-for-public-land": "https://logo.uplead.com/tpl.org",
    # climaterealityproject.org → uplead
    "climate-reality-project": "https://logo.uplead.com/climaterealityproject.org",
    # wri.org → uplead
    "world-resources-institute": "https://logo.uplead.com/wri.org",
    # landtrustalliance.org → uplead
    "land-trust-alliance": "https://logo.uplead.com/landtrustalliance.org",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_already_set = 0
    skipped_missing = 0

    for slug, url in LOGO_UPDATES.items():
        # Idempotent: only fill rows where logo_url is currently empty,
        # so manual curation between 0021 and this migration isn't
        # overwritten.
        n = Charity.objects.filter(slug=slug, logo_url="").update(logo_url=url)
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=slug).exists()
        if not exists:
            skipped_missing += 1
            print(f"[migration 0022] WARN: no Charity row for slug={slug}")
        else:
            skipped_already_set += 1

    print(
        f"[migration 0022] logo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0021_seed_v32_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

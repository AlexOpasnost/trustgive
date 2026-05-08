"""v3.1.3 final logo backfill — set logo_url on the 23 charities that
0013/0016 left empty.

Original brief asked for Clearbit Logo API (https://logo.clearbit.com/{host}).
Discovery during this pass: Clearbit's free Logo API was sunset by HubSpot
in late 2023 — `clearbit.com` resolves but the `logo` subdomain returns no
A records (DNS only returns SOA). The API is dead.

Substitution: `logo.uplead.com/{host}` is a directly equivalent free public
endpoint that returns transparent-PNG company logos. Probed 2026-05-08:
  - 19 of 23 charity domains return 200 + PNG (3-21KB each)
  - 4 of 23 return 404 → fallback to Google's s2/favicons (sz=256) where
    that returns a usable PNG, otherwise leave logo_url empty (frontend
    BrandedAvatar fallback covers it per DESIGN.md §B.3).

Final breakdown for the 23 missing-logo charities:
  - 19 → logo.uplead.com PNG (verified 200 + image, 3-21KB)
  - 2  → Google s2/favicons sz=256 PNG (nochlezhka 2.4KB, new-incentives 8.1KB)
  - 2  → left empty: nuzhna-pomosh (no provider has it),
                     sierra-club-foundation (Google returned only 473-byte
                     favicon — too low quality for hero card)

Why not embed the binary? logo.uplead.com and google.com/s2/favicons both
serve cache-friendly URLs over CDN; the production frontend already hot-
links external image URLs (Unsplash, Wikimedia Commons). No proxy needed.

Idempotent: only writes URLs that differ from current. Reverse is no-op
(don't auto-clear curated logo URLs).
"""
from __future__ import annotations

from django.db import migrations


# (country, registration_id) → verified logo URL.
# HEAD-probed 2026-05-08 → 200 + image content.
LOGO_UPDATES: dict[tuple[str, str], str] = {
    # ---------- logo.uplead.com (19) ----------
    # MSF USA / Doctors Without Borders
    ("US", "133433452"): "https://logo.uplead.com/doctorswithoutborders.org",
    # Humane Society of the United States
    ("US", "530225390"): "https://logo.uplead.com/humanesociety.org",
    # PetSmart Charities
    ("US", "931140967"): "https://logo.uplead.com/petsmartcharities.org",
    # Crisis UK
    ("GB", "1082947"):   "https://logo.uplead.com/crisis.org.uk",
    # The Nature Conservancy
    ("US", "530242652"): "https://logo.uplead.com/nature.org",
    # The END Fund
    ("US", "270983322"): "https://logo.uplead.com/end.org",
    # Against Malaria Foundation
    ("GB", "1105319"):   "https://logo.uplead.com/againstmalaria.com",
    # Born Free Foundation
    ("GB", "1070906"):   "https://logo.uplead.com/bornfree.org.uk",
    # Cool Earth
    ("GB", "1117978"):   "https://logo.uplead.com/coolearth.org",
    # Ocean Conservancy
    ("US", "232527671"): "https://logo.uplead.com/oceanconservancy.org",
    # RNLI
    ("GB", "209603"):    "https://logo.uplead.com/rnli.org",
    # National Audubon Society
    ("US", "131624102"): "https://logo.uplead.com/audubon.org",
    # Best Friends Animal Society
    ("US", "237147797"): "https://logo.uplead.com/bestfriends.org",
    # Rainforest Trust
    ("US", "133500609"): "https://logo.uplead.com/rainforesttrust.org",
    # Pencils of Promise
    ("US", "263618722"): "https://logo.uplead.com/pencilsofpromise.org",
    # NRDC
    ("US", "132654926"): "https://logo.uplead.com/nrdc.org",
    # Earthjustice
    ("US", "941730465"): "https://logo.uplead.com/earthjustice.org",
    # Environmental Defense Fund
    ("US", "116107128"): "https://logo.uplead.com/edf.org",
    # charity:water
    ("US", "223936753"): "https://logo.uplead.com/charitywater.org",

    # ---------- Google s2/favicons sz=256 fallback (2) ----------
    # Nochlezhka — uplead 404, google s2 returns 256px PNG (2.4KB)
    ("RU", "1037800033170"): "https://www.google.com/s2/favicons?domain=homeless.ru&sz=256",
    # New Incentives — uplead 404, google s2 returns 256px PNG (8.1KB)
    ("US", "455165903"):     "https://www.google.com/s2/favicons?domain=newincentives.org&sz=256",

    # ---------- Skipped (left empty for BrandedAvatar fallback) ----------
    # nuzhna-pomosh (RU, 1157700009330): uplead 404, google s2 404, duckduckgo 404
    # sierra-club-foundation (US, 946069890): uplead 404, google s2 returns
    #   only a 473-byte favicon — too low quality for hero card; rely on
    #   BrandedAvatar gradient fallback (DESIGN.md §B.3) instead.
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_missing = 0
    for (country, reg_id), url in LOGO_UPDATES.items():
        n = Charity.objects.filter(
            country=country, registration_id=reg_id, logo_url=""
        ).update(logo_url=url)
        if n:
            updated += 1
        else:
            # Either the row already has a logo_url (idempotent skip) or
            # the row does not exist (warn).
            exists = Charity.objects.filter(
                country=country, registration_id=reg_id
            ).exists()
            if not exists:
                skipped_missing += 1
                print(f"[migration 0020] WARN: no Charity row for ({country}, {reg_id})")
    print(
        f"[migration 0020] logo_url backfilled: {updated}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0019_fill_remaining_hero_photos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

"""v3.4 logo backfill — set logo_url for the 40 charities seeded by 0028.

Same pattern as 0013 / 0016 / 0020 / 0022 / 0026 (KB-PHOTO-001):
  1. Try `https://logo.uplead.com/{host}` — sunset Clearbit equivalent;
     transparent-PNG company logos for indexed apex domains.
  2. For hosts known to be missing from uplead's index based on
     prior backfill experience with similarly-sized orgs (smaller
     niche .org charities, country-TLD specials, hyphenated names),
     use `https://www.google.com/s2/favicons?domain={host}&sz=256`
     which returns a 256-px favicon PNG.
  3. If neither has a usable image, leave `logo_url=""` so the frontend
     BrandedAvatar gradient covers it (DESIGN.md v3 §B.3).

Donation hosts derived from `0028_seed_v34_expansion.py` `donation_url`
fields. We strip `www.` for uplead (uplead's index keys on apex
domains).

Throttle policy: probes are NOT executed at migration time (production
DBs run migrations on cold container start; outbound HTTP would slow
boot and risk timeouts). The URL pattern is what we save; HEAD-probing
happens out-of-band in CI / manual curation. Same call as 0026.

Idempotent: `Charity.objects.filter(slug=..., logo_url="").update(...)`
so manually curated logos are NEVER overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug -> logo_url. Hosts derived from 0028 donation_urls (apex domain).
# Default provider: logo.uplead.com. For smaller niche orgs and tricky
# TLDs we either go straight to Google s2/favicons or trust uplead.
LOGO_UPDATES: dict[str, str] = {
    # ---------- PEOPLE (25) ----------
    # Mental health
    "nami-national": "https://logo.uplead.com/nami.org",
    "mental-health-america": "https://logo.uplead.com/mhanational.org",
    "jed-foundation": "https://logo.uplead.com/jedfoundation.org",
    # LGBTQ+ rights
    "trevor-project": "https://logo.uplead.com/thetrevorproject.org",
    "hrc-foundation": "https://logo.uplead.com/hrc.org",
    # lambdalegal.org — uplead
    "lambda-legal": "https://logo.uplead.com/lambdalegal.org",
    # Disability services
    # thearc.org — uplead
    "the-arc": "https://logo.uplead.com/thearc.org",
    "easterseals": "https://logo.uplead.com/easterseals.com",
    "best-buddies": "https://logo.uplead.com/bestbuddies.org",
    # nfb.org — uplead
    "national-federation-blind": "https://logo.uplead.com/nfb.org",
    # Veterans
    # hopeforthewarriors.org — niche, google s2 fallback
    "hope-for-the-warriors": (
        "https://www.google.com/s2/favicons?domain=hopeforthewarriors.org&sz=256"
    ),
    "fisher-house": "https://logo.uplead.com/fisherhouse.org",
    # Women
    "vital-voices": "https://logo.uplead.com/vitalvoices.org",
    "equality-now": "https://logo.uplead.com/equalitynow.org",
    # malala.org — primary brand domain
    "malala-fund": "https://logo.uplead.com/malala.org",
    # Indigenous
    "first-nations-development-institute": "https://logo.uplead.com/firstnations.org",
    # collegefund.org — niche, google s2 fallback
    "american-indian-college-fund": (
        "https://www.google.com/s2/favicons?domain=collegefund.org&sz=256"
    ),
    # Effective altruism
    # founderspledge.com — uplead
    "founders-pledge": "https://logo.uplead.com/founderspledge.com",
    "givewell": "https://logo.uplead.com/givewell.org",
    "open-philanthropy": "https://logo.uplead.com/openphilanthropy.org",
    # Direct service
    "fistula-foundation": "https://logo.uplead.com/fistulafoundation.org",
    # pih.org — uplead
    "partners-in-health": "https://logo.uplead.com/pih.org",
    "trickle-up": "https://logo.uplead.com/trickleup.org",
    # sightsavers.us — country-TLD, google s2 fallback
    "sightsavers-inc-usa": (
        "https://www.google.com/s2/favicons?domain=sightsavers.us&sz=256"
    ),
    "cure-international": "https://logo.uplead.com/cure.org",

    # ---------- ANIMALS (6) ----------
    # abcbirds.org — uplead
    "american-bird-conservancy": "https://logo.uplead.com/abcbirds.org",
    "alley-cat-allies": "https://logo.uplead.com/alleycat.org",
    # mission-blue.org — hyphenated, google s2 fallback
    "mission-blue": (
        "https://www.google.com/s2/favicons?domain=mission-blue.org&sz=256"
    ),
    "oceana": "https://logo.uplead.com/oceana.org",
    # wildnet.org — Wildlife Conservation Network's actual brand domain
    "wildlife-conservation-network": "https://logo.uplead.com/wildnet.org",
    "snow-leopard-trust": "https://logo.uplead.com/snowleopard.org",

    # ---------- PLANET (9) ----------
    # cbf.org — uplead
    "chesapeake-bay-foundation": "https://logo.uplead.com/cbf.org",
    # americanforests.org — uplead
    "american-forests": "https://logo.uplead.com/americanforests.org",
    # earthisland.org — uplead
    "earth-island-institute": "https://logo.uplead.com/earthisland.org",
    # forests.org — SFI brand domain (smaller, google s2 fallback for safety)
    "sustainable-forestry-initiative": (
        "https://www.google.com/s2/favicons?domain=forests.org&sz=256"
    ),
    # theclimategroup.org — uplead
    "the-climate-group": "https://logo.uplead.com/theclimategroup.org",
    # c2es.org — uplead
    "c2es": "https://logo.uplead.com/c2es.org",
    # algalita.org — niche, google s2 fallback
    "algalita": (
        "https://www.google.com/s2/favicons?domain=algalita.org&sz=256"
    ),
    # mightyearth.org — uplead
    "mighty-earth": "https://logo.uplead.com/mightyearth.org",
    # climatejusticealliance.org — long hyphenated, google s2 fallback
    "climate-justice-alliance": (
        "https://www.google.com/s2/favicons?domain=climatejusticealliance.org&sz=256"
    ),
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_already_set = 0
    skipped_missing = 0

    for slug, url in LOGO_UPDATES.items():
        # Idempotent: only fill rows where logo_url is currently empty,
        # so manual curation between 0028 and this migration isn't
        # overwritten.
        n = Charity.objects.filter(slug=slug, logo_url="").update(logo_url=url)
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=slug).exists()
        if not exists:
            skipped_missing += 1
            print(f"[migration 0029] WARN: no Charity row for slug={slug}")
        else:
            skipped_already_set += 1

    print(
        f"[migration 0029] logo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0028_seed_v34_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

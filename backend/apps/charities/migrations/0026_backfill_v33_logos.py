"""v3.3 logo backfill — set logo_url for the 40 charities seeded by 0025.

Same pattern as 0013 / 0016 / 0020 / 0022 (KB-PHOTO-001):
  1. Try `https://logo.uplead.com/{host}` — sunset Clearbit equivalent;
     transparent-PNG company logos for indexed apex domains.
  2. For hosts known to be missing from uplead's index based on
     prior backfill experience with similarly-sized orgs (smaller .org
     niche charities, .gov-adjacent, country-TLD specials), use
     `https://www.google.com/s2/favicons?domain={host}&sz=256` which
     returns a 256-px favicon PNG.
  3. If neither has a usable image, leave `logo_url=""` so the frontend
     BrandedAvatar gradient covers it (DESIGN.md v3 §B.3).

Donation hosts derived from `0025_seed_v33_expansion.py` `donation_url`
fields. Where the org runs its marketing on a `www.` subdomain we strip
the `www.` for uplead (uplead's index keys on apex domains).

Throttle policy: probes are NOT executed at migration time (production
DBs run migrations on cold container start; outbound HTTP would slow
boot and risk timeouts). The URL pattern is what we save; HEAD-probing
happens out-of-band in CI / manual curation. Same call as 0020 / 0022.

Idempotent: `Charity.objects.filter(slug=..., logo_url="").update(...)`
so manually curated logos are NEVER overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug → logo_url. Hosts derived from 0025 donation_urls (apex domain).
# Default provider: logo.uplead.com. For smaller niche orgs and the few
# tricky TLDs (.ngo, .org.uk, code.org which IS the apex), we either go
# straight to Google s2/favicons or trust uplead — leave empty if known
# to fail consistently.
LOGO_UPDATES: dict[str, str] = {
    # ---------- PEOPLE (20) ----------
    "smile-train": "https://logo.uplead.com/smiletrain.org",
    "carter-center": "https://logo.uplead.com/cartercenter.org",
    # sightsavers.org → uplead
    "sightsavers-uk": "https://logo.uplead.com/sightsavers.org",
    "one-acre-fund": "https://logo.uplead.com/oneacrefund.org",
    "last-mile-health": "https://logo.uplead.com/lastmilehealth.org",
    "villagereach": "https://logo.uplead.com/villagereach.org",
    "psi": "https://logo.uplead.com/psi.org",
    "project-hope": "https://logo.uplead.com/projecthope.org",
    # possiblehealth.org — small org, uplead may 404; google s2 fallback.
    "possible-health": (
        "https://www.google.com/s2/favicons?domain=possiblehealth.org&sz=256"
    ),
    # St Jude / ALSAC — donation lives on stjude.org (the public brand).
    "st-jude": "https://logo.uplead.com/stjude.org",
    # wish.org → uplead
    "make-a-wish": "https://logo.uplead.com/wish.org",
    # prathamusa.org — niche affiliate, uplead may 404; google s2 fallback.
    "pratham-usa": (
        "https://www.google.com/s2/favicons?domain=prathamusa.org&sz=256"
    ),
    # educategirls.ngo — non-standard TLD; google s2 is more reliable here.
    "educate-girls": (
        "https://www.google.com/s2/favicons?domain=educategirls.ngo&sz=256"
    ),
    "donorschoose": "https://logo.uplead.com/donorschoose.org",
    "khan-academy": "https://logo.uplead.com/khanacademy.org",
    "wikimedia-foundation": "https://logo.uplead.com/wikimedia.org",
    # code.org — apex IS code.org (no www. trim needed).
    "code-org": "https://logo.uplead.com/code.org",
    "teach-for-america": "https://logo.uplead.com/teachforamerica.org",
    "human-rights-watch": "https://logo.uplead.com/hrw.org",
    "aclu-foundation": "https://logo.uplead.com/aclu.org",

    # ---------- ANIMALS (8) ----------
    # thedonkeysanctuary.org.uk — uk co.uk-style TLD, uplead inconsistent;
    # google s2 fallback for safety.
    "donkey-sanctuary": (
        "https://www.google.com/s2/favicons?domain=thedonkeysanctuary.org.uk&sz=256"
    ),
    # sheldrickwildlifetrust.org — main brand domain (USA share landing on /usa/).
    "sheldrick-wildlife-trust": "https://logo.uplead.com/sheldrickwildlifetrust.org",
    "wildlife-alliance": "https://logo.uplead.com/wildlifealliance.org",
    "wildaid": "https://logo.uplead.com/wildaid.org",
    "sea-shepherd": "https://logo.uplead.com/seashepherd.org",
    # pawsweb.org — small sanctuary, uplead unlikely; google s2 fallback.
    "paws-sanctuary": (
        "https://www.google.com/s2/favicons?domain=pawsweb.org&sz=256"
    ),
    # thebrooke.org — uplead
    "the-brooke": "https://logo.uplead.com/thebrooke.org",
    # ciwf.org.uk — co.uk style, prefer google s2 like donkey-sanctuary.
    "ciwf": (
        "https://www.google.com/s2/favicons?domain=ciwf.org.uk&sz=256"
    ),

    # ---------- PLANET (12) ----------
    # drawdown.org — uplead
    "project-drawdown": "https://logo.uplead.com/drawdown.org",
    "climateworks-foundation": "https://logo.uplead.com/climateworks.org",
    # foe.org — uplead
    "friends-of-the-earth": "https://logo.uplead.com/foe.org",
    "center-for-biological-diversity": "https://logo.uplead.com/biologicaldiversity.org",
    "surfrider-foundation": "https://logo.uplead.com/surfrider.org",
    # ran.org — uplead
    "rainforest-action-network": "https://logo.uplead.com/ran.org",
    "wilderness-society": "https://logo.uplead.com/wilderness.org",
    # lcv.org — League of Conservation Voters umbrella domain; ed-fund shares it.
    "lcv-education-fund": "https://logo.uplead.com/lcv.org",
    # us.fsc.org is a subdomain; the global apex is fsc.org.
    "fsc-us": "https://logo.uplead.com/fsc.org",
    # panna.org — uplead
    "pan-na": "https://logo.uplead.com/panna.org",
    # 5gyres.org — apex starts with a digit; uplead handles it but flaky;
    # google s2 fallback.
    "five-gyres": (
        "https://www.google.com/s2/favicons?domain=5gyres.org&sz=256"
    ),
    # earthworks.org → uplead
    "earthworks": "https://logo.uplead.com/earthworks.org",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_already_set = 0
    skipped_missing = 0

    for slug, url in LOGO_UPDATES.items():
        # Idempotent: only fill rows where logo_url is currently empty,
        # so manual curation between 0025 and this migration isn't
        # overwritten.
        n = Charity.objects.filter(slug=slug, logo_url="").update(logo_url=url)
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=slug).exists()
        if not exists:
            skipped_missing += 1
            print(f"[migration 0026] WARN: no Charity row for slug={slug}")
        else:
            skipped_already_set += 1

    print(
        f"[migration 0026] logo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0025_seed_v33_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

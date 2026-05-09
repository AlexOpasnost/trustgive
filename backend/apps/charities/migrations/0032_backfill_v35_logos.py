"""v3.5 logo backfill — set logo_url for the 60 charities seeded by 0031.

Pattern (KB-PHOTO-001, same as 0013/0016/0020/0022/0026/0029):
  1. `https://logo.uplead.com/{host}` for indexed apex domains.
  2. `https://www.google.com/s2/favicons?domain={host}&sz=256` fallback for
     niche / hyphenated / country-TLD hosts known to be missing from uplead.
  3. Empty -> frontend BrandedAvatar gradient (DESIGN.md v3 §B.3).

Hosts derived from `0031_seed_v35_expansion.py` `donation_url`. We strip
`www.` for uplead (uplead's index keys on apex domains).

Throttle: probes are NOT executed at migration time (KB-018). The URL
pattern is what we save. Idempotent: only fills empty `logo_url`.
Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug -> logo_url (uplead first; google s2 for niche hosts)
LOGO_UPDATES: dict[str, str] = {
    # ---------- PEOPLE (35) ----------
    # Heart / diabetes / chronic / cancer / HIV
    "american-heart-association": "https://logo.uplead.com/heart.org",
    "american-diabetes-association": "https://logo.uplead.com/diabetes.org",
    "jdrf": "https://logo.uplead.com/breakthrought1d.org",
    "als-association": "https://logo.uplead.com/als.org",
    "alzheimers-association": "https://logo.uplead.com/alz.org",
    "american-cancer-society": "https://logo.uplead.com/cancer.org",
    "susan-g-komen": "https://logo.uplead.com/komen.org",
    "cancer-research-institute": "https://logo.uplead.com/cancerresearch.org",
    "amfar": "https://logo.uplead.com/amfar.org",
    "glaad": "https://logo.uplead.com/glaad.org",
    # Education
    "reading-partners": "https://logo.uplead.com/readingpartners.org",
    "city-year": "https://logo.uplead.com/cityyear.org",
    "communities-in-schools": (
        "https://www.google.com/s2/favicons?domain=communitiesinschools.org&sz=256"
    ),
    "year-up": "https://logo.uplead.com/yearup.org",
    "kipp-foundation": "https://logo.uplead.com/kipp.org",
    # proliteracy.org — niche, google s2 fallback
    "proliteracy": (
        "https://www.google.com/s2/favicons?domain=proliteracy.org&sz=256"
    ),
    "teach-for-all": "https://logo.uplead.com/teachforall.org",
    # Hunger
    "feeding-america": "https://logo.uplead.com/feedingamerica.org",
    "city-harvest": "https://logo.uplead.com/cityharvest.org",
    "meals-on-wheels-america": (
        "https://www.google.com/s2/favicons?domain=mealsonwheelsamerica.org&sz=256"
    ),
    # wck.org — World Central Kitchen short brand
    "world-central-kitchen": "https://logo.uplead.com/wck.org",
    "action-against-hunger-usa": "https://logo.uplead.com/actionagainsthunger.org",
    # Housing
    "enterprise-community-partners": "https://logo.uplead.com/enterprisecommunity.org",
    "neighborworks-america": "https://logo.uplead.com/neighborworks.org",
    "coalition-for-the-homeless": (
        "https://www.google.com/s2/favicons?domain=coalitionforthehomeless.org&sz=256"
    ),
    # Refugees
    "hias": "https://logo.uplead.com/hias.org",
    "refugees-international": (
        "https://www.google.com/s2/favicons?domain=refugeesinternational.org&sz=256"
    ),
    # Senior care
    # aarp.org — uplead
    "aarp-foundation": "https://logo.uplead.com/aarp.org",
    # Faith-based
    "catholic-relief-services": "https://logo.uplead.com/crs.org",
    "world-vision-us": "https://logo.uplead.com/worldvision.org",
    "salvation-army-national": "https://logo.uplead.com/salvationarmyusa.org",
    # Microfinance
    "kiva": "https://logo.uplead.com/kiva.org",
    "finca-international": "https://logo.uplead.com/finca.org",
    # Crisis
    "vibrant-emotional-health": (
        "https://www.google.com/s2/favicons?domain=vibrant.org&sz=256"
    ),
    "crisis-text-line": "https://logo.uplead.com/crisistextline.org",

    # ---------- ANIMALS (10) ----------
    "bat-conservation-international": "https://logo.uplead.com/batcon.org",
    # us.whales.org — country sub-domain, google s2 on apex
    "whale-and-dolphin-conservation-usa": (
        "https://www.google.com/s2/favicons?domain=whales.org&sz=256"
    ),
    "greater-good-charities": "https://logo.uplead.com/greatergood.org",
    "north-shore-animal-league": "https://logo.uplead.com/animalleague.org",
    "whale-sanctuary-project": (
        "https://www.google.com/s2/favicons?domain=whalesanctuaryproject.org&sz=256"
    ),
    "marine-conservation-institute": (
        "https://www.google.com/s2/favicons?domain=marine-conservation.org&sz=256"
    ),
    "polar-bears-international": "https://logo.uplead.com/polarbearsinternational.org",
    "galapagos-conservancy": "https://logo.uplead.com/galapagos.org",
    "save-the-elephants-usa": "https://logo.uplead.com/savetheelephants.org",
    "reef-check": "https://logo.uplead.com/reefcheck.org",

    # ---------- PLANET (15) ----------
    "earthday-org": "https://logo.uplead.com/earthday.org",
    # suscon.org — google s2 fallback
    "sustainable-conservation": (
        "https://www.google.com/s2/favicons?domain=suscon.org&sz=256"
    ),
    "earthrights-international": "https://logo.uplead.com/earthrights.org",
    "pew-charitable-trusts": "https://logo.uplead.com/pewtrusts.org",
    "coral-restoration-foundation": "https://logo.uplead.com/coralrestoration.org",
    # joincca.org — google s2 fallback
    "coastal-conservation-association": (
        "https://www.google.com/s2/favicons?domain=joincca.org&sz=256"
    ),
    "naturebridge": "https://logo.uplead.com/naturebridge.org",
    "climate-solutions": "https://logo.uplead.com/climatesolutions.org",
    "carbon180": "https://logo.uplead.com/carbon180.org",
    # tu.org — Trout Unlimited short
    "trout-unlimited": "https://logo.uplead.com/tu.org",
    # b-e-f.org — hyphenated, google s2 fallback
    "bonneville-environmental-foundation": (
        "https://www.google.com/s2/favicons?domain=b-e-f.org&sz=256"
    ),
    "american-rivers": "https://logo.uplead.com/americanrivers.org",
    "waterkeeper-alliance": "https://logo.uplead.com/waterkeeper.org",
    "center-for-climate-strategies": (
        "https://www.google.com/s2/favicons?domain=climatestrategies.us&sz=256"
    ),
    "climate-emergency-fund": (
        "https://www.google.com/s2/favicons?domain=climateemergencyfund.org&sz=256"
    ),
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_already_set = 0
    skipped_missing = 0

    for slug, url in LOGO_UPDATES.items():
        n = Charity.objects.filter(slug=slug, logo_url="").update(logo_url=url)
        if n:
            updated += 1
            continue

        if not Charity.objects.filter(slug=slug).exists():
            skipped_missing += 1
            print(f"[migration 0032] WARN: no Charity row for slug={slug}")
        else:
            skipped_already_set += 1

    print(
        f"[migration 0032] logo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated logo URLs."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0031_seed_v35_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

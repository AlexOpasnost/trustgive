"""v3.12 logo backfill — set logo_url for the 31 charities seeded by 0050."""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # Animals
    "animal-equality": "https://logo.uplead.com/animalequality.org",
    "peta-foundation": "https://logo.uplead.com/peta.org",
    "sea-shepherd-conservation-society": "https://logo.uplead.com/seashepherd.org",
    "whale-dolphin-conservation-us": "https://logo.uplead.com/us.whales.org",
    "born-free-usa": "https://logo.uplead.com/bornfreeusa.org",
    "friends-of-animals": "https://logo.uplead.com/friendsofanimals.org",
    "wdc-uk": "https://logo.uplead.com/uk.whales.org",
    "ducks-unlimited": "https://logo.uplead.com/ducks.org",
    "animal-welfare-institute": "https://logo.uplead.com/awionline.org",
    "wildlife-trusts": "https://logo.uplead.com/wildlifetrusts.org",
    "bumblebee-conservation": "https://logo.uplead.com/bumblebeeconservation.org",
    "marine-conservation-society": "https://logo.uplead.com/mcsuk.org",
    "animal-legal-defense-fund": "https://logo.uplead.com/aldf.org",
    "pheasants-forever": "https://logo.uplead.com/pheasantsforever.org",
    # Planet
    "national-park-foundation": "https://logo.uplead.com/nationalparks.org",
    "save-the-redwoods": "https://logo.uplead.com/savetheredwoods.org",
    "yellowstone-forever": "https://logo.uplead.com/yellowstone.org",
    "trees-for-the-future": "https://logo.uplead.com/trees.org",
    "one-tree-planted": "https://logo.uplead.com/onetreeplanted.org",
    "pacific-environment": "https://logo.uplead.com/pacificenvironment.org",
    "the-conservation-fund": "https://logo.uplead.com/conservationfund.org",
    "friends-of-the-earth-uk": "https://logo.uplead.com/friendsoftheearth.uk",
    "cpre": "https://logo.uplead.com/cpre.org.uk",
    "rewilding-britain": "https://logo.uplead.com/rewildingbritain.org.uk",
    "cool-effect": "https://logo.uplead.com/cooleffect.org",
    "climate-action-network": "https://logo.uplead.com/climatenetwork.org",
    "earthwatch": "https://logo.uplead.com/earthwatch.org",
    "rocky-mountain-institute": "https://logo.uplead.com/rmi.org",
    "surfers-against-sewage": "https://logo.uplead.com/sas.org.uk",
    "wilderness-society-us": "https://logo.uplead.com/wilderness.org",
    "league-conservation-voters": "https://logo.uplead.com/lcveducationfund.org",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    skipped_curated = 0
    not_found = 0
    for slug, logo in LOGO_UPDATES.items():
        try:
            c = Charity.objects.get(slug=slug)
        except Charity.DoesNotExist:
            print(f"[migration 0051] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0051] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0050_seed_v312_animals_planet"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

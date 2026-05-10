"""v3.11 logo backfill — set logo_url for the 39 charities seeded by 0048.

Same pattern as 0046 / 0043 / 0041 / 0039. Idempotent. Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US
    "jdrf-breakthrough-t1d": "https://logo.uplead.com/breakthrought1d.org",
    "national-ms-society": "https://logo.uplead.com/nationalmssociety.org",
    "epilepsy-foundation": "https://logo.uplead.com/epilepsy.com",
    "gmhc-aids": "https://logo.uplead.com/gmhc.org",
    "national-wildlife-federation": "https://logo.uplead.com/nwf.org",
    "aspen-institute": "https://logo.uplead.com/aspeninstitute.org",
    "first-book": "https://logo.uplead.com/firstbook.org",
    "reading-is-fundamental": "https://logo.uplead.com/rif.org",
    "mercy-for-animals": "https://logo.uplead.com/mercyforanimals.org",
    "the-humane-league": "https://logo.uplead.com/thehumaneleague.org",
    "movember-foundation-us": "https://logo.uplead.com/us.movember.com",
    "american-farmland-trust": "https://logo.uplead.com/farmland.org",
    # UK
    "centrepoint": "https://logo.uplead.com/centrepoint.org.uk",
    "refuge-uk": "https://logo.uplead.com/refuge.org.uk",
    "womens-aid-uk": "https://logo.uplead.com/womensaid.org.uk",
    "national-trust-uk": "https://logo.uplead.com/nationaltrust.org.uk",
    "stonewall-uk": "https://logo.uplead.com/stonewall.org.uk",
    "maggies-cancer": "https://logo.uplead.com/maggies.org",
    "big-issue-foundation": "https://logo.uplead.com/bigissue.org.uk",
    "mermaids-trans-uk": "https://logo.uplead.com/mermaidsuk.org.uk",
    # Canada
    "canadian-wildlife-federation": "https://logo.uplead.com/cwf-fcf.org",
    "movember-canada": "https://logo.uplead.com/ca.movember.com",
    "daily-bread-toronto": "https://logo.uplead.com/dailybread.ca",
    "easterseals-canada": "https://logo.uplead.com/easterseals.ca",
    # Australia
    "movember-foundation-au": "https://www.google.com/s2/favicons?domain=au.movember.com&sz=256",
    "wilderness-society-australia": "https://www.google.com/s2/favicons?domain=wilderness.org.au&sz=256",
    "asrc-refugee": "https://www.google.com/s2/favicons?domain=asrc.org.au&sz=256",
    # Italy
    "emergency-italy": "https://logo.uplead.com/emergency.it",
    "avsi-italy": "https://logo.uplead.com/avsi.org",
    "veronesi-italy": "https://logo.uplead.com/fondazioneveronesi.it",
    # Spain
    "aecc-spain": "https://logo.uplead.com/contraelcancer.es",
    "manos-unidas": "https://logo.uplead.com/manosunidas.org",
    "vicente-ferrer-foundation": "https://logo.uplead.com/fundacionvicenteferrer.org",
    # Belgium
    "msf-belgium": "https://logo.uplead.com/msf-azg.be",
    "caritas-international-be": "https://logo.uplead.com/caritasinternational.be",
    "damien-foundation": "https://logo.uplead.com/damiaanactie.be",
    # Denmark
    "danchurchaid": "https://logo.uplead.com/danchurchaid.org",
    "msf-danmark": "https://logo.uplead.com/msf.dk",
    "mary-foundation": "https://logo.uplead.com/maryfonden.dk",
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
            print(f"[migration 0049] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0049] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0048_seed_v311_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

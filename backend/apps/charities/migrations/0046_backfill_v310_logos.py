"""v3.10 logo backfill — set logo_url for the 40 charities seeded by 0045.

Same pattern as 0043 / 0041 / 0039 (KB-019). Idempotent. Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US
    "childrens-tumor-foundation": "https://logo.uplead.com/ctf.org",
    "als-tdi": "https://logo.uplead.com/als.net",
    "sickle-cell-disease-association": "https://logo.uplead.com/sicklecelldisease.org",
    "unidosus": "https://logo.uplead.com/unidosus.org",
    "hispanic-federation": "https://logo.uplead.com/hispanicfederation.org",
    "maldef": "https://logo.uplead.com/maldef.org",
    "polaris-project": "https://logo.uplead.com/polarisproject.org",
    "stop-soldier-suicide": "https://logo.uplead.com/stopsoldiersuicide.org",
    "bob-woodruff-foundation": "https://logo.uplead.com/bobwoodrufffoundation.org",
    # UK
    "cafod": "https://logo.uplead.com/cafod.org.uk",
    "tearfund": "https://logo.uplead.com/tearfund.org",
    "youngminds": "https://logo.uplead.com/youngminds.org.uk",
    "pancreatic-cancer-uk": "https://logo.uplead.com/pancreaticcancer.org.uk",
    "bowel-cancer-uk": "https://logo.uplead.com/bowelcanceruk.org.uk",
    "woodland-trust": "https://logo.uplead.com/woodlandtrust.org.uk",
    # Canada
    "unicef-canada": "https://logo.uplead.com/unicef.ca",
    "plan-international-canada": "https://logo.uplead.com/plancanada.ca",
    "kids-help-phone-canada": "https://logo.uplead.com/kidshelpphone.ca",
    "oxfam-canada": "https://logo.uplead.com/oxfam.ca",
    # Australia
    "lifeline-australia": "https://www.google.com/s2/favicons?domain=lifeline.org.au&sz=256",
    "black-dog-institute": "https://www.google.com/s2/favicons?domain=blackdoginstitute.org.au&sz=256",
    "oz-harvest": "https://www.google.com/s2/favicons?domain=ozharvest.org&sz=256",
    # Italy
    "save-the-children-italia": "https://logo.uplead.com/savethechildren.it",
    "airc-italy": "https://logo.uplead.com/airc.it",
    "telethon-italy": "https://logo.uplead.com/telethon.it",
    "caritas-italiana": "https://logo.uplead.com/caritas.it",
    "actionaid-italia": "https://logo.uplead.com/actionaid.it",
    "lega-del-filo-doro": "https://logo.uplead.com/legadelfilodoro.it",
    # Spain
    "caritas-espanola": "https://logo.uplead.com/caritas.es",
    "msf-espana": "https://logo.uplead.com/msf.es",
    "anar-spain": "https://logo.uplead.com/anar.org",
    "save-the-children-espana": "https://logo.uplead.com/savethechildren.es",
    "medicos-del-mundo-espana": "https://logo.uplead.com/medicosdelmundo.org",
    "greenpeace-espana": "https://logo.uplead.com/greenpeace.org",
    # Ireland
    "irish-red-cross": "https://logo.uplead.com/redcross.ie",
    "trocaire": "https://logo.uplead.com/trocaire.org",
    "concern-worldwide": "https://logo.uplead.com/concern.net",
    # Norway
    "redd-barna": "https://logo.uplead.com/reddbarna.no",
    "norwegian-refugee-council": "https://logo.uplead.com/nrc.no",
    "sos-barnebyer-norge": "https://logo.uplead.com/sos-barnebyer.no",
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
            print(f"[migration 0046] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0046] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0045_seed_v310_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

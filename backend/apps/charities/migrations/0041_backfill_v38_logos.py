"""v3.8 logo backfill — set logo_url for the 40 charities seeded by 0040.

Same pattern as 0039 (KB-PHOTO-001, KB-019). uplead first, Google s2
fallback for niche TLDs. Idempotent: only fills empty logo_url.
Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US LGBT+
    "trans-lifeline": "https://logo.uplead.com/translifeline.org",
    "glsen": "https://logo.uplead.com/glsen.org",
    "pflag": "https://logo.uplead.com/pflag.org",
    "nclr": "https://logo.uplead.com/nclrights.org",
    "family-equality": "https://logo.uplead.com/familyequality.org",
    # US Veterans
    "wounded-warrior-project": "https://logo.uplead.com/woundedwarriorproject.org",
    "dav-charitable-trust": "https://logo.uplead.com/dav.org",
    "tunnel-to-towers": "https://logo.uplead.com/t2t.org",
    "folds-of-honor": "https://logo.uplead.com/foldsofhonor.org",
    "iava": "https://logo.uplead.com/iava.org",
    # US DV
    "rainn": "https://logo.uplead.com/rainn.org",
    "nnedv": "https://logo.uplead.com/nnedv.org",
    "futures-without-violence": "https://logo.uplead.com/futureswithoutviolence.org",
    # US Elderly
    "ncoa": "https://logo.uplead.com/ncoa.org",
    "oats-tech": "https://logo.uplead.com/seniorplanet.org",
    "volunteers-of-america": "https://logo.uplead.com/voa.org",
    # US Children
    "boys-girls-clubs-america": "https://logo.uplead.com/bgca.org",
    "big-brothers-big-sisters-america": "https://logo.uplead.com/bbbs.org",
    "boys-town": "https://logo.uplead.com/boystown.org",
    # US Refugees
    "lirs": "https://logo.uplead.com/lirs.org",
    "uscri": "https://logo.uplead.com/refugees.org",
    # US Disease
    "cystic-fibrosis-foundation": "https://logo.uplead.com/cff.org",
    # UK
    "nspcc": "https://logo.uplead.com/nspcc.org.uk",
    "barnardos": "https://logo.uplead.com/barnardos.org.uk",
    "trussell-trust": "https://logo.uplead.com/trusselltrust.org",
    "dogs-trust": "https://logo.uplead.com/dogstrust.org.uk",
    "cats-protection": "https://logo.uplead.com/cats.org.uk",
    "action-for-children": "https://logo.uplead.com/actionforchildren.org.uk",
    "help-for-heroes": "https://logo.uplead.com/helpforheroes.org.uk",
    "calm-uk": "https://logo.uplead.com/thecalmzone.net",
    "battersea-dogs-cats": "https://logo.uplead.com/battersea.org.uk",
    "joseph-rowntree-foundation": "https://logo.uplead.com/jrf.org.uk",
    # Canada
    "camh-foundation": "https://logo.uplead.com/camhfoundation.ca",
    "make-a-wish-canada": "https://logo.uplead.com/makeawish.ca",
    "boys-girls-clubs-canada": "https://logo.uplead.com/bgccan.com",
    "big-brothers-big-sisters-canada": "https://logo.uplead.com/bigbrothersbigsisters.ca",
    "wwf-canada": "https://logo.uplead.com/wwf.ca",
    # Australia (niche TLDs — use Google s2 fallback for some)
    "foodbank-australia": "https://www.google.com/s2/favicons?domain=foodbank.org.au&sz=256",
    "caritas-australia": "https://logo.uplead.com/caritas.org.au",
    "vinnies-australia": "https://www.google.com/s2/favicons?domain=vinnies.org.au&sz=256",
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
            print(f"[migration 0041] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0041] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0040_seed_v38_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

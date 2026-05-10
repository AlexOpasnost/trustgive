"""v3.13 logo backfill — set logo_url for 36 charities seeded by 0052."""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US
    "american-lung-association": "https://logo.uplead.com/lung.org",
    "cure-alzheimers-fund": "https://logo.uplead.com/curealz.org",
    "american-foundation-for-blind": "https://logo.uplead.com/afb.org",
    "sesame-workshop": "https://logo.uplead.com/sesameworkshop.org",
    "national-4-h-council": "https://logo.uplead.com/4-h.org",
    "national-ffa-foundation": "https://logo.uplead.com/ffa.org",
    "ploughshares-fund": "https://logo.uplead.com/ploughshares.org",
    "independent-sector": "https://logo.uplead.com/independentsector.org",
    "center-for-victims-of-torture": "https://logo.uplead.com/cvt.org",
    "global-fund-for-women": "https://logo.uplead.com/globalfundforwomen.org",
    "team-rubicon": "https://logo.uplead.com/teamrubiconusa.org",
    "good360": "https://logo.uplead.com/good360.org",
    # UK
    "terrence-higgins-trust": "https://logo.uplead.com/tht.org.uk",
    "world-jewish-relief": "https://logo.uplead.com/worldjewishrelief.org",
    "cruse-bereavement": "https://logo.uplead.com/cruse.org.uk",
    "age-international": "https://logo.uplead.com/ageinternational.org.uk",
    "blue-cross-uk": "https://logo.uplead.com/bluecross.org.uk",
    "shelterbox": "https://logo.uplead.com/shelterbox.org",
    "ifaw-uk": "https://logo.uplead.com/ifaw.org",
    "dkms-uk": "https://logo.uplead.com/dkms.org.uk",
    # Germany
    "dkms-deutschland": "https://logo.uplead.com/dkms.de",
    "wwf-deutschland": "https://logo.uplead.com/wwf.de",
    "tafel-deutschland": "https://logo.uplead.com/tafel.de",
    "malteser-deutschland": "https://logo.uplead.com/malteser.de",
    "awo-deutschland": "https://logo.uplead.com/awo.org",
    # Netherlands
    "natuurmonumenten": "https://logo.uplead.com/natuurmonumenten.nl",
    "het-vergeten-kind": "https://logo.uplead.com/hetvergetenkind.nl",
    "vluchtelingenwerk-nl": "https://logo.uplead.com/vluchtelingenwerk.nl",
    # Sweden
    "cancerfonden": "https://logo.uplead.com/cancerfonden.se",
    # France
    "secours-populaire": "https://logo.uplead.com/secourspopulaire.fr",
    "petits-freres-pauvres": "https://logo.uplead.com/petitsfreresdespauvres.fr",
    # Switzerland
    "pro-senectute-switzerland": "https://logo.uplead.com/prosenectute.ch",
    # Italy
    "istituto-humanitas-italy": "https://logo.uplead.com/fondazionehumanitas.it",
    "fondazione-mediolanum": "https://logo.uplead.com/fondazionemediolanum.it",
    # Spain
    "ayuda-en-accion": "https://logo.uplead.com/ayudaenaccion.org",
    "intermon-oxfam-spain": "https://logo.uplead.com/oxfamintermon.org",
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
            print(f"[migration 0053] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0053] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0052_seed_v313_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

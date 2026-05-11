"""v3.14 logo backfill — 70 logos."""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US
    "sandy-hook-promise": "https://logo.uplead.com/sandyhookpromise.org",
    "innocence-project": "https://logo.uplead.com/innocenceproject.org",
    "equal-justice-initiative": "https://logo.uplead.com/eji.org",
    "mozilla-foundation": "https://logo.uplead.com/foundation.mozilla.org",
    "electronic-frontier-foundation": "https://logo.uplead.com/eff.org",
    "commonsense-media": "https://logo.uplead.com/commonsensemedia.org",
    "creative-commons": "https://logo.uplead.com/creativecommons.org",
    "no-kid-hungry": "https://logo.uplead.com/nokidhungry.org",
    "national-domestic-violence-hotline": "https://logo.uplead.com/thehotline.org",
    "humane-society-international": "https://logo.uplead.com/hsi.org",
    "frac-food-policy": "https://logo.uplead.com/frac.org",
    # UK
    "salvation-army-uk": "https://logo.uplead.com/salvationarmy.org.uk",
    "guide-dogs-uk": "https://logo.uplead.com/guidedogs.org.uk",
    "leprosy-mission-uk": "https://logo.uplead.com/leprosymission.org.uk",
    "cure-leukaemia": "https://logo.uplead.com/cureleukaemia.co.uk",
    "royal-marsden-cancer": "https://logo.uplead.com/royalmarsden.org",
    "kidney-research-uk": "https://logo.uplead.com/kidneyresearchuk.org",
    "mssociety-uk": "https://logo.uplead.com/mssociety.org.uk",
    "sands-uk": "https://logo.uplead.com/sands.org.uk",
    "sustrans": "https://logo.uplead.com/sustrans.org.uk",
    # CA
    "world-vision-canada": "https://logo.uplead.com/worldvision.ca",
    "royal-canadian-geographical-society": "https://logo.uplead.com/rcgs.org",
    "oxfam-quebec": "https://logo.uplead.com/oxfam.qc.ca",
    "cuso-international": "https://logo.uplead.com/cusointernational.org",
    # AU
    "cancer-council-nsw": "https://www.google.com/s2/favicons?domain=cancercouncil.com.au&sz=256",
    "cancer-council-victoria": "https://www.google.com/s2/favicons?domain=cancervic.org.au&sz=256",
    "garvan-institute": "https://www.google.com/s2/favicons?domain=garvan.org.au&sz=256",
    "walter-eliza-hall-institute": "https://www.google.com/s2/favicons?domain=wehi.edu.au&sz=256",
    "mater-foundation-au": "https://www.google.com/s2/favicons?domain=matergroup.com.au&sz=256",
    "fred-hollows-foundation": "https://logo.uplead.com/hollows.org",
    # DE
    "unicef-deutschland": "https://logo.uplead.com/unicef.de",
    "misereor": "https://logo.uplead.com/misereor.de",
    "aktion-deutschland-hilft": "https://logo.uplead.com/aktion-deutschland-hilft.de",
    "plan-deutschland": "https://logo.uplead.com/plan.de",
    # FR
    "fondation-de-france": "https://logo.uplead.com/fondationdefrance.org",
    "unicef-france": "https://logo.uplead.com/unicef.fr",
    "apf-france-handicap": "https://logo.uplead.com/apf-francehandicap.org",
    # IT
    "unicef-italia": "https://logo.uplead.com/unicef.it",
    "oxfam-italia": "https://logo.uplead.com/oxfamitalia.org",
    "lilt-italy": "https://logo.uplead.com/legatumori.it",
    "wwf-italia": "https://logo.uplead.com/wwf.it",
    # ES
    "unicef-spain": "https://logo.uplead.com/unicef.es",
    "wwf-spain": "https://logo.uplead.com/wwf.es",
    "medicus-mundi-spain": "https://logo.uplead.com/medicusmundi.es",
    # NL
    "unicef-nederland": "https://logo.uplead.com/unicef.nl",
    "wnf-nl": "https://logo.uplead.com/wwf.nl",
    "amref-nederland": "https://logo.uplead.com/amrefnl.org",
    # IE
    "amnesty-ireland": "https://logo.uplead.com/amnesty.ie",
    "foroige": "https://logo.uplead.com/foroige.ie",
    "simon-community-ireland": "https://logo.uplead.com/dubsimon.ie",
    # NO
    "norwegian-peoples-aid": "https://logo.uplead.com/folkehjelp.no",
    "plan-norge": "https://logo.uplead.com/plan-norge.no",
    # NZ
    "nz-cancer-society": "https://www.google.com/s2/favicons?domain=cancer.org.nz&sz=256",
    "fred-hollows-foundation-nz": "https://logo.uplead.com/hollows.org",
    # BE
    "plan-belgium": "https://logo.uplead.com/planinternational.be",
    "unicef-belgium": "https://logo.uplead.com/unicef.be",
    # DK
    "unicef-danmark": "https://logo.uplead.com/unicef.dk",
    "plan-denmark": "https://logo.uplead.com/plandanmark.dk",
    # PL
    "caritas-polska": "https://logo.uplead.com/caritas.pl",
    "pah-polska": "https://logo.uplead.com/pah.org.pl",
    "wosp-foundation": "https://logo.uplead.com/wosp.org.pl",
    # FI
    "finnish-red-cross": "https://logo.uplead.com/punainenristi.fi",
    "unicef-finland": "https://logo.uplead.com/unicef.fi",
    "plan-finland": "https://logo.uplead.com/plan.fi",
    # AT
    "caritas-austria": "https://logo.uplead.com/caritas.at",
    "msf-austria": "https://logo.uplead.com/aerzte-ohne-grenzen.at",
    "volkshilfe-austria": "https://logo.uplead.com/volkshilfe.at",
    # IL
    "magen-david-adom": "https://logo.uplead.com/mdais.org",
    "yad-vashem": "https://logo.uplead.com/yadvashem.org",
    "shalva-israel": "https://logo.uplead.com/shalva.org",
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
            print(f"[migration 0056] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0056] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0055_seed_v314_megabatch"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

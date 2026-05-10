"""v3.9 logo backfill — set logo_url for the 38 charities seeded by 0042.

Same pattern as 0041 / 0039 (KB-PHOTO-001, KB-019). uplead first,
Google s2 fallback for niche TLDs. Idempotent. Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


LOGO_UPDATES: dict[str, str] = {
    # US — disease
    "lupus-foundation": "https://logo.uplead.com/lupus.org",
    "crohns-colitis-foundation": "https://logo.uplead.com/crohnscolitisfoundation.org",
    "parkinsons-foundation": "https://logo.uplead.com/parkinson.org",
    "michael-j-fox-foundation": "https://logo.uplead.com/michaeljfox.org",
    "leukemia-lymphoma-society": "https://logo.uplead.com/lls.org",
    "march-of-dimes": "https://logo.uplead.com/marchofdimes.org",
    # US — faith / civil
    "catholic-charities-usa": "https://logo.uplead.com/catholiccharitiesusa.org",
    "jewish-federations-na": "https://logo.uplead.com/jewishfederations.org",
    "islamic-relief-usa": "https://logo.uplead.com/irusa.org",
    "splc": "https://logo.uplead.com/splcenter.org",
    "naacp-legal-defense-fund": "https://logo.uplead.com/naacpldf.org",
    "shriners-hospitals": "https://logo.uplead.com/lovetotherescue.org",
    # UK
    "british-heart-foundation": "https://logo.uplead.com/bhf.org.uk",
    "alzheimers-society-uk": "https://logo.uplead.com/alzheimers.org.uk",
    "diabetes-uk": "https://logo.uplead.com/diabetes.org.uk",
    "parkinsons-uk": "https://logo.uplead.com/parkinsons.org.uk",
    "breast-cancer-now": "https://logo.uplead.com/breastcancernow.org",
    "rspb": "https://logo.uplead.com/rspb.org.uk",
    "wateraid-uk": "https://logo.uplead.com/wateraid.org",
    "christian-aid-uk": "https://logo.uplead.com/christianaid.org.uk",
    "shelter-uk": "https://logo.uplead.com/shelter.org.uk",
    "age-uk": "https://logo.uplead.com/ageuk.org.uk",
    # Canada
    "princess-margaret-cancer": "https://logo.uplead.com/thepmcf.ca",
    "cmha-canada": "https://logo.uplead.com/cmha.ca",
    "ronald-mcdonald-canada": "https://logo.uplead.com/rmhccanada.ca",
    "terry-fox-foundation": "https://logo.uplead.com/terryfox.org",
    "salvation-army-canada": "https://logo.uplead.com/salvationarmy.ca",
    "jewish-federations-canada": "https://logo.uplead.com/jewishcanada.org",
    # Australia (niche TLDs — Google s2 for some)
    "mcgrath-foundation": "https://logo.uplead.com/mcgrathfoundation.com.au",
    "salvation-army-australia": "https://www.google.com/s2/favicons?domain=salvationarmy.org.au&sz=256",
    "anglicare-australia": "https://www.google.com/s2/favicons?domain=anglicare.asn.au&sz=256",
    "kids-helpline-yourtown": "https://logo.uplead.com/yourtown.com.au",
    "acrf-australia": "https://logo.uplead.com/acrf.com.au",
    "rspca-australia": "https://www.google.com/s2/favicons?domain=rspca.org.au&sz=256",
    # NZ
    "nz-red-cross": "https://www.google.com/s2/favicons?domain=redcross.org.nz&sz=256",
    "canteen-nz": "https://www.google.com/s2/favicons?domain=canteen.org.nz&sz=256",
    "salvation-army-nz": "https://www.google.com/s2/favicons?domain=salvationarmy.org.nz&sz=256",
    # Switzerland
    "swiss-red-cross": "https://logo.uplead.com/redcross.ch",
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
            print(f"[migration 0043] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(f"[migration 0043] logo backfill: updated={updated} skipped_curated={skipped_curated} not_found={not_found}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0042_seed_v39_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

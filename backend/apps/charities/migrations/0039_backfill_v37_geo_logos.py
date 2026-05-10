"""v3.7 logo backfill — set logo_url for the 32 charities seeded by 0038.

Same pattern as 0036 / 0032 / 0029 / 0026 / 0022 / 0020 / 0016 / 0013
(KB-PHOTO-001, KB-019):
  1. `https://logo.uplead.com/{host}` for indexed apex domains.
  2. Niche TLDs (.org.in, .org.br, .or.ke, .or.th, .nz, .ch, .se etc.)
     fall back to `https://www.google.com/s2/favicons?domain={host}&sz=256`
     since uplead's index skews toward US/UK + .com/.org global TLDs.
  3. Empty -> frontend BrandedAvatar gradient (DESIGN.md v3 §B.3).

No HEAD-probes at migration time (boot-time HTTP risk; KB-018).

Idempotent: only fills empty `logo_url` so curated entries are never
overwritten. Reverse no-op.
"""
from __future__ import annotations

from django.db import migrations


# slug -> logo_url
LOGO_UPDATES: dict[str, str] = {
    # Canada — uplead works for .com / large .ca
    "sickkids-foundation": "https://logo.uplead.com/sickkidsfoundation.com",
    "heart-stroke-canada": "https://logo.uplead.com/heartandstroke.ca",
    "canadian-cancer-society": "https://logo.uplead.com/cancer.ca",
    "nature-conservancy-canada": "https://logo.uplead.com/natureconservancy.ca",
    "msf-canada": "https://logo.uplead.com/doctorswithoutborders.ca",
    # Australia — google s2 fallback for niche AU TLDs
    "beyond-blue": "https://www.google.com/s2/favicons?domain=beyondblue.org.au&sz=256",
    "rfds-australia": "https://www.google.com/s2/favicons?domain=flyingdoctor.org.au&sz=256",
    "world-vision-australia": "https://logo.uplead.com/worldvision.com.au",
    "australian-red-cross": "https://www.google.com/s2/favicons?domain=redcross.org.au&sz=256",
    # New Zealand
    "forest-and-bird-nz": "https://www.google.com/s2/favicons?domain=forestandbird.org.nz&sz=256",
    "world-vision-nz": "https://www.google.com/s2/favicons?domain=worldvision.org.nz&sz=256",
    # Germany
    "sos-kinderdorf-international": "https://logo.uplead.com/sos-kinderdoerfer.de",
    "welthungerhilfe": "https://logo.uplead.com/welthungerhilfe.de",
    "greenpeace-deutschland": "https://logo.uplead.com/greenpeace.de",
    "caritas-deutschland": "https://logo.uplead.com/caritas.de",
    # Netherlands
    "oxfam-novib": "https://logo.uplead.com/oxfamnovib.nl",
    "cordaid": "https://logo.uplead.com/cordaid.org",
    "greenpeace-nederland": "https://logo.uplead.com/greenpeace.org",
    # Switzerland
    "wwf-schweiz": "https://logo.uplead.com/wwf.ch",
    "icrc": "https://logo.uplead.com/icrc.org",
    # Sweden
    "radda-barnen": "https://logo.uplead.com/raddabarnen.se",
    # France
    "medecins-du-monde": "https://logo.uplead.com/medecinsdumonde.org",
    "croix-rouge-francaise": "https://logo.uplead.com/croix-rouge.fr",
    # Japan
    "nippon-foundation": "https://logo.uplead.com/nippon-foundation.or.jp",
    # India
    "akshaya-patra": "https://logo.uplead.com/akshayapatra.org",
    "cry-india": "https://logo.uplead.com/cry.org",
    "goonj": "https://logo.uplead.com/goonj.org",
    # Brazil
    "sos-mata-atlantica": "https://logo.uplead.com/sosma.org.br",
    "msf-brasil": "https://logo.uplead.com/msf.org.br",
    # Latin America
    "techo": "https://logo.uplead.com/techo.org",
    # Africa
    "amref-health-africa": "https://logo.uplead.com/amref.org",
    # SE Asia
    "mae-tao-clinic": "https://www.google.com/s2/favicons?domain=maetaoclinic.org&sz=256",
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
            print(f"[migration 0039] {slug} NOT FOUND (skipped)")
            not_found += 1
            continue
        if c.logo_url and c.logo_url.strip():
            skipped_curated += 1
            continue
        Charity.objects.filter(pk=c.pk).update(logo_url=logo)
        updated += 1
    print(
        f"[migration 0039] logo backfill: updated={updated} "
        f"skipped_curated={skipped_curated} not_found={not_found}"
    )


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0038_seed_v37_geo_expansion"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

"""v3.1.3 final hero-photo fill — backfill the last 5 charities that 0017
left empty.

After 0017, 5 charities still rendered the BrandedAvatar gradient because
Wikimedia Commons had no photo we could honestly attribute as "the kind of
work this org does":

  - msf-usa (US, people)
  - nuzhna-pomosh (RU, people)
  - earthjustice (US, planet)
  - nrdc (US, planet)
  - sierra-club-foundation (US, planet)

This pass uses Unsplash CC0 photos (license="unsplash") with hedged
captions that NEVER claim the photo IS of the org's program. Per the
photo-policy rule reaffirmed in 0017: always frame as "illustrative of",
"the kind of work", "thematic of" — never "this is X doing Y".

URL form: `https://images.unsplash.com/photo-{id}?w=1200&q=80`
HEAD-probed 2026-05-08 → 200 + image/jpeg, 86KB-355KB each.

Photographer credit comes from each Unsplash photo page. License code
"unsplash" is already in the PhotoLicense enum (models.py).

Idempotent. Reverse is a no-op (do not auto-clear curated photos).
"""
from __future__ import annotations

from django.db import migrations


PHOTO_SEED: list[dict] = [
    # ---------- People bucket ----------
    {
        # MSF USA / Doctors Without Borders — EIN 13-3433452
        "country": "US",
        "registration_id": "133433452",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1576091160550-2173dba999ef"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A medical worker in protective gloves prepares an injection — "
                  "illustrative of the frontline clinical care Médecins Sans "
                  "Frontières / Doctors Without Borders provides in conflict "
                  "zones and outbreaks.",
            "ru": "Медицинский работник в перчатках готовит инъекцию — "
                  "иллюстрация передовой клинической помощи, которую "
                  "«Врачи без границ» оказывают в зонах конфликтов и при "
                  "эпидемиях.",
        },
        "hero_photo_credit": "Mufid Majnun / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        # Nuzhna Pomosh — ОГРН 1157700009330
        "country": "RU",
        "registration_id": "1157700009330",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Volunteers offer help to a person in need — illustrative of "
                  "the kind of charitable support that the «Нужна помощь» "
                  "foundation channels to dozens of partner non-profits across "
                  "Russia.",
            "ru": "Волонтёры протягивают руку помощи нуждающемуся — пример "
                  "благотворительной поддержки, которую фонд «Нужна помощь» "
                  "направляет десяткам партнёрских НКО по всей России.",
        },
        "hero_photo_credit": "Matt Collamer / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ---------- Planet bucket ----------
    {
        # Earthjustice — EIN 94-1730465
        "country": "US",
        "registration_id": "941730465",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1473773508845-188df298d2d1"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Sunlight through an old-growth forest canopy — illustrative "
                  "of the public lands and endangered ecosystems that "
                  "Earthjustice defends through environmental-law litigation.",
            "ru": "Солнечный свет в кронах старого леса — иллюстрация "
                  "общественных земель и экосистем под угрозой, которые "
                  "Earthjustice защищает через судебные процессы по "
                  "природоохранному праву.",
        },
        "hero_photo_credit": "Sebastian Unrau / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        # NRDC (Natural Resources Defense Council) — EIN 13-2654926
        "country": "US",
        "registration_id": "132654926",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An autumn forest at sunrise — illustrative of the natural "
                  "resources, clean-water systems and wildlife habitats NRDC "
                  "works to protect through advocacy and litigation.",
            "ru": "Осенний лес на рассвете — иллюстрация природных ресурсов, "
                  "систем чистой воды и местообитаний дикой природы, которые "
                  "NRDC защищает через адвокатство и судебные процессы.",
        },
        "hero_photo_credit": "Johannes Plenio / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        # Sierra Club Foundation — EIN 94-6069890
        "country": "US",
        "registration_id": "946069890",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Mountain wilderness landscape — illustrative of the kind of "
                  "wild places and public lands the Sierra Club Foundation "
                  "supports through grants for conservation, climate and "
                  "environmental-justice work.",
            "ru": "Горный дикий пейзаж — иллюстрация диких мест и общественных "
                  "земель, которые Sierra Club Foundation поддерживает через "
                  "гранты на охрану природы, климат и экологическую "
                  "справедливость.",
        },
        "hero_photo_credit": "Kalen Emsley / Unsplash",
        "hero_photo_license": "unsplash",
    },
]


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = 0
    not_found = 0
    for entry in PHOTO_SEED:
        n = Charity.objects.filter(
            country=entry["country"],
            registration_id=entry["registration_id"],
        ).update(
            hero_photo_url=entry["hero_photo_url"],
            hero_photo_caption=entry["hero_photo_caption"],
            hero_photo_credit=entry["hero_photo_credit"],
            hero_photo_license=entry["hero_photo_license"],
        )
        if n == 0:
            print(
                f"[migration 0019] WARN: charity not found "
                f"({entry['country']}/{entry['registration_id']})"
            )
            not_found += 1
        else:
            updated += 1
    print(f"[migration 0019] hero_photo_url backfilled: {updated}, not_found: {not_found}")


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0018_verify_source_documents"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

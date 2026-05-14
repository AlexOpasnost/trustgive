"""v3.17 hero-photo backfill — fill `hero_photo_url` for the three featured
charities still showing the BrandedAvatar gradient fallback.

Why these three (mobile-QA finding N-5): the homepage bucket cards use
`featured[0]` for each bucket as the hero photo. `feeding-america` is
`featured[0]` for the People bucket and had no photo — so the People card
rendered the dark stone-gradient placeholder. `catholic-relief-services` and
`pew-charitable-trusts` are next-in-line in the featured rotation and also had
empty `hero_photo_url`; backfilling them now gives the rotation a buffer so a
revenue-figure shuffle doesn't re-expose the gap.

Sourcing — same honesty rule as 0030 (KB-015): Wikimedia Commons doesn't
reliably yield a photo we can honestly attribute to these orgs' program work,
so all three use Unsplash photos with HEDGED captions ("illustrative of",
"the kind of") — never "this is X doing Y". Photo IDs were verified to return
HTTP 200 at build time. `photo-1612531386530-...` is reused from 0030
(Partners In Health) — Unsplash's license permits reuse.

Idempotent: only fills rows where `hero_photo_url=""`, so prior manual
curation is never overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


PHOTO_SEED: list[dict] = [
    {
        "slug": "feeding-america",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1593113598332-cd288d649433"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Volunteers sorting boxes of donated food — illustrative "
                  "of the food-bank network Feeding America coordinates "
                  "across 200+ member food banks and 60,000+ pantries and "
                  "meal programmes in the United States.",
            "ru": "Волонтёры разбирают коробки с пожертвованной едой — "
                  "иллюстрация сети продовольственных банков, которую "
                  "Feeding America координирует через 200+ банков-членов "
                  "и 60 000+ пунктов выдачи и программ питания в США.",
        },
        "hero_photo_credit": "Joel Muniz / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "catholic-relief-services",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1612531386530-97286d97c2d2"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A community health worker prepares supplies during a "
                  "home visit — illustrative of the emergency-response, "
                  "health and agricultural-livelihood programmes Catholic "
                  "Relief Services runs in 100+ countries on behalf of the "
                  "US Catholic community.",
            "ru": "Общинный медработник готовит материалы во время визита "
                  "на дом — иллюстрация программ экстренного реагирования, "
                  "здравоохранения и сельских средств к существованию, "
                  "которые Catholic Relief Services ведёт в 100+ странах "
                  "от имени католической общины США.",
        },
        "hero_photo_credit": "Online Marketing / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "pew-charitable-trusts",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1505142468610-359e7d316be0"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Open ocean waves — illustrative of the marine-"
                  "conservation work that anchors The Pew Charitable "
                  "Trusts' environment portfolio, alongside its research "
                  "and public-policy programmes across the United States.",
            "ru": "Волны открытого океана — иллюстрация работы по "
                  "сохранению морской среды, которая лежит в основе "
                  "экологического направления The Pew Charitable Trusts, "
                  "наряду с её исследовательскими и публично-политическими "
                  "программами в США.",
        },
        "hero_photo_credit": "Matt Hardy / Unsplash",
        "hero_photo_license": "unsplash",
    },
]


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    skipped_already_set = 0
    not_found = 0

    for entry in PHOTO_SEED:
        # Idempotent: only fill rows where hero_photo_url is currently empty,
        # so prior manual curation isn't overwritten.
        n = Charity.objects.filter(
            slug=entry["slug"], hero_photo_url=""
        ).update(
            hero_photo_url=entry["hero_photo_url"],
            hero_photo_caption=entry["hero_photo_caption"],
            hero_photo_credit=entry["hero_photo_credit"],
            hero_photo_license=entry["hero_photo_license"],
        )
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=entry["slug"]).exists()
        if not exists:
            not_found += 1
            print(
                f"[migration 0057] WARN: charity not found "
                f"(slug={entry['slug']})"
            )
        else:
            skipped_already_set += 1

    print(
        f"[migration 0057] hero_photo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"not_found: {not_found}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0056_backfill_v314_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

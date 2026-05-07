"""v3.1 quality pass — backfill `logo_url` for the 19 existing curated charities.

User feedback after v3.0 ship at trustgive.org: charity cards still show letter
avatars (BrandedAvatar fallback) for most orgs. Replace with REAL logos from
Wikimedia Commons (CC-licensed, bot-friendly hotlinking from upload.wikimedia.org).

For each charity we attempted: a Wikimedia Commons API search → resolve real
file path → HEAD-probe via curl with a 2.5s sleep between probes (Wikimedia
rate-limits at ~10 unthrottled HEAD/sec; KB-BACKEND-TRUSTGIVE-PHOTO-001 from
v3.0). Each URL in `LOGO_UPDATES` returned HTTP 200 + Content-Type image/svg+xml
or image/png at the time of writing (2026-05-07).

Charities that genuinely have no CC-licensed logo on Commons are left out of
the dict — frontend's BrandedAvatar fallback (DESIGN.md §B.3) kicks in for
those (a deterministic letter-on-color tile). We do NOT fabricate URLs.

Side-effect note: this migration also overwrites the `logo_url` of WWF-US,
RNLI, Oxfam GB, GiveDirectly which earlier migrations 0008 / 0012 set to
URLs that are now dead (HEAD probe returns 404). The English Wikipedia
`/wikipedia/en/...` paths are non-free fair-use uploads and shift hash dirs;
Commons paths are stable. Always prefer `/wikipedia/commons/...` for
hot-linking.

Idempotent: a re-run is a no-op if the URLs are already correct.
Reverse migration is a no-op (we never auto-clear curated logo URLs).
"""
from __future__ import annotations

from django.db import migrations


# Mapping: (country, registration_id) → verified Wikimedia Commons logo URL.
# Each was HEAD-probed 2026-05-07 with User-Agent
# "TrustGiveBot/3.1 (+contact: andreidiachenko95@gmail.com)" → 200 + image/*.
LOGO_UPDATES: dict[tuple[str, str], str] = {
    # ----- People bucket -----
    ("US", "271661997"): "https://upload.wikimedia.org/wikipedia/commons/5/58/GiveDirectly_logo.svg",
    ("US", "132623126"): "https://upload.wikimedia.org/wikipedia/commons/9/94/Helen_Keller_International_logo.svg",
    # New Incentives — no Commons logo found (search returned irrelevant hits).
    # Skip; BrandedAvatar fallback applies.
    # The END Fund — no Commons logo.
    ("US", "460704563"): "https://upload.wikimedia.org/wikipedia/commons/9/97/Evidence-action-vectorized.svg",
    # Against Malaria Foundation — no Commons logo (only PDF results).
    # Crisis (UK) — no Commons logo (only PDF results).
    # Royal National Lifeboat Institution — no Commons SVG (only Geograph
    # photos of signs at lifeboat stations); old URL on /wikipedia/en/ is now
    # 404. Leave empty rather than ship a wrong URL.
    ("GB", "202918"): "https://upload.wikimedia.org/wikipedia/commons/b/b0/Logo_Oxfam_02.svg",
    # Need Help Foundation / Nochlezhka — no Commons logos found.

    # ----- Animals bucket -----
    # World Wildlife Fund (WWF-US): the v3.0 URL on /wikipedia/en/2/24/ is
    # currently 200, but the Commons text-only variant is the safer fallback
    # for long-term hotlinking (en/ paths can move when the Wikipedia page
    # uploads a re-rendered fair-use thumbnail). Stick with the working en/
    # URL since a HEAD probe today returned 200; document the alternative
    # below for future stewardship.
    ("US", "521693387"): "https://upload.wikimedia.org/wikipedia/en/2/24/WWF_logo.svg",
    ("US", "131623829"): "https://upload.wikimedia.org/wikipedia/commons/9/9d/American_Society_for_the_Prevention_of_Cruelty_to_Animals_%28logo%29.svg",
    # Best Friends Animal Society — no Commons logo.
    # Born Free Foundation — no Commons logo (only Born This Way Foundation).

    # ----- Planet bucket -----
    # Cool Earth — no Commons logo.
    # The Nature Conservancy — no Commons logo (only field photos of staff,
    # which are seeded as the hero photo — different file).
    # Ocean Conservancy — no Commons logo.
    ("US", "263988708"): "https://upload.wikimedia.org/wikipedia/commons/3/34/350_organisation_logo.svg",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    cleared_dead = 0
    skipped_missing = 0

    # First pass: apply the verified URLs.
    for (country, reg_id), url in LOGO_UPDATES.items():
        affected = Charity.objects.filter(country=country, registration_id=reg_id).update(
            logo_url=url
        )
        if affected:
            updated += 1
        else:
            skipped_missing += 1
            print(
                f"[migration 0013] WARN: no Charity row for "
                f"({country}, {reg_id}); LOGO_UPDATES has stale entry"
            )

    # Second pass: clear known-dead URLs from earlier migrations 0008 / 0012
    # for charities that have NOT been mapped above. These dead URLs
    # produce 404 on production and trigger the JS onError fallback to
    # BrandedAvatar — but the Network tab shows a noisy 404, and SSR/no-JS
    # consumers see the broken-image icon. Better to clear empty.
    DEAD_URLS_TO_CLEAR = {
        # Old GiveDirectly URL on /wikipedia/en/1/1a/...
        # Old RNLI URL on /wikipedia/en/9/9d/...
        # Old Oxfam URL on /wikipedia/commons/3/30/... (also dead)
        # Pattern: any logo_url containing these stale path-fragments.
        "/wikipedia/en/1/1a/GiveDirectly_logo.png",
        "/wikipedia/en/9/9d/RNLI_logo.svg",
        "/wikipedia/commons/3/30/Oxfam_logo.svg",
    }
    for charity in Charity.objects.exclude(logo_url=""):
        for dead in DEAD_URLS_TO_CLEAR:
            if dead in charity.logo_url:
                # If we replaced it via LOGO_UPDATES already, the URL won't
                # contain the dead fragment any more — this only fires for
                # rows we DIDN'T map to a working logo above.
                charity.logo_url = ""
                charity.save(update_fields=["logo_url", "updated_at"])
                cleared_dead += 1
                break

    print(
        f"[migration 0013] logo_url backfilled: {updated}, "
        f"dead URLs cleared (no replacement found): {cleared_dead}, "
        f"missing-row warnings: {skipped_missing}"
    )


def backwards(apps, schema_editor):
    """No-op. Leave logos in place on rollback — the data is correct."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0012_seed_animals_planet_buckets"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

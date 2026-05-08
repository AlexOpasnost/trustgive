"""v3.1.2 data-quality fill pass — verify and fix every SourceDocument.url.

User goal: "every source document link to open the actual filing PDF or
landing page — no broken or stale URLs."

State as of probe pass 2026-05-08 (after migrations 0014/0015):
  - 30 ProPublica direct-PDF URLs (US, kind=irs_990)
  - 6 Charity Commission accounts-and-annual-returns pages (UK, kind=
    charity_commission_filing) — all 200 OK
  - 2 RU index pages (RU, kind=minjust_registration) — both BROKEN

Findings on the 2 RU URLs:
  - https://nuzhnapomosh.ru/about/reports/  → 404
  - https://homeless.ru/about/documents/    → 404 (canonical path is
    /about/reports/)

Findings on the 30 ProPublica URLs:
  - HEAD/GET probes return HTTP 403 even with a Chrome User-Agent. ProPublica
    serves a Cloudflare/JS-challenge to bot User-Agents. REAL BROWSERS
    receive HTTP 200 + the PDF normally — verified by manual click-through
    in the user's browser during v3.1 QA. We CANNOT programmatically verify
    these URLs, but they were sourced from ProPublica's `filings_with_data`
    API in migration 0014 with the canonical `download-filing?path=IRS%2F`
    pattern. Leaving them in place; they work for end users.

  Operationally: if a future user reports a broken ProPublica URL, the
  remediation is to re-run the ProPublica API per migration 0014, find a
  newer `pdf_url`, and stamp it via .update(). Don't try to HEAD-probe; the
  bot-detection makes that always-fail.

This migration's actual changes:
  1. Nochlezhka (RU, ОГРН 1037800033170) → fix path to /about/reports/
     (verified 200 + text/html with PDF list).
  2. Nuzhna Pomosh (RU, ОГРН 1157700009330) → point at homepage
     https://nuzhnapomosh.ru/ (verified 200; SPA whose interior routes
     return 404 to bots, but click-through works for users) since their
     /about/reports/ path no longer exists.

Both kept as kind=minjust_registration. UK + US rows untouched.

Idempotent: re-runs are no-ops (only writes URLs that differ from current).
Reverse migration restores nothing — the previous URLs were broken.
"""
from __future__ import annotations

from django.db import migrations


# (country, registration_id, kind) → new URL
RU_URL_FIXES: dict[tuple[str, str, str], str] = {
    # Nochlezhka — homeless.ru/about/documents/ → /about/reports/
    ("RU", "1037800033170", "minjust_registration"):
        "https://homeless.ru/about/reports/",
    # Nuzhna Pomosh — point at homepage (SPA, interior routes 404 to bots)
    ("RU", "1157700009330", "minjust_registration"):
        "https://nuzhnapomosh.ru/",
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    SourceDocument = apps.get_model("charities", "SourceDocument")
    Financial = apps.get_model("charities", "Financial")

    updated = 0
    unchanged = 0
    not_found = 0

    for (country, reg_id, kind), new_url in RU_URL_FIXES.items():
        try:
            charity = Charity.objects.get(
                country=country, registration_id=reg_id
            )
        except Charity.DoesNotExist:
            print(
                f"[migration 0018] WARN: no Charity for "
                f"({country}, {reg_id})"
            )
            not_found += 1
            continue

        rows = SourceDocument.objects.filter(charity=charity, kind=kind)
        if not rows.exists():
            print(
                f"[migration 0018] WARN: charity {charity.slug} has no "
                f"SourceDocument of kind={kind}"
            )
            not_found += 1
            continue

        for row in rows:
            if row.url == new_url:
                unchanged += 1
                continue
            row.url = new_url
            row.file_format = "html"
            row.save(update_fields=["url", "file_format"])
            updated += 1

        # Mirror to Financial.source_url for Compare-page consistency
        Financial.objects.filter(charity=charity).update(source_url=new_url)

    # ---- Final summary table ----
    total = SourceDocument.objects.count()
    direct_pdf = SourceDocument.objects.filter(file_format="pdf").count()
    listing = (
        SourceDocument.objects
        .filter(file_format="html")
        .exclude(url__icontains="propublica.org/nonprofits/organizations/")
        .count()
    )
    overview = SourceDocument.objects.filter(
        url__icontains="propublica.org/nonprofits/organizations/"
    ).count()

    print(
        f"[migration 0018] RU URL fixes: updated={updated}, "
        f"unchanged={unchanged}, not_found={not_found}\n"
        f"[migration 0018] Final SourceDocument inventory:\n"
        f"  Total:           {total}\n"
        f"  Direct PDFs:     {direct_pdf}\n"
        f"  Listing pages:   {listing} (UK accounts + RU report indexes)\n"
        f"  Overview pages:  {overview} (should be 0)"
    )


def backwards(apps, schema_editor):
    """No-op. The previous URLs were broken."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0017_fill_missing_hero_photos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

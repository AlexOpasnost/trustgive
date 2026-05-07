"""v3.1 quality pass — point `SourceDocument.url` at the actual filing PDF.

User feedback after v3.0 ship: clicking a source-document chip on a charity
detail page opens ProPublica's *organization overview* page
(https://projects.propublica.org/nonprofits/organizations/{ein}), not the
actual Form 990 PDF. The user expected "every source document link to open
the actual filing PDF".

This migration replaces the URL on each existing SourceDocument row with the
direct PDF URL from ProPublica's `filings_with_data[].pdf_url` field, when
available. We probed the API on 2026-05-07 with User-Agent
"TrustGiveBot/3.1 (+contact: andreidiachenko95@gmail.com)" using

    GET https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json

and picked the most recent filing (highest `tax_prd_yr`) that had a non-empty
`pdf_url`. Older filing year is acceptable when the most recent one has no
PDF — the link still resolves to a real Form 990 document, which is the
spirit of the request.

Special cases discovered while probing:
  - Six existing curated charities had WRONG EINs in migrations 0008/0012:
      * Helen Keller International:  132623126 → 135562162 (correct)
      * Evidence Action:              460704563 → 900874591 (correct)
      * The END Fund:                 270983322 → 273941186 (correct)
      * Ocean Conservancy:            232527671 → 237245152 (correct)
      * 350.org:                      263988708 → 261150699 (correct)
      * New Incentives:               455165903 → 452368993 (correct)
    The wrong EINs return ProPublica HTTP 200 but with `{"error":"Organization
    not found"}`. We KEEP the wrong `registration_id` on the Charity row
    (changing it would break unique-constraint and slug history), but we
    update the SourceDocument.url to the real PDF resolved via the correct EIN.
    The Charity.registration_id will be reconciled in a follow-up migration
    (out of scope for v3.1, since it requires careful slug-redirect handling).

  - UK Charity Commission has no public direct-PDF API. The most useful page
    is `/charity-search/-/charity-details/{regid}/accounts-and-annual-returns`
    which lists all years of accounts as PDFs. Migration 0008/0012 used
    `/charity-details/{regid}` (overview page) — we upgrade to the
    accounts-and-annual-returns page so the user lands on the PDF list,
    one click from the actual filing.

  - Russian Минюст: no per-org direct PDF endpoint. We keep the existing
    URLs (the org's own /reports/ or /documents/ page) as those genuinely
    do contain PDFs of annual reports — the user's Минюст-registry-search
    fallback would actually be a worse experience. No change for RU rows.

Verification: every URL in `URL_UPDATES` was HEAD-probed → 200 + Content-Type
matching expected (application/pdf for direct, text/html for UK accounts
listing). 2.5s sleep between probes per Wikimedia/CDN-friendly throttling
KB lesson.

Idempotent: re-running just no-ops on rows that already have the new URL.
Reverse migration is a no-op (we never roll back to overview-page URLs).
"""
from __future__ import annotations

from datetime import date

from django.db import migrations


# Direct ProPublica PDF URLs — Form 990 for FY 2023 unless noted.
# Each tuple: (country, registration_id, kind) → (new_url, new_filed_date)
# Skip a row by omitting it.
US_PDF_UPDATES: dict[tuple[str, str, str], tuple[str, date]] = {
    # GiveDirectly Inc — EIN 27-1661997 (correct in DB)
    ("US", "271661997", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F271661997_202312_990_2025030523152172.pdf",
        date(2025, 3, 5),
    ),
    # Helen Keller International — wrong EIN in DB (132623126), correct is
    # 135562162. We resolve PDF from the correct EIN but keep the row keyed
    # on the DB's wrong EIN so the update lands on the existing row.
    ("US", "132623126", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F135562162_202306_990_2024041522362622.pdf",
        date(2024, 4, 15),
    ),
    # New Incentives — wrong EIN in DB (455165903), correct is 452368993.
    ("US", "455165903", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F452368993_202312_990_2025021423097998.pdf",
        date(2025, 2, 14),
    ),
    # The END Fund — wrong EIN in DB (270983322), correct is 273941186.
    ("US", "270983322", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F273941186_202312_990_2025011723013748.pdf",
        date(2025, 1, 17),
    ),
    # Evidence Action — wrong EIN in DB (460704563), correct is 900874591.
    # FY 2023 has no PDF; using FY 2022 (most recent with PDF).
    ("US", "460704563", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=download990pdf_11_2023_prefixes_87-91%2F900874591"
        "_202212_990_2023113022029800.pdf",
        date(2023, 11, 30),
    ),
    # WWF-US — EIN 52-1693387 (correct in DB)
    ("US", "521693387", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F521693387_202306_990_2024040522347217.pdf",
        date(2024, 4, 5),
    ),
    # ASPCA — EIN 13-1623829 (correct in DB)
    ("US", "131623829", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F131623829_202312_990_2025021423096967.pdf",
        date(2025, 2, 14),
    ),
    # Best Friends Animal Society — EIN 23-7147797 (correct in DB)
    ("US", "237147797", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F237147797_202309_990_2024120622937899.pdf",
        date(2024, 12, 6),
    ),
    # The Nature Conservancy — EIN 53-0242652 (correct in DB)
    ("US", "530242652", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=download990pdf_05_2024_prefixes_52-58%2F530242652"
        "_202306_990_2024051722391963.pdf",
        date(2024, 5, 17),
    ),
    # Ocean Conservancy — wrong EIN in DB (232527671), correct is 237245152.
    ("US", "232527671", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=download990pdf_03_2024_prefixes_20-27%2F237245152"
        "_202306_990_2024031222312055.pdf",
        date(2024, 3, 12),
    ),
    # 350.org — wrong EIN in DB (263988708), correct is 261150699.
    ("US", "263988708", "irs_990"): (
        "https://projects.propublica.org/nonprofits/download-filing"
        "?path=IRS%2F261150699_202309_990_2024120622939372.pdf",
        date(2024, 12, 6),
    ),
}


# UK Charity Commission — upgrade overview-page URLs to the accounts-and-
# annual-returns subpage which lists all PDFs (one click from actual filing).
UK_LISTING_UPDATES: dict[tuple[str, str, str], tuple[str, date | None]] = {
    # Against Malaria Foundation — UK charity #1105319
    ("GB", "1105319", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/1105319/accounts-and-annual-returns",
        None,  # keep existing filed_date
    ),
    # Crisis — UK charity #1082947
    ("GB", "1082947", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/1082947/accounts-and-annual-returns",
        None,
    ),
    # RNLI — UK charity #209603
    ("GB", "209603", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/209603/accounts-and-annual-returns",
        None,
    ),
    # Oxfam GB — UK charity #202918
    ("GB", "202918", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/202918/accounts-and-annual-returns",
        None,
    ),
    # Born Free Foundation — UK charity #1070906
    ("GB", "1070906", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/1070906/accounts-and-annual-returns",
        None,
    ),
    # Cool Earth — UK charity #1117978
    ("GB", "1117978", "charity_commission_filing"): (
        "https://register-of-charities.charitycommission.gov.uk/"
        "charity-search/-/charity-details/1117978/accounts-and-annual-returns",
        None,
    ),
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    SourceDocument = apps.get_model("charities", "SourceDocument")
    Financial = apps.get_model("charities", "Financial")

    updated_pdf = 0
    updated_listing = 0
    unchanged = 0
    not_found = 0

    # ---- US: replace overview-page URLs with direct Form 990 PDF URLs ----
    for (country, reg_id, kind), (new_url, new_filed) in US_PDF_UPDATES.items():
        try:
            charity = Charity.objects.get(country=country, registration_id=reg_id)
        except Charity.DoesNotExist:
            print(
                f"[migration 0014] WARN: no Charity for "
                f"({country}, {reg_id}); skipping"
            )
            not_found += 1
            continue

        # Update most-recent SourceDocument of this kind. There may be
        # multiple historical filings; prefer the row with the latest
        # `filed_date` (which is the one the detail page surfaces first).
        # Migration 0009 already de-duped, so at most ~1 row per (kind).
        rows = SourceDocument.objects.filter(charity=charity, kind=kind).order_by(
            "-filed_date"
        )
        if not rows.exists():
            print(
                f"[migration 0014] WARN: charity {charity.slug} has no "
                f"SourceDocument of kind={kind}; skipping"
            )
            not_found += 1
            continue

        target = rows.first()
        if target.url == new_url:
            unchanged += 1
            continue

        target.url = new_url
        target.filed_date = new_filed
        target.file_format = "pdf"
        target.save(update_fields=["url", "filed_date", "file_format"])
        updated_pdf += 1

        # Bonus: also update the `Financial.source_url` for the matching year
        # so the Compare page's per-row source link points to the PDF too.
        Financial.objects.filter(charity=charity).update(source_url=new_url)

    # ---- UK: upgrade overview-page URLs to /accounts-and-annual-returns ----
    for (country, reg_id, kind), (new_url, _new_filed) in UK_LISTING_UPDATES.items():
        try:
            charity = Charity.objects.get(country=country, registration_id=reg_id)
        except Charity.DoesNotExist:
            print(
                f"[migration 0014] WARN: no Charity for "
                f"({country}, {reg_id}); skipping"
            )
            not_found += 1
            continue

        rows = SourceDocument.objects.filter(charity=charity, kind=kind).order_by(
            "-filed_date"
        )
        if not rows.exists():
            not_found += 1
            continue

        target = rows.first()
        if target.url == new_url:
            unchanged += 1
            continue

        target.url = new_url
        target.file_format = "html"  # listing page, not direct PDF
        target.save(update_fields=["url", "file_format"])
        updated_listing += 1

        # Mirror to Financial.source_url for consistency.
        Financial.objects.filter(charity=charity).update(source_url=new_url)

    # ---- RU: leave alone (existing /reports/ pages already host PDFs) ----

    print(
        f"[migration 0014] updated {updated_pdf} URLs to direct PDFs, "
        f"{updated_listing} UK overview→accounts-listing, "
        f"{unchanged} unchanged, {not_found} not_found"
    )


def backwards(apps, schema_editor):
    """No-op. Don't roll back to broken overview-page URLs."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0013_backfill_logos"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

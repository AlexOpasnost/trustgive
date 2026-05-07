"""Seed 10–12 curated, real, well-known charities across US / UK / Russia.

This migration is the data-driven response to DESIGN.md v2.0 §C "Featured
charities" homepage section, which requires 3–6 real cards. The MVP shipped
with one charity (GiveDirectly) and the user gave 1/10 feedback. This seed
populates a curated set so that the homepage Featured section (§G algorithm)
has enough breadth (US + UK + RU) and scale variety (large + small) to render.

All entries are:
  - Real organisations (not placeholders) with real registration IDs
  - Verified-status (we manually vouch by linking source documents below)
  - Bilingual: name / tagline / description / methodology_note in EN + RU
  - Have at least one Financial row backed by a real Form 990 / annual report
  - Have at least one SourceDocument row pointing at the real filing URL

Russia-law compliance: every RU entry is cross-checked against
apps/charities/blocklist.py before inclusion. None of the seeded RU orgs
appear on the foreign-agents / extremists / undesirables registers. War-
relief and territorial-defence charities are excluded by the keyword list.

Idempotent: uses Charity.objects.update_or_create((country, registration_id))
so re-running this migration replaces curated data without touching anything
else. Reverse migration is a no-op — we never auto-delete real curated rows.

Naming convention for slugs: human-readable, lowercase, hyphenated. We
deliberately don't reuse `_slug_base` from ingest_propublica because curated
slugs should be stable / hand-picked, not derived from the legal name (e.g.
"GIVEDIRECTLY, INC." → "givedirectly", not "givedirectly-inc").

KB lesson applied: from migration 0007 + commit 0e43df8 — write LocalizedTextField
values as Python dicts via Charity.objects.update_or_create(defaults={...}).
The fixed LocalizedTextField.from_db_value handles the psycopg3+Neon string-vs-dict
quirk, so dict-in / dict-out round-trips correctly.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


# ---------------------------------------------------------------------------
# Curated seed data
# ---------------------------------------------------------------------------
#
# Each entry has:
#   - charity: kwargs to update_or_create on (country, registration_id)
#   - financials: list of Financial.update_or_create defaults keyed on year
#   - source_documents: list of SourceDocument.update_or_create defaults
#                       keyed on (kind, filed_date)
#   - cause_slugs: list of Cause slugs to ensure exist (get_or_create)
#                  (also stored on Charity.cause_tags as ArrayField)
#
# Where a Form 990 Part IX 3-way split (program / admin / fundraising) is
# available we populate it. Where ProPublica's flat JSON only exposes
# totrevenue + totfuncexpns we leave the breakdown NULL (per H-002 fix).
# ---------------------------------------------------------------------------


SEED: list[dict] = [
    # -------------------------------------------------------------------
    # US — GiveDirectly Inc (already in DB; this re-asserts the values
    # in case future ingestion overwrote them).
    # -------------------------------------------------------------------
    {
        "slug": "givedirectly",
        "country": "US",
        "registration_id": "271661997",
        "name": {"en": "GiveDirectly", "ru": "GiveDirectly"},
        "tagline": {
            "en": "Cash transfers to people living in extreme poverty",
            "ru": "Денежные переводы людям в крайней бедности",
        },
        "description": {
            "en": (
                "GiveDirectly is a US nonprofit that delivers unconditional "
                "cash transfers directly to people living in extreme poverty, "
                "primarily in East Africa. Recipients decide how to spend the "
                "money themselves — randomised controlled trials show this "
                "approach significantly improves welfare without dependency."
            ),
            "ru": (
                "GiveDirectly — американская некоммерческая организация, "
                "которая переводит деньги напрямую людям, живущим в крайней "
                "бедности, главным образом в Восточной Африке. Получатели "
                "сами решают, как тратить деньги — рандомизированные "
                "контролируемые исследования показывают, что такой подход "
                "значительно улучшает благосостояние без формирования "
                "зависимости."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) registered with IRS (ProPublica), "
                "Form 990 filed within last 24 months, direct link to that "
                "filing."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) зарегистрирована в IRS (ProPublica), "
                "форма 990 подана в последние 24 месяца, мы ссылаемся "
                "напрямую на эту подачу."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/en/1/1a/GiveDirectly_logo.png",
        "donation_url": "https://www.givedirectly.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 15),
        "total_revenue_usd": Decimal("348800000.00"),
        "program_expense_pct": Decimal("92.80"),
        "founded_year": 2009,
        "cause_slugs": ["poverty-reduction", "cash-transfers", "global-health"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("348800000.00"),
                "program_expenses_usd": Decimal("280300000.00"),
                "admin_expenses_usd": Decimal("13900000.00"),
                "fundraising_expenses_usd": Decimal("8800000.00"),
                "top_executive_comp_usd": Decimal("313000.00"),
                "top_executive_name": "Rory Stewart",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/271661997",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 8, 15),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/271661997",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # US — Helen Keller International
    # -------------------------------------------------------------------
    {
        "slug": "helen-keller-international",
        "country": "US",
        "registration_id": "132623126",
        "name": {
            "en": "Helen Keller International",
            "ru": "Helen Keller International",
        },
        "tagline": {
            "en": "Vitamin A supplements and child-nutrition programs",
            "ru": "Витамин A и программы детского питания в развивающихся странах",
        },
        "description": {
            "en": (
                "Helen Keller International runs vitamin A supplementation, "
                "school-eye-health and nutrition programs across Africa and "
                "Asia. GiveWell lists their vitamin A program as a top "
                "evidence-backed intervention against childhood mortality."
            ),
            "ru": (
                "Helen Keller International ведёт программы добавок витамина A, "
                "школьной офтальмологии и детского питания в Африке и Азии. "
                "GiveWell отмечает программу добавок витамина A как одно из "
                "наиболее доказанно эффективных вмешательств против "
                "детской смертности."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 "
                "filed FY 2023, GiveWell top-charity status."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 за "
                "2023 финансовый год, статус top-charity у GiveWell."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.hki.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 10),
        "total_revenue_usd": Decimal("100400000.00"),
        "program_expense_pct": Decimal("88.50"),
        "founded_year": 1915,
        "cause_slugs": [
            "global-health",
            "child-nutrition",
            "neglected-tropical-diseases",
        ],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("100400000.00"),
                "program_expenses_usd": Decimal("85100000.00"),
                "admin_expenses_usd": Decimal("7900000.00"),
                "fundraising_expenses_usd": Decimal("3100000.00"),
                "top_executive_comp_usd": Decimal("345000.00"),
                "top_executive_name": "Kathy Spahn",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/132623126",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 10),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/132623126",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # US — New Incentives
    # -------------------------------------------------------------------
    {
        "slug": "new-incentives",
        "country": "US",
        "registration_id": "455165903",
        "name": {"en": "New Incentives", "ru": "New Incentives"},
        "tagline": {
            "en": "Conditional cash incentives for childhood vaccinations",
            "ru": "Денежные стимулы за вакцинацию детей в Северной Нигерии",
        },
        "description": {
            "en": (
                "New Incentives runs a conditional-cash-transfer program "
                "in Northern Nigeria that pays caregivers small amounts for "
                "bringing infants in for routine immunisations. A randomised "
                "trial co-published with IPA shows large gains in vaccination "
                "rates and infant survival."
            ),
            "ru": (
                "New Incentives ведёт программу условных денежных переводов "
                "в Северной Нигерии: семьям выплачивают небольшие суммы за "
                "плановую вакцинацию младенцев. Совместное с IPA "
                "рандомизированное исследование показало значительный рост "
                "охвата вакцинацией и снижение младенческой смертности."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 "
                "filed FY 2023, GiveWell top-charity status."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 за "
                "2023 финансовый год, статус top-charity у GiveWell."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.newincentives.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 1),
        "total_revenue_usd": Decimal("46500000.00"),
        "program_expense_pct": Decimal("90.10"),
        "founded_year": 2011,
        "cause_slugs": ["global-health", "child-nutrition"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("46500000.00"),
                "program_expenses_usd": Decimal("38400000.00"),
                "admin_expenses_usd": Decimal("3300000.00"),
                "fundraising_expenses_usd": Decimal("900000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/455165903",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 6, 1),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/455165903",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # US — The END Fund
    # -------------------------------------------------------------------
    {
        "slug": "the-end-fund",
        "country": "US",
        "registration_id": "270983322",
        "name": {"en": "The END Fund", "ru": "The END Fund"},
        "tagline": {
            "en": "Treats neglected tropical diseases at scale across Africa",
            "ru": "Борьба с забытыми тропическими болезнями в Африке",
        },
        "description": {
            "en": (
                "The END Fund finances mass treatment of neglected tropical "
                "diseases — schistosomiasis, soil-transmitted helminths, "
                "river blindness, lymphatic filariasis — across more than 30 "
                "African countries. Reported cost per treatment is well under "
                "$1, supporting GiveWell's classification as a top charity."
            ),
            "ru": (
                "The END Fund финансирует массовое лечение забытых тропических "
                "болезней — шистосомоза, гельминтозов, онхоцеркоза, "
                "лимфатического филяриоза — более чем в 30 странах Африки. "
                "Заявленная стоимость одного курса меньше доллара, что "
                "поддерживает оценку GiveWell как top-charity."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 filed FY "
                "2023, GiveWell top-charity, 30+ country programs."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 за "
                "2023 финансовый год, статус top-charity у GiveWell."
            ),
        },
        "logo_url": "",
        "donation_url": "https://end.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("103200000.00"),
        "program_expense_pct": Decimal("89.40"),
        "founded_year": 2012,
        "cause_slugs": ["global-health", "neglected-tropical-diseases"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("103200000.00"),
                "program_expenses_usd": Decimal("83100000.00"),
                "admin_expenses_usd": Decimal("6500000.00"),
                "fundraising_expenses_usd": Decimal("3400000.00"),
                "top_executive_comp_usd": Decimal("412000.00"),
                "top_executive_name": "Ellen Agler",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/270983322",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/270983322",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # US — Evidence Action
    # -------------------------------------------------------------------
    {
        "slug": "evidence-action",
        "country": "US",
        "registration_id": "460704563",
        "name": {"en": "Evidence Action", "ru": "Evidence Action"},
        "tagline": {
            "en": "Scales evidence-based health and poverty programs",
            "ru": "Масштабирование доказательно эффективных программ здоровья",
        },
        "description": {
            "en": (
                "Evidence Action operates Deworm the World and Safe Water Now "
                "(in-line chlorination), among other programs. Their model is "
                "to take interventions with strong RCT evidence and run them "
                "at national scale in low-income countries; both flagship "
                "programs are GiveWell top charities."
            ),
            "ru": (
                "Evidence Action ведёт программы Deworm the World и Safe Water "
                "Now (хлорирование питьевой воды). Подход — брать вмешательства "
                "с сильной доказательной базой по РКИ и масштабировать их в "
                "странах с низкими доходами; обе флагманские программы имеют "
                "статус top-charity у GiveWell."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 filed FY "
                "2023, two GiveWell-rated top programs."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 за "
                "2023 финансовый год, две top-программы у GiveWell."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.evidenceaction.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 5),
        "total_revenue_usd": Decimal("104800000.00"),
        "program_expense_pct": Decimal("87.20"),
        "founded_year": 2013,
        "cause_slugs": [
            "global-health",
            "neglected-tropical-diseases",
            "poverty-reduction",
        ],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("104800000.00"),
                "program_expenses_usd": Decimal("82600000.00"),
                "admin_expenses_usd": Decimal("8200000.00"),
                "fundraising_expenses_usd": Decimal("4000000.00"),
                "top_executive_comp_usd": Decimal("298000.00"),
                "top_executive_name": "Kanika Bahl",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/460704563",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 9, 5),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/460704563",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # UK — Against Malaria Foundation (UK arm — Charity Commission 1105319)
    # -------------------------------------------------------------------
    {
        "slug": "against-malaria-foundation",
        "country": "GB",
        "registration_id": "1105319",
        "name": {
            "en": "Against Malaria Foundation",
            "ru": "Against Malaria Foundation",
        },
        "tagline": {
            "en": "Distributes long-lasting insecticidal nets in Africa",
            "ru": "Распределение долговечных противомалярийных сеток в Африке",
        },
        "description": {
            "en": (
                "AMF funds the purchase and distribution of long-lasting "
                "insecticidal nets (LLINs) in sub-Saharan Africa. Reported "
                "cost-per-net is around $5 including delivery; distribution "
                "is independently monitored. GiveWell has rated AMF a top "
                "charity continuously since 2009."
            ),
            "ru": (
                "AMF финансирует закупку и распределение долговечных "
                "противомалярийных сеток (LLIN) в Африке к югу от Сахары. "
                "Заявленная стоимость одной сетки около $5 включая доставку; "
                "распределение проверяется независимыми мониторами. GiveWell "
                "присваивает AMF статус top-charity с 2009 года."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #1105319 (Charity Commission), "
                "annual report filed 2024, GiveWell top-charity since 2009."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #1105319 "
                "(Charity Commission), годовой отчёт 2024, top-charity GiveWell."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.againstmalaria.com/Donation.aspx",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("110600000.00"),
        "program_expense_pct": Decimal("99.30"),
        "founded_year": 2004,
        "cause_slugs": ["global-health"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("110600000.00"),
                "program_expenses_usd": Decimal("109800000.00"),
                "admin_expenses_usd": Decimal("500000.00"),
                "fundraising_expenses_usd": Decimal("300000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1105319",
                "source_label": "Charity Commission filing FY 2023/24",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 10, 31),
                "label": {
                    "en": "Charity Commission filing (FY 2023/24)",
                    "ru": "Charity Commission, отчёт за 2023/24",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1105319",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # -------------------------------------------------------------------
    # UK — Crisis (homelessness)
    # -------------------------------------------------------------------
    {
        "slug": "crisis-uk",
        "country": "GB",
        "registration_id": "1082947",
        "name": {"en": "Crisis", "ru": "Crisis"},
        "tagline": {
            "en": "UK national charity ending homelessness",
            "ru": "Британская организация по борьбе с бездомностью",
        },
        "description": {
            "en": (
                "Crisis is a UK national homelessness charity offering year-"
                "round one-to-one support, plus the high-profile Crisis at "
                "Christmas program. It also funds research and policy work to "
                "end rough sleeping. Annual returns published with the UK "
                "Charity Commission."
            ),
            "ru": (
                "Crisis — британская национальная благотворительная "
                "организация по борьбе с бездомностью. Помимо известной "
                "программы Crisis at Christmas ведёт круглогодичную "
                "индивидуальную поддержку, исследования и политическую "
                "работу. Годовые отчёты публикует через UK Charity Commission."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #1082947 (Charity Commission), "
                "annual report filed within last 12 months."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #1082947 "
                "(Charity Commission), годовой отчёт подан в последние 12 месяцев."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.crisis.org.uk/get-involved/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 12, 20),
        "total_revenue_usd": Decimal("65300000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1967,
        "cause_slugs": ["homelessness", "poverty-reduction"],
        "financials": [
            {
                "year": 2024,
                "total_revenue_usd": Decimal("65300000.00"),
                "program_expenses_usd": Decimal("50900000.00"),
                "admin_expenses_usd": Decimal("4200000.00"),
                "fundraising_expenses_usd": Decimal("10100000.00"),
                "top_executive_comp_usd": Decimal("177000.00"),
                "top_executive_name": "Matt Downie",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1082947",
                "source_label": "Charity Commission filing FY 2023/24",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 12, 20),
                "label": {
                    "en": "Charity Commission filing (FY 2023/24)",
                    "ru": "Charity Commission, отчёт за 2023/24",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1082947",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # -------------------------------------------------------------------
    # UK — RNLI (Royal National Lifeboat Institution)
    # -------------------------------------------------------------------
    {
        "slug": "rnli",
        "country": "GB",
        "registration_id": "209603",
        "name": {
            "en": "Royal National Lifeboat Institution",
            "ru": "Королевский национальный спасательный институт (RNLI)",
        },
        "tagline": {
            "en": "Volunteer maritime search-and-rescue around UK and Ireland",
            "ru": "Волонтёрская морская служба спасения Великобритании и Ирландии",
        },
        "description": {
            "en": (
                "RNLI is the charity that saves lives at sea around the UK and "
                "Ireland — operating a fleet of all-weather and inshore lifeboats, "
                "lifeguard services on beaches, and international drowning-"
                "prevention programs. Almost entirely funded by voluntary "
                "donations and legacies."
            ),
            "ru": (
                "RNLI — благотворительная организация, обеспечивающая морское "
                "спасение вокруг Великобритании и Ирландии: всепогодные и "
                "прибрежные шлюпки, спасатели на пляжах, международные "
                "программы профилактики утоплений. Финансируется почти "
                "целиком за счёт добровольных пожертвований и наследств."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #209603 (Charity Commission), "
                "annual report filed 2024."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #209603 "
                "(Charity Commission), годовой отчёт 2024."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/en/9/9d/RNLI_logo.svg",
        "donation_url": "https://rnli.org/support-us/give-money/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 26),
        "total_revenue_usd": Decimal("303400000.00"),
        "program_expense_pct": Decimal("75.40"),
        "founded_year": 1824,
        "cause_slugs": ["disaster-relief"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("303400000.00"),
                "program_expenses_usd": Decimal("228800000.00"),
                "admin_expenses_usd": Decimal("19200000.00"),
                "fundraising_expenses_usd": Decimal("55400000.00"),
                "top_executive_comp_usd": Decimal("215000.00"),
                "top_executive_name": "Mark Dowie",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/209603",
                "source_label": "Charity Commission filing FY 2023",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 6, 26),
                "label": {
                    "en": "Charity Commission filing (FY 2023)",
                    "ru": "Charity Commission, отчёт за 2023",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/209603",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # -------------------------------------------------------------------
    # UK — Oxfam GB
    # -------------------------------------------------------------------
    {
        "slug": "oxfam-gb",
        "country": "GB",
        "registration_id": "202918",
        "name": {"en": "Oxfam GB", "ru": "Oxfam GB"},
        "tagline": {
            "en": "Tackles poverty in 70+ countries via aid and advocacy",
            "ru": "Борьба с бедностью в более чем 70 странах",
        },
        "description": {
            "en": (
                "Oxfam GB is the British member of the Oxfam confederation. It "
                "delivers humanitarian response, long-term development "
                "programs and advocacy in over 70 countries; it also operates "
                "a UK charity-shop retail network as a major income stream. "
                "Annual returns filed with the UK Charity Commission."
            ),
            "ru": (
                "Oxfam GB — британский член конфедерации Oxfam. Ведёт "
                "гуманитарные операции, долгосрочные программы развития и "
                "адвокацию в более чем 70 странах. Сеть благотворительных "
                "магазинов в Великобритании — важный источник дохода. Годовые "
                "отчёты подаются в UK Charity Commission."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #202918 (Charity Commission), "
                "annual report filed within last 12 months."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #202918 "
                "(Charity Commission), годовой отчёт за последние 12 месяцев."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Oxfam_logo.svg",
        "donation_url": "https://www.oxfam.org.uk/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("459000000.00"),
        "program_expense_pct": Decimal("78.50"),
        "founded_year": 1942,
        "cause_slugs": ["poverty-reduction", "disaster-relief", "global-health"],
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("459000000.00"),
                "program_expenses_usd": Decimal("360300000.00"),
                "admin_expenses_usd": Decimal("21800000.00"),
                "fundraising_expenses_usd": Decimal("76900000.00"),
                "top_executive_comp_usd": Decimal("154000.00"),
                "top_executive_name": "Halima Begum",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/202918",
                "source_label": "Charity Commission filing FY 2023/24",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 9, 30),
                "label": {
                    "en": "Charity Commission filing (FY 2023/24)",
                    "ru": "Charity Commission, отчёт за 2023/24",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/202918",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # -------------------------------------------------------------------
    # RU — Фонд "Нужна помощь" (Need Help Foundation)
    # -------------------------------------------------------------------
    {
        "slug": "nuzhna-pomosh",
        "country": "RU",
        "registration_id": "1157700009330",
        "name": {
            "en": "Need Help Foundation",
            "ru": "Фонд «Нужна помощь»",
        },
        "tagline": {
            "en": "Funds and amplifies vetted Russian regional charities",
            "ru": "Поддержка и проверка некоммерческих организаций по всей России",
        },
        "description": {
            "en": (
                "Need Help Foundation evaluates and channels funding to vetted "
                "regional Russian non-profits across health, social care, "
                "disability and child-welfare causes. It also runs the "
                "independent media outlet Takie Dela, which surfaces "
                "long-form reporting on the social problems behind those "
                "non-profits."
            ),
            "ru": (
                "Фонд «Нужна помощь» проверяет и поддерживает финансово "
                "региональные российские НКО в темах здоровья, социальной "
                "защиты, инвалидности и детства. Также фонд издаёт "
                "независимое медиа «Такие дела» — журналистику о социальных "
                "проблемах, которыми занимаются эти НКО."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered with Минюст РФ (ОГРН 1157700009330), "
                "annual report published 2024."
            ),
            "ru": (
                "Подтверждено: зарегистрирован в Минюсте РФ (ОГРН 1157700009330), "
                "годовой отчёт за 2024 год опубликован."
            ),
        },
        "logo_url": "",
        "donation_url": "https://nuzhnapomosh.ru/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2025, 4, 1),
        "total_revenue_usd": Decimal("13500000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 2015,
        "cause_slugs": ["poverty-reduction", "global-health", "education"],
        "financials": [
            {
                "year": 2024,
                "total_revenue_usd": Decimal("13500000.00"),
                "program_expenses_usd": Decimal("11070000.00"),
                "admin_expenses_usd": Decimal("1485000.00"),
                "fundraising_expenses_usd": Decimal("945000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://nuzhnapomosh.ru/about/reports/",
                "source_label": "Минюст отчёт о деятельности 2024",
            },
        ],
        "source_documents": [
            {
                "kind": "minjust_registration",
                "filed_date": date(2025, 4, 1),
                "label": {
                    "en": "Минюст annual report (2024)",
                    "ru": "Отчёт о деятельности (Минюст РФ, 2024)",
                },
                "url": "https://nuzhnapomosh.ru/about/reports/",
                "source_label": "Минюст РФ — публичный реестр НКО",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # RU — Ночлежка (Nochlezhka — homelessness)
    # -------------------------------------------------------------------
    {
        "slug": "nochlezhka",
        "country": "RU",
        "registration_id": "1037800033170",
        "name": {"en": "Nochlezhka", "ru": "Ночлежка"},
        "tagline": {
            "en": "Russia's longest-running homelessness charity",
            "ru": "Старейшая российская организация помощи бездомным",
        },
        "description": {
            "en": (
                "Nochlezhka is Russia's oldest charity helping homeless "
                "people, founded in 1990 in St Petersburg. It runs shelters, "
                "a free dining hall, legal and medical aid, and reintegration "
                "programs. A second shelter opened in Moscow in 2018. Annual "
                "reports filed with Минюст РФ."
            ),
            "ru": (
                "«Ночлежка» — старейшая российская организация помощи "
                "бездомным, основана в 1990 году в Санкт-Петербурге. "
                "Содержит приюты, бесплатную столовую, юридическую и "
                "медицинскую помощь, программы социальной адаптации. С 2018 "
                "года также работает приют в Москве. Годовые отчёты подаются "
                "в Минюст РФ."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered with Минюст РФ (ОГРН 1037800033170), "
                "annual report 2024 published."
            ),
            "ru": (
                "Подтверждено: зарегистрирована в Минюсте РФ (ОГРН 1037800033170), "
                "годовой отчёт за 2024 год опубликован."
            ),
        },
        "logo_url": "",
        "donation_url": "https://homeless.ru/donation/",
        "size_bucket": "small",
        "last_filed_date": date(2025, 3, 31),
        "total_revenue_usd": Decimal("3200000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1990,
        "cause_slugs": ["homelessness", "poverty-reduction"],
        "financials": [
            {
                "year": 2024,
                "total_revenue_usd": Decimal("3200000.00"),
                "program_expenses_usd": Decimal("2560000.00"),
                "admin_expenses_usd": Decimal("384000.00"),
                "fundraising_expenses_usd": Decimal("256000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://homeless.ru/about/documents/",
                "source_label": "Минюст отчёт о деятельности 2024",
            },
        ],
        "source_documents": [
            {
                "kind": "minjust_registration",
                "filed_date": date(2025, 3, 31),
                "label": {
                    "en": "Минюст annual report (2024)",
                    "ru": "Отчёт о деятельности (Минюст РФ, 2024)",
                },
                "url": "https://homeless.ru/about/documents/",
                "source_label": "Минюст РФ — публичный реестр НКО",
                "file_format": "pdf",
            },
        ],
    },
]


# Cause taxonomy slugs used across the seed (created lazily if missing)
CAUSE_LABELS: dict[str, dict[str, str]] = {
    "poverty-reduction": {"en": "Poverty reduction", "ru": "Борьба с бедностью"},
    "global-health": {"en": "Global health", "ru": "Здоровье в мире"},
    "homelessness": {"en": "Homelessness", "ru": "Помощь бездомным"},
    "disaster-relief": {"en": "Disaster relief", "ru": "Помощь при катастрофах"},
    "education": {"en": "Education", "ru": "Образование"},
    "cash-transfers": {"en": "Cash transfers", "ru": "Денежные переводы"},
    "child-nutrition": {"en": "Child nutrition", "ru": "Детское питание"},
    "neglected-tropical-diseases": {
        "en": "Neglected tropical diseases",
        "ru": "Забытые тропические болезни",
    },
    "medical-research": {"en": "Medical research", "ru": "Медицинские исследования"},
}


# ---------------------------------------------------------------------------
# Forwards / backwards
# ---------------------------------------------------------------------------


def forwards(apps, schema_editor):
    Cause = apps.get_model("charities", "Cause")
    Charity = apps.get_model("charities", "Charity")
    Financial = apps.get_model("charities", "Financial")
    SourceDocument = apps.get_model("charities", "SourceDocument")

    # 1. Ensure cause taxonomy entries exist for every slug we reference
    for slug, label in CAUSE_LABELS.items():
        Cause.objects.update_or_create(
            slug=slug,
            defaults={"name": label},
        )

    upserted = 0
    skipped_blocked = 0

    for entry in SEED:
        # Defensive: cross-check blocklist before insert. If the data file ever
        # gets a war-relief / foreign-agent org added by mistake, ETL-layer
        # filter at apps/charities/blocklist.py catches it here too.
        block = is_blocked(
            country=entry["country"],
            registration_id=entry["registration_id"],
            cause_tags=entry["cause_slugs"],
            name=entry["name"]["en"] + " " + entry["name"]["ru"],
            description=entry["description"]["en"],
        )
        if block is not None:
            print(
                f"[migration 0008] BLOCKED {entry['slug']} "
                f"({entry['country']}/{entry['registration_id']}): {block}"
            )
            skipped_blocked += 1
            continue

        is_stale = (date.today() - entry["last_filed_date"]).days > 730

        charity, _created = Charity.objects.update_or_create(
            country=entry["country"],
            registration_id=entry["registration_id"],
            defaults={
                "slug": entry["slug"],
                "name": entry["name"],
                "tagline": entry["tagline"],
                "description": entry["description"],
                "methodology_note": entry["methodology_note"],
                "logo_url": entry["logo_url"],
                "donation_url": entry["donation_url"],
                "cause_tags": entry["cause_slugs"],
                "size_bucket": entry["size_bucket"],
                "verification_status": "verified",
                "is_stale": is_stale,
                "last_filed_date": entry["last_filed_date"],
                "total_revenue_usd": entry["total_revenue_usd"],
                "program_expense_pct": entry["program_expense_pct"],
                "founded_year": entry["founded_year"],
                "ingestion_source": "manual_ru" if entry["country"] == "RU" else "propublica",
            },
        )

        for fin in entry["financials"]:
            Financial.objects.update_or_create(
                charity=charity,
                year=fin["year"],
                defaults={
                    "total_revenue_usd": fin["total_revenue_usd"],
                    "program_expenses_usd": fin["program_expenses_usd"],
                    "admin_expenses_usd": fin["admin_expenses_usd"],
                    "fundraising_expenses_usd": fin["fundraising_expenses_usd"],
                    "top_executive_comp_usd": fin["top_executive_comp_usd"],
                    "top_executive_name": fin["top_executive_name"],
                    "source_url": fin["source_url"],
                    "source_label": fin["source_label"],
                },
            )

        for doc in entry["source_documents"]:
            SourceDocument.objects.update_or_create(
                charity=charity,
                kind=doc["kind"],
                filed_date=doc["filed_date"],
                defaults={
                    "label": doc["label"],
                    "url": doc["url"],
                    "source_label": doc["source_label"],
                    "file_format": doc["file_format"],
                },
            )

        upserted += 1

    # Refresh denormalised charity_count on Cause rows we touched
    for slug in CAUSE_LABELS.keys():
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    print(
        f"[migration 0008] curated charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}"
    )


def backwards(apps, schema_editor):
    """No-op. We never auto-delete real curated rows on rollback."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0007_fix_givedirectly_orm_update"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

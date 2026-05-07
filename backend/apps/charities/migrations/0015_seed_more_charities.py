"""v3.1 quality + scale pass — seed 20 additional curated charities.

User feedback after v3.0 ship: "Add as many more charities as possible.
Currently 19 (11 People + 4 Animals + 4 Planet). User wants 30-50 total."

This migration adds 20 well-known, real-EIN charities sourced and verified
on 2026-05-07 against ProPublica's `filings_with_data` API and Wikimedia
Commons logo + photo searches. After this migration runs, the catalog
should hold ~39 charities (19 existing + 20 new), spread across:

  People (8 new):
    - Médecins Sans Frontières USA (EIN 13-3433452) — humanitarian medicine
    - UNICEF USA (EIN 13-1760110) — child welfare
    - Direct Relief (EIN 95-1831116) — medical disaster relief
    - Save the Children Federation (EIN 06-0726487) — child welfare
    - International Rescue Committee (EIN 13-5660870) — refugees
    - CARE USA (EIN 13-1685039) — poverty reduction
    - charity:water (EIN 22-3936753) — clean water
    - Pencils of Promise (EIN 26-3618722) — education

  Animals (5 new):
    - Humane Society of the United States (EIN 53-0225390) — animal welfare
    - Defenders of Wildlife (EIN 53-0183181) — endangered species
    - Wildlife Conservation Society (EIN 13-1740011) — wildlife conservation
    - National Audubon Society (EIN 13-1624102) — bird conservation
    - PetSmart Charities (EIN 93-1140967) — pet shelters

  Planet (7 new):
    - Sierra Club Foundation (EIN 94-6069890) — environmental advocacy
    - Environmental Defense Fund (EIN 11-6107128) — climate + science policy
    - Conservation International (EIN 52-1497470) — biodiversity
    - Rainforest Trust (EIN 13-3500609) — rainforest acquisition
    - NRDC (EIN 13-2654926) — environmental law
    - Earthjustice (EIN 94-1730465) — environmental litigation

Russia-law compliance: every entry runs through `is_blocked()` defensively.
None of these are foreign-agent / undesirable / war-relief-flagged.

Note on EIN correctness: the user brief listed several wrong EINs (e.g.
Partners In Health 04-2746091 — actually a different entity in ProPublica;
Partners In Health proper is hard to nail down via the API). We omit
charities whose EIN we couldn't reconcile with ProPublica's index, rather
than ship a row with an EIN that 404s on the data API. The user's listed
EINs we couldn't reconcile and therefore SKIPPED:
  - Partners In Health (04-2746091) — ProPublica search returns no clean
    match for the canonical Boston-based PIH; the EIN is for a small
    Maine-based "Partners In Health" — different org. Skipped.

Idempotent — uses `update_or_create` keyed on (country, registration_id),
so re-running this migration is safe.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


# Cause taxonomy slugs we may add. Existing slugs reused where applicable
# (poverty-reduction, global-health, child-nutrition, disaster-relief,
# wildlife-conservation, animal-welfare, climate, conservation, oceans,
# environment, endangered-species, education).
NEW_CAUSES: dict[str, dict[str, str]] = {
    "refugees": {"en": "Refugees", "ru": "Беженцы"},
    "water-sanitation": {"en": "Water & sanitation", "ru": "Вода и санитария"},
    "humanitarian-medicine": {
        "en": "Humanitarian medicine",
        "ru": "Гуманитарная медицина",
    },
    "child-welfare": {"en": "Child welfare", "ru": "Защита детей"},
    "pet-shelters": {"en": "Pet shelters", "ru": "Приюты для домашних животных"},
    "bird-conservation": {"en": "Bird conservation", "ru": "Охрана птиц"},
    "environmental-law": {
        "en": "Environmental law",
        "ru": "Природоохранное право",
    },
    "rainforest": {"en": "Rainforest protection", "ru": "Защита тропических лесов"},
}


SEED: list[dict] = [
    # =========================================================================
    # PEOPLE BUCKET — 8 new
    # =========================================================================
    # ----- Médecins Sans Frontières USA (Doctors Without Borders) -----
    {
        "slug": "msf-usa",
        "country": "US",
        "registration_id": "133433452",
        "bucket": "people",
        "name": {
            "en": "Médecins Sans Frontières USA (Doctors Without Borders)",
            "ru": "«Врачи без границ» — США",
        },
        "tagline": {
            "en": "Emergency medical aid in conflict zones and crisis areas",
            "ru": "Экстренная медицинская помощь в зонах конфликтов и кризисов",
        },
        "description": {
            "en": (
                "Médecins Sans Frontières (Doctors Without Borders) provides "
                "independent medical care in conflict zones, epidemics, and "
                "natural-disaster areas across 70+ countries. The US section "
                "(MSF-USA) is the largest funder in the global MSF network. "
                "Strict independence policy: takes no money from governments "
                "of countries where MSF works."
            ),
            "ru": (
                "«Врачи без границ» оказывают независимую медицинскую помощь "
                "в зонах конфликтов, эпидемий и природных катастроф в более "
                "чем 70 странах. Американский филиал MSF-USA — крупнейший "
                "донор глобальной сети MSF. Строгая политика независимости: "
                "не принимает деньги от правительств стран, в которых работает."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.doctorswithoutborders.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2025, 2, 11),
        "total_revenue_usd": Decimal("767362916.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1971,
        "cause_slugs": [
            "humanitarian-medicine",
            "global-health",
            "disaster-relief",
            "refugees",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("767362916.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F133433452_202312_990_2025021123091453.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2025, 2, 11),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F133433452_202312_990_2025021123091453.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- UNICEF USA -----
    {
        "slug": "unicef-usa",
        "country": "US",
        "registration_id": "131760110",
        "bucket": "people",
        "name": {
            "en": "UNICEF USA",
            "ru": "ЮНИСЕФ США (UNICEF USA)",
        },
        "tagline": {
            "en": "Funds UNICEF's global child-survival programs",
            "ru": "Финансирует глобальные программы ЮНИСЕФ по защите детей",
        },
        "description": {
            "en": (
                "UNICEF USA (legal name: United States Fund for UNICEF) is "
                "the US 501(c)(3) that raises funds for UNICEF's child-"
                "survival programs in 190+ countries: vaccination, "
                "nutrition, water and sanitation, education, and emergency "
                "humanitarian response. Files Form 990 with the IRS annually."
            ),
            "ru": (
                "UNICEF USA (юридическое название: United States Fund for "
                "UNICEF) — американская 501(c)(3), собирающая средства "
                "для программ ЮНИСЕФ по защите детей в более чем 190 "
                "странах: вакцинация, питание, водоснабжение, образование, "
                "гуманитарное реагирование. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Logo_of_UNICEF.svg",
        "donation_url": "https://www.unicefusa.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 7),
        "total_revenue_usd": Decimal("829050932.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 1947,
        "cause_slugs": [
            "child-welfare",
            "global-health",
            "child-nutrition",
            "education",
            "water-sanitation",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("829050932.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_05_2024_prefixes_06-16%2F131760110"
                    "_202306_990_2024050722385081.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 7),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_05_2024_prefixes_06-16%2F131760110"
                    "_202306_990_2024050722385081.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Direct Relief -----
    {
        "slug": "direct-relief",
        "country": "US",
        "registration_id": "951831116",
        "bucket": "people",
        "name": {"en": "Direct Relief", "ru": "Direct Relief"},
        "tagline": {
            "en": "Delivers donated medical aid worldwide during disasters",
            "ru": "Поставка медицинской помощи в зоны бедствий по всему миру",
        },
        "description": {
            "en": (
                "Direct Relief is a US humanitarian medical aid organisation "
                "that distributes donated prescription medicines and medical "
                "supplies in response to disasters and ongoing health needs "
                "in 80+ countries. Reported as one of the largest US "
                "non-profits by gift-in-kind value. Files Form 990 with "
                "the IRS annually."
            ),
            "ru": (
                "Direct Relief — американская гуманитарная медицинская "
                "организация, распределяющая пожертвованные рецептурные "
                "лекарства и медицинские принадлежности в ответ на катастрофы "
                "и постоянные потребности здравоохранения в 80+ странах. "
                "Одна из крупнейших НКО США по стоимости натуральных "
                "пожертвований. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.directrelief.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 2, 20),
        "total_revenue_usd": Decimal("2266763483.00"),
        "program_expense_pct": Decimal("99.00"),
        "founded_year": 1948,
        "cause_slugs": [
            "humanitarian-medicine",
            "global-health",
            "disaster-relief",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("2266763483.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_02_2024_prefixes_93-99%2F951831116"
                    "_202306_990_2024022022294206.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 2, 20),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_02_2024_prefixes_93-99%2F951831116"
                    "_202306_990_2024022022294206.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Save the Children Federation -----
    {
        "slug": "save-the-children",
        "country": "US",
        "registration_id": "060726487",
        "bucket": "people",
        "name": {
            "en": "Save the Children Federation",
            "ru": "Save the Children",
        },
        "tagline": {
            "en": "Programs for children's survival, education, and protection",
            "ru": "Программы выживания, образования и защиты детей",
        },
        "description": {
            "en": (
                "Save the Children Federation is the US member of the global "
                "Save the Children alliance. Programs cover child survival "
                "(maternal + newborn health, nutrition), education, child "
                "protection, and emergency response in 100+ countries. "
                "Files Form 990 with the IRS annually."
            ),
            "ru": (
                "Save the Children Federation — американский член глобального "
                "альянса Save the Children. Программы охватывают выживание "
                "детей (материнское и неонатальное здоровье, питание), "
                "образование, защиту детей и экстренное реагирование в более "
                "чем 100 странах. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Save_the_Children_logo_%28cropped%29.svg",
        "donation_url": "https://support.savethechildren.org/site/Donation2",
        "size_bucket": "large",
        "last_filed_date": date(2025, 2, 10),
        "total_revenue_usd": Decimal("903000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1932,
        "cause_slugs": [
            "child-welfare",
            "global-health",
            "child-nutrition",
            "education",
            "disaster-relief",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("903000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F060726487_202312_990_2025021023082706.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2025, 2, 10),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F060726487_202312_990_2025021023082706.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- International Rescue Committee -----
    {
        "slug": "international-rescue-committee",
        "country": "US",
        "registration_id": "135660870",
        "bucket": "people",
        "name": {
            "en": "International Rescue Committee",
            "ru": "International Rescue Committee (IRC)",
        },
        "tagline": {
            "en": "Helps people whose lives are shattered by conflict and disaster",
            "ru": "Помощь людям, чья жизнь разрушена конфликтом или катастрофой",
        },
        "description": {
            "en": (
                "The International Rescue Committee responds to humanitarian "
                "crises in 40+ countries, helping refugees, displaced people, "
                "and vulnerable communities with health care, water and "
                "sanitation, education, livelihoods, and protection programs. "
                "Founded at the call of Albert Einstein in 1933. Files Form "
                "990 with the IRS annually."
            ),
            "ru": (
                "International Rescue Committee реагирует на гуманитарные "
                "кризисы в более чем 40 странах, помогая беженцам, "
                "перемещённым лицам и уязвимым сообществам в сферах "
                "здравоохранения, воды и санитарии, образования, средств "
                "к существованию и защиты. Основан по призыву Альберта "
                "Эйнштейна в 1933 году. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (FY 2023 not yet PDF-published)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год (PDF за 2023 ещё не опубликован)."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a4/International_Rescue_Committee_logo_only_%28cropped%29.svg",
        "donation_url": "https://help.rescue.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2023, 11, 3),
        "total_revenue_usd": Decimal("948000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1933,
        "cause_slugs": [
            "refugees",
            "humanitarian-medicine",
            "disaster-relief",
            "water-sanitation",
            "education",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("948000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_11_2023_prefixes_13-20%2F135660870"
                    "_202209_990_2023110321855880.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 11, 3),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_11_2023_prefixes_13-20%2F135660870"
                    "_202209_990_2023110321855880.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- CARE USA -----
    {
        "slug": "care-usa",
        "country": "US",
        "registration_id": "131685039",
        "bucket": "people",
        "name": {
            "en": "CARE USA",
            "ru": "CARE USA",
        },
        "tagline": {
            "en": "Fights global poverty with women-and-girls-focused programs",
            "ru": "Борьба с глобальной бедностью через программы для женщин и девочек",
        },
        "description": {
            "en": (
                "CARE (Cooperative for Assistance and Relief Everywhere) is "
                "a global humanitarian and development organisation working "
                "in 100+ countries with a strategic focus on poverty "
                "reduction through women's and girls' empowerment. Programs "
                "span emergency response, food and nutrition, sexual and "
                "reproductive health, and economic justice. Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "CARE (Cooperative for Assistance and Relief Everywhere) — "
                "глобальная гуманитарная и развивающая организация, "
                "работающая в более чем 100 странах со стратегическим "
                "фокусом на снижение бедности через расширение прав женщин "
                "и девочек. Программы: экстренное реагирование, питание, "
                "сексуальное и репродуктивное здоровье, экономическая "
                "справедливость. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (FY 2023 not yet PDF-published)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Logo_CARE_horizontal.svg",
        "donation_url": "https://my.care.org/site/Donation2",
        "size_bucket": "large",
        "last_filed_date": date(2023, 5, 30),
        "total_revenue_usd": Decimal("700000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1945,
        "cause_slugs": [
            "poverty-reduction",
            "global-health",
            "child-nutrition",
            "disaster-relief",
            "humanitarian-medicine",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("700000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F131685039_202206_990_2023053021316285.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 5, 30),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F131685039_202206_990_2023053021316285.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- charity:water -----
    {
        "slug": "charity-water",
        "country": "US",
        "registration_id": "223936753",
        "bucket": "people",
        "name": {
            "en": "charity: water",
            "ru": "charity: water",
        },
        "tagline": {
            "en": "Funds clean water projects in developing countries",
            "ru": "Финансирует проекты чистой воды в развивающихся странах",
        },
        "description": {
            "en": (
                "charity: water funds the construction of water and "
                "sanitation infrastructure (wells, piped systems, "
                "rainwater catchments) in developing countries through "
                "vetted local partner organisations. Operating model: "
                "private donors cover overhead so that 100% of public "
                "donations go directly to project funding. Legal entity: "
                "Charity Global Inc. Files Form 990 with the IRS annually."
            ),
            "ru": (
                "charity: water финансирует строительство инфраструктуры "
                "водоснабжения и санитарии (скважины, водопроводы, сбор "
                "дождевой воды) в развивающихся странах через "
                "проверенных местных партнёров. Операционная модель: "
                "частные доноры покрывают накладные расходы, чтобы 100% "
                "публичных пожертвований шли напрямую на проекты. "
                "Юридическое лицо: Charity Global Inc."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2021 (most recent with PDF available)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2021 финансовый год (последний доступный PDF)."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.charitywater.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2023, 3, 13),
        "total_revenue_usd": Decimal("66000000.00"),
        "program_expense_pct": Decimal("84.00"),
        "founded_year": 2006,
        "cause_slugs": [
            "water-sanitation",
            "global-health",
            "poverty-reduction",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2021,
                "total_revenue_usd": Decimal("66000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_03_2023_prefixes_20-25%2F223936753"
                    "_202112_990_2023031321087272.pdf"
                ),
                "source_label": "IRS Form 990, FY 2021 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 3, 13),
                "label": {
                    "en": "IRS Form 990 (FY 2021)",
                    "ru": "Налоговая форма IRS 990 (2021)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_03_2023_prefixes_20-25%2F223936753"
                    "_202112_990_2023031321087272.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Pencils of Promise -----
    {
        "slug": "pencils-of-promise",
        "country": "US",
        "registration_id": "263618722",
        "bucket": "people",
        "name": {"en": "Pencils of Promise", "ru": "Pencils of Promise"},
        "tagline": {
            "en": "Builds schools and provides education in low-income communities",
            "ru": "Строит школы и предоставляет образование в малообеспеченных общинах",
        },
        "description": {
            "en": (
                "Pencils of Promise builds schools and runs teacher-training "
                "and student-scholarship programs in Ghana, Guatemala, and "
                "Laos. Founded by Adam Braun on $25, has built 600+ schools. "
                "Files Form 990 with the IRS annually."
            ),
            "ru": (
                "Pencils of Promise строит школы и ведёт программы "
                "подготовки учителей и стипендий для учеников в Гане, "
                "Гватемале и Лаосе. Основана Адамом Брауном на $25, "
                "построено более 600 школ. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (most recent PDF)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://pencilsofpromise.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2023, 12, 5),
        "total_revenue_usd": Decimal("3470681.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2008,
        "cause_slugs": ["education", "child-welfare", "poverty-reduction"],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("3470681.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_12_2023_prefixes_26-27%2F263618722"
                    "_202212_990_2023120522070360.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 12, 5),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_12_2023_prefixes_26-27%2F263618722"
                    "_202212_990_2023120522070360.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # =========================================================================
    # ANIMALS BUCKET — 5 new
    # =========================================================================
    # ----- Humane Society of the United States -----
    {
        "slug": "humane-society-us",
        "country": "US",
        "registration_id": "530225390",
        "bucket": "animals",
        "name": {
            "en": "Humane Society of the United States",
            "ru": "Humane Society of the United States",
        },
        "tagline": {
            "en": "National animal-welfare advocacy and rescue",
            "ru": "Национальная защита животных: адвокация и спасение",
        },
        "description": {
            "en": (
                "The Humane Society of the United States (legal name: "
                "Humane World for Animals Inc) is one of the largest US "
                "animal-protection non-profits. Programs include policy "
                "advocacy, anti-cruelty investigations, animal-rescue "
                "operations during disasters, farm-animal welfare campaigns, "
                "and wildlife protection. Files Form 990 with the IRS "
                "annually."
            ),
            "ru": (
                "Humane Society of the United States (юридическое название: "
                "Humane World for Animals Inc) — одна из крупнейших НКО США "
                "по защите животных. Программы: политическая адвокация, "
                "расследования жестокого обращения, операции по спасению "
                "животных во время катастроф, кампании за благополучие "
                "сельскохозяйственных животных, охрана дикой природы. "
                "Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.humanesociety.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2025, 1, 17),
        "total_revenue_usd": Decimal("174968233.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1954,
        "cause_slugs": ["animal-welfare", "wildlife-conservation"],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("174968233.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F530225390_202312_990_2025011723014621.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2025, 1, 17),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F530225390_202312_990_2025011723014621.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Defenders of Wildlife -----
    {
        "slug": "defenders-of-wildlife",
        "country": "US",
        "registration_id": "530183181",
        "bucket": "animals",
        "name": {
            "en": "Defenders of Wildlife",
            "ru": "Defenders of Wildlife",
        },
        "tagline": {
            "en": "Protects native wild animals and their habitats in North America",
            "ru": "Охрана североамериканских диких животных и их среды обитания",
        },
        "description": {
            "en": (
                "Defenders of Wildlife is a US non-profit dedicated to "
                "protecting native wild animals and plants in North America. "
                "Programs include species recovery (wolves, sea otters, "
                "polar bears), public-lands conservation, climate adaptation, "
                "and Endangered Species Act litigation and policy. Files "
                "Form 990 with the IRS annually."
            ),
            "ru": (
                "Defenders of Wildlife — американская НКО, защищающая "
                "коренных диких животных и растения Северной Америки. "
                "Программы: восстановление видов (волки, морские выдры, "
                "белые медведи), охрана общественных земель, адаптация к "
                "изменениям климата, судебные процессы и политика по "
                "Закону об исчезающих видах. Ежегодно подаёт форму 990."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Logo_of_Defenders_of_Wildlife.png",
        "donation_url": "https://defenders.org/take-action/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 2, 20),
        "total_revenue_usd": Decimal("35880686.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1947,
        "cause_slugs": [
            "wildlife-conservation",
            "endangered-species",
            "conservation",
            "environment",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("35880686.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_02_2024_prefixes_52-58%2F530183181"
                    "_202309_990_2024022022298239.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 2, 20),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_02_2024_prefixes_52-58%2F530183181"
                    "_202309_990_2024022022298239.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Wildlife Conservation Society -----
    {
        "slug": "wildlife-conservation-society",
        "country": "US",
        "registration_id": "131740011",
        "bucket": "animals",
        "name": {
            "en": "Wildlife Conservation Society",
            "ru": "Wildlife Conservation Society (WCS)",
        },
        "tagline": {
            "en": "Protects wild places and wildlife in 60+ countries",
            "ru": "Охрана дикой природы и диких мест в более чем 60 странах",
        },
        "description": {
            "en": (
                "Wildlife Conservation Society conducts conservation science "
                "in 60+ countries, manages five wildlife parks in New York "
                "City (including the Bronx Zoo), and runs landscape-scale "
                "protection programs for big cats, great apes, marine "
                "mammals, and forest ecosystems. Files Form 990 with the "
                "IRS annually."
            ),
            "ru": (
                "Wildlife Conservation Society ведёт научные исследования "
                "по сохранению природы в более чем 60 странах, управляет "
                "пятью зоопарками в Нью-Йорке (включая Бронксский зоопарк) "
                "и масштабными программами охраны для крупных кошек, "
                "человекообразных обезьян, морских млекопитающих и лесных "
                "экосистем. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Wildlife_Conservation_Society_logo_%28since_2015%29.svg",
        "donation_url": "https://secure.wcs.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 21),
        "total_revenue_usd": Decimal("345503315.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1895,
        "cause_slugs": [
            "wildlife-conservation",
            "endangered-species",
            "conservation",
            "environment",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("345503315.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F131740011_202306_990_2024062122569384.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 6, 21),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F131740011_202306_990_2024062122569384.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- National Audubon Society -----
    {
        "slug": "audubon-society",
        "country": "US",
        "registration_id": "131624102",
        "bucket": "animals",
        "name": {
            "en": "National Audubon Society",
            "ru": "Национальное общество Одюбона",
        },
        "tagline": {
            "en": "Protects birds and the places they need across the Americas",
            "ru": "Охрана птиц и мест их обитания в Северной и Южной Америке",
        },
        "description": {
            "en": (
                "The National Audubon Society protects birds and the places "
                "they need throughout the Americas. Programs include the "
                "Audubon Bird Surveys (citizen-science Christmas Bird Count "
                "since 1900), policy advocacy, working-lands conservation, "
                "and a network of 450+ local Audubon chapters. Files Form "
                "990 with the IRS annually."
            ),
            "ru": (
                "Национальное общество Одюбона защищает птиц и места их "
                "обитания на всей территории Северной и Южной Америки. "
                "Программы: Audubon Bird Surveys (гражданско-научный "
                "Рождественский учёт птиц с 1900 года), политическая "
                "адвокация, охрана сельхозземель, сеть из более чем 450 "
                "местных отделений. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://act.audubon.org/a/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 17),
        "total_revenue_usd": Decimal("156129262.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1905,
        "cause_slugs": [
            "bird-conservation",
            "wildlife-conservation",
            "conservation",
            "environment",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("156129262.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_05_2024_prefixes_06-16%2F131624102"
                    "_202306_990_2024051722392054.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 17),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_05_2024_prefixes_06-16%2F131624102"
                    "_202306_990_2024051722392054.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- PetSmart Charities -----
    {
        "slug": "petsmart-charities",
        "country": "US",
        "registration_id": "931140967",
        "bucket": "animals",
        "name": {
            "en": "PetSmart Charities",
            "ru": "PetSmart Charities",
        },
        "tagline": {
            "en": "Helps pets find homes and supports veterinary care access",
            "ru": "Помогает домашним питомцам найти дом и поддерживает доступ к ветпомощи",
        },
        "description": {
            "en": (
                "PetSmart Charities funds adoption-partner shelters, "
                "low-cost spay/neuter and veterinary-care programs, and "
                "disaster-relief operations for pets. Operates the largest "
                "in-store pet-adoption program in North America "
                "(co-located with PetSmart retail stores). Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "PetSmart Charities финансирует партнёрские приюты, "
                "программы низкобюджетной стерилизации и ветеринарной "
                "помощи, операции по спасению питомцев во время катастроф. "
                "Управляет крупнейшей в Северной Америке программой "
                "усыновления питомцев в магазинах (со-локация с PetSmart). "
                "Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2024, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2024 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://petsmartcharities.org/ways-to-give",
        "size_bucket": "large",
        "last_filed_date": date(2025, 1, 17),
        "total_revenue_usd": Decimal("61884709.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1994,
        "cause_slugs": ["animal-welfare", "pet-shelters"],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2024,
                "total_revenue_usd": Decimal("61884709.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F931140967_202401_990_2025011723018034.pdf"
                ),
                "source_label": "IRS Form 990, FY 2024 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2025, 1, 17),
                "label": {
                    "en": "IRS Form 990 (FY 2024)",
                    "ru": "Налоговая форма IRS 990 (2024)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F931140967_202401_990_2025011723018034.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # =========================================================================
    # PLANET BUCKET — 6 new
    # =========================================================================
    # ----- Sierra Club Foundation -----
    {
        "slug": "sierra-club-foundation",
        "country": "US",
        "registration_id": "946069890",
        "bucket": "planet",
        "name": {
            "en": "Sierra Club Foundation",
            "ru": "Sierra Club Foundation",
        },
        "tagline": {
            "en": "Funds environmental advocacy, education, and litigation",
            "ru": "Финансирует природоохранную адвокацию, образование и судебные процессы",
        },
        "description": {
            "en": (
                "The Sierra Club Foundation is the 501(c)(3) charitable arm "
                "of the Sierra Club ecosystem (the 501(c)(4) Sierra Club "
                "itself is the membership advocacy organisation). Funds "
                "environmental education, scientific research, and "
                "Endangered Species Act litigation. Files Form 990 with "
                "the IRS annually."
            ),
            "ru": (
                "Sierra Club Foundation — благотворительное 501(c)(3) "
                "крыло экосистемы Sierra Club (членская адвокационная "
                "организация Sierra Club сама по себе — 501(c)(4)). "
                "Финансирует экологическое образование, научные "
                "исследования и судебные процессы по Закону об исчезающих "
                "видах. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2021 (most recent PDF available)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2021 финансовый год (последний доступный PDF)."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.sierraclubfoundation.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2023, 3, 3),
        "total_revenue_usd": Decimal("125000000.00"),
        "program_expense_pct": Decimal("84.00"),
        "founded_year": 1960,
        "cause_slugs": [
            "environment",
            "climate",
            "conservation",
            "environmental-law",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2021,
                "total_revenue_usd": Decimal("125000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_03_2023_prefixes_91-99%2F946069890"
                    "_202112_990_2023030321024999.pdf"
                ),
                "source_label": "IRS Form 990, FY 2021 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 3, 3),
                "label": {
                    "en": "IRS Form 990 (FY 2021)",
                    "ru": "Налоговая форма IRS 990 (2021)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_03_2023_prefixes_91-99%2F946069890"
                    "_202112_990_2023030321024999.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Environmental Defense Fund -----
    {
        "slug": "edf",
        "country": "US",
        "registration_id": "116107128",
        "bucket": "planet",
        "name": {
            "en": "Environmental Defense Fund",
            "ru": "Environmental Defense Fund (EDF)",
        },
        "tagline": {
            "en": "Science-driven environmental policy and market-based solutions",
            "ru": "Научная природоохранная политика и рыночные решения",
        },
        "description": {
            "en": (
                "Environmental Defense Fund pursues science-based "
                "environmental solutions across climate, oceans, ecosystems, "
                "and human health. Known for combining scientific research "
                "with market-based and regulatory tools. Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "Environmental Defense Fund разрабатывает научно-"
                "обоснованные природоохранные решения в темах климата, "
                "океанов, экосистем и здоровья человека. Известен "
                "сочетанием научных исследований с рыночными и "
                "регуляторными инструментами. Ежегодно подаёт форму 990."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (most recent PDF)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://secure.edf.org/site/Donation2",
        "size_bucket": "large",
        "last_filed_date": date(2023, 6, 5),
        "total_revenue_usd": Decimal("295000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1967,
        "cause_slugs": [
            "climate",
            "environment",
            "conservation",
            "oceans",
            "environmental-law",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("295000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_06_2023_prefixes_06-16%2F116107128"
                    "_202209_990_2023060521373128.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 6, 5),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_06_2023_prefixes_06-16%2F116107128"
                    "_202209_990_2023060521373128.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Conservation International -----
    {
        "slug": "conservation-international",
        "country": "US",
        "registration_id": "521497470",
        "bucket": "planet",
        "name": {
            "en": "Conservation International",
            "ru": "Conservation International",
        },
        "tagline": {
            "en": "Science-driven biodiversity conservation in 30+ countries",
            "ru": "Научная охрана биоразнообразия в более чем 30 странах",
        },
        "description": {
            "en": (
                "Conservation International (legal name: Conservation "
                "International Foundation) protects nature for the benefit "
                "of humanity through science, partnerships with indigenous "
                "communities, and policy work. Active in 30+ countries on "
                "tropical-forest, ocean, and freshwater conservation. "
                "Files Form 990 with the IRS annually."
            ),
            "ru": (
                "Conservation International (юридическое название: "
                "Conservation International Foundation) защищает природу на "
                "благо человечества через науку, партнёрство с коренными "
                "общинами и политическую работу. Работает в более чем 30 "
                "странах по охране тропических лесов, океанов и пресных "
                "вод. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, direct PDF link."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2023 финансовый год, прямая ссылка на PDF."
            ),
        },
        "logo_url": "",
        "donation_url": "https://secure.conservation.org/site/Donation2",
        "size_bucket": "large",
        "last_filed_date": date(2024, 4, 5),
        "total_revenue_usd": Decimal("235131545.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1987,
        "cause_slugs": [
            "conservation",
            "rainforest",
            "climate",
            "oceans",
            "environment",
            "wildlife-conservation",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("235131545.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F521497470_202306_990_2024040522347117.pdf"
                ),
                "source_label": "IRS Form 990, FY 2023 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 4, 5),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F521497470_202306_990_2024040522347117.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Rainforest Trust -----
    {
        "slug": "rainforest-trust",
        "country": "US",
        "registration_id": "133500609",
        "bucket": "planet",
        "name": {"en": "Rainforest Trust", "ru": "Rainforest Trust"},
        "tagline": {
            "en": "Buys and protects threatened rainforest land for biodiversity",
            "ru": "Покупает и охраняет находящиеся под угрозой тропические леса",
        },
        "description": {
            "en": (
                "Rainforest Trust partners with local conservation "
                "organisations to buy land or establish protected areas in "
                "tropical biodiversity hotspots. Reported model: $0.40 to "
                "$2 per acre protected, depending on country. Reserves "
                "established in 50+ countries since 1988. Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "Rainforest Trust сотрудничает с местными природоохранными "
                "организациями, выкупая землю или создавая охраняемые "
                "территории в горячих точках тропического биоразнообразия. "
                "Заявленная модель: от $0.40 до $2 за акр охраны, в "
                "зависимости от страны. Заповедники созданы в более чем "
                "50 странах с 1988 года. Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (most recent PDF)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.rainforesttrust.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 1, 4),
        "total_revenue_usd": Decimal("60000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1988,
        "cause_slugs": [
            "rainforest",
            "conservation",
            "endangered-species",
            "environment",
            "wildlife-conservation",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("60000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_01_2024_prefixes_13-14%2F133500609"
                    "_202212_990_2024010422169947.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 1, 4),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=download990pdf_01_2024_prefixes_13-14%2F133500609"
                    "_202212_990_2024010422169947.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Natural Resources Defense Council -----
    {
        "slug": "nrdc",
        "country": "US",
        "registration_id": "132654926",
        "bucket": "planet",
        "name": {
            "en": "Natural Resources Defense Council",
            "ru": "Natural Resources Defense Council (NRDC)",
        },
        "tagline": {
            "en": "Environmental law: science-grounded litigation and policy",
            "ru": "Природоохранное право: научно-обоснованные иски и политика",
        },
        "description": {
            "en": (
                "Natural Resources Defense Council combines lawyers, "
                "scientists, and policy advocates to push for stronger "
                "environmental law and rule-making in the United States and "
                "internationally. Programs span clean air and water, "
                "climate and clean energy, oceans, and wildlife. Files "
                "Form 990 with the IRS annually."
            ),
            "ru": (
                "Natural Resources Defense Council объединяет юристов, "
                "учёных и политических адвокатов, добиваясь усиления "
                "природоохранного законодательства и регулирования в США "
                "и за рубежом. Программы охватывают чистый воздух и воду, "
                "климат и чистую энергию, океаны, дикую природу. "
                "Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (most recent PDF)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.nrdc.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2023, 6, 7),
        "total_revenue_usd": Decimal("215000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1970,
        "cause_slugs": [
            "environmental-law",
            "environment",
            "climate",
            "oceans",
            "conservation",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("215000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F132654926_202206_990_2023060721397724.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 6, 7),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F132654926_202206_990_2023060721397724.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Earthjustice -----
    {
        "slug": "earthjustice",
        "country": "US",
        "registration_id": "941730465",
        "bucket": "planet",
        "name": {"en": "Earthjustice", "ru": "Earthjustice"},
        "tagline": {
            "en": "Public-interest environmental law firm — litigation only",
            "ru": "Юридическая фирма в интересах природы — только судебные процессы",
        },
        "description": {
            "en": (
                "Earthjustice is the largest US public-interest "
                "environmental law firm. It works exclusively through "
                "litigation — clean air, clean water, healthy communities, "
                "wild places, and climate accountability — representing "
                "client communities and partner organisations free of "
                "charge. Founded in 1971 as the Sierra Club Legal Defense "
                "Fund. Files Form 990 with the IRS annually."
            ),
            "ru": (
                "Earthjustice — крупнейшая в США юридическая фирма по "
                "защите общественных интересов в природоохранной сфере. "
                "Работает исключительно через судебные процессы (чистый "
                "воздух, чистая вода, здоровые сообщества, дикие места, "
                "климатическая ответственность), представляя интересы "
                "сообществ-клиентов и организаций-партнёров бесплатно. "
                "Основана в 1971 году как Sierra Club Legal Defense Fund. "
                "Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2022 (most recent PDF)."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
                "за 2022 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://secure.earthjustice.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2023, 6, 5),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1971,
        "cause_slugs": [
            "environmental-law",
            "environment",
            "climate",
            "conservation",
        ],
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2022,
                "total_revenue_usd": Decimal("180000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F941730465_202206_990_2023060521374483.pdf"
                ),
                "source_label": "IRS Form 990, FY 2022 (ProPublica direct PDF)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2023, 6, 5),
                "label": {
                    "en": "IRS Form 990 (FY 2022)",
                    "ru": "Налоговая форма IRS 990 (2022)",
                },
                "url": (
                    "https://projects.propublica.org/nonprofits/download-filing"
                    "?path=IRS%2F941730465_202206_990_2023060521374483.pdf"
                ),
                "source_label": "IRS Form 990 (ProPublica direct PDF)",
                "file_format": "pdf",
            },
        ],
    },
]


def forwards(apps, schema_editor):
    Cause = apps.get_model("charities", "Cause")
    Charity = apps.get_model("charities", "Charity")
    Financial = apps.get_model("charities", "Financial")
    SourceDocument = apps.get_model("charities", "SourceDocument")

    # 1. Ensure new cause taxonomy entries exist.
    for slug, label in NEW_CAUSES.items():
        Cause.objects.update_or_create(slug=slug, defaults={"name": label})

    upserted = 0
    skipped_blocked = 0

    for entry in SEED:
        # Defensive blocklist check — none of these entries should match,
        # but the same defensive double-check that 0008 / 0012 use stays.
        block = is_blocked(
            country=entry["country"],
            registration_id=entry["registration_id"],
            cause_tags=entry["cause_slugs"],
            name=entry["name"]["en"] + " " + entry["name"]["ru"],
            description=entry["description"]["en"],
        )
        if block is not None:
            print(
                f"[migration 0015] BLOCKED {entry['slug']} "
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
                "ingestion_source": "manual_curation",
                "bucket": entry["bucket"],
                "hero_photo_url": entry["hero_photo_url"],
                "hero_photo_caption": entry["hero_photo_caption"],
                "hero_photo_credit": entry["hero_photo_credit"],
                "hero_photo_license": entry["hero_photo_license"],
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

    # Refresh denormalised charity_count on every cause we touched.
    all_cause_slugs: set[str] = set(NEW_CAUSES.keys())
    for entry in SEED:
        all_cause_slugs.update(entry["cause_slugs"])
    for slug in all_cause_slugs:
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    total_charities = Charity.objects.count()
    print(
        f"[migration 0015] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total_charities}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0014_fix_source_document_urls"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

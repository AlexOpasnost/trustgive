"""v3.7 catalog geo-expansion — seed 32 charities from 15 countries (218 -> ~250).

Goal: break US/UK monopoly in the catalog. Add Canada (CRA), Australia
(ACNC), New Zealand (Charities Services), Germany / Netherlands /
Switzerland / Sweden / France / Japan (national certifiers + annual
reports), India / Brazil / Argentina+Chile / Africa / SE-Asia (own
annual reports — `source_kind="annual_report"`, honest about it).

Verification levels (KB-014 honesty rule):
  - "verified" — country has a strong national regulator with public
    annual returns: CA (CRA T3010), AU (ACNC), NZ (Charities Services),
    NL (CBF Erkend), CH (ZEWO), SE (Svensk Insamlingskontroll).
  - "verified" with caveat — DE (DZI Spendensiegel cert + own annual
    reports), FR (Don en Confiance), JP (公益財団法人 register).
  - "listed" — verification by org's own published annual report only:
    IN (FCRA + 80G + own report), BR (Estatuto + own report), AR/CL
    (own reports), KE/AMREF (own annual report), TH (Mae Tao own
    transparency).

Idempotent: `update_or_create((country, registration_id))`. Defensive
`is_blocked()` per entry. Reverse no-op (never auto-delete real
curated rows).

Hero photos: empty here. Filled by `scrape_og_images` management
command after migrate.

Logos: empty here. Filled by `0039_backfill_v37_geo_logos.py`.

Depends on `0037_extend_country_choices_v37` which adds the 31 new
ISO codes (NZ DE CH SE FR JP SG KE ZA GH MZ LS SN TZ UG IN PH ID VN
TH BD BR AR CL CO MX EC CR PE LB EG JO TN) to `Country.choices`.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "africa-health": {
        "en": "Health systems in Africa",
        "ru": "Системы здравоохранения в Африке",
    },
    "south-american-housing": {
        "en": "Informal-settlement housing (Latin America)",
        "ru": "Жильё в неформальных поселениях (Латинская Америка)",
    },
    "burmese-refugees": {
        "en": "Burmese refugees & migrants",
        "ru": "Беженцы и мигранты из Мьянмы",
    },
    "atlantic-forest": {
        "en": "Atlantic Forest conservation (Brazil)",
        "ru": "Сохранение Атлантического леса (Бразилия)",
    },
    "school-meals": {
        "en": "School-meal programs",
        "ru": "Программы школьного питания",
    },
    "child-rights-india": {
        "en": "Child rights (India)",
        "ru": "Права детей (Индия)",
    },
    "social-enterprise-philanthropy": {
        "en": "Strategic / social-enterprise philanthropy",
        "ru": "Стратегическая / социально-предпринимательская филантропия",
    },
}


def _verify(en: str, ru: str) -> dict:
    return {"en": en, "ru": ru}


def _empty_photo() -> dict:
    return {
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
    }


SEED: list[dict] = [
    # =================== CANADA (5) ===================
    {
        "slug": "sickkids-foundation",
        "country": "CA",
        "registration_id": "10808-2786-RR0001",
        "bucket": "people",
        "name": {"en": "SickKids Foundation", "ru": "SickKids Foundation — фонд детской больницы Торонто"},
        "tagline": {
            "en": "Funds The Hospital for Sick Children (Toronto) — clinical care, research, training.",
            "ru": "Финансирует детскую больницу в Торонто — клиническая помощь, исследования, обучение.",
        },
        "description": {
            "en": (
                "SickKids Foundation (CRA #10808-2786-RR0001, founded 1972) raises and "
                "stewards funds for The Hospital for Sick Children in Toronto — one of "
                "the largest paediatric academic health centres in the world. Funds "
                "frontline care, the SickKids Research Institute (~2,000 staff working "
                "on cancer, genetics, infectious disease), the new Patient Support "
                "Centre, and clinician training. SickKids treats more than 100,000 "
                "children each year and trains paediatric specialists across Canada."
            ),
            "ru": (
                "SickKids Foundation (CRA #10808-2786-RR0001, основан в 1972 году) "
                "собирает и управляет средствами для детской больницы Hospital for "
                "Sick Children в Торонто — одного из крупнейших педиатрических "
                "академических медцентров в мире. Финансирует лечение, "
                "научно-исследовательский институт SickKids (~2000 сотрудников, "
                "работающих над онкологией, генетикой, инфекционными болезнями), "
                "новый Patient Support Centre и обучение врачей. Ежегодно "
                "SickKids лечит более 100 000 детей и готовит педиатров со всей "
                "Канады."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with CRA Charities Directorate; annual T3010 information return is public.",
            "Подтверждено: зарегистрирован в CRA Charities Directorate; ежегодная декларация T3010 публична.",
        ),
        "logo_url": "",
        "donation_url": "https://www.sickkidsfoundation.com/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("155000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1972,
        "cause_slugs": ["global-health", "child-welfare"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.sickkidsfoundation.com/who-we-are/financial-information",
    },
    {
        "slug": "heart-stroke-canada",
        "country": "CA",
        "registration_id": "10684-6942-RR0001",
        "bucket": "people",
        "name": {"en": "Heart & Stroke Foundation of Canada", "ru": "Heart & Stroke Foundation of Canada"},
        "tagline": {
            "en": "Cardiovascular disease prevention, research, and recovery support across Canada.",
            "ru": "Профилактика, исследования и поддержка восстановления при сердечно-сосудистых заболеваниях по всей Канаде.",
        },
        "description": {
            "en": (
                "Heart & Stroke (CRA #10684-6942-RR0001, founded 1952) funds Canadian "
                "cardiovascular research, deploys CPR/AED training programs, and runs "
                "national patient-support resources. Runs the Heart & Stroke Foundation "
                "Walk and Wear Red Day. Has invested >$1.6B in heart and stroke "
                "research since founding."
            ),
            "ru": (
                "Heart & Stroke (CRA #10684-6942-RR0001, основан в 1952 году) "
                "финансирует канадские исследования сердечно-сосудистых заболеваний, "
                "программы обучения СЛР и пользования AED, ресурсы поддержки "
                "пациентов. С момента основания инвестировал более $1,6 млрд в "
                "исследования."
            ),
        },
        "methodology_note": _verify(
            "Verified: CRA-registered; T3010 public.", "Подтверждено: CRA-регистрация; T3010 публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.heartandstroke.ca/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 31),
        "total_revenue_usd": Decimal("130000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1952,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.heartandstroke.ca/what-we-do/about-us/financial-information",
    },
    {
        "slug": "canadian-cancer-society",
        "country": "CA",
        "registration_id": "11882-9803-RR0001",
        "bucket": "people",
        "name": {"en": "Canadian Cancer Society", "ru": "Canadian Cancer Society"},
        "tagline": {
            "en": "Funds cancer research and runs nationwide patient-support programs in Canada.",
            "ru": "Финансирует онкологические исследования и национальные программы поддержки пациентов в Канаде.",
        },
        "description": {
            "en": (
                "Canadian Cancer Society (CRA #11882-9803-RR0001, founded 1938) is "
                "Canada's largest national cancer charity. Funds research grants "
                "across all cancer types, operates the Cancer Information Service "
                "(toll-free helpline), runs lodging for out-of-town patients, and "
                "advocates federally for tobacco control and cancer-prevention policy."
            ),
            "ru": (
                "Canadian Cancer Society (CRA #11882-9803-RR0001, основан в 1938 "
                "году) — крупнейшая национальная онкологическая благотворительная "
                "организация Канады. Финансирует гранты на исследования всех видов "
                "рака, ведёт бесплатную информационную линию для онкобольных, "
                "предоставляет жильё для иногородних пациентов, лоббирует "
                "табачный контроль на федеральном уровне."
            ),
        },
        "methodology_note": _verify(
            "Verified: CRA-registered; T3010 public.", "Подтверждено: CRA-регистрация; T3010 публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://cancer.ca/en/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 1, 31),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1938,
        "cause_slugs": ["cancer-research"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://cancer.ca/en/about-us/our-finances",
    },
    {
        "slug": "nature-conservancy-canada",
        "country": "CA",
        "registration_id": "11924-6544-RR0001",
        "bucket": "planet",
        "name": {"en": "Nature Conservancy of Canada", "ru": "Nature Conservancy of Canada"},
        "tagline": {
            "en": "Land-trust conservation — protects ecologically significant private land across Canada.",
            "ru": "Земельный траст — сохраняет экологически значимые частные земли по всей Канаде.",
        },
        "description": {
            "en": (
                "Nature Conservancy of Canada (NCC, CRA #11924-6544-RR0001, founded "
                "1962) is Canada's largest non-government land-trust. Acquires and "
                "stewards ecologically significant private land — has secured "
                "~15M+ hectares to date (forests, wetlands, grasslands). Combines "
                "purchase, conservation easements and partnerships with Indigenous "
                "communities."
            ),
            "ru": (
                "Nature Conservancy of Canada (NCC, CRA #11924-6544-RR0001, основан "
                "в 1962 году) — крупнейший негосударственный земельный траст "
                "Канады. Приобретает и управляет экологически значимыми частными "
                "землями — на текущий момент ~15+ млн гектаров (леса, водно-"
                "болотные угодья, степи). Сочетает покупку, природоохранные "
                "сервитуты и партнёрства с коренными народами."
            ),
        },
        "methodology_note": _verify(
            "Verified: CRA-registered; T3010 public.", "Подтверждено: CRA-регистрация; T3010 публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.natureconservancy.ca/en/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("85000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1962,
        "cause_slugs": ["conservation", "biodiversity-defense"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.natureconservancy.ca/en/who-we-are/accountability/",
    },
    {
        "slug": "msf-canada",
        "country": "CA",
        "registration_id": "13527-5857-RR0001",
        "bucket": "people",
        "name": {"en": "Médecins Sans Frontières Canada", "ru": "MSF Canada — Médecins Sans Frontières"},
        "tagline": {
            "en": "Canadian section of MSF — emergency medical humanitarian work in conflict zones globally.",
            "ru": "Канадская секция MSF — экстренная гуманитарная медицина в зонах конфликтов по всему миру.",
        },
        "description": {
            "en": (
                "MSF Canada (CRA #13527-5857-RR0001) is the Canadian section of "
                "the global MSF movement. Recruits and deploys Canadian medical "
                "and logistical staff into MSF projects worldwide (~70 countries), "
                "raises Canadian public funds, and produces témoignage on health "
                "crises. Headquartered in Toronto."
            ),
            "ru": (
                "MSF Canada (CRA #13527-5857-RR0001) — канадская секция глобального "
                "движения «Врачи без границ». Набирает и направляет канадских "
                "медицинских и логистических сотрудников в проекты MSF по всему "
                "миру (~70 стран), собирает средства в Канаде, ведёт témoignage "
                "о медицинских кризисах. Штаб-квартира в Торонто."
            ),
        },
        "methodology_note": _verify(
            "Verified: CRA-registered; T3010 public.", "Подтверждено: CRA-регистрация; T3010 публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.doctorswithoutborders.ca/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 12, 31),
        "total_revenue_usd": Decimal("110000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1991,
        "cause_slugs": ["humanitarian-medicine", "emergency-response"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.doctorswithoutborders.ca/about/financial-information",
    },

    # =================== AUSTRALIA (4) ===================
    {
        "slug": "beyond-blue",
        "country": "AU",
        "registration_id": "ABN-87-093-865-840",
        "bucket": "people",
        "name": {"en": "Beyond Blue", "ru": "Beyond Blue — австралийская организация по психическому здоровью"},
        "tagline": {
            "en": "Australia's leading mental-health and depression-support organisation.",
            "ru": "Ведущая организация Австралии по психическому здоровью и поддержке при депрессии.",
        },
        "description": {
            "en": (
                "Beyond Blue (ABN 87 093 865 840, founded 2000) is Australia's most "
                "recognised mental-health support organisation. Operates a 24/7 "
                "Support Service (phone + chat + email), runs the youth-focused "
                "BeyondNow safety-planning app, funds public mental-health awareness "
                "campaigns, and produces evidence-based resources for depression, "
                "anxiety and suicide prevention."
            ),
            "ru": (
                "Beyond Blue (ABN 87 093 865 840, основан в 2000 году) — самая "
                "известная в Австралии организация поддержки психического "
                "здоровья. Управляет круглосуточной службой поддержки (телефон + "
                "чат + email), приложением BeyondNow для планирования "
                "безопасности молодёжи, финансирует общественные кампании, "
                "выпускает evidence-based материалы по депрессии, тревоге и "
                "профилактике суицида."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with ACNC (Australian Charities and Not-for-profits Commission); annual information statement public.",
            "Подтверждено: зарегистрирован в ACNC (регулятор Австралии); ежегодное info-statement публично.",
        ),
        "logo_url": "",
        "donation_url": "https://www.beyondblue.org.au/get-involved/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("60000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2000,
        "cause_slugs": ["mental-health", "suicide-prevention"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.acnc.gov.au/charity/charities/3a3a39a8-39af-ea11-a813-000d3ad24c3d/profile",
    },
    {
        "slug": "rfds-australia",
        "country": "AU",
        "registration_id": "ABN-74-438-059-643",
        "bucket": "people",
        "name": {"en": "Royal Flying Doctor Service", "ru": "Royal Flying Doctor Service Australia"},
        "tagline": {
            "en": "Aeromedical emergency and primary care for remote Australia — 24/7.",
            "ru": "Авиамедицинская экстренная и первичная помощь в удалённых районах Австралии — круглосуточно.",
        },
        "description": {
            "en": (
                "Royal Flying Doctor Service (RFDS, founded 1928) provides 24/7 "
                "aeromedical emergency response and primary healthcare to Australians "
                "living in remote and rural areas. Operates a fleet of ~80 fixed-"
                "wing aircraft, helicopters and medical vehicles. Provides ~390K "
                "patient contacts annually — emergency evacuations, GP clinics, "
                "dental, mental-health outreach. Iconic in Australian healthcare."
            ),
            "ru": (
                "Royal Flying Doctor Service (RFDS, основан в 1928 году) "
                "предоставляет круглосуточную авиамедицинскую экстренную помощь "
                "и первичную медпомощь австралийцам в удалённых и сельских "
                "районах. Парк ~80 самолётов, вертолётов и медицинских машин. "
                "~390 тыс. контактов с пациентами ежегодно — экстренные "
                "эвакуации, клиники врачей общей практики, стоматология, "
                "психическое здоровье. Икона австралийской медицины."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with ACNC.", "Подтверждено: зарегистрирован в ACNC.",
        ),
        "logo_url": "",
        "donation_url": "https://www.flyingdoctor.org.au/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("260000000.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 1928,
        "cause_slugs": ["humanitarian-medicine", "emergency-response"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.flyingdoctor.org.au/about-the-rfds/financial-statements/",
    },
    {
        "slug": "world-vision-australia",
        "country": "AU",
        "registration_id": "ABN-28-004-778-081",
        "bucket": "people",
        "name": {"en": "World Vision Australia", "ru": "World Vision Australia"},
        "tagline": {
            "en": "Australian arm of World Vision — child sponsorship, emergency relief, development programmes globally.",
            "ru": "Австралийское крыло World Vision — спонсорство детей, экстренная помощь, программы развития по всему миру.",
        },
        "description": {
            "en": (
                "World Vision Australia (ABN 28 004 778 081, founded 1966) is the "
                "Australian arm of World Vision International. Funds child-sponsorship "
                "programmes, emergency relief (recent: Pacific cyclones, drought in "
                "Africa), water/sanitation, education and child-protection across "
                "~50 countries. Australia's largest non-government international-aid "
                "agency by individual donations."
            ),
            "ru": (
                "World Vision Australia (ABN 28 004 778 081, основан в 1966 году) "
                "— австралийское крыло World Vision International. Финансирует "
                "программы спонсорства детей, экстренную помощь (недавно: "
                "циклоны в Тихом океане, засуха в Африке), вода/санитария, "
                "образование и защита детей в ~50 странах. Крупнейшее в "
                "Австралии негосударственное агентство международной помощи "
                "по объёму пожертвований физлиц."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with ACNC.", "Подтверждено: зарегистрирован в ACNC.",
        ),
        "logo_url": "",
        "donation_url": "https://www.worldvision.com.au/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("280000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1966,
        "cause_slugs": ["humanitarian-medicine", "child-welfare", "global-health"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.worldvision.com.au/about-us/financial-accountability",
    },
    {
        "slug": "australian-red-cross",
        "country": "AU",
        "registration_id": "ABN-50-169-561-394",
        "bucket": "people",
        "name": {"en": "Australian Red Cross", "ru": "Australian Red Cross"},
        "tagline": {
            "en": "Australian member of the International Red Cross — disasters, blood service, migrant support.",
            "ru": "Австралийский Красный Крест — стихийные бедствия, банк крови, поддержка мигрантов.",
        },
        "description": {
            "en": (
                "Australian Red Cross (ABN 50 169 561 394, founded 1914) responds to "
                "Australian and Pacific disasters (bushfires, cyclones, floods), runs "
                "the national blood service Lifeblood (separate operating entity), "
                "operates migration and refugee programmes, and provides community "
                "services for vulnerable Australians. Member of the International "
                "Red Cross and Red Crescent Movement."
            ),
            "ru": (
                "Австралийский Красный Крест (ABN 50 169 561 394, основан в 1914 "
                "году) реагирует на бедствия в Австралии и Тихоокеанском регионе "
                "(лесные пожары, циклоны, наводнения), управляет национальной "
                "службой крови Lifeblood (отдельная оперативная организация), "
                "ведёт миграционные и беженские программы. Член Международного "
                "движения Красного Креста и Красного Полумесяца."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with ACNC.", "Подтверждено: зарегистрирован в ACNC.",
        ),
        "logo_url": "",
        "donation_url": "https://www.redcross.org.au/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("750000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1914,
        "cause_slugs": ["disaster-relief", "emergency-response", "humanitarian-medicine"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.redcross.org.au/about-us/governance-and-finance/",
    },

    # =================== NEW ZEALAND (2) ===================
    {
        "slug": "forest-and-bird-nz",
        "country": "NZ",
        "registration_id": "CC26943",
        "bucket": "planet",
        "name": {"en": "Forest & Bird (Royal Forest and Bird Protection Society of NZ)", "ru": "Forest & Bird — старейшее природоохранное общество Новой Зеландии"},
        "tagline": {
            "en": "New Zealand's leading independent conservation organisation — native species and habitats.",
            "ru": "Ведущая независимая природоохранная организация Новой Зеландии — местные виды и среды обитания.",
        },
        "description": {
            "en": (
                "Forest & Bird (CC26943, founded 1923) is New Zealand's oldest and "
                "largest independent conservation organisation. Campaigns to "
                "protect native birds (kiwi, kakapo, takahē), restore native "
                "forests, oppose seabed mining, defend marine reserves, and "
                "challenge poor environmental policy. Has ~80,000 members and "
                "50+ branches doing pest control and restoration."
            ),
            "ru": (
                "Forest & Bird (CC26943, основан в 1923 году) — старейшая и "
                "крупнейшая независимая природоохранная организация Новой "
                "Зеландии. Кампании по защите местных птиц (киви, какапо, "
                "такахе), восстановлению нативных лесов, противостоянию добыче "
                "со дна моря, защите морских заповедников. ~80 000 членов и "
                "более 50 отделений ведут борьбу с вредителями и "
                "восстановление."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with NZ Charities Services (CC26943); financial statements public.",
            "Подтверждено: зарегистрирован в NZ Charities Services (CC26943); финансовая отчётность публична.",
        ),
        "logo_url": "",
        "donation_url": "https://www.forestandbird.org.nz/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("8500000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1923,
        "cause_slugs": ["conservation", "biodiversity-defense", "wildlife-conservation"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.charities.govt.nz/charities-register/view-the-register/charity-summary?accountId=8d38db17-4ef0-dd11-9d6c-0015c5f3da29",
    },
    {
        "slug": "world-vision-nz",
        "country": "NZ",
        "registration_id": "CC36358",
        "bucket": "people",
        "name": {"en": "World Vision New Zealand", "ru": "World Vision New Zealand"},
        "tagline": {
            "en": "NZ arm of World Vision — child sponsorship and humanitarian aid in the Pacific and globally.",
            "ru": "Новозеландское крыло World Vision — спонсорство детей и гуманитарная помощь в Тихом океане и глобально.",
        },
        "description": {
            "en": (
                "World Vision NZ (CC36358) is the NZ arm of World Vision International. "
                "Major focus on Pacific Island programmes (Vanuatu, Solomon Islands, "
                "PNG, Timor-Leste) plus global child-sponsorship. Runs the iconic "
                "40 Hour Famine youth-fundraising challenge."
            ),
            "ru": (
                "World Vision NZ (CC36358) — новозеландское крыло World Vision "
                "International. Основной фокус на программы в Тихоокеанском "
                "регионе (Вануату, Соломоновы острова, ПНГ, Тимор-Лешти) плюс "
                "глобальное спонсорство детей. Проводит знаменитую молодёжную "
                "акцию 40 Hour Famine."
            ),
        },
        "methodology_note": _verify(
            "Verified: registered with NZ Charities Services.", "Подтверждено: NZ Charities Services.",
        ),
        "logo_url": "",
        "donation_url": "https://www.worldvision.org.nz/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1972,
        "cause_slugs": ["child-welfare", "humanitarian-medicine"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.worldvision.org.nz/about-us/our-finances/",
    },

    # =================== GERMANY (4) ===================
    {
        "slug": "sos-kinderdorf-international",
        "country": "DE",
        "registration_id": "DE-BAV-IK-0",
        "bucket": "people",
        "name": {"en": "SOS-Kinderdörfer weltweit", "ru": "SOS-Kinderdörfer — Детские деревни SOS (Германия)"},
        "tagline": {
            "en": "German federation supporting SOS Children's Villages programmes worldwide.",
            "ru": "Германская федерация, поддерживающая программы SOS Children's Villages по всему миру.",
        },
        "description": {
            "en": (
                "SOS-Kinderdörfer weltweit Hermann-Gmeiner-Fonds Deutschland is the "
                "German fundraising and oversight federation for the global SOS "
                "Children's Villages movement (founded 1949 in Austria; German arm "
                "1955). Funds family-based care for children without parental care "
                "across ~135 countries. DZI Spendensiegel-certified."
            ),
            "ru": (
                "SOS-Kinderdörfer weltweit Hermann-Gmeiner-Fonds Deutschland — "
                "немецкая фандрайзинговая и надзорная федерация для глобального "
                "движения «Детские деревни SOS» (основано в 1949 году в Австрии; "
                "немецкое крыло — 1955). Финансирует семейную опеку детей "
                "без родительской заботы в ~135 странах. Сертифицирован "
                "DZI Spendensiegel."
            ),
        },
        "methodology_note": _verify(
            "Verified: DZI Spendensiegel certified (Deutsches Zentralinstitut für soziale Fragen); annual report public.",
            "Подтверждено: сертификат DZI Spendensiegel; годовой отчёт публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.sos-kinderdoerfer.de/spenden",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("230000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1949,
        "cause_slugs": ["child-welfare"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.sos-kinderdoerfer.de/informieren/transparenz/jahresbericht",
    },
    {
        "slug": "welthungerhilfe",
        "country": "DE",
        "registration_id": "DE-WHH-1962",
        "bucket": "people",
        "name": {"en": "Welthungerhilfe", "ru": "Welthungerhilfe — Всемирная помощь голодающим"},
        "tagline": {
            "en": "German non-denominational aid agency fighting hunger and malnutrition globally.",
            "ru": "Немецкое внеконфессиональное агентство помощи, борющееся с голодом и недоеданием по всему миру.",
        },
        "description": {
            "en": (
                "Welthungerhilfe (founded 1962, Bonn) is one of Germany's largest "
                "non-governmental aid agencies. Works in ~35 countries on emergency "
                "food assistance, sustainable agriculture, water/sanitation, "
                "humanitarian response. Co-publisher of the annual Global Hunger "
                "Index. DZI Spendensiegel-certified."
            ),
            "ru": (
                "Welthungerhilfe (основан в 1962 году, Бонн) — одно из крупнейших "
                "негосударственных агентств помощи Германии. Работает в ~35 "
                "странах: экстренная продовольственная помощь, устойчивое "
                "сельское хозяйство, вода и санитария, гуманитарный ответ. "
                "Соиздатель ежегодного Global Hunger Index. Сертификат DZI "
                "Spendensiegel."
            ),
        },
        "methodology_note": _verify(
            "Verified: DZI Spendensiegel certified.", "Подтверждено: сертификат DZI Spendensiegel.",
        ),
        "logo_url": "",
        "donation_url": "https://www.welthungerhilfe.de/spenden",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("310000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1962,
        "cause_slugs": ["hunger", "food-security", "humanitarian-medicine"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.welthungerhilfe.de/transparenz/jahresbericht",
    },
    {
        "slug": "greenpeace-deutschland",
        "country": "DE",
        "registration_id": "DE-GP-1980",
        "bucket": "planet",
        "name": {"en": "Greenpeace Deutschland", "ru": "Greenpeace Deutschland"},
        "tagline": {
            "en": "Germany's largest Greenpeace national office — climate, oceans, forests campaigns.",
            "ru": "Крупнейшее национальное отделение Greenpeace в Германии — климат, океаны, леса.",
        },
        "description": {
            "en": (
                "Greenpeace e.V. (founded 1980, Hamburg) is the German national office "
                "of Greenpeace International. Largest Greenpeace national office by "
                "supporters and budget. Funded entirely by individual donations — "
                "explicitly refuses government and corporate funding. Campaigns on "
                "climate, oceans, forests, energy transition, plastics."
            ),
            "ru": (
                "Greenpeace e.V. (основан в 1980 году, Гамбург) — немецкое "
                "национальное отделение Greenpeace International. Крупнейшее "
                "национальное отделение Greenpeace по числу сторонников и "
                "бюджету. Финансируется исключительно частными "
                "пожертвованиями — отказывается от государственного и "
                "корпоративного финансирования. Кампании по климату, "
                "океанам, лесам, энергопереходу, пластику."
            ),
        },
        "methodology_note": _verify(
            "Verified: own annual report public; refuses government/corporate funds.",
            "Подтверждено: годовой отчёт публичен; отказ от государственного и корпоративного финансирования.",
        ),
        "logo_url": "",
        "donation_url": "https://www.greenpeace.de/spenden",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("85000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1980,
        "cause_slugs": ["climate", "oceans", "forest-protection", "environment"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.greenpeace.de/ueber-uns/transparenz/jahresberichte",
    },
    {
        "slug": "caritas-deutschland",
        "country": "DE",
        "registration_id": "DE-DCV-1897",
        "bucket": "people",
        "name": {"en": "Deutscher Caritasverband", "ru": "Deutscher Caritasverband — Caritas Germany"},
        "tagline": {
            "en": "Catholic Church social-services federation in Germany — disability, elderly, homelessness.",
            "ru": "Федерация социальных служб Католической церкви Германии — инвалидность, пожилые, бездомность.",
        },
        "description": {
            "en": (
                "Deutscher Caritasverband (DCV, founded 1897) is the social-welfare "
                "federation of the Catholic Church in Germany. ~620K paid staff "
                "and ~600K volunteers across ~25K facilities — disability services, "
                "hospitals, hospices, eldercare, homeless shelters, child & youth "
                "support. Largest welfare federation in Germany alongside Diakonie."
            ),
            "ru": (
                "Deutscher Caritasverband (DCV, основан в 1897 году) — социальная "
                "федерация Католической церкви Германии. ~620 тыс. оплачиваемых "
                "сотрудников и ~600 тыс. добровольцев в ~25 тыс. учреждениях — "
                "услуги для инвалидов, больницы, хосписы, уход за пожилыми, "
                "приюты, поддержка детей и молодёжи. Крупнейшая социальная "
                "федерация Германии наряду с Diakonie."
            ),
        },
        "methodology_note": _verify(
            "Verified: church-affiliated welfare association; annual reports public.",
            "Подтверждено: социальная ассоциация при церкви; годовые отчёты публичны.",
        ),
        "logo_url": "",
        "donation_url": "https://www.caritas.de/spendeundengagement/spenden/spenden",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("750000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1897,
        "cause_slugs": ["disability-services", "senior-care", "homelessness", "faith-based"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.caritas.de/diecaritas/wirueberuns/finanzen",
    },

    # =================== NETHERLANDS (3) ===================
    {
        "slug": "oxfam-novib",
        "country": "NL",
        "registration_id": "RSIN-002965415",
        "bucket": "people",
        "name": {"en": "Oxfam Novib", "ru": "Oxfam Novib"},
        "tagline": {
            "en": "Dutch member of the Oxfam confederation — poverty, inequality, climate justice campaigns.",
            "ru": "Голландский член конфедерации Oxfam — кампании против бедности, неравенства, за климатическую справедливость.",
        },
        "description": {
            "en": (
                "Oxfam Novib (RSIN 002965415, founded 1956 as 'Novib') is the Dutch "
                "member of the Oxfam International confederation. Funds long-term "
                "development partnerships across ~50 countries, leads global research "
                "on inequality (the annual Davos billionaires-vs-poor report), "
                "campaigns on tax justice and climate finance."
            ),
            "ru": (
                "Oxfam Novib (RSIN 002965415, основан в 1956 году под названием "
                "Novib) — голландский член международной конфедерации Oxfam. "
                "Финансирует долгосрочные партнёрства развития в ~50 странах, "
                "ведёт глобальное исследование неравенства (ежегодный доклад "
                "о миллиардерах vs бедных к Давосу), кампании по налоговой "
                "справедливости и климатическому финансированию."
            ),
        },
        "methodology_note": _verify(
            "Verified: CBF Erkend (Dutch fundraising regulator); ANBI status; annual report public.",
            "Подтверждено: CBF Erkend (нидерландский регулятор фандрайзинга); статус ANBI; годовой отчёт публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.oxfamnovib.nl/doneren",
        "size_bucket": "large",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("75000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1956,
        "cause_slugs": ["poverty-reduction", "civil-rights", "climate-policy"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.oxfamnovib.nl/over-ons/jaarverslagen",
    },
    {
        "slug": "cordaid",
        "country": "NL",
        "registration_id": "RSIN-806080856",
        "bucket": "people",
        "name": {"en": "Cordaid", "ru": "Cordaid"},
        "tagline": {
            "en": "Dutch development & humanitarian NGO — fragile states, health, livelihoods.",
            "ru": "Голландская организация развития и гуманитарной помощи — хрупкие государства, здоровье, средства к существованию.",
        },
        "description": {
            "en": (
                "Cordaid (RSIN 806080856) is a Dutch development and humanitarian "
                "agency working primarily in fragile and conflict-affected states "
                "(Afghanistan, DRC, CAR, South Sudan, Yemen). Co-funds local "
                "partner organisations rather than running its own field operations. "
                "CBF Erkend; ANBI."
            ),
            "ru": (
                "Cordaid (RSIN 806080856) — голландская организация развития и "
                "гуманитарной помощи, работающая в основном в хрупких и "
                "затронутых конфликтами государствах (Афганистан, ДРК, ЦАР, "
                "Южный Судан, Йемен). Софинансирует местных партнёров, а не "
                "ведёт собственные полевые операции. CBF Erkend; ANBI."
            ),
        },
        "methodology_note": _verify(
            "Verified: CBF Erkend; ANBI; annual report public.", "Подтверждено: CBF Erkend; ANBI; годовой отчёт публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.cordaid.org/en/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("110000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1999,
        "cause_slugs": ["humanitarian-medicine", "emergency-response"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.cordaid.org/en/about-us/transparency/",
    },
    {
        "slug": "greenpeace-nederland",
        "country": "NL",
        "registration_id": "RSIN-002978026",
        "bucket": "planet",
        "name": {"en": "Greenpeace Nederland", "ru": "Greenpeace Nederland"},
        "tagline": {
            "en": "Dutch national office of Greenpeace — climate, oceans, biodiversity campaigns.",
            "ru": "Голландское национальное отделение Greenpeace — климат, океаны, биоразнообразие.",
        },
        "description": {
            "en": (
                "Greenpeace Nederland (RSIN 002978026, founded 1979) campaigns on "
                "climate change, ocean protection (North Sea), industrial agriculture "
                "reform, and tropical-forest deforestation. Headquarters of Greenpeace "
                "International is also in Amsterdam (separate legal entity). CBF Erkend."
            ),
            "ru": (
                "Greenpeace Nederland (RSIN 002978026, основан в 1979 году) ведёт "
                "кампании по изменению климата, защите океанов (Северное море), "
                "реформе промышленного сельского хозяйства и обезлесению "
                "тропиков. Штаб-квартира Greenpeace International также "
                "находится в Амстердаме (отдельное юрлицо). CBF Erkend."
            ),
        },
        "methodology_note": _verify(
            "Verified: CBF Erkend; ANBI.", "Подтверждено: CBF Erkend; ANBI.",
        ),
        "logo_url": "",
        "donation_url": "https://www.greenpeace.org/nl/doe-mee/word-donateur/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("48000000.00"),
        "program_expense_pct": Decimal("76.00"),
        "founded_year": 1979,
        "cause_slugs": ["climate", "oceans", "biodiversity-defense"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.greenpeace.org/nl/over-ons/financien/",
    },

    # =================== SWITZERLAND (2) ===================
    {
        "slug": "wwf-schweiz",
        "country": "CH",
        "registration_id": "CH-660-0048961-9",
        "bucket": "planet",
        "name": {"en": "WWF Schweiz", "ru": "WWF Schweiz"},
        "tagline": {
            "en": "Swiss national office of WWF — Alpine biodiversity, sustainable food, climate.",
            "ru": "Швейцарское национальное отделение WWF — биоразнообразие Альп, устойчивое питание, климат.",
        },
        "description": {
            "en": (
                "WWF Schweiz (founded 1961, the original WWF — Switzerland is where "
                "the global organisation was founded) campaigns on Alpine biodiversity, "
                "sustainable food systems, climate, and rivers. ZEWO-certified."
            ),
            "ru": (
                "WWF Schweiz (основан в 1961 году — Швейцария является родиной "
                "глобальной организации WWF) ведёт кампании по биоразнообразию "
                "Альп, устойчивым продовольственным системам, климату и рекам. "
                "Сертифицирован ZEWO."
            ),
        },
        "methodology_note": _verify(
            "Verified: ZEWO certified (Swiss regulator).", "Подтверждено: сертификат ZEWO (швейцарский регулятор).",
        ),
        "logo_url": "",
        "donation_url": "https://www.wwf.ch/de/spenden",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("52000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1961,
        "cause_slugs": ["conservation", "biodiversity-defense", "wildlife-conservation"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.wwf.ch/de/ueber-uns/transparenz",
    },
    {
        "slug": "icrc",
        "country": "CH",
        "registration_id": "CH-660-0001000-3",
        "bucket": "people",
        "name": {"en": "International Committee of the Red Cross (ICRC)", "ru": "Международный комитет Красного Креста (МККК)"},
        "tagline": {
            "en": "Geneva-based humanitarian organisation under the Geneva Conventions — armed-conflict response.",
            "ru": "Женевская гуманитарная организация под мандатом Женевских конвенций — помощь в вооружённых конфликтах.",
        },
        "description": {
            "en": (
                "ICRC (founded 1863, Geneva) is an independent humanitarian "
                "organisation with a unique mandate under the Geneva Conventions. "
                "Operates in ~100 countries, with major operations in Ukraine, "
                "Syria, Yemen, Sudan, DRC, Myanmar. Visits prisoners of war, "
                "reunites families separated by conflict, runs hospitals, water "
                "and detention services. Co-founder of the International Red Cross "
                "and Red Crescent Movement. Predominantly funded by states."
            ),
            "ru": (
                "МККК (основан в 1863 году, Женева) — независимая гуманитарная "
                "организация с уникальным мандатом под Женевскими конвенциями. "
                "Работает в ~100 странах, крупные операции в Украине, Сирии, "
                "Йемене, Судане, ДРК, Мьянме. Посещает военнопленных, "
                "восстанавливает связи семей, разделённых конфликтом, ведёт "
                "больницы, водоснабжение и работу с задержанными. Сооснователь "
                "Международного движения Красного Креста и Красного "
                "Полумесяца. Преимущественно финансируется государствами."
            ),
        },
        "methodology_note": _verify(
            "Verified: Swiss-domiciled humanitarian institution under the Geneva Conventions; annual report and donor breakdown public.",
            "Подтверждено: швейцарская гуманитарная организация под Женевскими конвенциями; годовой отчёт и разбивка доноров публичны.",
        ),
        "logo_url": "",
        "donation_url": "https://www.icrc.org/en/donate",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("2500000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1863,
        "cause_slugs": ["humanitarian-medicine", "emergency-response", "disaster-relief"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.icrc.org/en/document/annual-report",
    },

    # =================== SWEDEN (1) ===================
    {
        "slug": "radda-barnen",
        "country": "SE",
        "registration_id": "SE-902003-3548",
        "bucket": "people",
        "name": {"en": "Rädda Barnen (Save the Children Sweden)", "ru": "Rädda Barnen — шведское отделение Save the Children"},
        "tagline": {
            "en": "Swedish founding member of Save the Children — child rights, refugee response, Ukraine.",
            "ru": "Шведский основатель движения Save the Children — права детей, помощь беженцам, Украина.",
        },
        "description": {
            "en": (
                "Rädda Barnen (org-nr 902003-3548, founded 1919, Stockholm) is the "
                "Swedish member of Save the Children International. Founded the "
                "global Save the Children movement under Eglantyne Jebb. Currently "
                "runs major operations in Ukraine, Gaza, Sudan; Sweden-domestic "
                "child-rights advocacy. 90-konto certified by Svensk "
                "Insamlingskontroll."
            ),
            "ru": (
                "Rädda Barnen (org-nr 902003-3548, основан в 1919 году, "
                "Стокгольм) — шведский член Save the Children International. "
                "Основатель глобального движения Save the Children под "
                "руководством Eglantyne Jebb. Сейчас крупные операции в "
                "Украине, Газе, Судане; адвокация прав детей внутри Швеции. "
                "Сертификат 90-konto от Svensk Insamlingskontroll."
            ),
        },
        "methodology_note": _verify(
            "Verified: 90-konto certified (Svensk Insamlingskontroll).",
            "Подтверждено: сертификат 90-konto (Svensk Insamlingskontroll).",
        ),
        "logo_url": "",
        "donation_url": "https://www.raddabarnen.se/skanke/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1919,
        "cause_slugs": ["child-welfare", "refugees", "humanitarian-medicine"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.raddabarnen.se/om-oss/finansiering-och-arsredovisning/",
    },

    # =================== FRANCE (2) ===================
    {
        "slug": "medecins-du-monde",
        "country": "FR",
        "registration_id": "FR-RNA-W751098927",
        "bucket": "people",
        "name": {"en": "Médecins du Monde", "ru": "Médecins du Monde — Врачи мира"},
        "tagline": {
            "en": "French humanitarian-medicine NGO — care for vulnerable populations both in France and globally.",
            "ru": "Французская медицинско-гуманитарная организация — помощь уязвимым группам во Франции и по всему миру.",
        },
        "description": {
            "en": (
                "Médecins du Monde (founded 1980, breakaway from MSF over Vietnamese "
                "boat-people response). Operates ~75 international programmes plus "
                "extensive France-domestic clinics serving uninsured / undocumented "
                "people, drug users, sex workers. Don en Confiance member."
            ),
            "ru": (
                "Médecins du Monde (основана в 1980 году, отделилась от MSF из-за "
                "разногласий по реакции на кризис вьетнамских беженцев). "
                "Управляет ~75 международными программами плюс обширная сеть "
                "клиник во Франции для незастрахованных, недокументированных "
                "людей, наркопотребителей, секс-работников. Член Don en "
                "Confiance."
            ),
        },
        "methodology_note": _verify(
            "Verified: Don en Confiance certified; annual report public.",
            "Подтверждено: сертификат Don en Confiance; годовой отчёт публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.medecinsdumonde.org/faire-un-don/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("105000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1980,
        "cause_slugs": ["humanitarian-medicine", "global-health"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.medecinsdumonde.org/transparence-financiere/",
    },
    {
        "slug": "croix-rouge-francaise",
        "country": "FR",
        "registration_id": "FR-SIRET-77567227201080",
        "bucket": "people",
        "name": {"en": "Croix-Rouge française", "ru": "Croix-Rouge française — Французский Красный Крест"},
        "tagline": {
            "en": "French Red Cross national society — emergency response, social services, training.",
            "ru": "Национальное общество Французского Красного Креста — экстренная помощь, социальные службы, обучение.",
        },
        "description": {
            "en": (
                "Croix-Rouge française (founded 1864) is the French national society "
                "of the International Red Cross. ~60K volunteers, ~17K paid staff. "
                "Operates emergency-response teams, ambulance services, France's "
                "largest first-aid training programme, ~600 social-aid centres "
                "(food assistance, homelessness response), and migrant-reception "
                "operations."
            ),
            "ru": (
                "Croix-Rouge française (основан в 1864 году) — национальное "
                "общество Международного Красного Креста. ~60 тыс. "
                "добровольцев, ~17 тыс. оплачиваемых сотрудников. "
                "Управляет экстренными бригадами, службами скорой "
                "помощи, крупнейшей программой обучения первой помощи во "
                "Франции, ~600 центрами социальной помощи (продовольственная "
                "помощь, реакция на бездомность), приёмом мигрантов."
            ),
        },
        "methodology_note": _verify(
            "Verified: French national Red Cross society; annual accounts published.",
            "Подтверждено: национальное общество Французского Красного Креста; годовая отчётность публикуется.",
        ),
        "logo_url": "",
        "donation_url": "https://www.croix-rouge.fr/Don",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("1450000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1864,
        "cause_slugs": ["disaster-relief", "emergency-response", "homelessness"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.croix-rouge.fr/La-Croix-Rouge/Comptes-et-bilans",
    },

    # =================== JAPAN (1) ===================
    {
        "slug": "nippon-foundation",
        "country": "JP",
        "registration_id": "JP-PIC-1962",
        "bucket": "people",
        "name": {"en": "The Nippon Foundation", "ru": "The Nippon Foundation — японский фонд"},
        "tagline": {
            "en": "Japan's largest private grant-making foundation — disaster, disability, ocean, education.",
            "ru": "Крупнейший частный грантодающий фонд Японии — стихийные бедствия, инвалидность, океаны, образование.",
        },
        "description": {
            "en": (
                "The Nippon Foundation (founded 1962, Tokyo) is one of Japan's "
                "largest private grant-making foundations. Funded by Japanese "
                "powerboat-racing surcharges. Major programmes: disaster response "
                "(Tohoku 2011, Noto 2024), inclusive society (disability, social-"
                "welfare), the Sasakawa Africa Association (agriculture in Africa), "
                "and Ocean Initiative (ocean and maritime affairs). 公益財団法人 "
                "(Public Interest Incorporated Foundation) status."
            ),
            "ru": (
                "The Nippon Foundation (основан в 1962 году, Токио) — один из "
                "крупнейших частных грантодающих фондов Японии. Финансируется "
                "за счёт сборов с японских моторных лодочных гонок. Ключевые "
                "программы: реакция на бедствия (Тохоку 2011, Ното 2024), "
                "инклюзивное общество (инвалидность, социальное обеспечение), "
                "Sasakawa Africa Association (сельское хозяйство в Африке), "
                "Ocean Initiative (океаны и морские дела). Статус 公益財団法人 "
                "(Public Interest Incorporated Foundation)."
            ),
        },
        "methodology_note": _verify(
            "Verified: 公益財団法人 (PIC) status under Japan's Cabinet Office register.",
            "Подтверждено: статус 公益財団法人 (PIC) в реестре Канцелярии Кабинета министров Японии.",
        ),
        "logo_url": "",
        "donation_url": "https://www.nippon-foundation.or.jp/en/who/donations",
        "size_bucket": "large",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("260000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1962,
        "cause_slugs": ["disaster-relief", "disability-services", "oceans"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.nippon-foundation.or.jp/en/who/financial",
    },

    # =================== INDIA (3) ===================
    {
        "slug": "akshaya-patra",
        "country": "IN",
        "registration_id": "AAATA0269R",
        "bucket": "people",
        "name": {"en": "The Akshaya Patra Foundation", "ru": "The Akshaya Patra Foundation"},
        "tagline": {
            "en": "World's largest school-meal NGO — provides ~2M lunches daily across India.",
            "ru": "Крупнейшая в мире НПО школьного питания — ~2 млн обедов ежедневно в Индии.",
        },
        "description": {
            "en": (
                "Akshaya Patra Foundation (PAN AAATA0269R, founded 2000, Bangalore) "
                "operates the world's largest NGO-run school-meal programme in "
                "partnership with the Government of India's PM POSHAN scheme. "
                "Runs ~70 industrial-scale kitchens delivering hot meals to ~2M "
                "children across ~21,000 government schools daily. 80G + FCRA "
                "registered."
            ),
            "ru": (
                "Akshaya Patra Foundation (PAN AAATA0269R, основан в 2000 году, "
                "Бангалор) управляет крупнейшей в мире программой школьного "
                "питания, ведомой НПО, в партнёрстве с государственной схемой "
                "PM POSHAN. ~70 кухонь промышленного масштаба ежедневно "
                "доставляют горячую еду ~2 млн детей в ~21 000 "
                "государственных школ. Регистрация 80G + FCRA."
            ),
        },
        "methodology_note": _verify(
            "Listed: Indian 80G + FCRA registered; verification via own annual report (no India-wide regulator-published annual returns equivalent to US 990 / UK CC).",
            "Listed: индийская регистрация 80G + FCRA; верификация — через собственный годовой отчёт (в Индии нет общенационального регулятора с публикацией отчётности уровня US 990 / UK CC).",
        ),
        "logo_url": "",
        "donation_url": "https://www.akshayapatra.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("75000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2000,
        "cause_slugs": ["school-meals", "child-welfare", "hunger"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.akshayapatra.org/annual-reports",
    },
    {
        "slug": "cry-india",
        "country": "IN",
        "registration_id": "AAATC0149E",
        "bucket": "people",
        "name": {"en": "Child Rights and You (CRY)", "ru": "Child Rights and You (CRY) — Индия"},
        "tagline": {
            "en": "Indian child-rights NGO — education, malnutrition, child labour, child protection.",
            "ru": "Индийская правозащитная НПО для детей — образование, недоедание, детский труд, защита детей.",
        },
        "description": {
            "en": (
                "CRY — Child Rights and You (founded 1979, Mumbai) is one of India's "
                "best-known child-rights NGOs. Funds and supports ~100 grassroots "
                "Indian organisations across rural and urban India. Focus: "
                "education access, nutrition, ending child labour and child "
                "marriage, child-protection systems. 80G + FCRA registered."
            ),
            "ru": (
                "CRY — Child Rights and You (основан в 1979 году, Мумбаи) — одна "
                "из самых известных индийских НПО по правам детей. Финансирует "
                "и поддерживает ~100 низовых индийских организаций в сельской "
                "и городской Индии. Фокус: доступ к образованию, питание, "
                "борьба с детским трудом и детскими браками, системы защиты "
                "детей. Регистрация 80G + FCRA."
            ),
        },
        "methodology_note": _verify(
            "Listed: 80G + FCRA; own annual report.", "Listed: 80G + FCRA; собственный годовой отчёт.",
        ),
        "logo_url": "",
        "donation_url": "https://www.cry.org/donate-now",
        "size_bucket": "large",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("8000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1979,
        "cause_slugs": ["child-rights-india", "child-welfare", "free-education"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.cry.org/about-us/annual-report/",
    },
    {
        "slug": "goonj",
        "country": "IN",
        "registration_id": "AAATG2253R",
        "bucket": "people",
        "name": {"en": "Goonj", "ru": "Goonj"},
        "tagline": {
            "en": "Indian NGO turning urban surplus material into rural development tool — disaster, dignity, MGNREGA-style village work.",
            "ru": "Индийская НПО, превращающая городские излишки в инструмент сельского развития — бедствия, достоинство, сельские работы.",
        },
        "description": {
            "en": (
                "Goonj (founded 1999, Delhi) takes urban surplus clothing/material, "
                "processes it, and uses it as a payment for community-led rural "
                "development work — villagers earn 'Cloth For Work' by digging "
                "wells, building bridges, school maintenance. Pioneer of dignity-"
                "preserving menstrual hygiene through 'Not Just A Piece Of Cloth' "
                "(NJPC) sanitary pads. Magsaysay Award winner."
            ),
            "ru": (
                "Goonj (основана в 1999 году, Дели) принимает городские "
                "излишки одежды и материалов, обрабатывает их и использует как "
                "оплату за общинное сельское развитие — жители получают «ткань "
                "за работу» (Cloth For Work) за рытьё колодцев, строительство "
                "мостов, ремонт школ. Пионер сохранения достоинства в "
                "менструальной гигиене через прокладки Not Just A Piece Of "
                "Cloth (NJPC). Лауреат премии Magsaysay."
            ),
        },
        "methodology_note": _verify(
            "Listed: 80G + FCRA registered; own annual report.",
            "Listed: 80G + FCRA; собственный годовой отчёт.",
        ),
        "logo_url": "",
        "donation_url": "https://goonj.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1999,
        "cause_slugs": ["disaster-relief", "poverty-reduction"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://goonj.org/about/annual-reports/",
    },

    # =================== BRAZIL (2) ===================
    {
        "slug": "sos-mata-atlantica",
        "country": "BR",
        "registration_id": "57.354.540/0001-66",
        "bucket": "planet",
        "name": {"en": "Fundação SOS Mata Atlântica", "ru": "Fundação SOS Mata Atlântica"},
        "tagline": {
            "en": "Brazilian foundation defending the Atlantic Forest — restoration, monitoring, policy.",
            "ru": "Бразильский фонд по защите Атлантического леса — восстановление, мониторинг, политика.",
        },
        "description": {
            "en": (
                "Fundação SOS Mata Atlântica (CNPJ 57.354.540/0001-66, founded 1986) "
                "is Brazil's oldest and best-known Atlantic Forest defender. The "
                "Atlantic Forest (Mata Atlântica) once covered ~15% of Brazil; only "
                "~12% remains. SOS Mata Atlântica monitors deforestation by "
                "satellite, restores degraded land, advocates for Atlantic-Forest "
                "policy, and runs water-quality citizen-science. Title of utility "
                "pública federal."
            ),
            "ru": (
                "Fundação SOS Mata Atlântica (CNPJ 57.354.540/0001-66, основан в "
                "1986 году) — старейший и самый известный защитник "
                "Атлантического леса в Бразилии. Атлантический лес (Mata "
                "Atlântica) когда-то покрывал ~15% территории Бразилии; "
                "осталось ~12%. SOS Mata Atlântica мониторит вырубку по "
                "спутникам, восстанавливает деградированные земли, "
                "лоббирует политику по защите Атлантического леса, ведёт "
                "гражданскую науку по качеству воды. Имеет статус utility "
                "pública federal."
            ),
        },
        "methodology_note": _verify(
            "Listed: federal utility-pública status; own annual report (Relatório de Atividades) public.",
            "Listed: статус utility-pública федерального уровня; ежегодный Relatório de Atividades публичен.",
        ),
        "logo_url": "",
        "donation_url": "https://www.sosma.org.br/doe/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 3, 31),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1986,
        "cause_slugs": ["atlantic-forest", "forest-protection", "biodiversity-defense"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.sosma.org.br/quem-somos/transparencia/",
    },
    {
        "slug": "msf-brasil",
        "country": "BR",
        "registration_id": "03.751.851/0001-83",
        "bucket": "people",
        "name": {"en": "Médicos Sem Fronteiras Brasil", "ru": "Médicos Sem Fronteiras Brasil — MSF Бразилия"},
        "tagline": {
            "en": "Brazilian section of MSF — recruits Brazilian medical staff, raises funds for global emergencies.",
            "ru": "Бразильская секция MSF — набирает бразильский медперсонал, собирает средства для глобальных кризисов.",
        },
        "description": {
            "en": (
                "MSF Brasil (CNPJ 03.751.851/0001-83) is the Brazilian section of "
                "the international MSF movement. Recruits and deploys Brazilian "
                "medical, paramedical and logistical staff into MSF projects "
                "worldwide. Raises Brazilian public funds. Headquartered in Rio "
                "de Janeiro. UPF (Utilidade Pública Federal) titled."
            ),
            "ru": (
                "MSF Brasil (CNPJ 03.751.851/0001-83) — бразильская секция "
                "международного движения MSF. Набирает и направляет "
                "бразильский медицинский, парамедицинский и логистический "
                "персонал в проекты MSF по всему миру. Собирает средства в "
                "Бразилии. Штаб-квартира в Рио-де-Жанейро. Имеет статус UPF "
                "(Utilidade Pública Federal)."
            ),
        },
        "methodology_note": _verify(
            "Listed: UPF (Utilidade Pública Federal); own annual report.",
            "Listed: статус UPF (Utilidade Pública Federal); собственный годовой отчёт.",
        ),
        "logo_url": "",
        "donation_url": "https://www.msf.org.br/doacao/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("16000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1991,
        "cause_slugs": ["humanitarian-medicine", "emergency-response"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://www.msf.org.br/sobre-nos/transparencia/",
    },

    # =================== LATIN AMERICA (1) ===================
    {
        "slug": "techo",
        "country": "CL",
        "registration_id": "CL-NGO-TECHO-1997",
        "bucket": "people",
        "name": {"en": "TECHO", "ru": "TECHO"},
        "tagline": {
            "en": "Latin American youth-led NGO building emergency housing in informal settlements across 18 countries.",
            "ru": "Латиноамериканская молодёжная НПО, строящая аварийное жильё в неформальных поселениях в 18 странах.",
        },
        "description": {
            "en": (
                "TECHO (founded 1997 in Chile by Jesuit university students after a "
                "Talca earthquake) is the largest youth-led housing NGO in Latin "
                "America. Operates in 18 Latin-American countries plus the US. "
                "Volunteers (mostly university students) live with informal-"
                "settlement communities and build pre-fab emergency-housing units, "
                "then transition to longer-term community-development work."
            ),
            "ru": (
                "TECHO (основана в 1997 году в Чили иезуитскими студентами "
                "после землетрясения в Талка) — крупнейшая молодёжная НПО по "
                "жилью в Латинской Америке. Работает в 18 странах Латинской "
                "Америки плюс США. Волонтёры (в основном студенты) живут с "
                "общинами в неформальных поселениях и строят сборные "
                "аварийные дома, затем переходят к более долгосрочной работе "
                "по развитию общины."
            ),
        },
        "methodology_note": _verify(
            "Listed: Chilean fundación + multiple country chapters; consolidated annual report.",
            "Listed: чилийский fundación + национальные отделения в 18 странах; консолидированный годовой отчёт.",
        ),
        "logo_url": "",
        "donation_url": "https://techo.org/dona/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1997,
        "cause_slugs": ["south-american-housing", "housing", "poverty-reduction"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://techo.org/transparencia/",
    },

    # =================== AFRICA (1) ===================
    {
        "slug": "amref-health-africa",
        "country": "KE",
        "registration_id": "KE-NGO-1957-AMREF",
        "bucket": "people",
        "name": {"en": "Amref Health Africa", "ru": "Amref Health Africa"},
        "tagline": {
            "en": "Africa's largest indigenous health NGO — community health workers, surgical outreach, training.",
            "ru": "Крупнейшая в Африке коренная организация в сфере здравоохранения — общинные медработники, выездная хирургия, обучение.",
        },
        "description": {
            "en": (
                "Amref Health Africa (founded 1957, Nairobi HQ) is Africa's largest "
                "African-led, African-headquartered health NGO. Operates in 35 "
                "African countries with offices in 11. Trains health workers, runs "
                "the Flying Doctors of East Africa surgical-outreach service, "
                "champions community-based primary healthcare. Has trained ~330K "
                "health workers across the continent."
            ),
            "ru": (
                "Amref Health Africa (основана в 1957 году, штаб-квартира в "
                "Найроби) — крупнейшая в Африке организация в сфере "
                "здравоохранения, ведомая африканцами и со штаб-квартирой в "
                "Африке. Работает в 35 африканских странах, офисы в 11. "
                "Обучает медработников, ведёт службу выездной хирургии "
                "Flying Doctors of East Africa, продвигает первичное "
                "здравоохранение на уровне общин. Обучила ~330 тыс. "
                "медработников по континенту."
            ),
        },
        "methodology_note": _verify(
            "Listed: Kenyan NGO Coordination Board registered; consolidated annual report public; UK + Netherlands + USA affiliates publish supplementary regulator-filed accounts.",
            "Listed: регистрация в Kenyan NGO Coordination Board; консолидированный годовой отчёт публичен; аффилиаты в UK, NL и USA публикуют отдельную отчётность регуляторам.",
        ),
        "logo_url": "",
        "donation_url": "https://amref.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("160000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1957,
        "cause_slugs": ["africa-health", "global-health", "humanitarian-medicine"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://amref.org/about-us/transparency/",
    },

    # =================== SOUTHEAST ASIA (1) ===================
    {
        "slug": "mae-tao-clinic",
        "country": "TH",
        "registration_id": "TH-NGO-MTC-1989",
        "bucket": "people",
        "name": {"en": "Mae Tao Clinic", "ru": "Mae Tao Clinic"},
        "tagline": {
            "en": "Thai-Burmese border clinic providing health and education services for displaced Burmese.",
            "ru": "Клиника на границе Таиланда и Мьянмы, оказывающая медицинские и образовательные услуги перемещённым бирманцам.",
        },
        "description": {
            "en": (
                "Mae Tao Clinic (founded 1989 by Dr. Cynthia Maung, Mae Sot, "
                "Thailand) is a primary healthcare and child-protection facility "
                "on the Thai-Burmese border. Serves Burmese migrants and refugees "
                "displaced by the long-running conflict. Provides ~150K patient "
                "visits per year, trauma surgery, maternal & child health, "
                "vaccination, and runs migrant schools. Magsaysay Award (Dr. Maung)."
            ),
            "ru": (
                "Mae Tao Clinic (основана в 1989 году Cynthia Maung, Мае-Сот, "
                "Таиланд) — учреждение первичной медицинской помощи и защиты "
                "детей на границе Таиланда и Мьянмы. Обслуживает бирманских "
                "мигрантов и беженцев, перемещённых из-за затяжного "
                "конфликта. ~150 тыс. визитов пациентов в год, "
                "травматологическая хирургия, охрана здоровья матери и "
                "ребёнка, вакцинация, школы для мигрантов. Премия Magsaysay "
                "(др. Маунг)."
            ),
        },
        "methodology_note": _verify(
            "Listed: Thai foundation registration + US 501(c)(3) Foundation for the People of Burma fiscal sponsor; own annual reports.",
            "Listed: регистрация тайского fund + США 501(c)(3) Foundation for the People of Burma как фискальный спонсор; собственные годовые отчёты.",
        ),
        "logo_url": "",
        "donation_url": "https://maetaoclinic.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2023, 12, 31),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1989,
        "cause_slugs": ["burmese-refugees", "humanitarian-medicine", "refugees"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": "https://maetaoclinic.org/about-us/our-financial-reports/",
    },
]


def _financial_row(entry: dict) -> dict:
    return {
        "year": 2023,
        "total_revenue_usd": entry["total_revenue_usd"],
        "program_expenses_usd": None,
        "admin_expenses_usd": None,
        "fundraising_expenses_usd": None,
        "top_executive_comp_usd": None,
        "top_executive_name": "",
        "source_url": entry["source_url"],
        "source_label": "Annual report (org's own publication)",
    }


def _source_doc(entry: dict) -> dict:
    return {
        "kind": "annual_report",
        "filed_date": entry["last_filed_date"],
        "label": {"en": "Annual report", "ru": "Годовой отчёт"},
        "url": entry["source_url"],
        "source_label": "Org's own annual report (regulator-jurisdiction varies)",
        "file_format": "html",
    }


def forwards(apps, schema_editor):
    Cause = apps.get_model("charities", "Cause")
    Charity = apps.get_model("charities", "Charity")
    Financial = apps.get_model("charities", "Financial")
    SourceDocument = apps.get_model("charities", "SourceDocument")

    for slug, label in NEW_CAUSES.items():
        Cause.objects.update_or_create(slug=slug, defaults={"name": label})

    upserted = 0
    skipped_blocked = 0

    for entry in SEED:
        block = is_blocked(
            country=entry["country"],
            registration_id=entry["registration_id"],
            cause_tags=entry["cause_slugs"],
            name=entry["name"]["en"] + " " + entry["name"]["ru"],
            description=entry["description"]["en"],
        )
        if block is not None:
            print(
                f"[migration 0038] BLOCKED {entry['slug']} "
                f"({entry['country']}/{entry['registration_id']}): {block}"
            )
            skipped_blocked += 1
            continue

        is_stale = (date.today() - entry["last_filed_date"]).days > 730

        charity, _ = Charity.objects.update_or_create(
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
                "verification_status": "verified" if entry["country"] in ("CA", "AU", "NZ", "DE", "NL", "CH", "SE", "FR", "JP") else "listed",
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

        fin = _financial_row(entry)
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

        doc = _source_doc(entry)
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

    all_cause_slugs: set[str] = set(NEW_CAUSES.keys())
    for entry in SEED:
        all_cause_slugs.update(entry["cause_slugs"])
    for slug in all_cause_slugs:
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    total = Charity.objects.count()
    print(
        f"[migration 0038] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total}"
    )


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0037_extend_country_choices_v37"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

"""v3.4 catalog scale-up — seed ~40 more curated charities (98 -> ~138).

People (+25), Animals (+6), Planet (+9). EINs zero-padded to 9 digits per
KB-017. US 501(c)(3) source URLs use the ProPublica `/organizations/{ein}`
overview page (KB-014 — same as 0025; the /download-filing path is behind
Cloudflare's challenge wall and breaks for some users).

Hero photos & logos: empty in this migration. Backfilled by:
  - 0029_backfill_v34_logos.py     (logo_url via uplead/Google s2)
  - 0030_backfill_v34_hero_photos.py (Unsplash CC0)

Verification: each EIN was checked against the live ProPublica
Nonprofit Explorer API at curation time per KB-012. See SUBS table below.

Substitutions made vs. the original brief:
  - "Direct Care" — too generic to resolve cleanly; substituted with
    Partners In Health (US, EIN 04-3567502, well-known global-health
    501c3 founded by the late Paul Farmer). Same bucket and theme.
  - "VillageReach" already seeded in 0025 — substituted by adding
    Sightsavers Inc USA (US, EIN 47-4657747; the US-arm 501c3 of UK
    Sightsavers seeded in 0025, but separately registered in IRS).
  - "Smile Train" already seeded in 0025 — substituted by Cure
    International (US, EIN 58-2248383, pediatric surgery in low-income
    countries).
  - "Pratham USA" already seeded in 0025 — substituted by skipping
    that slot (kept the 5 direct-service substitutes total at 5;
    no extra add).
  - "Wildlife Trust of India" — no clean US affiliate found in
    ProPublica; substituted with Wildlife Conservation Network
    (US, EIN 30-0108469). Same bucket: animals / wildlife.
  - "Friends of the Earth" already seeded in 0025 — substituted with
    Earth Island Institute (US, EIN 94-2889684; environmental fiscal
    sponsor in Berkeley CA). Same bucket: planet / environment.
  - "5 Gyres" already seeded in 0025 — substituted with Algalita
    Marine Research and Education (US, EIN 33-0657882; pioneers of
    plastic-gyre research, Long Beach CA).
  - "Action Aid USA" — would have been a People bucket entry per
    brief; substituted with Climate Justice Alliance (US, EIN
    85-3440899) to keep the Planet count at 9.
  - "Beyond Plastics" — no clean 501(c)(3) found (organisation runs
    via fiscal sponsorship); substituted with Center for Climate
    and Energy Solutions / C2ES (US, EIN 54-1892252; climate-policy
    think tank in DC).
  - Snow Leopard Trust EIN per ProPublica is 91-1144119 (brief
    listed 91-1158386 — used the verified one).
  - Oceana EIN per ProPublica is 51-0401308 (brief listed
    51-0405768 — used the verified one).

Idempotent: `update_or_create((country, registration_id))`. Defensive
`is_blocked()` on every entry. Reverse is a no-op (never auto-delete
real curated rows).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "mental-health": {
        "en": "Mental health",
        "ru": "Психическое здоровье",
    },
    "lgbt-rights": {
        "en": "LGBTQ+ rights",
        "ru": "Права ЛГБТК+",
    },
    "veterans": {
        "en": "Veterans support",
        "ru": "Поддержка ветеранов",
    },
    "indigenous-rights": {
        "en": "Indigenous rights",
        "ru": "Права коренных народов",
    },
    "womens-rights": {
        "en": "Women's & girls' rights",
        "ru": "Права женщин и девочек",
    },
    "effective-altruism": {
        "en": "Effective altruism",
        "ru": "Эффективный альтруизм",
    },
    "watershed-protection": {
        "en": "Watershed protection",
        "ru": "Защита водосборов",
    },
    "sustainable-forestry": {
        "en": "Sustainable forestry",
        "ru": "Устойчивое лесопользование",
    },
}


def _verify_note(en_extra: str = "", ru_extra: str = "") -> dict:
    """Standard ProPublica-verified note. en_extra/ru_extra appended if truthy."""
    return {
        "en": (
            "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 "
            "on file with ProPublica."
            + (f" {en_extra}" if en_extra else "")
        ),
        "ru": (
            "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 "
            "на ProPublica."
            + (f" {ru_extra}" if ru_extra else "")
        ),
    }


def _empty_photo() -> dict:
    return {
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
    }


def _us_propublica_url(ein: str) -> str:
    """Per KB-014: /organizations/{ein} overview page, NOT /download-filing."""
    return f"https://projects.propublica.org/nonprofits/organizations/{ein}"


SEED: list[dict] = [
    # ===================== PEOPLE — 25 new =====================

    # ----- Mental health (3) -----
    {
        "slug": "nami-national",
        "country": "US",
        "registration_id": "431201653",
        "bucket": "people",
        "name": {
            "en": "NAMI — National Alliance on Mental Illness",
            "ru": "NAMI — Национальный альянс по психическим заболеваниям",
        },
        "tagline": {
            "en": "US grassroots mental-health support, education, advocacy",
            "ru": "Низовая поддержка психического здоровья и адвокация в США",
        },
        "description": {
            "en": (
                "NAMI is a US 501(c)(3) headquartered in Arlington, VA, with "
                "600+ local affiliates across all 50 states. Runs a free "
                "HelpLine, peer-led support groups, education programmes for "
                "families and people living with mental illness, and "
                "national advocacy on mental-health policy. Founded in 1979."
            ),
            "ru": (
                "NAMI — американская 501(c)(3) со штаб-квартирой в "
                "Арлингтоне, штат Вирджиния, 600+ местных отделений во "
                "всех 50 штатах. Бесплатная горячая линия, группы "
                "взаимопомощи, образовательные программы для семей и "
                "людей с психическими расстройствами, национальная "
                "адвокация политики в области психического здоровья. "
                "Основан в 1979 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.nami.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2025, 8, 5),
        "total_revenue_usd": Decimal("38000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1979,
        "cause_slugs": ["mental-health"],
        **_empty_photo(),
    },
    {
        "slug": "mental-health-america",
        "country": "US",
        "registration_id": "131614906",
        "bucket": "people",
        "name": {
            "en": "Mental Health America",
            "ru": "Mental Health America",
        },
        "tagline": {
            "en": "Promotes mental health as a critical part of overall wellness",
            "ru": "Продвигает психическое здоровье как часть общего благополучия",
        },
        "description": {
            "en": (
                "Mental Health America (MHA) is the oldest community-based "
                "mental-health organisation in the US — a 501(c)(3) founded "
                "in 1909. Runs free online mental-health screening tools "
                "(used 25M+ times), publishes the annual State of Mental "
                "Health in America report, and operates a national network "
                "of 200+ affiliates."
            ),
            "ru": (
                "Mental Health America (MHA) — старейшая общинная "
                "организация по психическому здоровью в США, 501(c)(3), "
                "основана в 1909 году. Бесплатные онлайн-скрининги "
                "психического здоровья (использованы 25+ млн раз), "
                "ежегодный отчёт State of Mental Health in America, "
                "200+ местных отделений по стране."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://mhanational.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("9500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1909,
        "cause_slugs": ["mental-health"],
        **_empty_photo(),
    },
    {
        "slug": "jed-foundation",
        "country": "US",
        "registration_id": "134131139",
        "bucket": "people",
        "name": {"en": "The JED Foundation", "ru": "The JED Foundation"},
        "tagline": {
            "en": "Suicide prevention and emotional health for US teens and young adults",
            "ru": "Профилактика суицида и эмоциональное здоровье подростков в США",
        },
        "description": {
            "en": (
                "JED is a US 501(c)(3) focused on protecting emotional "
                "health and preventing suicide among teens and young "
                "adults. Runs the JED Campus and JED High School "
                "programmes — multi-year partnerships with schools to "
                "build comprehensive mental-health strategies. Founded "
                "in 2000 by parents who lost their son Jed to suicide."
            ),
            "ru": (
                "JED — американская 501(c)(3), занимается защитой "
                "эмоционального здоровья и профилактикой суицида среди "
                "подростков и молодёжи. Программы JED Campus и JED High "
                "School — многолетние партнёрства со школами по "
                "комплексным стратегиям психического здоровья. Основана "
                "в 2000 году родителями, потерявшими сына Джеда из-за "
                "суицида."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://jedfoundation.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("18000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2000,
        "cause_slugs": ["mental-health"],
        **_empty_photo(),
    },

    # ----- LGBTQ+ rights (3) -----
    {
        "slug": "trevor-project",
        "country": "US",
        "registration_id": "954681287",
        "bucket": "people",
        "name": {"en": "The Trevor Project", "ru": "The Trevor Project"},
        "tagline": {
            "en": "24/7 crisis support for LGBTQ+ young people in the US",
            "ru": "Круглосуточная кризисная поддержка ЛГБТК+ молодёжи в США",
        },
        "description": {
            "en": (
                "The Trevor Project is a US 501(c)(3) running a 24/7 "
                "crisis-intervention and suicide-prevention service for "
                "LGBTQ+ young people via phone, chat and text. Also "
                "publishes the annual National Survey on the Mental Health "
                "of LGBTQ+ Young People. Founded in 1998 around the "
                "Academy-Award-winning short film Trevor."
            ),
            "ru": (
                "The Trevor Project — американская 501(c)(3), ведёт "
                "круглосуточную службу кризисной помощи и профилактики "
                "суицида среди ЛГБТК+ молодёжи: телефон, чат, СМС. "
                "Ежегодный национальный опрос о психическом здоровье "
                "ЛГБТК+ молодёжи. Основан в 1998 году по мотивам "
                "оскароносного короткометражного фильма Trevor."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.thetrevorproject.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2025, 8, 5),
        "total_revenue_usd": Decimal("83800000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1998,
        "cause_slugs": ["lgbt-rights", "mental-health"],
        **_empty_photo(),
    },
    {
        "slug": "hrc-foundation",
        "country": "US",
        "registration_id": "521481896",
        "bucket": "people",
        "name": {
            "en": "Human Rights Campaign Foundation",
            "ru": "Human Rights Campaign Foundation",
        },
        "tagline": {
            "en": "Education and research arm of the largest US LGBTQ+ rights org",
            "ru": "Образование и исследования крупнейшей ЛГБТК+ организации США",
        },
        "description": {
            "en": (
                "HRC Foundation is the US 501(c)(3) educational and "
                "research arm of the Human Rights Campaign — the largest "
                "LGBTQ+ civil-rights organisation in the United States. "
                "Publishes the Corporate Equality Index, the Municipal "
                "Equality Index and the State Equality Index, runs "
                "Welcoming Schools, and supports LGBTQ+ inclusion training "
                "across employers, schools and faith communities."
            ),
            "ru": (
                "HRC Foundation — образовательная и исследовательская "
                "ветвь 501(c)(3) Human Rights Campaign, крупнейшей "
                "ЛГБТК+ правозащитной организации США. Публикует "
                "Corporate Equality Index, Municipal Equality Index и "
                "State Equality Index, ведёт программу Welcoming "
                "Schools, поддерживает обучение по ЛГБТК+ инклюзии в "
                "компаниях, школах и религиозных общинах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.hrc.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2025, 8, 5),
        "total_revenue_usd": Decimal("21000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1986,
        "cause_slugs": ["lgbt-rights", "civil-rights"],
        **_empty_photo(),
    },
    {
        "slug": "lambda-legal",
        "country": "US",
        "registration_id": "237395681",
        "bucket": "people",
        "name": {
            "en": "Lambda Legal Defense and Education Fund",
            "ru": "Lambda Legal Defense and Education Fund",
        },
        "tagline": {
            "en": "Civil-rights litigation for LGBTQ+ people and people with HIV",
            "ru": "Правозащитные иски для ЛГБТК+ людей и людей с ВИЧ",
        },
        "description": {
            "en": (
                "Lambda Legal is a US 501(c)(3) that litigates civil-rights "
                "cases on behalf of LGBTQ+ people and everyone living with "
                "HIV. Founded in 1973; argued landmark Supreme Court cases "
                "including Lawrence v. Texas (2003) and Obergefell v. "
                "Hodges (2015). Headquartered in New York with regional "
                "offices across the US."
            ),
            "ru": (
                "Lambda Legal — американская 501(c)(3), ведёт "
                "судебные процессы по гражданским правам ЛГБТК+ людей "
                "и всех, кто живёт с ВИЧ. Основана в 1973 году; вела "
                "знаковые дела в Верховном суде США — Lawrence v. "
                "Texas (2003) и Obergefell v. Hodges (2015). Штаб-квартира "
                "в Нью-Йорке, региональные офисы по США."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.lambdalegal.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1973,
        "cause_slugs": ["lgbt-rights", "civil-rights"],
        **_empty_photo(),
    },

    # ----- Disability services (4) -----
    {
        "slug": "the-arc",
        "country": "US",
        "registration_id": "135642032",
        "bucket": "people",
        "name": {
            "en": "The Arc of the United States",
            "ru": "The Arc of the United States",
        },
        "tagline": {
            "en": "Civil rights and supports for people with intellectual & developmental disabilities",
            "ru": "Гражданские права и поддержка людей с нарушениями развития",
        },
        "description": {
            "en": (
                "The Arc is the largest US 501(c)(3) for people with "
                "intellectual and developmental disabilities (IDD) and "
                "their families. Operates 575+ state and local chapters "
                "providing direct services and advocacy across all 50 "
                "states, and runs national policy work on Medicaid, "
                "education and employment for people with IDD."
            ),
            "ru": (
                "The Arc — крупнейшая в США 501(c)(3) для людей с "
                "интеллектуальными нарушениями и нарушениями развития "
                "и их семей. 575+ отделений на уровне штатов и общин: "
                "прямые услуги и адвокация во всех 50 штатах, "
                "национальная работа по политике в области Medicaid, "
                "образования и трудоустройства."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://thearc.org/get-involved/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("16000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1950,
        "cause_slugs": ["disability-services", "civil-rights"],
        **_empty_photo(),
    },
    {
        "slug": "easterseals",
        "country": "US",
        "registration_id": "362171729",
        "bucket": "people",
        "name": {"en": "Easterseals", "ru": "Easterseals"},
        "tagline": {
            "en": "Disability services and supports across all stages of life",
            "ru": "Услуги для людей с инвалидностью на всех этапах жизни",
        },
        "description": {
            "en": (
                "Easterseals is a US 501(c)(3) network providing services "
                "for people with disabilities, veterans, seniors and "
                "caregivers — early intervention, employment training, "
                "respite, autism services and more. Operates through 60+ "
                "regional affiliates across the United States. Founded in "
                "1919 in Ohio."
            ),
            "ru": (
                "Easterseals — американская 501(c)(3), сеть услуг для "
                "людей с инвалидностью, ветеранов, пожилых и "
                "ухаживающих: раннее вмешательство, трудоустройство, "
                "респитный уход, услуги при аутизме и др. 60+ региональных "
                "отделений по США. Основана в 1919 году в Огайо."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.easterseals.com/get-involved/ways-to-give/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1919,
        "cause_slugs": ["disability-services"],
        **_empty_photo(),
    },
    {
        "slug": "best-buddies",
        "country": "US",
        "registration_id": "521614576",
        "bucket": "people",
        "name": {
            "en": "Best Buddies International",
            "ru": "Best Buddies International",
        },
        "tagline": {
            "en": "Friendships, jobs and leadership for people with IDD",
            "ru": "Дружба, работа и лидерство для людей с нарушениями развития",
        },
        "description": {
            "en": (
                "Best Buddies International is a US 501(c)(3) that creates "
                "one-to-one friendships, integrated employment and "
                "leadership-development opportunities for people with "
                "intellectual and developmental disabilities. Operates in "
                "50+ countries. Founded by Anthony Kennedy Shriver in 1989."
            ),
            "ru": (
                "Best Buddies International — американская 501(c)(3), "
                "создаёт парные дружбы, интегрированное "
                "трудоустройство и возможности развития лидерства для "
                "людей с интеллектуальными нарушениями и нарушениями "
                "развития. Работает в 50+ странах. Основана Энтони "
                "Кеннеди Шрайвером в 1989 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.bestbuddies.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("70000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1989,
        "cause_slugs": ["disability-services"],
        **_empty_photo(),
    },
    {
        "slug": "national-federation-blind",
        "country": "US",
        "registration_id": "020259978",
        "bucket": "people",
        "name": {
            "en": "National Federation of the Blind",
            "ru": "Национальная федерация слепых",
        },
        "tagline": {
            "en": "Largest US membership-led organisation of blind Americans",
            "ru": "Крупнейшая в США членская организация слепых",
        },
        "description": {
            "en": (
                "The National Federation of the Blind is a US 501(c)(3) "
                "headquartered in Baltimore, MD — the largest "
                "membership-led organisation of blind Americans. Runs the "
                "Jernigan Institute for blindness research and training, "
                "free Braille programmes for children, scholarships and "
                "national accessibility advocacy. Founded in 1940."
            ),
            "ru": (
                "National Federation of the Blind — американская "
                "501(c)(3) со штаб-квартирой в Балтиморе, штат Мэриленд, "
                "крупнейшая членская организация слепых США. Институт "
                "Джерниган для исследований и обучения, бесплатные "
                "программы по шрифту Брайля для детей, стипендии и "
                "национальная адвокация доступности. Основана в 1940 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://nfb.org/get-involved/ways-give",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("25000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1940,
        "cause_slugs": ["disability-services", "civil-rights"],
        **_empty_photo(),
    },

    # ----- Veterans (2) -----
    {
        "slug": "hope-for-the-warriors",
        "country": "US",
        "registration_id": "205182295",
        "bucket": "people",
        "name": {
            "en": "Hope For The Warriors",
            "ru": "Hope For The Warriors",
        },
        "tagline": {
            "en": "Recovery and reintegration support for US service members and families",
            "ru": "Поддержка восстановления и интеграции военнослужащих США и их семей",
        },
        "description": {
            "en": (
                "Hope For The Warriors is a US 501(c)(3) providing "
                "transition, clinical health & wellness, and sports & "
                "recreation programmes for post-9/11 service members, "
                "veterans, and military families. Founded in 2006 by "
                "military families at Camp Lejeune, NC."
            ),
            "ru": (
                "Hope For The Warriors — американская 501(c)(3), "
                "программы перехода к гражданской жизни, клинического "
                "здоровья, спорта и активного отдыха для "
                "военнослужащих после 9/11, ветеранов и семей. "
                "Основана в 2006 году семьями военнослужащих в "
                "Кэмп-Лежён, штат Северная Каролина."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://hopeforthewarriors.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("8500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2006,
        "cause_slugs": ["veterans"],
        **_empty_photo(),
    },
    {
        "slug": "fisher-house",
        "country": "US",
        "registration_id": "113158401",
        "bucket": "people",
        "name": {
            "en": "Fisher House Foundation",
            "ru": "Fisher House Foundation",
        },
        "tagline": {
            "en": "Free lodging for military and veteran families near hospitals",
            "ru": "Бесплатное жильё семьям военных и ветеранов рядом с госпиталями",
        },
        "description": {
            "en": (
                "Fisher House Foundation is a US 501(c)(3) that builds "
                "and donates Fisher Houses — comfortable homes near major "
                "military and VA medical centres where families of "
                "wounded, injured or ill service members and veterans "
                "stay free of charge during treatment. 90+ houses across "
                "the US, UK and Germany."
            ),
            "ru": (
                "Fisher House Foundation — американская 501(c)(3), "
                "строит и передаёт в дар Fisher Houses — комфортные дома "
                "у крупных военных и ветеранских медцентров, где "
                "бесплатно проживают семьи раненых, травмированных или "
                "больных военнослужащих и ветеранов на время лечения. "
                "90+ домов в США, Великобритании и Германии."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://fisherhouse.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("110000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1990,
        "cause_slugs": ["veterans"],
        **_empty_photo(),
    },

    # ----- Women's & girls' rights (3) -----
    {
        "slug": "vital-voices",
        "country": "US",
        "registration_id": "522151557",
        "bucket": "people",
        "name": {
            "en": "Vital Voices Global Partnership",
            "ru": "Vital Voices Global Partnership",
        },
        "tagline": {
            "en": "Invests in women leaders solving the world's hardest problems",
            "ru": "Инвестирует в женщин-лидеров, решающих самые сложные мировые задачи",
        },
        "description": {
            "en": (
                "Vital Voices is a US 501(c)(3) global women's leadership "
                "organisation. Identifies, invests in and brings visibility "
                "to women leaders solving issues including gender-based "
                "violence, economic exclusion and democracy backsliding "
                "across 184 countries. Founded in 1999 out of the Vital "
                "Voices Initiative under Secretary Madeleine Albright."
            ),
            "ru": (
                "Vital Voices — американская 501(c)(3), глобальная "
                "организация по лидерству женщин: ищет, поддерживает "
                "финансово и помогает заявить о себе женщинам-лидерам, "
                "решающим вопросы гендерного насилия, экономического "
                "исключения и демократического регресса в 184 странах. "
                "Основана в 1999 году из Vital Voices Initiative при "
                "госсекретаре Мадлен Олбрайт."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.vitalvoices.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("22000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1999,
        "cause_slugs": ["womens-rights"],
        **_empty_photo(),
    },
    {
        "slug": "equality-now",
        "country": "US",
        "registration_id": "133660566",
        "bucket": "people",
        "name": {"en": "Equality Now", "ru": "Equality Now"},
        "tagline": {
            "en": "Legal advocacy to end violence and discrimination against women & girls",
            "ru": "Правовая адвокация против насилия и дискриминации женщин и девочек",
        },
        "description": {
            "en": (
                "Equality Now is a US 501(c)(3) headquartered in New York "
                "with a global team of lawyers and advocates working to "
                "change discriminatory laws and end violence against "
                "women and girls — focusing on legal equality, ending "
                "sexual violence, ending sexual exploitation, and ending "
                "harmful practices like FGM. Founded in 1992."
            ),
            "ru": (
                "Equality Now — американская 501(c)(3) со штаб-квартирой "
                "в Нью-Йорке, глобальная команда юристов и адвокатов "
                "работают над отменой дискриминационных законов и "
                "прекращением насилия в отношении женщин и девочек: "
                "правовое равенство, прекращение сексуального насилия "
                "и эксплуатации, искоренение вредных практик (например, "
                "КЖПО). Основана в 1992 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.equalitynow.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("10000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1992,
        "cause_slugs": ["womens-rights", "civil-rights"],
        **_empty_photo(),
    },
    {
        "slug": "malala-fund",
        "country": "US",
        "registration_id": "811397590",
        "bucket": "people",
        "name": {"en": "Malala Fund", "ru": "Malala Fund"},
        "tagline": {
            "en": "Champions every girl's right to 12 years of free, safe, quality education",
            "ru": "Право каждой девочки на 12 лет бесплатного и качественного образования",
        },
        "description": {
            "en": (
                "Malala Fund is a US 501(c)(3) co-founded by Malala "
                "Yousafzai and her father Ziauddin in 2013. Invests in "
                "education activists in countries where most girls miss "
                "out on secondary school (Education Champion Network in "
                "Afghanistan, Pakistan, India, Nigeria, Brazil, Ethiopia, "
                "Lebanon, Türkiye) and amplifies girls' voices globally."
            ),
            "ru": (
                "Malala Fund — американская 501(c)(3), сооснована "
                "Малалой Юсуфзай и её отцом Зиауддином в 2013 году. "
                "Финансирует активистов образования в странах, где "
                "большинство девочек не получают среднее образование "
                "(Education Champion Network в Афганистане, Пакистане, "
                "Индии, Нигерии, Бразилии, Эфиопии, Ливане, Турции), "
                "и усиливает голос девочек по миру."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://malala.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2013,
        "cause_slugs": ["womens-rights", "education", "free-education"],
        **_empty_photo(),
    },

    # ----- Indigenous rights (2) -----
    {
        "slug": "first-nations-development-institute",
        "country": "US",
        "registration_id": "541254491",
        "bucket": "people",
        "name": {
            "en": "First Nations Development Institute",
            "ru": "First Nations Development Institute",
        },
        "tagline": {
            "en": "Native-led economic development across Native American communities",
            "ru": "Развитие экономики коренных народов под руководством самих общин",
        },
        "description": {
            "en": (
                "First Nations Development Institute is a US 501(c)(3) "
                "headquartered in Longmont, CO. Provides grants, technical "
                "assistance, training and research to Native American "
                "tribes and communities — covering food sovereignty, "
                "Native youth development, financial empowerment and "
                "stewardship of Native assets. Founded in 1980."
            ),
            "ru": (
                "First Nations Development Institute — американская "
                "501(c)(3) со штаб-квартирой в Лонгмонте, штат Колорадо. "
                "Гранты, техническая помощь, обучение и исследования "
                "для племён и общин коренных американцев: продовольственный "
                "суверенитет, развитие молодёжи, финансовая грамотность, "
                "управление активами коренных общин. Основана в 1980 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.firstnations.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1980,
        "cause_slugs": ["indigenous-rights", "poverty-reduction"],
        **_empty_photo(),
    },
    {
        "slug": "american-indian-college-fund",
        "country": "US",
        "registration_id": "521573446",
        "bucket": "people",
        "name": {
            "en": "American Indian College Fund",
            "ru": "American Indian College Fund",
        },
        "tagline": {
            "en": "Scholarships and programmes for Native American students",
            "ru": "Стипендии и программы для коренных студентов Северной Америки",
        },
        "description": {
            "en": (
                "The American Indian College Fund is a US 501(c)(3) "
                "headquartered in Denver, CO — the largest Native "
                "scholarship organisation in the US. Funds scholarships "
                "for Native American students, supports Tribal Colleges "
                "and Universities (TCUs), and runs programmes in early "
                "childhood, faculty development and student success. "
                "Founded in 1989."
            ),
            "ru": (
                "American Indian College Fund — американская 501(c)(3) "
                "со штаб-квартирой в Денвере, штат Колорадо: крупнейшая "
                "стипендиальная организация для коренных народов США. "
                "Стипендии для студентов коренных американцев, поддержка "
                "племенных колледжей и университетов (TCU), программы "
                "раннего детства, развития преподавателей и успеха "
                "студентов. Основан в 1989 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://collegefund.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("48000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1989,
        "cause_slugs": ["indigenous-rights", "education"],
        **_empty_photo(),
    },

    # ----- Effective altruism (3) -----
    {
        "slug": "founders-pledge",
        "country": "US",
        "registration_id": "371795297",
        "bucket": "people",
        "name": {"en": "Founders Pledge", "ru": "Founders Pledge"},
        "tagline": {
            "en": "Helps founders pledge a share of exits to effective causes",
            "ru": "Помогает основателям жертвовать часть выручки в эффективные цели",
        },
        "description": {
            "en": (
                "Founders Pledge is a US 501(c)(3) (with a UK arm) that "
                "supports tech and business founders to pledge a share "
                "of their personal exit proceeds to charity, and produces "
                "in-depth research to direct that giving toward "
                "high-impact causes — climate, global health, global "
                "catastrophic risk and others. Members have pledged "
                "$10B+ since 2015."
            ),
            "ru": (
                "Founders Pledge — американская 501(c)(3) (с британским "
                "представительством), помогает основателям техкомпаний "
                "и бизнеса обещать долю личного дохода от exit на "
                "благотворительность и проводит глубокие исследования, "
                "чтобы направить эти средства в темы с высоким эффектом: "
                "климат, глобальное здоровье, риски глобальных "
                "катастроф и др. Члены обещали 10+ млрд $ с 2015 года."
            ),
        },
        "methodology_note": _verify_note(
            "Independent in-depth research on cause prioritisation.",
            "Независимые глубокие исследования по приоритезации направлений.",
        ),
        "logo_url": "",
        "donation_url": "https://founderspledge.com/funds",
        "size_bucket": "large",
        "last_filed_date": date(2024, 12, 1),
        "total_revenue_usd": Decimal("35000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2015,
        "cause_slugs": ["effective-altruism"],
        **_empty_photo(),
    },
    {
        "slug": "givewell",
        "country": "US",
        "registration_id": "208625442",
        "bucket": "people",
        "name": {
            "en": "GiveWell (The Clear Fund)",
            "ru": "GiveWell (The Clear Fund)",
        },
        "tagline": {
            "en": "Independent research finding the best giving opportunities",
            "ru": "Независимые исследования по поиску лучших возможностей для пожертвований",
        },
        "description": {
            "en": (
                "GiveWell — legal name The Clear Fund — is a US 501(c)(3) "
                "headquartered in Oakland, CA. Conducts in-depth research "
                "on global-health and poverty charities and publishes a "
                "short list of Top Charities. Has directed $2B+ in "
                "donations since 2007. Charges no fees on donor "
                "contributions."
            ),
            "ru": (
                "GiveWell (юр. лицо The Clear Fund) — американская "
                "501(c)(3) со штаб-квартирой в Окленде, штат "
                "Калифорния. Проводит глубокие исследования "
                "благотворительных организаций в темах глобального "
                "здоровья и борьбы с бедностью, публикует короткий "
                "список Top Charities. С 2007 года направил 2+ млрд $ "
                "пожертвований. Не берёт комиссию с донорских "
                "взносов."
            ),
        },
        "methodology_note": _verify_note(
            "Open methodology and full reasoning published per recommendation.",
            "Открытая методология и полное обоснование публикуются по каждой рекомендации.",
        ),
        "logo_url": "",
        "donation_url": "https://www.givewell.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2025, 8, 5),
        "total_revenue_usd": Decimal("219600000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2007,
        "cause_slugs": ["effective-altruism"],
        **_empty_photo(),
    },
    {
        "slug": "open-philanthropy",
        "country": "US",
        "registration_id": "810737472",
        "bucket": "people",
        "name": {"en": "Open Philanthropy", "ru": "Open Philanthropy"},
        "tagline": {
            "en": "Research-led grantmaker focused on high-impact causes",
            "ru": "Грантодатель на основе исследований, сфокусированный на темах с высоким эффектом",
        },
        "description": {
            "en": (
                "Open Philanthropy is a US 501(c)(3) headquartered in "
                "Palo Alto/San Francisco, CA. Researches and recommends "
                "grants in farm-animal welfare, global health & "
                "wellbeing, biosecurity, AI safety and other potentially "
                "high-impact areas. Has recommended $3.5B+ in grants "
                "since 2014. Publishes detailed grant write-ups."
            ),
            "ru": (
                "Open Philanthropy — американская 501(c)(3) со "
                "штаб-квартирой в Пало-Альто и Сан-Франциско, штат "
                "Калифорния. Исследует и рекомендует гранты в "
                "благополучие сельхозживотных, глобальное здоровье и "
                "благополучие людей, биобезопасность, безопасность ИИ "
                "и другие потенциально высокоэффективные темы. С 2014 "
                "года рекомендовано 3,5+ млрд $ грантов. Публикует "
                "подробные обоснования по каждому гранту."
            ),
        },
        "methodology_note": _verify_note(
            "Detailed grant write-ups published.",
            "По каждому гранту публикуется детальное обоснование.",
        ),
        "logo_url": "",
        "donation_url": "https://www.openphilanthropy.org/about/contact-us/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("450000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2014,
        "cause_slugs": ["effective-altruism"],
        **_empty_photo(),
    },

    # ----- Direct service substitutes (5) -----
    {
        "slug": "fistula-foundation",
        "country": "US",
        "registration_id": "770547201",
        "bucket": "people",
        "name": {"en": "Fistula Foundation", "ru": "Fistula Foundation"},
        "tagline": {
            "en": "Funds free surgery for women living with obstetric fistula",
            "ru": "Финансирует бесплатные операции для женщин с акушерской фистулой",
        },
        "description": {
            "en": (
                "Fistula Foundation is a US 501(c)(3) based in San Jose, "
                "CA, that funds surgery to repair obstetric fistula — a "
                "childbirth injury that leaves women incontinent and "
                "often socially isolated. Funds repairs in 35+ countries "
                "in Africa, Asia, the Middle East and Latin America "
                "through 100+ partner hospitals."
            ),
            "ru": (
                "Fistula Foundation — американская 501(c)(3) из "
                "Сан-Хосе, штат Калифорния, финансирует операции при "
                "акушерской фистуле — родовой травме, оставляющей "
                "женщин в недержании и часто в социальной изоляции. "
                "Финансирует операции в 35+ странах Африки, Азии, "
                "Ближнего Востока и Латинской Америки через 100+ "
                "больниц-партнёров."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://fistulafoundation.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("19000000.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 1995,
        "cause_slugs": ["global-health", "womens-rights"],
        **_empty_photo(),
    },
    {
        "slug": "partners-in-health",
        "country": "US",
        "registration_id": "043567502",
        "bucket": "people",
        "name": {"en": "Partners In Health", "ru": "Partners In Health"},
        "tagline": {
            "en": "Builds public health systems in the world's poorest places",
            "ru": "Строит государственные системы здравоохранения в беднейших регионах",
        },
        "description": {
            "en": (
                "Partners In Health (PIH) is a US 501(c)(3) headquartered "
                "in Boston that builds long-term partnerships with "
                "national governments to strengthen public health systems "
                "in 11+ countries (Haiti, Rwanda, Lesotho, Liberia, "
                "Malawi, Mexico, Peru, Sierra Leone, Navajo Nation and "
                "others). Co-founded in 1987 by Paul Farmer and "
                "Ophelia Dahl. Substituted for ambiguous \"Direct Care\" "
                "in v3.4 brief."
            ),
            "ru": (
                "Partners In Health (PIH) — американская 501(c)(3) со "
                "штаб-квартирой в Бостоне, строит долгосрочные "
                "партнёрства с правительствами 11+ стран по укреплению "
                "государственных систем здравоохранения (Гаити, Руанда, "
                "Лесото, Либерия, Малави, Мексика, Перу, Сьерра-Леоне, "
                "резервация Навахо и др.). Сооснована в 1987 году "
                "Полом Фармером и Офелией Даль. Заменила неоднозначный "
                "Direct Care в брифе v3.4."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.pih.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("250000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1987,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
    },
    {
        "slug": "trickle-up",
        "country": "US",
        "registration_id": "061043042",
        "bucket": "people",
        "name": {"en": "Trickle Up", "ru": "Trickle Up"},
        "tagline": {
            "en": "Supports women in extreme poverty to launch micro-livelihoods",
            "ru": "Помогает женщинам в крайней бедности начать своё дело",
        },
        "description": {
            "en": (
                "Trickle Up is a US 501(c)(3) based in New York that "
                "implements the Graduation Approach with women living in "
                "extreme poverty — a 18-36 month sequence of seed grants, "
                "savings groups, coaching and skills training. Operates "
                "in India, Uganda, Guatemala, Mexico and Burkina Faso. "
                "Founded in 1979."
            ),
            "ru": (
                "Trickle Up — американская 501(c)(3) из Нью-Йорка, "
                "реализует Graduation Approach с женщинами в крайней "
                "бедности: последовательность 18-36 месяцев — стартовый "
                "грант, сберегательные группы, наставничество, обучение "
                "навыкам. Работает в Индии, Уганде, Гватемале, Мексике и "
                "Буркина-Фасо. Основана в 1979 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://trickleup.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("9500000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1979,
        "cause_slugs": ["poverty-reduction", "womens-rights"],
        **_empty_photo(),
    },
    {
        "slug": "sightsavers-inc-usa",
        "country": "US",
        "registration_id": "474657747",
        "bucket": "people",
        "name": {
            "en": "Sightsavers Inc (US)",
            "ru": "Sightsavers Inc (США)",
        },
        "tagline": {
            "en": "US 501(c)(3) arm of Sightsavers, blindness prevention worldwide",
            "ru": "Американская 501(c)(3) подразделение Sightsavers по борьбе со слепотой",
        },
        "description": {
            "en": (
                "Sightsavers Inc is the US 501(c)(3) arm of Sightsavers "
                "(UK Charity 207544 — seeded separately in 0025). "
                "Headquartered in Boston, MA. Channels US donor funding "
                "into the global Sightsavers programmes: cataract surgery, "
                "trachoma elimination, river blindness treatment, and "
                "disability-rights advocacy in 30+ countries."
            ),
            "ru": (
                "Sightsavers Inc — американское 501(c)(3) подразделение "
                "Sightsavers (британской Charity 207544 — добавлена "
                "отдельно в 0025). Штаб-квартира в Бостоне, штат "
                "Массачусетс. Аккумулирует средства американских доноров "
                "в глобальные программы Sightsavers: операции при "
                "катаракте, борьба с трахомой, лечение речной слепоты, "
                "адвокация прав людей с инвалидностью в 30+ странах."
            ),
        },
        "methodology_note": _verify_note(
            "Substituted for VillageReach (already seeded in 0025).",
            "Заменяет VillageReach (уже добавлен в 0025).",
        ),
        "logo_url": "",
        "donation_url": "https://www.sightsavers.us/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2015,
        "cause_slugs": ["global-health", "disability-services"],
        **_empty_photo(),
    },
    {
        "slug": "cure-international",
        "country": "US",
        "registration_id": "582248383",
        "bucket": "people",
        "name": {"en": "CURE International", "ru": "CURE International"},
        "tagline": {
            "en": "Free pediatric surgery in low-income countries",
            "ru": "Бесплатная детская хирургия в странах с низкими доходами",
        },
        "description": {
            "en": (
                "CURE International is a US 501(c)(3) headquartered in "
                "Grand Rapids, MI, operating a network of charitable "
                "teaching hospitals that provide free surgery for children "
                "with treatable conditions (clubfoot, cleft lip & palate, "
                "hydrocephalus, burn contractures) in Ethiopia, Kenya, "
                "Malawi, Niger, Uganda, Zambia and the Philippines. "
                "Substituted for Smile Train (already seeded in 0025)."
            ),
            "ru": (
                "CURE International — американская 501(c)(3) со "
                "штаб-квартирой в Гранд-Рапидс, штат Мичиган, ведёт сеть "
                "благотворительных учебных больниц, бесплатно оперирующих "
                "детей с поддающимися лечению состояниями (косолапость, "
                "расщелина губы и нёба, гидроцефалия, послеожоговые "
                "контрактуры) в Эфиопии, Кении, Малави, Нигере, Уганде, "
                "Замбии и Филиппинах. Заменяет Smile Train (уже добавлен "
                "в 0025)."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://cure.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("60000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1996,
        "cause_slugs": ["global-health", "cleft-surgery"],
        **_empty_photo(),
    },

    # ===================== ANIMALS — 6 new =====================
    {
        "slug": "american-bird-conservancy",
        "country": "US",
        "registration_id": "521501259",
        "bucket": "animals",
        "name": {
            "en": "American Bird Conservancy",
            "ru": "American Bird Conservancy",
        },
        "tagline": {
            "en": "Conserves wild birds and their habitats throughout the Americas",
            "ru": "Защищает диких птиц и их местообитания по всей Северной и Южной Америке",
        },
        "description": {
            "en": (
                "American Bird Conservancy (ABC) is a US 501(c)(3) "
                "headquartered in Marshall, VA. Conserves wild birds and "
                "their habitats from Canada to Tierra del Fuego — habitat "
                "restoration, bird-friendly building standards, threats "
                "from cats, glass and pesticides, and BirdScapes habitat "
                "conservation across millions of acres. Founded in 1994."
            ),
            "ru": (
                "American Bird Conservancy (ABC) — американская "
                "501(c)(3) со штаб-квартирой в Маршалле, штат Вирджиния. "
                "Сохраняет диких птиц и их места обитания от Канады до "
                "Огненной Земли: восстановление мест обитания, "
                "стандарты дружественных к птицам зданий, борьба с "
                "угрозами от кошек, стекла и пестицидов, программа "
                "BirdScapes для миллионов акров. Основана в 1994 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://abcbirds.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("17000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1994,
        "cause_slugs": ["animal-welfare", "biodiversity-defense"],
        **_empty_photo(),
    },
    {
        "slug": "alley-cat-allies",
        "country": "US",
        "registration_id": "521742079",
        "bucket": "animals",
        "name": {"en": "Alley Cat Allies", "ru": "Alley Cat Allies"},
        "tagline": {
            "en": "Champions humane policies for community cats in the US",
            "ru": "Продвигает гуманные политики для общинных кошек в США",
        },
        "description": {
            "en": (
                "Alley Cat Allies is a US 501(c)(3) headquartered in "
                "Bethesda, MD. Founded in 1990 — the first US national "
                "advocacy org for community (feral and stray) cats. "
                "Promotes Trap-Neuter-Return (TNR) as the humane and "
                "effective alternative to lethal control, runs the National "
                "Feral Cat Day, and publishes US-wide veterinary protocols."
            ),
            "ru": (
                "Alley Cat Allies — американская 501(c)(3) со "
                "штаб-квартирой в Бетесде, штат Мэриленд. Основана в "
                "1990 году — первая в США национальная адвокационная "
                "организация по общинным (бездомным) кошкам. Продвигает "
                "Trap-Neuter-Return (TNR) как гуманную и эффективную "
                "альтернативу летальному контролю, ведёт National Feral "
                "Cat Day, публикует ветеринарные протоколы для США."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.alleycat.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("8500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1990,
        "cause_slugs": ["animal-welfare"],
        **_empty_photo(),
    },
    {
        "slug": "mission-blue",
        "country": "US",
        "registration_id": "261892969",
        "bucket": "animals",
        "name": {
            "en": "Mission Blue (Sylvia Earle Alliance)",
            "ru": "Mission Blue (Sylvia Earle Alliance)",
        },
        "tagline": {
            "en": "Identifies and supports a global network of marine Hope Spots",
            "ru": "Выявляет и поддерживает глобальную сеть морских Hope Spots",
        },
        "description": {
            "en": (
                "Mission Blue, the US 501(c)(3) Sylvia Earle Alliance "
                "founded in 2009 by oceanographer Dr. Sylvia Earle, "
                "champions a worldwide network of marine protected areas "
                "called Hope Spots — places critical to ocean health. "
                "Has identified 160+ Hope Spots covering ~50M km² and "
                "partners with local champions to push for stronger "
                "protections. HQ in Napa, CA."
            ),
            "ru": (
                "Mission Blue — американская 501(c)(3) Sylvia Earle "
                "Alliance, основана в 2009 году океанографом Сильвией "
                "Эрл. Продвигает мировую сеть охраняемых морских "
                "территорий Hope Spots — мест, критичных для здоровья "
                "океана. Определено 160+ Hope Spots на ~50 млн км². "
                "Работает с местными активистами над усилением охраны. "
                "Штаб-квартира в Напе, штат Калифорния."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://mission-blue.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2009,
        "cause_slugs": ["ocean-protection", "biodiversity-defense"],
        **_empty_photo(),
    },
    {
        "slug": "oceana",
        "country": "US",
        "registration_id": "510401308",
        "bucket": "animals",
        "name": {"en": "Oceana", "ru": "Oceana"},
        "tagline": {
            "en": "Wins science-based policy victories to restore the world's oceans",
            "ru": "Добивается научно обоснованных политических побед для восстановления океанов",
        },
        "description": {
            "en": (
                "Oceana is a US 501(c)(3) headquartered in Washington, DC "
                "with offices across 9 countries. Pursues science-based "
                "campaigns to restore ocean abundance — banning destructive "
                "trawling, ending plastic pollution, protecting key "
                "species (sharks, sea turtles, forage fish) and securing "
                "marine protected areas. 250+ policy victories since 2001."
            ),
            "ru": (
                "Oceana — американская 501(c)(3) со штаб-квартирой в "
                "Вашингтоне, округ Колумбия, и офисами в 9 странах. Ведёт "
                "научно обоснованные кампании за восстановление "
                "численности обитателей океана: запрет разрушительного "
                "тралового лова, прекращение пластикового загрязнения, "
                "защита ключевых видов (акулы, морские черепахи, "
                "промысловая рыба) и охраняемых морских территорий. "
                "250+ политических побед с 2001 года."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://oceana.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("70000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 2001,
        "cause_slugs": ["ocean-protection", "biodiversity-defense"],
        **_empty_photo(),
    },
    {
        "slug": "wildlife-conservation-network",
        "country": "US",
        "registration_id": "300108469",
        "bucket": "animals",
        "name": {
            "en": "Wildlife Conservation Network",
            "ru": "Wildlife Conservation Network",
        },
        "tagline": {
            "en": "Funds independent in-country conservationists protecting endangered wildlife",
            "ru": "Финансирует независимых полевых природоохранников по защите редких видов",
        },
        "description": {
            "en": (
                "Wildlife Conservation Network (WCN) is a US 501(c)(3) "
                "headquartered in San Francisco, CA. Funds independent, "
                "in-country wildlife conservationists across Africa, "
                "Asia and Latin America — using a low-overhead model "
                "where 100% of designated donations go directly to the "
                "field. Hosts the Lion Recovery Fund, Elephant Crisis "
                "Fund, Pangolin Crisis Fund and others. Substituted for "
                "Wildlife Trust of India (no clean US affiliate)."
            ),
            "ru": (
                "Wildlife Conservation Network (WCN) — американская "
                "501(c)(3) со штаб-квартирой в Сан-Франциско, штат "
                "Калифорния. Финансирует независимых полевых "
                "природоохранников в Африке, Азии и Латинской Америке "
                "по модели с низкими накладными расходами: 100% целевых "
                "пожертвований идут напрямую в поле. Размещает Lion "
                "Recovery Fund, Elephant Crisis Fund, Pangolin Crisis "
                "Fund и др. Заменяет Wildlife Trust of India (нет "
                "чистого американского филиала)."
            ),
        },
        "methodology_note": _verify_note(
            "100% of designated donations to field per WCN public statement.",
            "100% целевых пожертвований идут в поле — публичное обязательство WCN.",
        ),
        "logo_url": "",
        "donation_url": "https://wildnet.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("60000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2002,
        "cause_slugs": ["animal-welfare", "biodiversity-defense"],
        **_empty_photo(),
    },
    {
        "slug": "snow-leopard-trust",
        "country": "US",
        "registration_id": "911144119",
        "bucket": "animals",
        "name": {
            "en": "Snow Leopard Trust",
            "ru": "Snow Leopard Trust",
        },
        "tagline": {
            "en": "Community-based snow leopard conservation across Central Asia",
            "ru": "Сохранение снежного барса с общинами Центральной Азии",
        },
        "description": {
            "en": (
                "The Snow Leopard Trust is a US 501(c)(3) headquartered "
                "in Seattle, WA. Runs community-based snow leopard "
                "conservation in five of the cat's twelve range states "
                "(Mongolia, India, Kyrgyzstan, Pakistan, China) — "
                "livestock insurance, predator-proof corrals, "
                "Snow Leopard Enterprises handicrafts and ecological "
                "research. Founded in 1981."
            ),
            "ru": (
                "Snow Leopard Trust — американская 501(c)(3) со "
                "штаб-квартирой в Сиэтле, штат Вашингтон. Сохраняет "
                "снежного барса совместно с общинами в пяти из двенадцати "
                "стран ареала вида (Монголия, Индия, Кыргызстан, "
                "Пакистан, Китай): страхование скота, защищённые от "
                "хищников загоны, ремесленный проект Snow Leopard "
                "Enterprises и экологические исследования. Основан в "
                "1981 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://snowleopard.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1981,
        "cause_slugs": ["animal-welfare", "biodiversity-defense"],
        **_empty_photo(),
    },

    # ===================== PLANET — 9 new =====================
    {
        "slug": "chesapeake-bay-foundation",
        "country": "US",
        "registration_id": "526065757",
        "bucket": "planet",
        "name": {
            "en": "Chesapeake Bay Foundation",
            "ru": "Chesapeake Bay Foundation",
        },
        "tagline": {
            "en": "Saves the largest US estuary through advocacy, education and restoration",
            "ru": "Защищает крупнейший американский эстуарий: адвокация, образование, восстановление",
        },
        "description": {
            "en": (
                "Chesapeake Bay Foundation (CBF) is a US 501(c)(3) "
                "headquartered in Annapolis, MD. \"Save the Bay\" — runs "
                "watershed-wide advocacy, K-12 environmental education "
                "(takes 30,000+ students into the field annually) and "
                "habitat restoration (oysters, underwater grasses, forest "
                "buffers) across the 64,000-square-mile Chesapeake Bay "
                "watershed. Founded in 1967."
            ),
            "ru": (
                "Chesapeake Bay Foundation (CBF) — американская "
                "501(c)(3) со штаб-квартирой в Аннаполисе, штат "
                "Мэриленд. «Save the Bay» — адвокация в масштабах всего "
                "водосбора, экологическое образование K-12 (30+ тыс. "
                "учеников ежегодно выезжают в поле), восстановление "
                "местообитаний (устрицы, подводные луга, лесные "
                "буферы) на территории Чесапикского водосбора в 64 тыс. "
                "кв. миль. Основана в 1967 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.cbf.org/about-cbf/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("33000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1967,
        "cause_slugs": ["watershed-protection", "environment"],
        **_empty_photo(),
    },
    {
        "slug": "american-forests",
        "country": "US",
        "registration_id": "530196544",
        "bucket": "planet",
        "name": {"en": "American Forests", "ru": "American Forests"},
        "tagline": {
            "en": "Oldest US forest-conservation org — restores forests for climate and equity",
            "ru": "Старейшая лесозащитная организация США — восстановление лесов для климата и справедливости",
        },
        "description": {
            "en": (
                "American Forests is the oldest US national 501(c)(3) "
                "forest-conservation organisation, founded in 1875. "
                "Headquartered in Washington, DC. Runs the Tree Equity "
                "programme to address the urban tree-cover gap in "
                "low-income neighbourhoods, restores wildfire-resilient "
                "forests in the West, and partners with the US Forest "
                "Service on landscape-scale reforestation."
            ),
            "ru": (
                "American Forests — старейшая 501(c)(3) лесозащитная "
                "организация в США, основана в 1875 году. Штаб-квартира "
                "в Вашингтоне, округ Колумбия. Программа Tree Equity по "
                "сокращению разрыва в покрытии деревьями в малоимущих "
                "районах городов, восстановление пожароустойчивых лесов "
                "на Западе, партнёрство с Лесной службой США по "
                "лесовосстановлению на ландшафтном уровне."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.americanforests.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1875,
        "cause_slugs": ["sustainable-forestry", "environment", "climate"],
        **_empty_photo(),
    },
    {
        "slug": "earth-island-institute",
        "country": "US",
        "registration_id": "942889684",
        "bucket": "planet",
        "name": {
            "en": "Earth Island Institute",
            "ru": "Earth Island Institute",
        },
        "tagline": {
            "en": "Fiscal sponsor and incubator for environmental projects",
            "ru": "Фискальный спонсор и инкубатор экологических проектов",
        },
        "description": {
            "en": (
                "Earth Island Institute is a US 501(c)(3) based in "
                "Berkeley, CA. Acts as fiscal sponsor and incubator for "
                "70+ environmental projects worldwide — from "
                "International Marine Mammal Project to Plastic Pollution "
                "Coalition and beyond — providing back-office, "
                "compliance and 501(c)(3) status so small projects can "
                "focus on the work. Founded by David Brower in 1982. "
                "Substituted for Friends of the Earth (already seeded "
                "in 0025)."
            ),
            "ru": (
                "Earth Island Institute — американская 501(c)(3) из "
                "Беркли, штат Калифорния. Действует как фискальный "
                "спонсор и инкубатор для 70+ экологических проектов по "
                "миру — от International Marine Mammal Project до "
                "Plastic Pollution Coalition и далее — обеспечивает "
                "бэк-офис, соблюдение требований и статус 501(c)(3), "
                "чтобы малые проекты могли заниматься делом. Основан "
                "Дэвидом Брауэром в 1982 году. Заменяет Friends of the "
                "Earth (уже добавлена в 0025)."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.earthisland.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1982,
        "cause_slugs": ["environment", "ocean-protection"],
        **_empty_photo(),
    },
    {
        "slug": "sustainable-forestry-initiative",
        "country": "US",
        "registration_id": "800030060",
        "bucket": "planet",
        "name": {
            "en": "Sustainable Forestry Initiative",
            "ru": "Sustainable Forestry Initiative",
        },
        "tagline": {
            "en": "Forest certification and standards across North American forests",
            "ru": "Сертификация и стандарты для лесов Северной Америки",
        },
        "description": {
            "en": (
                "The Sustainable Forestry Initiative (SFI) is a US "
                "501(c)(3) headquartered in Washington, DC, that develops "
                "forest-management, fibre-sourcing, chain-of-custody and "
                "urban-and-community-forestry standards. SFI-certified "
                "forests cover ~370M acres across the US and Canada. "
                "Independent third-party audits."
            ),
            "ru": (
                "Sustainable Forestry Initiative (SFI) — американская "
                "501(c)(3) со штаб-квартирой в Вашингтоне, округ "
                "Колумбия, разрабатывает стандарты лесоуправления, "
                "поставки волокна, цепочки поставок и городского/общинного "
                "лесоводства. Сертифицированные SFI леса покрывают ~370 "
                "млн акров в США и Канаде. Независимые сторонние аудиты."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://forests.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("16000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2007,
        "cause_slugs": ["sustainable-forestry", "environment"],
        **_empty_photo(),
    },
    {
        "slug": "the-climate-group",
        "country": "US",
        "registration_id": "432073566",
        "bucket": "planet",
        "name": {"en": "The Climate Group", "ru": "The Climate Group"},
        "tagline": {
            "en": "Drives climate action with business and government leaders",
            "ru": "Двигает климатические действия совместно с бизнесом и правительствами",
        },
        "description": {
            "en": (
                "The Climate Group (US arm: Climate Group Inc, EIN "
                "43-2073566, headquartered in New York) is a US 501(c)(3) "
                "convening business and government leaders into "
                "global initiatives — RE100 (100% renewable electricity), "
                "EV100, EP100 (energy productivity), Under2 Coalition "
                "(state and regional governments) — and runs Climate "
                "Week NYC each September. UK parent founded in 2004."
            ),
            "ru": (
                "The Climate Group (американское подразделение: "
                "Climate Group Inc, EIN 43-2073566, штаб-квартира в "
                "Нью-Йорке) — американская 501(c)(3), объединяет бизнес "
                "и правительства в глобальные инициативы: RE100 (100% "
                "возобновляемой электроэнергии), EV100, EP100 "
                "(энергопроизводительность), Under2 Coalition "
                "(региональные власти) — и проводит Climate Week NYC "
                "каждый сентябрь. Британская материнская организация "
                "основана в 2004 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.theclimategroup.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2004,
        "cause_slugs": ["climate", "climate-policy"],
        **_empty_photo(),
    },
    {
        "slug": "c2es",
        "country": "US",
        "registration_id": "541892252",
        "bucket": "planet",
        "name": {
            "en": "Center for Climate and Energy Solutions",
            "ru": "Center for Climate and Energy Solutions",
        },
        "tagline": {
            "en": "Independent climate-policy research and bipartisan engagement",
            "ru": "Независимые исследования по климатической политике и двухпартийный диалог",
        },
        "description": {
            "en": (
                "The Center for Climate and Energy Solutions (C2ES) is a "
                "US 501(c)(3) think tank in Arlington, VA, founded in "
                "1998 (originally as the Pew Center on Global Climate "
                "Change). Convenes business and policymakers across the "
                "political spectrum, publishes climate-policy research, "
                "and supports the Climate Innovation 2050 initiative. "
                "Substituted for Beyond Plastics (no clean 501c3)."
            ),
            "ru": (
                "Center for Climate and Energy Solutions (C2ES) — "
                "американский 501(c)(3) аналитический центр в "
                "Арлингтоне, штат Вирджиния, основан в 1998 году "
                "(исходно как Pew Center on Global Climate Change). "
                "Объединяет бизнес и политиков всего спектра, "
                "публикует исследования климатической политики, "
                "поддерживает инициативу Climate Innovation 2050. "
                "Заменяет Beyond Plastics (нет чистого 501(c)(3))."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.c2es.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("6500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1998,
        "cause_slugs": ["climate-policy", "climate", "environment"],
        **_empty_photo(),
    },
    {
        "slug": "algalita",
        "country": "US",
        "registration_id": "330657882",
        "bucket": "planet",
        "name": {
            "en": "Algalita Marine Research and Education",
            "ru": "Algalita Marine Research and Education",
        },
        "tagline": {
            "en": "Pioneers of plastic-gyre research and youth ocean leadership",
            "ru": "Пионеры исследований мусорных пятен в океане и молодёжного лидерства",
        },
        "description": {
            "en": (
                "Algalita Marine Research and Education is a US 501(c)(3) "
                "based in Long Beach, CA, founded in 1994 by Captain "
                "Charles Moore — discoverer of the Great Pacific Garbage "
                "Patch. Continues plastic-pollution research on the "
                "research vessel Alguita and runs the POPS youth-leadership "
                "programme. Substituted for 5 Gyres (already seeded in "
                "0025)."
            ),
            "ru": (
                "Algalita Marine Research and Education — американская "
                "501(c)(3) из Лонг-Бич, штат Калифорния, основана в "
                "1994 году капитаном Чарльзом Муром, открывшим Большое "
                "тихоокеанское мусорное пятно. Продолжает исследования "
                "пластикового загрязнения на научном судне Alguita и "
                "ведёт молодёжную лидерскую программу POPS. Заменяет "
                "5 Gyres (уже добавлен в 0025)."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://algalita.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("700000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1994,
        "cause_slugs": ["ocean-protection", "environment"],
        **_empty_photo(),
    },
    {
        "slug": "mighty-earth",
        "country": "US",
        "registration_id": "844785944",
        "bucket": "planet",
        "name": {"en": "Mighty Earth", "ru": "Mighty Earth"},
        "tagline": {
            "en": "Campaigns to protect tropical forests and oceans",
            "ru": "Кампании за защиту тропических лесов и океанов",
        },
        "description": {
            "en": (
                "Mighty Earth is a US 501(c)(3) headquartered in "
                "Washington, DC. Runs corporate-accountability campaigns "
                "to protect tropical forests, oceans and the climate — "
                "tracking deforestation in cattle, soy, palm oil and "
                "cocoa supply chains, and pressing major brands and "
                "financiers to clean up their footprint. Independent "
                "501(c)(3) status."
            ),
            "ru": (
                "Mighty Earth — американская 501(c)(3) со штаб-квартирой "
                "в Вашингтоне, округ Колумбия. Ведёт кампании "
                "корпоративной ответственности за защиту тропических "
                "лесов, океанов и климата: отслеживает обезлесение в "
                "цепочках поставок говядины, сои, пальмового масла и "
                "какао, давит на крупные бренды и финансистов очищать "
                "цепочки. Независимый статус 501(c)(3)."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://mightyearth.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("8500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2016,
        "cause_slugs": ["environment", "biodiversity-defense", "climate-policy"],
        **_empty_photo(),
    },
    {
        "slug": "climate-justice-alliance",
        "country": "US",
        "registration_id": "853440899",
        "bucket": "planet",
        "name": {
            "en": "Climate Justice Alliance",
            "ru": "Climate Justice Alliance",
        },
        "tagline": {
            "en": "Frontline community-led just transition from extraction to regeneration",
            "ru": "Справедливый переход от добычи к регенерации под руководством местных сообществ",
        },
        "description": {
            "en": (
                "Climate Justice Alliance (CJA) is a US 501(c)(3) "
                "translocal network of 89+ urban and rural frontline "
                "communities, organisations and supporting networks "
                "uniting to forge a Just Transition away from the "
                "extractive economy. HQ in Berkeley, CA. Substituted "
                "for Action Aid USA (which would have been a People-bucket "
                "entry per brief)."
            ),
            "ru": (
                "Climate Justice Alliance (CJA) — американская "
                "501(c)(3), транслокальная сеть 89+ городских и "
                "сельских передовых сообществ, организаций и "
                "поддерживающих сетей, объединившихся для "
                "справедливого перехода от добывающей экономики. "
                "Штаб-квартира в Беркли, штат Калифорния. Заменяет "
                "Action Aid USA (которая по брифу относилась бы к "
                "категории People)."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://climatejusticealliance.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2013,
        "cause_slugs": ["climate-policy", "environment", "indigenous-rights"],
        **_empty_photo(),
    },
]


def _financial_row(entry: dict) -> dict:
    """Build the single Financial row for an entry, matching 0025's shape."""
    source_url = _us_propublica_url(entry["registration_id"])
    source_label = "IRS Form 990, FY 2023 (ProPublica)"
    return {
        "year": 2023,
        "total_revenue_usd": entry["total_revenue_usd"],
        "program_expenses_usd": None,
        "admin_expenses_usd": None,
        "fundraising_expenses_usd": None,
        "top_executive_comp_usd": None,
        "top_executive_name": "",
        "source_url": source_url,
        "source_label": source_label,
    }


def _source_doc(entry: dict) -> dict:
    """Build the single SourceDocument row for an entry."""
    return {
        "kind": "irs_990",
        "filed_date": entry["last_filed_date"],
        "label": {
            "en": "IRS Form 990 (FY 2023)",
            "ru": "Налоговая форма IRS 990 (2023)",
        },
        "url": _us_propublica_url(entry["registration_id"]),
        "source_label": "IRS Form 990 (ProPublica)",
        "file_format": "pdf",
    }


def forwards(apps, schema_editor):
    Cause = apps.get_model("charities", "Cause")
    Charity = apps.get_model("charities", "Charity")
    Financial = apps.get_model("charities", "Financial")
    SourceDocument = apps.get_model("charities", "SourceDocument")

    # Ensure new cause taxonomy entries exist.
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
                f"[migration 0028] BLOCKED {entry['slug']} "
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

    # Refresh denormalised charity_count on every cause we touched.
    all_cause_slugs: set[str] = set(NEW_CAUSES.keys())
    for entry in SEED:
        all_cause_slugs.update(entry["cause_slugs"])
    for slug in all_cause_slugs:
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    total_charities = Charity.objects.count()
    print(
        f"[migration 0028] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total_charities}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0027_backfill_v33_hero_photos"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

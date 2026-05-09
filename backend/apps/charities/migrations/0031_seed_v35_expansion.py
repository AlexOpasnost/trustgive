"""v3.5 catalog scale-up — seed 60 more curated charities (138 -> ~198).

People (+35), Animals (+10), Planet (+15). EINs verified against ProPublica
Nonprofit Explorer at curation time per KB-012; substitutions noted below
when the original brief org didn't ProPublica-verify cleanly. EINs are
zero-padded to 9 digits per KB-017. US source URL is the ProPublica
`/organizations/{ein}` overview page (KB-014).

Hero photos & logos: empty here. Filled by:
  - 0032_backfill_v35_logos.py            (logo_url via uplead/Google s2)
  - 0033_backfill_site_og_images.py       (REAL site OG images via scrape;
                                           covers 0031 NEW + earlier batches'
                                           Unsplash placeholders)

Substitutions (kept count per bucket):
  - "988 Suicide Prevention Lifeline" -> Vibrant Emotional Health
    (US, EIN 13-2992133), the parent 501(c)(3) that operates 988.
  - "Salvation Army (US)" -> The Salvation Army National Corporation
    (EIN 22-2406433); regional Salvation Army corps file separately.
  - "Carbon Lighthouse Foundation" -> not a clean US 501(c)(3); used
    Carbon180 (US, EIN 47-3221717) — carbon-removal policy & R&D.
  - "Solar Foundation" merged into IREC in 2021 — substituted with
    Bonneville Environmental Foundation (US, EIN 93-1217139).
  - "Yale School of the Environment Foundation" — not its own 501c3 —
    substituted by adding American Rivers (US, EIN 23-7305963).
  - "GAVI Alliance USA" — no clean US 501(c)(3) under that exact name
    (GAVI is a Swiss foundation); substituted with Save the Elephants
    USA (US, EIN 26-2603478) to keep the People bucket count.
    -> ACTUALLY moved to Animals; replaced with Crisis Text Line
    (US, EIN 32-0395877) so People stays at 35.
  - "Whale Sanctuary Project" — used (US, EIN 81-1454193) for Animals.

Idempotent: `update_or_create((country, registration_id))`. Defensive
`is_blocked()` per entry. Reverse no-op (never auto-delete curated rows).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "heart-disease": {"en": "Heart disease", "ru": "Сердечно-сосудистые заболевания"},
    "diabetes": {"en": "Diabetes", "ru": "Диабет"},
    "cancer-research": {"en": "Cancer research", "ru": "Исследования рака"},
    "hiv-aids": {"en": "HIV/AIDS", "ru": "ВИЧ/СПИД"},
    "hunger": {"en": "Hunger relief", "ru": "Борьба с голодом"},
    "housing": {"en": "Housing & homelessness", "ru": "Жильё и бездомность"},
    "senior-care": {"en": "Senior care", "ru": "Помощь пожилым"},
    "microfinance": {"en": "Microfinance", "ru": "Микрофинансирование"},
    "suicide-prevention": {"en": "Suicide prevention", "ru": "Профилактика суицида"},
    "faith-based": {"en": "Faith-based service", "ru": "Религиозная благотворительность"},
    "refugees": {"en": "Refugee support", "ru": "Помощь беженцам"},
    "neurology": {"en": "Neurological disease", "ru": "Неврологические заболевания"},
    "marine-mammals": {"en": "Marine mammal protection", "ru": "Защита морских млекопитающих"},
    "polar-wildlife": {"en": "Polar wildlife", "ru": "Полярная фауна"},
    "rivers": {"en": "Rivers & freshwater", "ru": "Реки и пресная вода"},
    "carbon-removal": {"en": "Carbon removal", "ru": "Удаление углерода"},
    "coral-reefs": {"en": "Coral reefs", "ru": "Коралловые рифы"},
}


def _verify_note(en_extra: str = "", ru_extra: str = "") -> dict:
    return {
        "en": (
            "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 on file."
            + (f" {en_extra}" if en_extra else "")
        ),
        "ru": (
            "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 на ProPublica."
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


def _us_pp(ein: str) -> str:
    return f"https://projects.propublica.org/nonprofits/organizations/{ein}"


def _people(slug, ein, name_en, tagline_en, tagline_ru, desc_en, desc_ru,
            donation, size, filed, rev, prog, founded, causes, name_ru=None):
    return {
        "slug": slug, "country": "US", "registration_id": ein, "bucket": "people",
        "name": {"en": name_en, "ru": name_ru or name_en},
        "tagline": {"en": tagline_en, "ru": tagline_ru},
        "description": {"en": desc_en, "ru": desc_ru},
        "methodology_note": _verify_note(),
        "logo_url": "", "donation_url": donation,
        "size_bucket": size, "last_filed_date": filed,
        "total_revenue_usd": Decimal(rev), "program_expense_pct": Decimal(prog),
        "founded_year": founded, "cause_slugs": causes,
        **_empty_photo(),
    }


def _animals(slug, ein, name_en, tagline_en, tagline_ru, desc_en, desc_ru,
             donation, size, filed, rev, prog, founded, causes, name_ru=None):
    d = _people(slug, ein, name_en, tagline_en, tagline_ru, desc_en, desc_ru,
                donation, size, filed, rev, prog, founded, causes, name_ru)
    d["bucket"] = "animals"
    return d


def _planet(slug, ein, name_en, tagline_en, tagline_ru, desc_en, desc_ru,
            donation, size, filed, rev, prog, founded, causes, name_ru=None):
    d = _people(slug, ein, name_en, tagline_en, tagline_ru, desc_en, desc_ru,
                donation, size, filed, rev, prog, founded, causes, name_ru)
    d["bucket"] = "planet"
    return d


SEED: list[dict] = [
    # ============== PEOPLE — 35 ==============

    # ----- Heart / diabetes / chronic -----
    _people("american-heart-association", "135613797",
            "American Heart Association",
            "Fights heart disease and stroke through research and prevention",
            "Борется с сердечно-сосудистыми заболеваниями через исследования и профилактику",
            "American Heart Association is a US 501(c)(3) headquartered in Dallas, TX, "
            "founded in 1924. Funds cardiovascular and stroke research (#2 funder after NIH), "
            "publishes evidence-based guidelines that shape ACLS/BLS protocols, and runs "
            "national prevention programmes including Go Red For Women.",
            "American Heart Association — американская 501(c)(3) со штаб-квартирой в "
            "Далласе, Техас, основана в 1924 году. Финансирует исследования сердечно-"
            "сосудистых заболеваний и инсульта (№2 после NIH), публикует доказательные "
            "клинические рекомендации (ACLS/BLS), ведёт национальные программы "
            "профилактики, включая Go Red For Women.",
            "https://www.heart.org/en/get-involved/ways-to-give",
            "huge", date(2024, 11, 14), "950000000.00", "78.00", 1924,
            ["heart-disease"]),
    _people("american-diabetes-association", "131623888",
            "American Diabetes Association",
            "Research, advocacy and care for the 38M+ Americans living with diabetes",
            "Исследования, адвокация и помощь 38+ млн американцев, живущих с диабетом",
            "ADA is a US 501(c)(3) headquartered in Arlington, VA, founded in 1940. "
            "Publishes the Standards of Medical Care in Diabetes guidelines, funds "
            "diabetes research, and runs Camp programmes for children with type 1 "
            "diabetes nationwide.",
            "ADA — американская 501(c)(3), штаб-квартира в Арлингтоне, Вирджиния, "
            "основана в 1940 году. Издаёт ежегодные клинические рекомендации Standards "
            "of Medical Care in Diabetes, финансирует исследования диабета и ведёт "
            "детские лагеря Camp для детей с СД 1 типа по всей стране.",
            "https://diabetes.org/donate",
            "large", date(2024, 11, 14), "150000000.00", "76.00", 1940,
            ["diabetes"]),
    _people("jdrf", "231907729",
            "JDRF (Breakthrough T1D)",
            "World's largest funder of type 1 diabetes research",
            "Крупнейший в мире финансист исследований СД 1 типа",
            "JDRF (rebranded Breakthrough T1D in 2024) is a US 501(c)(3) founded in "
            "1970 by parents of children with type 1 diabetes. Headquartered in New "
            "York; has funded $2.5B+ in research toward type 1 diabetes cures, "
            "prevention and treatments.",
            "JDRF (с 2024 — Breakthrough T1D) — американская 501(c)(3), основана в "
            "1970 году родителями детей с СД 1 типа. Штаб-квартира в Нью-Йорке; "
            "профинансировала исследования СД 1 типа на $2,5+ млрд (лечение, "
            "профилактика, излечение).",
            "https://www.breakthrought1d.org/donate/",
            "large", date(2024, 11, 14), "210000000.00", "75.00", 1970,
            ["diabetes"]),
    _people("als-association", "133271855",
            "The ALS Association",
            "Care services and research toward a cure for ALS",
            "Помощь и исследования в поисках лечения БАС",
            "The ALS Association is a US 501(c)(3) headquartered in Arlington, VA, "
            "founded in 1985. Funds research on amyotrophic lateral sclerosis (ALS / "
            "Lou Gehrig's disease) and runs Certified Treatment Centers of Excellence "
            "across the US for people living with ALS and their families.",
            "ALS Association — американская 501(c)(3), штаб-квартира в Арлингтоне, "
            "Вирджиния, основана в 1985 году. Финансирует исследования БАС (бокового "
            "амиотрофического склероза, болезни Лу Герига), сертифицирует "
            "специализированные клиники Certified Treatment Centers по США для "
            "пациентов с БАС и их семей.",
            "https://www.als.org/donate",
            "large", date(2024, 11, 14), "33000000.00", "72.00", 1985,
            ["neurology"]),
    _people("alzheimers-association", "133039601",
            "Alzheimer's Association",
            "Leading US voluntary health organisation in Alzheimer's care and research",
            "Ведущая добровольная организация США по болезни Альцгеймера",
            "The Alzheimer's Association is a US 501(c)(3) headquartered in Chicago, "
            "IL, founded in 1980. Operates a 24/7 free Helpline, funds Alzheimer's "
            "and dementia research worldwide, and advocates for federal research "
            "funding and care policy.",
            "Alzheimer's Association — американская 501(c)(3), штаб-квартира в "
            "Чикаго, основана в 1980 году. Бесплатная круглосуточная линия помощи, "
            "финансирование исследований болезни Альцгеймера и других деменций по "
            "миру, адвокация федерального финансирования исследований.",
            "https://www.alz.org/get_involved/donate",
            "huge", date(2024, 11, 14), "440000000.00", "76.00", 1980,
            ["neurology", "senior-care"]),

    # ----- Cancer -----
    _people("american-cancer-society", "131788491",
            "American Cancer Society",
            "Largest non-government cancer-research funder in the US",
            "Крупнейший негосударственный финансист онкологических исследований в США",
            "American Cancer Society is a US 501(c)(3) headquartered in Atlanta, GA, "
            "founded in 1913. Funds cancer research (49 Nobel laureates among grantees), "
            "operates Hope Lodges (free lodging for patients and caregivers near "
            "treatment centres), and runs the 24/7 cancer information helpline.",
            "American Cancer Society — американская 501(c)(3), штаб-квартира в "
            "Атланте, Джорджия, основана в 1913 году. Финансирует онкологические "
            "исследования (49 нобелевских лауреатов среди грантополучателей), Hope "
            "Lodges — бесплатное жильё для пациентов и сопровождающих рядом с "
            "клиниками, круглосуточная линия информации о раке.",
            "https://www.cancer.org/donate.html",
            "huge", date(2024, 11, 14), "830000000.00", "73.00", 1913,
            ["cancer-research"]),
    _people("susan-g-komen", "751835298",
            "Susan G. Komen",
            "Funds breast-cancer research, screening and patient navigation",
            "Финансирует исследования рака груди, скрининг и сопровождение пациентов",
            "Susan G. Komen is a US 501(c)(3) headquartered in Dallas, TX, founded "
            "in 1982 by Nancy Brinker after her sister's death from breast cancer. "
            "Has invested $4.5B+ in breast-cancer research, community programmes and "
            "free patient-navigation services nationwide.",
            "Susan G. Komen — американская 501(c)(3), штаб-квартира в Далласе, "
            "Техас, основана в 1982 году Нэнси Бринкер после смерти сестры от рака "
            "груди. Инвестировано $4,5+ млрд в исследования рака груди, общинные "
            "программы и бесплатное сопровождение пациентов по стране.",
            "https://www.komen.org/donate/",
            "large", date(2024, 11, 14), "120000000.00", "76.00", 1982,
            ["cancer-research"]),
    _people("cancer-research-institute", "131837442",
            "Cancer Research Institute",
            "Pioneers immunotherapy research for cancer",
            "Пионеры исследований иммунотерапии рака",
            "Cancer Research Institute is a US 501(c)(3) headquartered in New York, "
            "founded in 1953. The first non-profit dedicated solely to cancer "
            "immunotherapy — has funded fundamental research that led to checkpoint "
            "inhibitors and CAR-T cell therapy.",
            "Cancer Research Institute — американская 501(c)(3), штаб-квартира в "
            "Нью-Йорке, основана в 1953 году. Первая некоммерческая организация, "
            "посвящённая исключительно иммунотерапии рака; финансировала "
            "фундаментальные исследования, приведшие к ингибиторам контрольных "
            "точек и CAR-T клеточной терапии.",
            "https://www.cancerresearch.org/donate",
            "medium", date(2024, 5, 14), "55000000.00", "82.00", 1953,
            ["cancer-research"]),

    # ----- HIV/AIDS -----
    _people("amfar", "133163817",
            "amfAR — Foundation for AIDS Research",
            "Funds research toward a cure for HIV/AIDS",
            "Финансирует исследования по излечению ВИЧ/СПИД",
            "amfAR is a US 501(c)(3) headquartered in New York, founded in 1985 by "
            "Mathilde Krim, MD, with founding chair Elizabeth Taylor. Has invested "
            "$650M+ in HIV/AIDS research, with focused programmes on cure research "
            "and ending the epidemic among key populations.",
            "amfAR — американская 501(c)(3), штаб-квартира в Нью-Йорке, основана в "
            "1985 году Матильдой Крим (MD) с Элизабет Тейлор как сопредседателем. "
            "Инвестировано $650+ млн в исследования ВИЧ/СПИД, отдельные программы "
            "по излечению и по работе с ключевыми группами риска.",
            "https://www.amfar.org/donate/",
            "medium", date(2024, 5, 14), "30000000.00", "76.00", 1985,
            ["hiv-aids"]),
    _people("glaad", "133384027",
            "GLAAD",
            "LGBTQ media advocacy organisation in the US",
            "Американская правозащитная медиа-организация ЛГБТК+",
            "GLAAD is a US 501(c)(3) headquartered in New York, founded in 1985 in "
            "response to defamatory AIDS coverage. Monitors and advocates for "
            "accurate LGBTQ representation in news, entertainment and online media; "
            "publishes the annual Where We Are on TV report and Accelerating "
            "Acceptance survey.",
            "GLAAD — американская 501(c)(3), штаб-квартира в Нью-Йорке, основана в "
            "1985 году в ответ на клеветнические публикации о СПИДе. Мониторит и "
            "продвигает корректное освещение ЛГБТК+ в новостях, развлечениях и "
            "онлайн-СМИ; издаёт ежегодные отчёты Where We Are on TV и Accelerating "
            "Acceptance.",
            "https://www.glaad.org/donate",
            "medium", date(2024, 5, 14), "26000000.00", "75.00", 1985,
            ["hiv-aids", "lgbt-rights"]),

    # ----- Education -----
    _people("reading-partners", "770568469",
            "Reading Partners",
            "One-on-one tutoring to help K–4 students read at grade level",
            "Индивидуальное наставничество, чтобы школьники K–4 читали по программе",
            "Reading Partners is a US 501(c)(3) founded in 1999, operating in 14 "
            "regions across the US. Pairs trained community volunteers with K–4 "
            "students reading below grade level for twice-weekly 45-minute "
            "sessions; uses a structured, evidence-based curriculum.",
            "Reading Partners — американская 501(c)(3), основана в 1999 году, "
            "работает в 14 регионах США. Подбирает обученных волонтёров для "
            "учеников K–4, читающих ниже уровня класса: занятия дважды в неделю по "
            "45 минут по структурированной доказательной программе.",
            "https://readingpartners.org/donate/",
            "large", date(2024, 11, 14), "32000000.00", "78.00", 1999,
            ["education"]),
    _people("city-year", "222882549",
            "City Year",
            "AmeriCorps tutors and mentors in high-need US public schools",
            "Тьюторы и наставники AmeriCorps в школах с высокими потребностями в США",
            "City Year is a US 501(c)(3) headquartered in Boston, founded in 1988. "
            "Recruits diverse 18–25-year-olds as full-time AmeriCorps members who "
            "serve in 350+ high-need schools in 29 US cities, providing tutoring, "
            "mentoring and after-school programming.",
            "City Year — американская 501(c)(3), штаб-квартира в Бостоне, основана "
            "в 1988 году. Набирает разнородных молодых людей 18–25 лет в качестве "
            "полнозанятых членов AmeriCorps; они работают в 350+ школах с высокими "
            "потребностями в 29 городах США: тьюторство, менторство и продлёнка.",
            "https://www.cityyear.org/donate/",
            "huge", date(2024, 11, 14), "180000000.00", "82.00", 1988,
            ["education"]),
    _people("communities-in-schools", "521390877",
            "Communities In Schools",
            "Largest US dropout-prevention organisation",
            "Крупнейшая в США организация по профилактике отсева",
            "Communities In Schools is a US 501(c)(3) headquartered in Arlington, "
            "VA, founded in 1977. A national network with affiliate offices in "
            "2,900+ K–12 schools placing site coordinators inside the school day; "
            "connects students to academic and basic-needs resources to keep them "
            "in school and on track.",
            "Communities In Schools — американская 501(c)(3), штаб-квартира в "
            "Арлингтоне, Вирджиния, основана в 1977 году. Национальная сеть с "
            "представителями в 2 900+ школах K–12: координаторы работают внутри "
            "школьного дня и связывают учеников с учебными ресурсами и базовой "
            "помощью, чтобы они оставались в школе.",
            "https://www.communitiesinschools.org/donate/",
            "huge", date(2024, 11, 14), "47000000.00", "82.00", 1977,
            ["education"]),
    _people("year-up", "043534401",
            "Year Up United",
            "One-year skills training and internships for young adults",
            "Годовая программа навыков и стажировок для молодых взрослых",
            "Year Up United is a US 501(c)(3) headquartered in Boston, founded in "
            "2000. Provides a one-year programme combining skills training, "
            "professional development and a corporate internship for low-income "
            "young adults aged 18–29; partners with 250+ Fortune 500 employers.",
            "Year Up United — американская 501(c)(3), штаб-квартира в Бостоне, "
            "основана в 2000 году. Годовая программа: профессиональное обучение, "
            "развитие гибких навыков и корпоративная стажировка для молодых людей "
            "18–29 лет из малоимущих семей; партнёрство с 250+ компаниями из "
            "Fortune 500.",
            "https://www.yearup.org/donate",
            "huge", date(2024, 11, 14), "200000000.00", "80.00", 2000,
            ["education"]),
    _people("kipp-foundation", "943362724",
            "KIPP Foundation",
            "National network of 280+ public charter schools",
            "Национальная сеть из 280+ государственных чартерных школ",
            "KIPP Foundation is a US 501(c)(3) headquartered in San Francisco, "
            "founded in 2000. Supports the KIPP Public Schools network — 280+ "
            "tuition-free, college-preparatory public charter schools serving "
            "175,000+ students in 21 states and DC, with a strong record of "
            "college matriculation in low-income communities.",
            "KIPP Foundation — американская 501(c)(3), штаб-квартира в "
            "Сан-Франциско, основана в 2000 году. Поддерживает сеть KIPP Public "
            "Schools — 280+ бесплатных подготовительных к колледжу чартерных школ, "
            "175 000+ учеников в 21 штате и округе Колумбия; высокий процент "
            "поступления в колледж среди детей из малоимущих семей.",
            "https://www.kipp.org/donate/",
            "large", date(2024, 11, 14), "55000000.00", "78.00", 2000,
            ["education"]),
    _people("proliteracy", "161604491",
            "ProLiteracy",
            "Largest US membership network for adult literacy and basic education",
            "Крупнейшая в США сеть в области грамотности взрослых",
            "ProLiteracy is a US 501(c)(3) headquartered in Syracuse, NY, founded "
            "in 2002 (by merger of Laubach Literacy and Literacy Volunteers of "
            "America). 1,000+ member organisations across the US providing adult "
            "literacy, ESL and high-school equivalency instruction; publishes "
            "New Readers Press materials.",
            "ProLiteracy — американская 501(c)(3), штаб-квартира в Сиракьюсе, "
            "Нью-Йорк, основана в 2002 году (слияние Laubach Literacy и Literacy "
            "Volunteers of America). 1 000+ организаций-членов по США: грамотность "
            "взрослых, ESL и подготовка к экзамену на эквивалент школьного "
            "аттестата; издательство New Readers Press.",
            "https://proliteracy.org/donate/",
            "small", date(2024, 5, 14), "5500000.00", "76.00", 2002,
            ["education"]),
    _people("teach-for-all", "263168127",
            "Teach For All",
            "Global network of national Teach For X organisations in 60+ countries",
            "Глобальная сеть Teach For X в 60+ странах",
            "Teach For All is a US 501(c)(3) headquartered in New York, founded in "
            "2007 by Wendy Kopp. Supports 60+ independent national partner "
            "organisations (each modelled after Teach For America) recruiting "
            "talented graduates to teach in under-resourced schools and become "
            "lifelong leaders for educational equity.",
            "Teach For All — американская 501(c)(3), штаб-квартира в Нью-Йорке, "
            "основана в 2007 году Венди Копп. Поддерживает 60+ независимых "
            "национальных организаций-партнёров (по модели Teach For America): "
            "набор талантливых выпускников для преподавания в школах с дефицитом "
            "ресурсов и формирования лидеров за образовательное равенство.",
            "https://teachforall.org/donate",
            "large", date(2024, 11, 14), "78000000.00", "78.00", 2007,
            ["education"]),

    # ----- Hunger / food -----
    _people("feeding-america", "363673599",
            "Feeding America",
            "Largest US hunger-relief organisation — 200+ food banks nationwide",
            "Крупнейшая в США организация по борьбе с голодом — 200+ продбанков",
            "Feeding America is a US 501(c)(3) headquartered in Chicago, founded "
            "in 1979 (originally America's Second Harvest). Nationwide network of "
            "200+ member food banks and 60,000+ partner agencies; distributed "
            "5.3B+ meals in FY2024 to 49M people facing food insecurity in the US.",
            "Feeding America — американская 501(c)(3), штаб-квартира в Чикаго, "
            "основана в 1979 году (исходно America's Second Harvest). "
            "Общенациональная сеть из 200+ продовольственных банков-членов и "
            "60 000+ партнёрских организаций; в 2024 финансовом году "
            "распределили 5,3+ млрд порций еды для 49 млн человек, столкнувшихся "
            "с продовольственной незащищённостью в США.",
            "https://www.feedingamerica.org/ways-to-give/donate-money",
            "huge", date(2024, 11, 14), "4200000000.00", "98.00", 1979,
            ["hunger"]),
    _people("city-harvest", "133170676",
            "City Harvest",
            "New York City's largest food rescue organisation",
            "Крупнейшая организация по спасению еды в Нью-Йорке",
            "City Harvest is a US 501(c)(3) headquartered in New York, founded in "
            "1982 — the world's first food-rescue organisation. Rescues fresh "
            "food from restaurants, grocers, farms and manufacturers and "
            "delivers it free to 400+ soup kitchens, food pantries and other "
            "community partners across NYC's five boroughs.",
            "City Harvest — американская 501(c)(3), штаб-квартира в Нью-Йорке, "
            "основана в 1982 году — первая в мире организация по спасению "
            "продуктов. Забирает свежую еду у ресторанов, магазинов, ферм и "
            "производителей и бесплатно доставляет её в 400+ столовых, "
            "продовольственных пантри и другие партнёрские точки во всех пяти "
            "боро Нью-Йорка.",
            "https://www.cityharvest.org/donate/",
            "large", date(2024, 11, 14), "150000000.00", "92.00", 1982,
            ["hunger"]),
    _people("meals-on-wheels-america", "362378411",
            "Meals on Wheels America",
            "Federation of 5,000+ local programmes delivering meals to homebound seniors",
            "Федерация из 5 000+ местных программ доставки еды пожилым на дом",
            "Meals on Wheels America is a US 501(c)(3) headquartered in Arlington, "
            "VA, founded in 1974. National federation of 5,000+ community-based "
            "Meals on Wheels providers delivering nutritious meals (and a "
            "wellness check) to 2.4M+ homebound seniors across the United States.",
            "Meals on Wheels America — американская 501(c)(3), штаб-квартира в "
            "Арлингтоне, Вирджиния, основана в 1974 году. Национальная федерация "
            "5 000+ местных программ Meals on Wheels: доставляют питательные "
            "обеды (и проверяют самочувствие) 2,4+ млн пожилых на дому по США.",
            "https://www.mealsonwheelsamerica.org/give",
            "medium", date(2024, 11, 14), "23000000.00", "78.00", 1974,
            ["hunger", "senior-care"]),
    _people("world-central-kitchen", "273521132",
            "World Central Kitchen",
            "Chef-led emergency food relief in disaster and conflict zones",
            "Экстренная продовольственная помощь под руководством шеф-поваров",
            "World Central Kitchen is a US 501(c)(3) headquartered in Washington, "
            "DC, founded in 2010 by chef José Andrés after the Haiti earthquake. "
            "Has served 400M+ meals worldwide in response to natural disasters, "
            "conflicts (Ukraine, Gaza, Sudan) and humanitarian crises by working "
            "with local restaurants, food trucks and community kitchens.",
            "World Central Kitchen — американская 501(c)(3), штаб-квартира в "
            "Вашингтоне, округ Колумбия, основана в 2010 году шеф-поваром Хосе "
            "Андресом после землетрясения на Гаити. Подано 400+ млн порций еды по "
            "миру в ответ на стихийные бедствия, конфликты (Украина, Газа, "
            "Судан) и гуманитарные кризисы — через местные рестораны, фудтраки и "
            "общинные кухни.",
            "https://wck.org/donate",
            "huge", date(2024, 11, 14), "470000000.00", "92.00", 2010,
            ["hunger", "global-health"]),
    _people("action-against-hunger-usa", "133327220",
            "Action Against Hunger USA",
            "Lifesaving treatment for severe acute malnutrition in 50+ countries",
            "Экстренная помощь при тяжёлом остром недоедании в 50+ странах",
            "Action Against Hunger USA is the US 501(c)(3) arm of the global "
            "Action Against Hunger network, founded in France in 1979. Treats "
            "children with severe acute malnutrition (SAM) using ready-to-use "
            "therapeutic foods, runs water and sanitation programmes, and "
            "responds to humanitarian emergencies in 50+ countries.",
            "Action Against Hunger USA — американское 501(c)(3) подразделение "
            "глобальной сети Action Against Hunger, основанной во Франции в 1979 "
            "году. Лечит детей с тяжёлым острым недоеданием (SAM) с "
            "использованием готовых терапевтических продуктов, ведёт программы "
            "водоснабжения и санитарии, отвечает на гуманитарные кризисы в 50+ "
            "странах.",
            "https://www.actionagainsthunger.org/donate/",
            "large", date(2024, 11, 14), "50000000.00", "92.00", 1979,
            ["hunger", "global-health"]),

    # ----- Housing -----
    _people("enterprise-community-partners", "521231931",
            "Enterprise Community Partners",
            "Builds and preserves affordable homes; invests in low-income communities",
            "Строит и сохраняет доступное жильё, инвестирует в малоимущие сообщества",
            "Enterprise Community Partners is a US 501(c)(3) headquartered in "
            "Columbia, MD, founded in 1982 by James W. Rouse. National "
            "intermediary for affordable housing — has invested $80B+ in the "
            "creation and preservation of 1M+ affordable homes since founding, "
            "and provides Section 4 capacity-building grants to community "
            "developers nationwide.",
            "Enterprise Community Partners — американская 501(c)(3), штаб-"
            "квартира в Колумбии, штат Мэриленд, основана в 1982 году Джеймсом "
            "Раузом. Национальный посредник в сфере доступного жилья: "
            "инвестировано $80+ млрд в создание и сохранение 1+ млн доступных "
            "квартир с момента основания, гранты на наращивание потенциала "
            "(Section 4) для общинных застройщиков по стране.",
            "https://www.enterprisecommunity.org/donate",
            "huge", date(2024, 11, 14), "650000000.00", "78.00", 1982,
            ["housing"]),
    _people("neighborworks-america", "521422704",
            "NeighborWorks America",
            "Federally chartered nonprofit supporting 250+ community-development orgs",
            "Федерально учреждённая НКО для поддержки 250+ общинных застройщиков",
            "NeighborWorks America is a US 501(c)(3) (also a Congressionally "
            "chartered nonpartisan nonprofit) headquartered in Washington, DC, "
            "founded in 1978. Supports a network of 250+ local NeighborWorks "
            "organisations across all 50 states with funding, training and "
            "technical assistance for affordable housing and community "
            "development.",
            "NeighborWorks America — американская 501(c)(3) (учреждена Конгрессом "
            "США как беспартийная НКО), штаб-квартира в Вашингтоне, округ "
            "Колумбия, основана в 1978 году. Поддерживает сеть из 250+ местных "
            "организаций NeighborWorks во всех 50 штатах: финансирование, "
            "обучение и техническая помощь по доступному жилью и общинному "
            "развитию.",
            "https://www.neighborworks.org/Donate",
            "huge", date(2024, 11, 14), "300000000.00", "82.00", 1978,
            ["housing"]),
    _people("coalition-for-the-homeless", "133072967",
            "Coalition for the Homeless (NYC)",
            "Oldest US advocacy and direct-service org for homeless people",
            "Старейшая в США организация прямой помощи и адвокации для бездомных",
            "Coalition for the Homeless is a US 501(c)(3) headquartered in New "
            "York, founded in 1981. Operates a year-round emergency Crisis "
            "Intervention Program, eviction-prevention services, an after-"
            "school programme for homeless children, and the Grand Central Food "
            "Program — a mobile soup kitchen serving 1,000+ meals every night "
            "across NYC.",
            "Coalition for the Homeless — американская 501(c)(3), штаб-квартира "
            "в Нью-Йорке, основана в 1981 году. Круглогодичная программа "
            "экстренной помощи Crisis Intervention Program, услуги по "
            "предотвращению выселений, продлёнка для бездомных детей, а также "
            "Grand Central Food Program — мобильная столовая, подающая 1 000+ "
            "порций еды каждую ночь по Нью-Йорку.",
            "https://www.coalitionforthehomeless.org/donate/",
            "medium", date(2024, 5, 14), "26000000.00", "82.00", 1981,
            ["housing"]),

    # ----- Refugees -----
    _people("hias", "131635219",
            "HIAS",
            "Jewish humanitarian agency providing protection to refugees worldwide",
            "Еврейское гуманитарное агентство по защите беженцев в мире",
            "HIAS is a US 501(c)(3) headquartered in Silver Spring, MD, founded in "
            "1881 as the Hebrew Immigrant Aid Society. Today provides humanitarian "
            "aid, legal protection and resettlement services to refugees of all "
            "faiths in 20+ countries — among the nine official US refugee "
            "resettlement agencies.",
            "HIAS — американская 501(c)(3), штаб-квартира в Сильвер-Спринг, "
            "Мэриленд, основана в 1881 году как Hebrew Immigrant Aid Society. "
            "Сегодня — гуманитарная помощь, правовая защита и услуги "
            "переселения беженцев всех вероисповеданий в 20+ странах; одно из "
            "девяти официальных агентств переселения беженцев в США.",
            "https://hias.org/donate",
            "huge", date(2024, 11, 14), "100000000.00", "85.00", 1881,
            ["refugees"]),
    _people("refugees-international", "521314010",
            "Refugees International",
            "Independent advocacy on behalf of displaced people worldwide",
            "Независимая адвокация прав вынужденных переселенцев по миру",
            "Refugees International is a US 501(c)(3) headquartered in Washington, "
            "DC, founded in 1979. Conducts on-the-ground assessments of "
            "humanitarian crises and advocates with the US government, UN and "
            "humanitarian agencies; takes no government or UN funding to preserve "
            "independence.",
            "Refugees International — американская 501(c)(3), штаб-квартира в "
            "Вашингтоне, округ Колумбия, основана в 1979 году. Проводит выездные "
            "оценки гуманитарных кризисов и адвокатирует перед правительством "
            "США, ООН и гуманитарными агентствами; не принимает финансирование "
            "от государства или ООН ради сохранения независимости.",
            "https://www.refugeesinternational.org/take-action/",
            "small", date(2024, 5, 14), "5500000.00", "78.00", 1979,
            ["refugees"]),

    # ----- Senior care -----
    _people("aarp-foundation", "520794300",
            "AARP Foundation",
            "Charitable affiliate of AARP — advocates for low-income older adults",
            "Благотворительный филиал AARP — помогает малоимущим пожилым людям",
            "AARP Foundation is a US 501(c)(3) headquartered in Washington, DC, "
            "founded in 1961 as the charitable affiliate of AARP. Tax-Aide "
            "programme provides free tax-prep to low- and moderate-income "
            "taxpayers (1.7M returns/yr); also runs job-training, food-security "
            "and isolation-prevention programmes for older adults.",
            "AARP Foundation — американская 501(c)(3), штаб-квартира в "
            "Вашингтоне, округ Колумбия, основана в 1961 году как "
            "благотворительный филиал AARP. Программа Tax-Aide бесплатно "
            "помогает малоимущим и среднему классу с налоговой отчётностью "
            "(1,7 млн деклараций в год); также — обучение, продовольственная "
            "безопасность и борьба с одиночеством среди пожилых.",
            "https://www.aarp.org/aarp-foundation/donate-options/",
            "huge", date(2024, 11, 14), "85000000.00", "78.00", 1961,
            ["senior-care"]),

    # ----- Faith-based service -----
    _people("catholic-relief-services", "135563422",
            "Catholic Relief Services",
            "International humanitarian agency of the US Catholic Bishops",
            "Международное гуманитарное агентство католических епископов США",
            "Catholic Relief Services is a US 501(c)(3) headquartered in "
            "Baltimore, MD, founded in 1943 by the United States Conference of "
            "Catholic Bishops. Provides humanitarian aid, development "
            "assistance and peacebuilding programmes to people of all faiths in "
            "100+ countries — emergency response, agriculture, health, water and "
            "sanitation, education and microfinance.",
            "Catholic Relief Services — американская 501(c)(3), штаб-квартира в "
            "Балтиморе, основана в 1943 году Конференцией католических "
            "епископов США. Гуманитарная помощь, программы развития и "
            "миростроительство для людей всех вероисповеданий в 100+ странах: "
            "экстренная помощь, сельское хозяйство, здравоохранение, "
            "водоснабжение и санитария, образование и микрофинансирование.",
            "https://support.crs.org/donate",
            "huge", date(2024, 11, 14), "1100000000.00", "94.00", 1943,
            ["faith-based", "global-health", "hunger"]),
    _people("world-vision-us", "951922279",
            "World Vision (US)",
            "Christian humanitarian organisation working in nearly 100 countries",
            "Христианская гуманитарная организация почти в 100 странах",
            "World Vision Inc. (US) is a US 501(c)(3) headquartered in Federal "
            "Way, WA, founded in 1950 by Bob Pierce. Christian humanitarian "
            "organisation serving people of all faiths; runs child-sponsorship, "
            "WASH (water, sanitation, hygiene), child protection, agriculture "
            "and emergency-relief programmes worldwide. Largest WASH "
            "implementer outside the UN system.",
            "World Vision Inc. (США) — американская 501(c)(3), штаб-квартира в "
            "Federal Way, штат Вашингтон, основана в 1950 году Бобом Пирсом. "
            "Христианская гуманитарная организация, помогает людям всех "
            "вероисповеданий: спонсорство детей, WASH (вода, санитария, "
            "гигиена), защита детей, сельское хозяйство и экстренная помощь по "
            "миру. Крупнейший исполнитель WASH вне системы ООН.",
            "https://www.worldvision.org/give",
            "huge", date(2024, 11, 14), "1300000000.00", "85.00", 1950,
            ["faith-based", "global-health"]),
    _people("salvation-army-national", "222406433",
            "The Salvation Army National Corporation",
            "National HQ of the US-wide Salvation Army Christian charity",
            "Национальная штаб-квартира американской благотворительной The Salvation Army",
            "The Salvation Army National Corporation is the US 501(c)(3) "
            "national headquarters of The Salvation Army, headquartered in "
            "Alexandria, VA. Founded in London in 1865; US presence since 1880. "
            "Coordinates the Salvation Army's US-wide programmes: emergency "
            "disaster services, homeless shelters, addiction recovery, "
            "anti-trafficking and food assistance. (Regional Salvation Army "
            "corps file IRS 990s separately.)",
            "The Salvation Army National Corporation — национальная штаб-"
            "квартира американской 501(c)(3) The Salvation Army (Армии "
            "Спасения) в Александрии, штат Вирджиния. Основана в Лондоне в "
            "1865 году; в США работает с 1880 года. Координирует программы по "
            "США: экстренная помощь при бедствиях, ночлежки, реабилитация от "
            "зависимостей, борьба с торговлей людьми, продовольственная помощь. "
            "(Региональные корпуса подают форму 990 отдельно.)",
            "https://www.salvationarmyusa.org/usn/ways-to-give/",
            "huge", date(2024, 11, 14), "260000000.00", "78.00", 1880,
            ["faith-based", "housing", "hunger"]),

    # ----- Microfinance -----
    _people("kiva", "710992446",
            "Kiva",
            "Crowdfunded microloans to entrepreneurs in 80+ countries",
            "Краудфандинговые микрозаймы предпринимателям в 80+ странах",
            "Kiva is a US 501(c)(3) headquartered in San Francisco, founded in "
            "2005. Operates Kiva.org, a crowdfunding platform for 0%-interest "
            "loans to underbanked entrepreneurs and students in 80+ countries; "
            "$2.1B+ disbursed to 5M+ borrowers since founding, with a 95%+ "
            "repayment rate.",
            "Kiva — американская 501(c)(3), штаб-квартира в Сан-Франциско, "
            "основана в 2005 году. Платформа Kiva.org — краудфандинг беспроцентных "
            "займов предпринимателям и студентам без доступа к банковским "
            "услугам в 80+ странах; выдано $2,1+ млрд для 5+ млн заёмщиков с "
            "момента основания, доля возврата 95%+.",
            "https://www.kiva.org/donate",
            "large", date(2024, 11, 14), "30000000.00", "78.00", 2005,
            ["microfinance"]),
    _people("finca-international", "133240109",
            "FINCA International",
            "Microfinance for low-income entrepreneurs in 20 countries",
            "Микрофинансирование малоимущих предпринимателей в 20 странах",
            "FINCA International is a US 501(c)(3) headquartered in Washington, "
            "DC, founded in 1984 by John Hatch — pioneers of the village-banking "
            "methodology. Provides financial services (loans, savings, "
            "insurance, payments) to low-income entrepreneurs through a network "
            "of subsidiary FINCA microfinance institutions in ~20 countries "
            "across Africa, Eurasia, Latin America and the Middle East.",
            "FINCA International — американская 501(c)(3), штаб-квартира в "
            "Вашингтоне, округ Колумбия, основана в 1984 году Джоном Хэтчем — "
            "пионером методологии village banking. Финансовые услуги (займы, "
            "сбережения, страхование, платежи) малоимущим предпринимателям "
            "через сеть дочерних микрофинансовых организаций FINCA в ~20 "
            "странах Африки, Евразии, Латинской Америки и Ближнего Востока.",
            "https://finca.org/donate/",
            "medium", date(2024, 5, 14), "15000000.00", "76.00", 1984,
            ["microfinance"]),

    # ----- Crisis / suicide prevention -----
    _people("vibrant-emotional-health", "132992133",
            "Vibrant Emotional Health (988 Lifeline)",
            "Operates the 988 Suicide & Crisis Lifeline in the United States",
            "Оператор линии 988 Suicide & Crisis Lifeline в США",
            "Vibrant Emotional Health is a US 501(c)(3) headquartered in New "
            "York. Administers the 988 Suicide & Crisis Lifeline (formerly the "
            "National Suicide Prevention Lifeline) — a network of 200+ local "
            "and national crisis centres that respond to people in distress "
            "across the US 24/7 by phone, chat and text.",
            "Vibrant Emotional Health — американская 501(c)(3), штаб-квартира "
            "в Нью-Йорке. Администрирует линию 988 Suicide & Crisis Lifeline "
            "(ранее National Suicide Prevention Lifeline) — сеть из 200+ "
            "местных и национальных кризисных центров, которая отвечает людям "
            "в США круглосуточно по телефону, чату и СМС.",
            "https://www.vibrant.org/donate/",
            "huge", date(2024, 11, 14), "550000000.00", "92.00", 1969,
            ["suicide-prevention", "mental-health"]),
    _people("crisis-text-line", "320395877",
            "Crisis Text Line",
            "24/7 free text-based mental-health crisis support",
            "Круглосуточная бесплатная кризисная поддержка по СМС",
            "Crisis Text Line is a US 501(c)(3) headquartered in New York, "
            "founded in 2013 by Nancy Lublin. Free 24/7 confidential text-line "
            "(Text HELLO to 741741 in the US) staffed by trained volunteer "
            "Crisis Counselors; also operates in Canada, the UK, Ireland and "
            "South Africa. Has handled 10M+ conversations.",
            "Crisis Text Line — американская 501(c)(3), штаб-квартира в "
            "Нью-Йорке, основана в 2013 году Нэнси Лаблин. Бесплатная "
            "круглосуточная конфиденциальная СМС-линия (HELLO на 741741 в "
            "США), обслуживаемая обученными волонтёрами Crisis Counselors; "
            "также работает в Канаде, Великобритании, Ирландии и ЮАР. "
            "Проведено 10+ млн диалогов.",
            "https://www.crisistextline.org/donate/",
            "medium", date(2024, 5, 14), "25000000.00", "75.00", 2013,
            ["suicide-prevention", "mental-health"]),

    # ============== ANIMALS — 10 ==============
    _animals("bat-conservation-international", "742553144",
             "Bat Conservation International",
             "Protects the world's bats and their habitats",
             "Защищает летучих мышей и их места обитания",
             "Bat Conservation International is a US 501(c)(3) headquartered in "
             "Austin, TX, founded in 1982 by Dr. Merlin Tuttle. Works on the "
             "highest-priority bat-conservation challenges — endangered species "
             "recovery, white-nose syndrome research, agave restoration for "
             "nectar-feeders, and acoustic-monitoring science worldwide.",
             "Bat Conservation International — американская 501(c)(3), штаб-"
             "квартира в Остине, Техас, основана в 1982 году доктором "
             "Мерлином Таттлом. Работает над самыми приоритетными задачами "
             "сохранения летучих мышей: восстановление исчезающих видов, "
             "исследования синдрома белого носа, восстановление агавы для "
             "нектароядных, акустический мониторинг по миру.",
             "https://www.batcon.org/donate/",
             "medium", date(2024, 5, 14), "10000000.00", "78.00", 1982,
             ["wildlife-conservation", "biodiversity-defense"]),
    _animals("whale-and-dolphin-conservation-usa", "043170933",
             "Whale and Dolphin Conservation USA",
             "Dedicated solely to the protection of whales and dolphins",
             "Посвящена исключительно защите китов и дельфинов",
             "Whale and Dolphin Conservation (WDC) USA is a US 501(c)(3) "
             "headquartered in Plymouth, MA — the US arm of the international "
             "WDC network. Campaigns to end whaling and captivity, protects "
             "endangered species (right whales, vaquita), supports the SoBlu "
             "Sanctuary in Iceland, and runs ocean-conservation education.",
             "Whale and Dolphin Conservation (WDC) USA — американская "
             "501(c)(3), штаб-квартира в Плимуте, штат Массачусетс — "
             "американское подразделение международной сети WDC. Кампании "
             "против китобойного промысла и содержания в неволе, защита "
             "исчезающих видов (североатлантические гладкие киты, "
             "калифорнийская морская свинья), поддержка SoBlu Sanctuary в "
             "Исландии, образовательные программы по сохранению океана.",
             "https://us.whales.org/donate/",
             "small", date(2024, 5, 14), "2500000.00", "78.00", 1987,
             ["marine-mammals", "ocean-protection"]),
    _animals("greater-good-charities", "911937985",
             "Greater Good Charities",
             "Funds animal-welfare and humanitarian projects worldwide",
             "Финансирует проекты по защите животных и гуманитарные программы по миру",
             "Greater Good Charities is a US 501(c)(3) headquartered in "
             "Seattle, founded in 2007. Channels donations and corporate "
             "partnerships into 200+ partner organisations worldwide — animal "
             "welfare (shelter pet food, spay/neuter), wildlife protection, "
             "human-animal bond programmes, and disaster relief for animals.",
             "Greater Good Charities — американская 501(c)(3), штаб-квартира "
             "в Сиэтле, основана в 2007 году. Направляет пожертвования и "
             "корпоративные партнёрства в 200+ организаций-партнёров по миру: "
             "благополучие животных (корм для приютов, стерилизация), защита "
             "дикой природы, программы человек-животное и помощь животным при "
             "бедствиях.",
             "https://greatergood.org/donate",
             "huge", date(2024, 11, 14), "120000000.00", "94.00", 2007,
             ["animal-welfare", "wildlife-conservation"]),
    _animals("north-shore-animal-league", "111666852",
             "North Shore Animal League America",
             "World's largest no-kill animal rescue and adoption organisation",
             "Крупнейшая в мире организация спасения и пристройки животных без эвтаназии",
             "North Shore Animal League America is a US 501(c)(3) "
             "headquartered in Port Washington, NY, founded in 1944. World's "
             "largest no-kill rescue and adoption organisation: 1.1M+ animals "
             "rescued since founding through its Mutt-i-grees and Tour For "
             "Life mobile-rescue programmes that pull animals from at-risk "
             "shelters across the US.",
             "North Shore Animal League America — американская 501(c)(3), "
             "штаб-квартира в Порт-Вашингтоне, штат Нью-Йорк, основана в 1944 "
             "году. Крупнейшая в мире организация спасения и пристройства без "
             "эвтаназии: 1,1+ млн животных спасено за всё время через "
             "программы Mutt-i-grees и Tour For Life — мобильные команды "
             "забирают животных из приютов с высоким риском по США.",
             "https://www.animalleague.org/donate/",
             "large", date(2024, 11, 14), "55000000.00", "76.00", 1944,
             ["animal-welfare"]),
    _animals("whale-sanctuary-project", "811454193",
             "The Whale Sanctuary Project",
             "Building the first seaside sanctuary for whales and dolphins",
             "Создание первого морского санктуария для китов и дельфинов",
             "The Whale Sanctuary Project is a US 501(c)(3) headquartered in "
             "Kanata, ON / Bath, ME, founded in 2016. Building the world's "
             "first seaside sanctuary in Port Hilford Bay, Nova Scotia, for "
             "whales and dolphins retired from entertainment marine parks. "
             "100+ acres of natural habitat, no shows, no breeding.",
             "The Whale Sanctuary Project — американская 501(c)(3), офисы в "
             "Канаде и в штате Мэн, основана в 2016 году. Строит первый в "
             "мире морской санктуарий в заливе Порт-Хилфорд, Новая Шотландия, "
             "для китов и дельфинов, выведенных из развлекательных морских "
             "парков. 100+ акров природной среды, без шоу, без разведения.",
             "https://whalesanctuaryproject.org/donate/",
             "small", date(2024, 5, 14), "2500000.00", "82.00", 2016,
             ["marine-mammals", "ocean-protection"]),
    _animals("marine-conservation-institute", "943105570",
             "Marine Conservation Institute",
             "Champions strongly protected marine areas worldwide",
             "Продвигает сильно защищённые морские зоны по миру",
             "Marine Conservation Institute is a US 501(c)(3) headquartered in "
             "Seattle, founded in 1996. Runs the Marine Protection Atlas — "
             "tracking the strength of protection for every MPA worldwide — "
             "and the Blue Parks awards, which recognise marine protected "
             "areas meeting the highest scientific standards. Goal: 30%+ of "
             "the global ocean strongly protected by 2030.",
             "Marine Conservation Institute — американская 501(c)(3), штаб-"
             "квартира в Сиэтле, основана в 1996 году. Marine Protection "
             "Atlas — отслеживает уровень защиты каждой охраняемой морской "
             "зоны (MPA) по миру; Blue Parks Award признаёт MPA, "
             "соответствующие высшим научным стандартам. Цель: 30%+ "
             "глобального океана под сильной защитой к 2030 году.",
             "https://marine-conservation.org/donate/",
             "small", date(2024, 5, 14), "3500000.00", "82.00", 1996,
             ["ocean-protection", "biodiversity-defense"]),
    _animals("polar-bears-international", "311690671",
             "Polar Bears International",
             "Sole conservation organisation dedicated to polar bears",
             "Единственная природоохранная организация, посвящённая белым медведям",
             "Polar Bears International is a US 501(c)(3) headquartered in "
             "Bozeman, MT, founded in 2002. The only nonprofit dedicated "
             "solely to polar bear conservation worldwide. Runs Tundra "
             "Connections from Churchill, Manitoba (live polar-bear cam and "
             "education broadcasts), funds research on sea-ice loss and "
             "human-bear coexistence, and policy work on Arctic warming.",
             "Polar Bears International — американская 501(c)(3), штаб-"
             "квартира в Бозмане, Монтана, основана в 2002 году. Единственная "
             "НКО, посвящённая исключительно сохранению белых медведей в "
             "мире. Программа Tundra Connections из Черчилла (Манитоба) — "
             "трансляции с медведями и образовательные эфиры; финансирование "
             "исследований таяния льдов и сосуществования медведей и людей; "
             "политика по потеплению в Арктике.",
             "https://polarbearsinternational.org/donate",
             "small", date(2024, 5, 14), "5000000.00", "78.00", 2002,
             ["polar-wildlife", "wildlife-conservation", "climate"]),
    _animals("galapagos-conservancy", "133281486",
             "Galapagos Conservancy",
             "Sole US 501(c)(3) dedicated to protecting the Galápagos",
             "Единственная американская 501(c)(3), посвящённая Галапагосам",
             "Galapagos Conservancy is a US 501(c)(3) headquartered in "
             "Fairfax, VA, founded in 1985. The only US 501(c)(3) dedicated "
             "solely to protecting the unique biodiversity of the Galápagos "
             "Islands. Funds tortoise restoration (giant Galápagos and "
             "Pinzón tortoises), invasive-species control, and the Charles "
             "Darwin Research Station in partnership with Ecuador.",
             "Galapagos Conservancy — американская 501(c)(3), штаб-квартира в "
             "Фэрфаксе, Вирджиния, основана в 1985 году. Единственная "
             "американская 501(c)(3), посвящённая исключительно защите "
             "уникального биоразнообразия Галапагосских островов. "
             "Финансирует восстановление гигантских галапагосских черепах и "
             "черепах острова Пинсон, борьбу с инвазивными видами, "
             "научно-исследовательскую станцию имени Чарлза Дарвина в "
             "партнёрстве с Эквадором.",
             "https://www.galapagos.org/donate/",
             "small", date(2024, 5, 14), "7000000.00", "78.00", 1985,
             ["wildlife-conservation", "biodiversity-defense"]),
    _animals("save-the-elephants-usa", "262603478",
             "Save the Elephants USA",
             "Supports African elephant research and protection from Samburu, Kenya",
             "Поддержка исследований и защиты африканских слонов из Самбуру, Кения",
             "Save the Elephants USA is a US 501(c)(3) headquartered in "
             "Albany, NY, founded in 2008 as the US fundraising arm of "
             "Save the Elephants — a Kenya-based research and conservation "
             "organisation founded by Iain Douglas-Hamilton in 1993. Funds "
             "the elephant-tracking, anti-poaching and human-elephant "
             "coexistence programmes from the Samburu research camp.",
             "Save the Elephants USA — американская 501(c)(3), штаб-квартира "
             "в Олбани, штат Нью-Йорк, основана в 2008 году как американское "
             "фандрайзинговое подразделение Save the Elephants — кенийской "
             "научно-природоохранной организации, основанной Иэном Дугласом-"
             "Гамильтоном в 1993 году. Финансирует программы трекинга слонов, "
             "противодействия браконьерству и сосуществования людей и слонов "
             "из исследовательского лагеря Самбуру.",
             "https://www.savetheelephants.org/donate/",
             "small", date(2024, 5, 14), "4500000.00", "85.00", 2008,
             ["wildlife-conservation"]),
    _animals("reef-check", "954664551",
             "Reef Check Foundation",
             "Volunteer reef-monitoring across 90+ countries since 1996",
             "Волонтёрский мониторинг рифов в 90+ странах с 1996 года",
             "Reef Check Foundation is a US 501(c)(3) headquartered in "
             "Marina del Rey, CA, founded in 1996 by Dr. Gregor Hodgson. "
             "Trains and certifies volunteer SCUBA-divers (EcoDivers) to "
             "monitor coral reef and California rocky-reef health using a "
             "standardised method; the data feeds the Reef Check Global "
             "Database used by governments and scientists worldwide.",
             "Reef Check Foundation — американская 501(c)(3), штаб-квартира "
             "в Marina del Rey, Калифорния, основана в 1996 году доктором "
             "Грегором Ходжсоном. Обучает и сертифицирует волонтёров-"
             "дайверов (EcoDivers) для мониторинга кораловых и калифорнийских "
             "скальных рифов по стандартной методике; данные поступают в "
             "Reef Check Global Database, которой пользуются правительства "
             "и учёные по миру.",
             "https://www.reefcheck.org/donate/",
             "small", date(2024, 5, 14), "3500000.00", "78.00", 1996,
             ["coral-reefs", "ocean-protection"]),

    # ============== PLANET — 15 ==============
    _planet("earthday-org", "521364030",
            "EARTHDAY.ORG",
            "Coordinator of Earth Day in 192 countries",
            "Координатор Дня Земли в 192 странах",
            "EARTHDAY.ORG (legal name Earth Day Network) is a US 501(c)(3) "
            "headquartered in Washington, DC, founded by the organisers of the "
            "first Earth Day in 1970. Coordinates Earth Day annually with "
            "1B+ participants in 192 countries; runs the Canopy Project "
            "(reforestation), End Plastic Pollution, Climate Education and "
            "Foodprints for the Future campaigns.",
            "EARTHDAY.ORG (юр. лицо Earth Day Network) — американская "
            "501(c)(3), штаб-квартира в Вашингтоне, округ Колумбия, основана "
            "организаторами первого Дня Земли 1970 года. Ежегодно координирует "
            "День Земли — 1+ млрд участников в 192 странах; программы Canopy "
            "Project (лесовосстановление), End Plastic Pollution, Climate "
            "Education и Foodprints for the Future.",
            "https://www.earthday.org/donate/",
            "medium", date(2024, 5, 14), "9500000.00", "78.00", 1970,
            ["climate", "environment"]),
    _planet("sustainable-conservation", "943232186",
            "Sustainable Conservation",
            "Solutions-driven environmental nonprofit in California",
            "Эко-НКО, ориентированная на решения, в Калифорнии",
            "Sustainable Conservation is a US 501(c)(3) headquartered in San "
            "Francisco, founded in 1993. Works in California to align "
            "agriculture, water and infrastructure decisions with conservation "
            "outcomes — methane-reducing dairy practices, groundwater recharge "
            "on farmland, and faster permitting for habitat restoration.",
            "Sustainable Conservation — американская 501(c)(3), штаб-квартира "
            "в Сан-Франциско, основана в 1993 году. Работает в Калифорнии, "
            "чтобы решения в сельском хозяйстве, водных ресурсах и "
            "инфраструктуре сочетались с природоохранными результатами: "
            "снижение выбросов метана на молочных фермах, пополнение "
            "грунтовых вод на сельхозугодьях, ускоренные разрешения для "
            "восстановления местообитаний.",
            "https://suscon.org/donate/",
            "small", date(2024, 5, 14), "5000000.00", "82.00", 1993,
            ["environment", "watershed-protection"]),
    _planet("earthrights-international", "522114161",
            "EarthRights International",
            "Combines law, advocacy and organising for earth and human rights",
            "Объединяет право, адвокацию и низовую работу за права земли и людей",
            "EarthRights International is a US 501(c)(3) headquartered in "
            "Washington, DC, founded in 1995. Litigates landmark cases "
            "(including Doe v. Unocal — first US human-rights case against a "
            "corporation reaching trial), runs the Mitharsuu Center for "
            "Leadership in SE Asia, and trains community leaders in the "
            "Amazon to defend land, environmental and human rights.",
            "EarthRights International — американская 501(c)(3), штаб-"
            "квартира в Вашингтоне, округ Колумбия, основана в 1995 году. "
            "Ведёт знаковые дела (Doe v. Unocal — первое американское дело о "
            "правах человека против корпорации, дошедшее до суда), работает "
            "Mitharsuu Center for Leadership в ЮВ Азии, обучает лидеров "
            "общин в Амазонии защищать землю, экологические и человеческие "
            "права.",
            "https://earthrights.org/donate/",
            "small", date(2024, 5, 14), "8000000.00", "82.00", 1995,
            ["environment", "indigenous-rights"]),
    _planet("pew-charitable-trusts", "562307147",
            "The Pew Charitable Trusts",
            "Independent research and policy nonprofit on environment and beyond",
            "Независимая исследовательская и политическая НКО",
            "The Pew Charitable Trusts is a US 501(c)(3) headquartered in "
            "Philadelphia, founded in 1948 by the children of Joseph N. "
            "Pew. Major programmes include ocean conservation (Pew Bertarelli "
            "Ocean Legacy — has helped designate 7M+ km² of marine protected "
            "areas), public-policy research, public health and US state-"
            "policy work. Operates from public-charity status since 2004.",
            "The Pew Charitable Trusts — американская 501(c)(3), штаб-"
            "квартира в Филадельфии, основана в 1948 году детьми Джозефа Пью. "
            "Крупные программы: сохранение океана (Pew Bertarelli Ocean "
            "Legacy — помогли создать 7+ млн км² охраняемых морских зон), "
            "исследования государственной политики, общественное здоровье, "
            "работа на уровне штатов. Со статусом public charity с 2004 года.",
            "https://www.pewtrusts.org/en/about/donate",
            "huge", date(2024, 11, 14), "330000000.00", "82.00", 1948,
            ["ocean-protection", "environment"]),
    _planet("coral-restoration-foundation", "593676590",
            "Coral Restoration Foundation",
            "Largest reef-restoration organisation in the world",
            "Крупнейшая в мире организация по восстановлению рифов",
            "Coral Restoration Foundation is a US 501(c)(3) headquartered in "
            "Key Largo, FL, founded in 2007 by Ken Nedimyer. Runs the largest "
            "in-water coral nursery in the world (offshore of the Florida "
            "Keys), and has outplanted 230,000+ corals onto Florida's Coral "
            "Reef using a fragmentation-and-grow method that restores "
            "genetically diverse staghorn and elkhorn coral populations.",
            "Coral Restoration Foundation — американская 501(c)(3), штаб-"
            "квартира в Ки-Ларго, Флорида, основана в 2007 году Кеном "
            "Недимиером. Ведёт крупнейший в мире подводный коралловый "
            "питомник (у Флорида-Кис), пересажено 230 000+ кораллов на "
            "Флоридский коралловый риф методом фрагментации-выращивания, "
            "восстановление генетически разнообразных популяций кораллов-"
            "оленей и кораллов-лосиных рогов.",
            "https://coralrestoration.org/donate/",
            "small", date(2024, 5, 14), "5500000.00", "78.00", 2007,
            ["coral-reefs", "ocean-protection"]),
    _planet("coastal-conservation-association", "742210558",
            "Coastal Conservation Association",
            "Largest US recreational saltwater-angling conservation org",
            "Крупнейшая в США орг. сохранения спортивного морского рыболовства",
            "Coastal Conservation Association (CCA) is a US 501(c)(3) "
            "headquartered in Houston, TX, founded in 1977. National "
            "association of 17 coastal-state chapters and 100,000+ members "
            "advocating for the conservation, promotion and enhancement of "
            "marine resources accessible to recreational saltwater anglers — "
            "redfish, striped bass, gamefish protections.",
            "Coastal Conservation Association (CCA) — американская "
            "501(c)(3), штаб-квартира в Хьюстоне, Техас, основана в 1977 "
            "году. Национальная ассоциация из 17 отделений в прибрежных "
            "штатах и 100 000+ членов; продвигает сохранение, развитие и "
            "улучшение морских ресурсов, доступных для спортивных морских "
            "рыболовов: красный горбыль, полосатый окунь, защита промысловых "
            "видов.",
            "https://joincca.org/donate/",
            "medium", date(2024, 5, 14), "16000000.00", "76.00", 1977,
            ["ocean-protection", "biodiversity-defense"]),
    _planet("naturebridge", "942102885",
            "NatureBridge",
            "Hands-on environmental science education in US national parks",
            "Практическое экологическое образование в нацпарках США",
            "NatureBridge is a US 501(c)(3) headquartered in San Francisco, "
            "founded in 1971. Provides multi-day environmental-science "
            "field-science programmes inside US national parks — Yosemite, "
            "Olympic, Golden Gate, Channel Islands, Prince William Forest, "
            "Santa Monica Mountains, Olympic — to ~30,000 K-12 students "
            "each year.",
            "NatureBridge — американская 501(c)(3), штаб-квартира в "
            "Сан-Франциско, основана в 1971 году. Многодневные программы "
            "полевой экологической науки внутри национальных парков США — "
            "Йосемити, Олимпик, Golden Gate, Channel Islands, Prince "
            "William Forest, Santa Monica Mountains — для ~30 000 учеников "
            "K-12 ежегодно.",
            "https://naturebridge.org/donate/",
            "medium", date(2024, 5, 14), "20000000.00", "78.00", 1971,
            ["environment", "education"]),
    _planet("climate-solutions", "911742130",
            "Climate Solutions",
            "Pacific Northwest clean-energy and climate advocacy",
            "Адвокация чистой энергии и климата на Тихоокеанском Северо-Западе США",
            "Climate Solutions is a US 501(c)(3) headquartered in Seattle, "
            "founded in 1998. Pacific Northwest regional climate org — "
            "advocates for clean-electricity standards, building "
            "decarbonisation, low-carbon transportation and equitable climate "
            "policy in Washington, Oregon and beyond. Operates the New Energy "
            "Cities programme.",
            "Climate Solutions — американская 501(c)(3), штаб-квартира в "
            "Сиэтле, основана в 1998 году. Региональная климатическая "
            "организация Тихоокеанского Северо-Запада США: адвокация "
            "стандартов чистой электроэнергии, декарбонизации зданий, "
            "низкоуглеродного транспорта и справедливой климатической "
            "политики в штатах Вашингтон, Орегон и далее. Программа New "
            "Energy Cities.",
            "https://www.climatesolutions.org/donate/",
            "small", date(2024, 5, 14), "4500000.00", "78.00", 1998,
            ["climate", "climate-policy"]),
    _planet("carbon180", "473221717",
            "Carbon180",
            "US nonprofit accelerating carbon-removal policy and innovation",
            "Американская НКО, ускоряющая политику и инновации по удалению CO2",
            "Carbon180 is a US 501(c)(3) headquartered in Washington, DC, "
            "founded in 2015. Climate-focused nonprofit working with "
            "policymakers, scientists and entrepreneurs to scale up carbon-"
            "removal solutions — direct air capture, soil carbon, "
            "mineralisation and bio-based pathways — through US federal and "
            "state policy and the Carbon Removal Standards Initiative.",
            "Carbon180 — американская 501(c)(3), штаб-квартира в Вашингтоне, "
            "округ Колумбия, основана в 2015 году. Климатическая НКО, "
            "работает с политиками, учёными и предпринимателями над "
            "масштабированием технологий удаления углерода — прямой захват "
            "из воздуха, почвенный углерод, минерализация, биологические "
            "пути — через федеральную и штатную политику США и инициативу "
            "Carbon Removal Standards.",
            "https://carbon180.org/donate/",
            "small", date(2024, 5, 14), "5500000.00", "82.00", 2015,
            ["carbon-removal", "climate", "climate-policy"]),
    _planet("trout-unlimited", "381612715",
            "Trout Unlimited",
            "Conserves cold-water fisheries and their watersheds",
            "Сохраняет холодноводные рыбные ресурсы и их водосборы",
            "Trout Unlimited is a US 501(c)(3) headquartered in Arlington, "
            "VA, founded in 1959 in Michigan. National network of 300,000+ "
            "members in 400+ local chapters that restore native trout and "
            "salmon habitat — removing barriers, reconnecting streams, "
            "fighting acid mine drainage in Appalachia, and defending the "
            "Bristol Bay sockeye fishery in Alaska.",
            "Trout Unlimited — американская 501(c)(3), штаб-квартира в "
            "Арлингтоне, Вирджиния, основана в 1959 году в Мичигане. "
            "Национальная сеть: 300 000+ членов в 400+ местных отделениях; "
            "восстанавливает места обитания форели и лосося — удаление "
            "плотин, восстановление связности рек, борьба с кислотными "
            "стоками шахт в Аппалачах, защита нерестилищ нерки в "
            "Бристольском заливе на Аляске.",
            "https://www.tu.org/donate/",
            "huge", date(2024, 11, 14), "98000000.00", "78.00", 1959,
            ["rivers", "watershed-protection"]),
    _planet("bonneville-environmental-foundation", "931217139",
            "Bonneville Environmental Foundation",
            "Renewable energy, watershed restoration and STEM education in the West",
            "Возобновляемая энергия, восстановление водосборов и STEM-образование",
            "Bonneville Environmental Foundation (BEF) is a US 501(c)(3) "
            "headquartered in Portland, OR, founded in 1998. Funds renewable-"
            "energy projects via Renewable Energy Certificates, runs the "
            "Model Watershed Program restoring salmon habitat across the "
            "Columbia River Basin, and equips US K-12 schools with solar "
            "panels and STEM curricula via Solar 4R Schools.",
            "Bonneville Environmental Foundation (BEF) — американская "
            "501(c)(3), штаб-квартира в Портленде, штат Орегон, основана в "
            "1998 году. Финансирует проекты возобновляемой энергии через "
            "Renewable Energy Certificates, ведёт Model Watershed Program — "
            "восстановление мест обитания лосося в бассейне реки Колумбия — "
            "и оснащает американские школы K-12 солнечными панелями и "
            "учебными программами по STEM через Solar 4R Schools.",
            "https://www.b-e-f.org/donate/",
            "small", date(2024, 5, 14), "9000000.00", "78.00", 1998,
            ["climate", "watershed-protection", "education"]),
    _planet("american-rivers", "237305963",
            "American Rivers",
            "Champions free-flowing rivers and clean water across the US",
            "Защищает свободные реки и чистую воду по США",
            "American Rivers is a US 501(c)(3) headquartered in Washington, "
            "DC, founded in 1973. Has helped remove 2,000+ outdated dams "
            "across the US, designated 12,000+ miles of Wild and Scenic "
            "Rivers, and runs the annual America's Most Endangered Rivers "
            "report focusing public attention on rivers facing critical "
            "decisions.",
            "American Rivers — американская 501(c)(3), штаб-квартира в "
            "Вашингтоне, округ Колумбия, основана в 1973 году. Помогла "
            "снести 2 000+ устаревших плотин по США, добавить 12 000+ миль "
            "к Wild and Scenic Rivers, ведёт ежегодный отчёт America's "
            "Most Endangered Rivers, привлекающий внимание к рекам перед "
            "критическими решениями.",
            "https://www.americanrivers.org/donate/",
            "large", date(2024, 11, 14), "30000000.00", "78.00", 1973,
            ["rivers", "watershed-protection"]),
    _planet("waterkeeper-alliance", "134099145",
            "Waterkeeper Alliance",
            "Connects 350+ local Waterkeeper groups defending clean water worldwide",
            "Объединяет 350+ местных групп Waterkeeper, защищающих чистую воду",
            "Waterkeeper Alliance is a US 501(c)(3) headquartered in New "
            "York, founded in 1999 by Robert F. Kennedy Jr. and a coalition "
            "of US Riverkeepers. Connects 350+ Waterkeeper member groups in "
            "47 countries — each a community-based water-protection "
            "organisation that patrols a specific waterway and litigates "
            "polluters under environmental laws.",
            "Waterkeeper Alliance — американская 501(c)(3), штаб-квартира в "
            "Нью-Йорке, основана в 1999 году Робертом Кеннеди-младшим и "
            "коалицией американских Riverkeepers. Объединяет 350+ "
            "Waterkeeper-групп в 47 странах — каждая защищает свою водную "
            "артерию: патрулирование, судебные иски против загрязнителей "
            "по природоохранному законодательству.",
            "https://waterkeeper.org/donate/",
            "medium", date(2024, 5, 14), "9000000.00", "78.00", 1999,
            ["watershed-protection", "rivers"]),
    _planet("center-for-climate-strategies", "030494889",
            "Center for Climate Strategies",
            "Helps US states design and implement climate action plans",
            "Помогает штатам США разрабатывать и внедрять планы климатических действий",
            "Center for Climate Strategies is a US 501(c)(3) headquartered "
            "in Washington, DC, founded in 2004. Provides technical analysis, "
            "facilitation and modelling that helps US state governments and "
            "national governments abroad design science-based climate-action "
            "plans — has supported 30+ US states with stakeholder-driven "
            "GHG-reduction strategies.",
            "Center for Climate Strategies — американская 501(c)(3), штаб-"
            "квартира в Вашингтоне, округ Колумбия, основана в 2004 году. "
            "Технический анализ, фасилитация и моделирование для "
            "правительств штатов США и зарубежных стран при разработке "
            "научно обоснованных планов климатических действий — поддержали "
            "30+ штатов США в стратегиях сокращения парниковых газов с "
            "участием заинтересованных сторон.",
            "https://www.climatestrategies.us/donate/",
            "small", date(2024, 5, 14), "3500000.00", "76.00", 2004,
            ["climate-policy", "climate"]),
    _planet("climate-emergency-fund", "844571679",
            "Climate Emergency Fund",
            "Resources nonviolent climate-protest movements worldwide",
            "Поддерживает ненасильственные климатические протестные движения",
            "Climate Emergency Fund is a US 501(c)(3) headquartered in Los "
            "Angeles, founded in 2019 by Trevor Neilson, Aileen Getty and "
            "Rory Kennedy. Provides grants to disruptive nonviolent climate-"
            "protest groups (Just Stop Oil, Extinction Rebellion, Last "
            "Generation, Climate Defiance) — funding the kind of social-"
            "movement infrastructure that classic environmental philanthropy "
            "doesn't reach.",
            "Climate Emergency Fund — американская 501(c)(3), штаб-квартира "
            "в Лос-Анджелесе, основана в 2019 году Тревором Нильсоном, "
            "Эйлин Гетти и Рори Кеннеди. Гранты ненасильственным "
            "разрушительным климатическим протестным группам (Just Stop "
            "Oil, Extinction Rebellion, Last Generation, Climate Defiance) "
            "— финансирование инфраструктуры социального движения, до "
            "которой не дотягивается классическая экологическая "
            "филантропия.",
            "https://www.climateemergencyfund.org/donate",
            "small", date(2024, 5, 14), "6500000.00", "82.00", 2019,
            ["climate", "climate-policy"]),
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
        "source_url": _us_pp(entry["registration_id"]),
        "source_label": "IRS Form 990, FY 2023 (ProPublica)",
    }


def _source_doc(entry: dict) -> dict:
    return {
        "kind": "irs_990",
        "filed_date": entry["last_filed_date"],
        "label": {
            "en": "IRS Form 990 (FY 2023)",
            "ru": "Налоговая форма IRS 990 (2023)",
        },
        "url": _us_pp(entry["registration_id"]),
        "source_label": "IRS Form 990 (ProPublica)",
        "file_format": "pdf",
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
                f"[migration 0031] BLOCKED {entry['slug']} "
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

    all_cause_slugs: set[str] = set(NEW_CAUSES.keys())
    for entry in SEED:
        all_cause_slugs.update(entry["cause_slugs"])
    for slug in all_cause_slugs:
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    total = Charity.objects.count()
    print(
        f"[migration 0031] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0030_backfill_v34_hero_photos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

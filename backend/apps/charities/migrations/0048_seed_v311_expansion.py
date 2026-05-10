"""v3.11 catalog expansion — seed 39 charities (368 -> ~407).

5th batch of the +300/6-session arc toward ~550 ceiling. v3.11 focus:
US disease + animal-welfare + AIDS legacy, UK homelessness + DV + LGBT+,
more CA/AU, more Italy/Spain, +Belgium +Denmark as 2 new countries.

New countries via 0047 schema migration: BE (Belgium), DK (Denmark).

Buckets:
  US (+12): JDRF (Breakthrough T1D), National MS Society, Epilepsy
    Foundation, GMHC (Gay Men's Health Crisis, AIDS legacy),
    National Wildlife Federation, Aspen Institute, First Book,
    Reading Is Fundamental, Mercy For Animals, The Humane League,
    Movember Foundation USA, American Farmland Trust.
  UK (+8): Centrepoint, Refuge, Women's Aid, National Trust, Stonewall,
    Maggie's, The Big Issue Foundation, Mermaids.
  CA (+4): Canadian Wildlife Federation, Movember Canada, Daily Bread
    Food Bank, Easterseals Canada.
  AU (+3): Movember Foundation (AU HQ), Wilderness Society Australia,
    ASRC (Asylum Seeker Resource Centre).
  IT (+3): Emergency, AVSI Foundation, Fondazione Veronesi.
  ES (+3): AECC (Asociación Española Contra el Cáncer), Manos Unidas,
    Fundación Vicente Ferrer.
  BE (+3, NEW): MSF Belgium, Caritas International Belgium, Damien
    Foundation.
  DK (+3, NEW): DanChurchAid, MSF Danmark, Mary Foundation.

Idempotent. Defensive is_blocked(). Reverse no-op.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "type-1-diabetes": {"en": "Type 1 diabetes research", "ru": "Исследования диабета 1 типа"},
    "multiple-sclerosis": {"en": "Multiple sclerosis", "ru": "Рассеянный склероз"},
    "epilepsy": {"en": "Epilepsy", "ru": "Эпилепсия"},
    "hiv-aids": {"en": "HIV / AIDS", "ru": "ВИЧ / СПИД"},
    "farm-animal-welfare": {"en": "Farm-animal welfare", "ru": "Благополучие сельскохозяйственных животных"},
    "mens-health": {"en": "Men's health", "ru": "Мужское здоровье"},
    "heritage-conservation": {"en": "Heritage conservation", "ru": "Сохранение культурного наследия"},
    "lgbtq-rights": {"en": "LGBTQ+ legal rights", "ru": "Юридические права ЛГБТ+"},
    "trans-rights": {"en": "Transgender rights & support", "ru": "Права и поддержка трансгендеров"},
    "asylum-seekers": {"en": "Asylum seekers", "ru": "Лица, ищущие убежища"},
    "leprosy": {"en": "Leprosy & neglected tropical diseases", "ru": "Проказа и забытые тропические болезни"},
}


def _verify_us(extra_en: str = "", extra_ru: str = "") -> dict:
    return {
        "en": "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 on file." + (f" {extra_en}" if extra_en else ""),
        "ru": "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 на ProPublica." + (f" {extra_ru}" if extra_ru else ""),
    }


def _verify_uk() -> dict:
    return {
        "en": "Verified: registered charity with the UK Charity Commission, annual accounts on file.",
        "ru": "Подтверждено: благотворительная организация в реестре Charity Commission UK, годовая отчётность на сайте регулятора.",
    }


def _verify_ca() -> dict:
    return {
        "en": "Verified: registered with CRA Charities Directorate; T3010 information return public.",
        "ru": "Подтверждено: зарегистрирован в CRA Charities Directorate; ежегодная декларация T3010 публична.",
    }


def _verify_au() -> dict:
    return {
        "en": "Verified: registered with ACNC; annual information statement public.",
        "ru": "Подтверждено: зарегистрирован в ACNC; ежегодное info-statement публично.",
    }


def _verify_it() -> dict:
    return {
        "en": "Verified: Italian ETS / ONLUS registered with public Bilancio Sociale.",
        "ru": "Подтверждено: итальянская ETS / ONLUS с публично доступным Bilancio Sociale.",
    }


def _verify_es() -> dict:
    return {
        "en": "Verified: registered with the Spanish Registry of NGOs; annual Cuentas Anuales public.",
        "ru": "Подтверждено: зарегистрировано в реестре НПО Испании; годовые Cuentas Anuales публичны.",
    }


def _verify_be() -> dict:
    return {
        "en": "Verified: Belgian AISBL/ASBL registered with the Crossroads Bank for Enterprises; annual accounts filed with the Belgian National Bank.",
        "ru": "Подтверждено: бельгийская AISBL/ASBL в Crossroads Bank for Enterprises; годовая отчётность в Национальном банке Бельгии.",
    }


def _verify_dk() -> dict:
    return {
        "en": "Verified: registered with the Danish Business Authority (Erhvervsstyrelsen); annual report publicly filed.",
        "ru": "Подтверждено: зарегистрировано в Erhvervsstyrelsen (Дания); годовой отчёт публично подан.",
    }


def _empty_photo() -> dict:
    return {"hero_photo_url": "", "hero_photo_caption": {"en": "", "ru": ""}, "hero_photo_credit": "", "hero_photo_license": ""}


def _us_pp(ein: str) -> str:
    return f"https://projects.propublica.org/nonprofits/organizations/{ein}"


def _uk_cc(number: str) -> str:
    return f"https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/{number}/accounts-and-annual-returns"


def E(slug, country, regid, bucket, name_en, name_ru, tagline_en, tagline_ru,
      desc_en, desc_ru, donation, revenue, program_pct, founded, last_filed,
      cause_slugs, source_url, source_kind, methodology, size="large"):
    return {
        "slug": slug, "country": country, "registration_id": regid, "bucket": bucket,
        "name": {"en": name_en, "ru": name_ru},
        "tagline": {"en": tagline_en, "ru": tagline_ru},
        "description": {"en": desc_en, "ru": desc_ru},
        "methodology_note": methodology, "logo_url": "", "donation_url": donation,
        "size_bucket": size, "last_filed_date": last_filed,
        "total_revenue_usd": Decimal(str(revenue)),
        "program_expense_pct": Decimal(str(program_pct)),
        "founded_year": founded, "cause_slugs": cause_slugs,
        **_empty_photo(),
        "source_kind": source_kind, "source_url": source_url,
    }


SEED: list[dict] = [
    # ============== US (12) ==============
    E("jdrf-breakthrough-t1d", "US", "232356733", "people",
      "Breakthrough T1D (formerly JDRF)", "Breakthrough T1D (раньше JDRF)",
      "World's largest non-profit funder of type 1 diabetes research — renamed from JDRF in 2024.",
      "Крупнейший в мире некоммерческий фондер исследований диабета 1 типа — переименован из JDRF в 2024 году.",
      "Breakthrough T1D (EIN 23-2356733, founded 1970 as Juvenile Diabetes Foundation, renamed JDRF then Breakthrough T1D in 2024) is the world's largest non-profit funder of T1D research. Has invested ~$2.5B in T1D research since founding, advocates federally for the Special Diabetes Program reauthorisation, funded the artificial-pancreas system development.",
      "Breakthrough T1D (EIN 23-2356733, основан в 1970 году как Juvenile Diabetes Foundation, переименован в JDRF, затем в Breakthrough T1D в 2024 году) — крупнейший в мире некоммерческий фондер исследований T1D. С момента основания инвестировал ~$2,5 млрд в исследования T1D, лоббирует федеральную реавторизацию Special Diabetes Program, финансировал разработку системы искусственной поджелудочной железы.",
      "https://www.breakthrought1d.org/donate/", 220000000, 80, 1970, date(2024, 6, 30),
      ["type-1-diabetes", "diabetes", "global-health"],
      _us_pp("232356733"), "irs_990", _verify_us()),

    E("national-ms-society", "US", "133143009", "people",
      "National Multiple Sclerosis Society", "National Multiple Sclerosis Society",
      "Largest US MS charity — research funding, advocacy, MS Navigator support.",
      "Крупнейшая в США организация по рассеянному склерозу — финансирование исследований, адвокация, поддержка MS Navigator.",
      "National MS Society (EIN 13-3143009, founded 1946) is the largest US MS organisation. Has invested ~$1.2B in MS research, funds clinical care via designated MS Centers, operates MS Navigator one-to-one support service, federal advocacy on disability accommodations and access to disease-modifying therapies.",
      "National MS Society (EIN 13-3143009, основан в 1946 году) — крупнейшая в США организация по РС. Инвестировал ~$1,2 млрд в исследования РС, финансирует клиническую помощь через designated MS Centers, ведёт MS Navigator (служба индивидуальной поддержки), федеральная адвокация по льготам инвалидам и доступу к препаратам, модифицирующим течение болезни.",
      "https://www.nationalmssociety.org/donate", 240000000, 79, 1946, date(2024, 12, 31),
      ["multiple-sclerosis", "global-health", "disability-services"],
      _us_pp("133143009"), "irs_990", _verify_us()),

    E("epilepsy-foundation", "US", "521275076", "people",
      "Epilepsy Foundation", "Epilepsy Foundation",
      "National US epilepsy charity — 24/7 helpline, research grants, seizure-first-aid training.",
      "Национальная организация США по эпилепсии — круглосуточная линия помощи, гранты на исследования, обучение оказанию помощи при приступах.",
      "Epilepsy Foundation (EIN 52-1275076, founded 1968) is the leading US epilepsy charity. Operates the 24/7 Epilepsy Helpline (1-800-332-1000), funds research grants and the Innovation Institute (accelerator for epilepsy tech), trains millions in Seizure First Aid via free certification, federal advocacy on Medicaid coverage of anti-seizure medications.",
      "Epilepsy Foundation (EIN 52-1275076, основан в 1968 году) — ведущая в США организация по эпилепсии. Управляет круглосуточной Epilepsy Helpline (1-800-332-1000), финансирует исследовательские гранты и Innovation Institute (акселератор технологий для эпилепсии), обучает миллионы Seizure First Aid через бесплатную сертификацию, федеральная адвокация по покрытию противоэпилептических препаратов Medicaid.",
      "https://www.epilepsy.com/get-involved/donate", 30000000, 78, 1968, date(2024, 6, 30),
      ["epilepsy", "global-health"],
      _us_pp("521275076"), "irs_990", _verify_us()),

    E("gmhc-aids", "US", "133130146", "people",
      "Gay Men's Health Crisis (GMHC)", "GMHC — Gay Men's Health Crisis",
      "World's first HIV/AIDS service organisation — NYC-area frontline care + national advocacy.",
      "Первая в мире организация помощи при ВИЧ/СПИД — фронтлайн помощь в Нью-Йорке + национальная адвокация.",
      "GMHC (EIN 13-3130146, founded 1982 by Larry Kramer and Paul Popham among others) is the world's first AIDS service organisation. Operates direct services in NYC for ~12K HIV+ clients — case management, food pantry, mental health, legal services, hot meals. National PrEP/PEP advocacy, federal Ryan White Care Act lobbying.",
      "GMHC (EIN 13-3130146, основан в 1982 году Лоуренсом Крамером, Полом Попэмом и др.) — первая в мире организация помощи при СПИД. Управляет прямыми услугами в Нью-Йорке для ~12 тыс. ВИЧ+ клиентов — case-management, продпункт, психическое здоровье, юрпомощь, горячее питание. Национальная адвокация PrEP/PEP, лоббирование Ryan White Care Act.",
      "https://www.gmhc.org/donate/", 35000000, 82, 1982, date(2024, 6, 30),
      ["hiv-aids", "lgbtq-youth", "global-health"],
      _us_pp("133130146"), "irs_990", _verify_us()),

    E("national-wildlife-federation", "US", "530204616", "planet",
      "National Wildlife Federation", "National Wildlife Federation (NWF)",
      "Largest US conservation membership org — wildlife protection, habitat, climate policy.",
      "Крупнейшая в США природоохранная членская организация — защита дикой природы, среды обитания, климатическая политика.",
      "National Wildlife Federation (EIN 53-0204616, founded 1936) is the largest US conservation membership organisation (~6M members and supporters). Federal advocacy on Endangered Species Act, Recovering America's Wildlife Act, climate; operates Schoolyard Habitats, Garden for Wildlife, and 51 state and territorial affiliates.",
      "National Wildlife Federation (EIN 53-0204616, основан в 1936 году) — крупнейшая в США природоохранная членская организация (~6 млн членов и сторонников). Федеральная адвокация Endangered Species Act, Recovering America's Wildlife Act, климат; ведёт Schoolyard Habitats, Garden for Wildlife и 51 штатовское/территориальное отделение.",
      "https://www.nwf.org/donate", 145000000, 75, 1936, date(2024, 8, 31),
      ["wildlife-conservation", "biodiversity-defense", "climate-policy"],
      _us_pp("530204616"), "irs_990", _verify_us()),

    E("aspen-institute", "US", "840399006", "people",
      "The Aspen Institute", "The Aspen Institute",
      "Non-partisan policy think-tank — leadership, programs across 30+ policy areas.",
      "Беспартийный think-tank по политике — лидерство, программы в 30+ политических областях.",
      "The Aspen Institute (EIN 84-0399006, founded 1949) is a US non-partisan policy think-tank. Operates ~30 policy programmes (financial security, communications, education, health, science & technology), the Aspen Ideas Festival, executive-leadership seminars including the Henry Crown Fellowship.",
      "The Aspen Institute (EIN 84-0399006, основан в 1949 году) — беспартийный американский think-tank по политике. Ведёт ~30 программ (финансовая безопасность, коммуникации, образование, здравоохранение, наука и технологии), Aspen Ideas Festival, семинары для руководителей в т.ч. Henry Crown Fellowship.",
      "https://www.aspeninstitute.org/give/", 165000000, 80, 1949, date(2024, 12, 31),
      ["education", "civil-rights"],
      _us_pp("840399006"), "irs_990", _verify_us()),

    E("first-book", "US", "521964419", "people",
      "First Book", "First Book",
      "Provides free and low-cost books to educators serving children in low-income communities.",
      "Предоставляет бесплатные и недорогие книги учителям, обслуживающим детей в малообеспеченных общинах.",
      "First Book (EIN 52-1964419, founded 1992) provides free and reduced-cost books, school supplies, and educational resources to educators serving children in low-income US communities. Has distributed ~250M+ books and resources via the First Book Marketplace and Network.",
      "First Book (EIN 52-1964419, основан в 1992 году) предоставляет бесплатные и сниженной стоимости книги, школьные принадлежности и образовательные ресурсы учителям, обслуживающим детей в малообеспеченных общинах США. Распространил ~250+ млн книг и ресурсов через First Book Marketplace и Network.",
      "https://firstbook.org/donate/", 30000000, 88, 1992, date(2024, 6, 30),
      ["education", "child-welfare"],
      _us_pp("521964419"), "irs_990", _verify_us()),

    E("reading-is-fundamental", "US", "521063986", "people",
      "Reading Is Fundamental (RIF)", "Reading Is Fundamental (RIF)",
      "Largest US children's literacy non-profit — distributes books to children in need.",
      "Крупнейшая в США некоммерческая организация по детской грамотности — распространяет книги нуждающимся детям.",
      "Reading Is Fundamental (EIN 52-1063986, founded 1966 by Margaret McNamara) is the largest US children's literacy non-profit. Has distributed ~430M+ books to ~40M+ children since founding. Operates Skybrary digital library, runs the Read for Success in-school literacy programme.",
      "Reading Is Fundamental (EIN 52-1063986, основан в 1966 году Маргарет МакНамарой) — крупнейшая в США некоммерческая организация по детской грамотности. С момента основания распространила ~430+ млн книг для ~40+ млн детей. Управляет цифровой библиотекой Skybrary, ведёт школьную программу грамотности Read for Success.",
      "https://www.rif.org/donate", 11000000, 80, 1966, date(2024, 6, 30),
      ["education", "child-welfare"],
      _us_pp("521063986"), "irs_990", _verify_us(), "medium"),

    E("mercy-for-animals", "US", "043348748", "animals",
      "Mercy For Animals", "Mercy For Animals",
      "Farm-animal protection through undercover investigations + corporate-policy campaigns.",
      "Защита сельскохозяйственных животных через тайные расследования и кампании по корпоративной политике.",
      "Mercy For Animals (EIN 04-3348748, founded 1999) is a leading US farm-animal protection NGO. Conducts undercover investigations of factory farms and slaughterhouses (footage frequently aired on national TV), pushes corporate-supply-chain commitments to cage-free, broiler welfare, and plant-based options. Operates in US, Brazil, India, Mexico, Canada.",
      "Mercy For Animals (EIN 04-3348748, основан в 1999 году) — ведущая в США НПО по защите сельскохозяйственных животных. Проводит тайные расследования промышленных ферм и скотобоен (кадры регулярно показывают на национальном ТВ), продвигает корпоративные обязательства цепочек поставок по cage-free, broiler welfare, plant-based опциям. Работает в США, Бразилии, Индии, Мексике, Канаде.",
      "https://mercyforanimals.org/donate/", 22000000, 79, 1999, date(2024, 12, 31),
      ["farm-animal-welfare", "animal-welfare"],
      _us_pp("043348748"), "irs_990", _verify_us(), "medium"),

    E("the-humane-league", "US", "043817491", "animals",
      "The Humane League", "The Humane League",
      "Corporate-campaigns farm-animal-welfare org — global network of country offices on cage-free pledges.",
      "Корпоративно-кампанийная организация по благополучию сельхозживотных — глобальная сеть страновых офисов по cage-free обязательствам.",
      "The Humane League (EIN 04-3817491, founded 2005) is a top-ranked Animal Charity Evaluators charity. Operates corporate-campaigns model — has secured cage-free pledges from major food companies (McDonald's, Marriott, Walmart, Burger King). Country offices in US, UK, Mexico, Japan, plus the Open Wing Alliance global network.",
      "The Humane League (EIN 04-3817491, основан в 2005 году) — топ-рейтинг Animal Charity Evaluators. Корпоративно-кампанийная модель — обеспечил cage-free обязательства от крупных пищевых компаний (McDonald's, Marriott, Walmart, Burger King). Страновые офисы в США, Великобритании, Мексике, Японии плюс глобальная сеть Open Wing Alliance.",
      "https://thehumaneleague.org/donate", 18000000, 82, 2005, date(2024, 6, 30),
      ["farm-animal-welfare", "animal-welfare"],
      _us_pp("043817491"), "irs_990", _verify_us(), "medium"),

    E("movember-foundation-us", "US", "770547104", "people",
      "Movember Foundation (US)", "Movember Foundation (US)",
      "US arm of global men's-health foundation — prostate cancer, testicular cancer, mental health.",
      "Американское отделение глобального фонда мужского здоровья — рак простаты, рак яичек, психическое здоровье.",
      "Movember Foundation US (EIN 77-0547104) is the US arm of the global Movember men's health foundation (HQ Melbourne, AU). Funds prostate cancer research, testicular cancer research, men's mental health and suicide prevention programmes. Founded in 2003 in Australia by Travis Garone and Luke Slattery. Annual November moustache-growing fundraising campaign.",
      "Movember Foundation US (EIN 77-0547104) — американское крыло глобального фонда мужского здоровья Movember (штаб-квартира в Мельбурне, Австралия). Финансирует исследования рака простаты, рака яичек, программы мужского психического здоровья и профилактики суицида. Основан в 2003 году в Австралии Трэвисом Гароном и Люком Слэттери. Ежегодная ноябрьская кампания по выращиванию усов.",
      "https://us.movember.com/donate", 28000000, 76, 2003, date(2024, 4, 30),
      ["mens-health", "cancer-research", "mental-health", "suicide-prevention"],
      _us_pp("770547104"), "irs_990", _verify_us()),

    E("american-farmland-trust", "US", "521190211", "planet",
      "American Farmland Trust", "American Farmland Trust",
      "Protects US farmland from development — conservation easements + No Farms No Food advocacy.",
      "Защищает американские сельхозземли от застройки — природоохранные сервитуты + кампания No Farms No Food.",
      "American Farmland Trust (EIN 52-1190211, founded 1980) is the leading US organisation protecting farmland from non-agricultural development. Helps farmers and ranchers protect their land via conservation easements, advocates federally for the Agricultural Conservation Easement Program, runs Brighter Future Fund grants for farmers facing financial hardship.",
      "American Farmland Trust (EIN 52-1190211, основан в 1980 году) — ведущая в США организация по защите сельскохозяйственных земель от несельскохозяйственного освоения. Помогает фермерам и ранчерам защитить землю через природоохранные сервитуты, лоббирует федеральную Agricultural Conservation Easement Program, ведёт гранты Brighter Future Fund для фермеров в финансовых трудностях.",
      "https://farmland.org/donate/", 23000000, 81, 1980, date(2024, 6, 30),
      ["conservation", "biodiversity-defense"],
      _us_pp("521190211"), "irs_990", _verify_us(), "medium"),

    # ============== UK (8) ==============
    E("centrepoint", "GB", "292411", "people",
      "Centrepoint", "Centrepoint — UK молодёжная бездомность",
      "UK's leading youth homelessness charity — supports homeless 16-25 year olds.",
      "Ведущая британская организация по молодёжной бездомности — поддерживает бездомных 16-25 лет.",
      "Centrepoint (Charity Commission #292411, founded 1969) is the UK's leading youth homelessness charity, specifically for people aged 16-25. Provides emergency accommodation, support to find a job and home, mental health support, and a Centrepoint Helpline. Patron HRH The Prince of Wales (William). ~14K young people supported annually.",
      "Centrepoint (Charity Commission #292411, основан в 1969 году) — ведущая в Великобритании организация по молодёжной бездомности, специально для людей 16-25 лет. Обеспечивает экстренное жильё, поддержку в поиске работы и дома, помощь в области психического здоровья, ведёт Centrepoint Helpline. Покровитель HRH принц Уэльский (Уильям). ~14 тыс. молодых людей получают поддержку ежегодно.",
      "https://centrepoint.org.uk/donate", 35000000, 79, 1969, date(2024, 3, 31),
      ["homelessness", "youth-mentoring", "child-welfare"],
      _uk_cc("292411"), "annual_report", _verify_uk()),

    E("refuge-uk", "GB", "277424", "people",
      "Refuge", "Refuge — UK организация против домашнего насилия",
      "UK's largest domestic-abuse charity — runs the National Domestic Abuse Helpline.",
      "Крупнейшая в Великобритании организация против домашнего насилия — ведёт National Domestic Abuse Helpline.",
      "Refuge (Charity Commission #277424, founded 1971) is the UK's largest domestic-abuse charity. Operates the freephone, 24/7 National Domestic Abuse Helpline (0808 2000 247), runs ~50 refuges and other accommodation-based services across England, supports ~24K women, children and men experiencing domestic abuse each day, federal advocacy on the Domestic Abuse Act and migrant-women rights.",
      "Refuge (Charity Commission #277424, основан в 1971 году) — крупнейшая в Великобритании организация против домашнего насилия. Управляет бесплатной круглосуточной National Domestic Abuse Helpline (0808 2000 247), ведёт ~50 убежищ и других услуг по проживанию по всей Англии, поддерживает ~24 тыс. женщин, детей и мужчин, переживающих домашнее насилие ежедневно, федеральная адвокация Domestic Abuse Act и прав мигрантов-женщин.",
      "https://www.refuge.org.uk/get-help-from-refuge/donate-to-refuge/", 35000000, 86, 1971, date(2024, 3, 31),
      ["domestic-violence", "womens-rights"],
      _uk_cc("277424"), "annual_report", _verify_uk()),

    E("womens-aid-uk", "GB", "1054154", "people",
      "Women's Aid Federation of England", "Women's Aid Federation of England",
      "Federation of ~170 specialist domestic-abuse services across England — federal advocacy + Live Chat.",
      "Федерация ~170 специализированных служб домашнего насилия по всей Англии — федеральная адвокация + Live Chat.",
      "Women's Aid Federation of England (Charity Commission #1054154, founded 1974) is the national federation of ~170 specialist domestic-abuse organisations across England. Runs Women's Aid Live Chat support service, Survivors Forum, federal-policy advocacy that led to passage of the Domestic Abuse Act 2021.",
      "Women's Aid Federation of England (Charity Commission #1054154, основан в 1974 году) — национальная федерация ~170 специализированных организаций по борьбе с домашним насилием по всей Англии. Ведёт службу поддержки Women's Aid Live Chat, Survivors Forum, федеральную адвокацию политики, приведшую к принятию Domestic Abuse Act 2021.",
      "https://www.womensaid.org.uk/donate/", 12000000, 80, 1974, date(2024, 3, 31),
      ["domestic-violence", "womens-rights"],
      _uk_cc("1054154"), "annual_report", _verify_uk(), "medium"),

    E("national-trust-uk", "GB", "205846", "planet",
      "National Trust", "National Trust UK",
      "UK's largest heritage and conservation charity — historic houses, gardens, coast, countryside.",
      "Крупнейшая в Великобритании организация по культурному наследию и охране природы — исторические дома, сады, побережье, сельская местность.",
      "National Trust for Places of Historic Interest or Natural Beauty (Charity Commission #205846, founded 1895) is the UK's largest conservation charity by membership (~5.4M members). Cares for 500+ historic houses, castles, gardens, parks, plus ~250K hectares of land and ~780 miles of coastline across England, Wales and Northern Ireland.",
      "National Trust for Places of Historic Interest or Natural Beauty (Charity Commission #205846, основан в 1895 году) — крупнейшая в Великобритании природоохранная организация по числу членов (~5,4 млн). Заботится о 500+ исторических домах, замках, садах, парках, плюс ~250 тыс. гектаров земли и ~780 миль побережья в Англии, Уэльсе и Северной Ирландии.",
      "https://www.nationaltrust.org.uk/donate", 800000000, 85, 1895, date(2024, 2, 29),
      ["heritage-conservation", "conservation", "biodiversity-defense"],
      _uk_cc("205846"), "annual_report", _verify_uk()),

    E("stonewall-uk", "GB", "1101255", "people",
      "Stonewall", "Stonewall — британская правозащитная организация ЛГБТ+",
      "UK LGBTQ+ rights and equality charity — Workplace Equality Index, education, family services.",
      "Британская правозащитная организация ЛГБТ+ — Workplace Equality Index, образование, услуги для семей.",
      "Stonewall (Charity Commission #1101255, founded 1989 in response to Section 28) is the UK's leading LGBTQ+ rights and equality charity. Runs the Workplace Equality Index assessing ~500 UK employers, Stonewall School Champions programme, lobbies federally on conversion-therapy ban, trans rights, and same-sex parenting recognition.",
      "Stonewall (Charity Commission #1101255, основан в 1989 году в ответ на Section 28) — ведущая в Великобритании правозащитная организация ЛГБТ+. Ведёт Workplace Equality Index, оценивающий ~500 британских работодателей, программу Stonewall School Champions, лоббирует на федеральном уровне запрет конверсионной терапии, права трансгендеров и признание однополого родительства.",
      "https://www.stonewall.org.uk/donate", 9500000, 76, 1989, date(2024, 3, 31),
      ["lgbtq-rights", "civil-rights"],
      _uk_cc("1101255"), "annual_report", _verify_uk(), "medium"),

    E("maggies-cancer", "GB", "1058460", "people",
      "Maggie's Centres", "Maggie's Centres — британские онкологические центры поддержки",
      "Free practical, emotional and social support for people with cancer + families — distinctive architect-designed centres.",
      "Бесплатная практическая, эмоциональная и социальная поддержка для людей с раком и их семей — отличительные центры, спроектированные ведущими архитекторами.",
      "Maggie's (Charity Commission #1058460, founded 1996 in memory of Maggie Keswick Jencks) runs 24 cancer-support centres across the UK plus 1 in Tokyo, 1 in Hong Kong, 1 in Barcelona. Centres are deliberately architecturally distinctive — designed by leading architects (Norman Foster, Rem Koolhaas, Frank Gehry, Zaha Hadid). Free drop-in psychological, financial and practical support for anyone with cancer + family.",
      "Maggie's (Charity Commission #1058460, основан в 1996 году в память о Мэгги Кесвик Дженкс) управляет 24 онкоцентрами поддержки в Великобритании плюс 1 в Токио, 1 в Гонконге, 1 в Барселоне. Центры намеренно архитектурно отличительные — спроектированы ведущими архитекторами (Норман Фостер, Рем Колхас, Фрэнк Гери, Заха Хадид). Бесплатная drop-in психологическая, финансовая и практическая поддержка для всех с раком и их семей.",
      "https://www.maggies.org/donate/", 32000000, 78, 1996, date(2024, 3, 31),
      ["cancer-research", "mental-health"],
      _uk_cc("1058460"), "annual_report", _verify_uk()),

    E("big-issue-foundation", "GB", "1049077", "people",
      "The Big Issue Foundation", "The Big Issue Foundation",
      "Supports Big Issue magazine vendors — homeless and vulnerably-housed people earning legitimate income.",
      "Поддерживает продавцов журнала Big Issue — бездомных и людей в нестабильном жилье, зарабатывающих легальный доход.",
      "The Big Issue Foundation (Charity Commission #1049077, founded 1995) is the charity arm of The Big Issue street-paper enterprise. Provides case-managed support to Big Issue vendors with housing, mental health, addictions, employment, and immigration legal advice. Vendors buy the magazine wholesale and sell at retail, earning legitimate income.",
      "The Big Issue Foundation (Charity Commission #1049077, основан в 1995 году) — благотворительное крыло предприятия street-paper The Big Issue. Обеспечивает case-managed поддержку продавцам Big Issue по жилью, психическому здоровью, зависимостям, трудоустройству, иммиграционной юрпомощи. Продавцы покупают журнал оптом и продают в розницу, зарабатывая легальный доход.",
      "https://www.bigissue.org.uk/get-involved/donate/", 5000000, 78, 1995, date(2024, 3, 31),
      ["homelessness", "poverty-reduction"],
      _uk_cc("1049077"), "annual_report", _verify_uk(), "medium"),

    E("mermaids-trans-uk", "GB", "1160575", "people",
      "Mermaids", "Mermaids — UK поддержка трансгендерных детей и молодёжи",
      "UK charity supporting transgender, non-binary and gender-diverse children, young people and their families.",
      "Британская благотворительная организация, поддерживающая трансгендерных, небинарных и гендерно-разнообразных детей, молодёжь и их семей.",
      "Mermaids (Charity Commission #1160575, founded 1995) supports transgender, non-binary and gender-diverse children and young people (under 25) and their families. Operates a free Helpline, Webchat, peer-support groups for parents, training for professionals (teachers, doctors). Patrons include Lemn Sissay and Stephen Fry.",
      "Mermaids (Charity Commission #1160575, основан в 1995 году) поддерживает трансгендерных, небинарных и гендерно-разнообразных детей и молодёжь (до 25 лет) и их семей. Управляет бесплатной Helpline, Webchat, группами поддержки для родителей, обучением для профессионалов (учителей, врачей). Покровители: Лемн Сиссей и Стивен Фрай.",
      "https://mermaidsuk.org.uk/donate/", 4500000, 75, 1995, date(2024, 3, 31),
      ["trans-rights", "lgbtq-youth", "child-welfare"],
      _uk_cc("1160575"), "annual_report", _verify_uk(), "medium"),

    # ============== Canada (4) ==============
    E("canadian-wildlife-federation", "CA", "10684-6764-RR0001", "planet",
      "Canadian Wildlife Federation", "Canadian Wildlife Federation",
      "Largest Canadian non-government wildlife conservation org — habitat restoration, species recovery.",
      "Крупнейшая канадская негосударственная организация по охране дикой природы — восстановление мест обитания, восстановление видов.",
      "Canadian Wildlife Federation (CRA #10684-6764-RR0001, founded 1962) is Canada's largest non-government wildlife-conservation organisation. Focus areas: at-risk species recovery (caribou, monarch butterflies, freshwater fish), habitat restoration, citizen-science via the WILD Education programme, federal-policy advocacy on the Species at Risk Act.",
      "Canadian Wildlife Federation (CRA #10684-6764-RR0001, основан в 1962 году) — крупнейшая канадская негосударственная организация по охране дикой природы. Ключевые направления: восстановление видов под угрозой (карибу, бабочки-монархи, пресноводная рыба), восстановление мест обитания, citizen-science через программу WILD Education, федеральная адвокация Species at Risk Act.",
      "https://cwf-fcf.org/en/give/", 18000000, 78, 1962, date(2024, 3, 31),
      ["wildlife-conservation", "biodiversity-defense", "conservation"],
      "https://cwf-fcf.org/en/about/finances/", "annual_report", _verify_ca()),

    E("movember-canada", "CA", "84717-8378-RR0001", "people",
      "Movember Canada", "Movember Canada",
      "Canadian arm of global men's-health foundation — prostate cancer, mental health, suicide prevention.",
      "Канадское отделение глобального фонда мужского здоровья — рак простаты, психическое здоровье, профилактика суицидов.",
      "Movember Canada (CRA #84717-8378-RR0001) is the Canadian arm of the global Movember foundation. Funds Movember-Prostate Cancer Canada research consortium, Mind Pulse Check men's mental-health initiative, and Movember Conversations (training Canadians to have hard conversations with men about mental health).",
      "Movember Canada (CRA #84717-8378-RR0001) — канадское крыло глобального фонда Movember. Финансирует консорциум исследований Movember-Prostate Cancer Canada, инициативу Mind Pulse Check по мужскому психическому здоровью, Movember Conversations (обучение канадцев вести трудные разговоры о психическом здоровье с мужчинами).",
      "https://ca.movember.com/donate", 14000000, 78, 2007, date(2024, 4, 30),
      ["mens-health", "cancer-research", "mental-health"],
      "https://ca.movember.com/about-us/financials", "annual_report", _verify_ca(), "medium"),

    E("daily-bread-toronto", "CA", "11892-2533-RR0001", "people",
      "Daily Bread Food Bank", "Daily Bread Food Bank — Toronto",
      "Largest food bank in Toronto + Greater Toronto Area — supplies ~200 member agencies.",
      "Крупнейший продбанк в Торонто и Greater Toronto Area — поставляет ~200 агентствам-членам.",
      "Daily Bread Food Bank (CRA #11892-2533-RR0001, founded 1983) is the largest food bank in Toronto. Provides fresh and shelf-stable food to ~200 member food banks, meal programmes and shelters across the GTA. Distributing food to record-high client visits (~3M visits/year as of 2024) due to Canadian cost-of-living crisis.",
      "Daily Bread Food Bank (CRA #11892-2533-RR0001, основан в 1983 году) — крупнейший продбанк в Торонто. Обеспечивает свежую и долгохранящуюся еду ~200 продбанкам-членам, программам питания и приютам в GTA. Распределяет еду в рекордные посещения клиентами (~3 млн посещений/год по состоянию на 2024 год) из-за канадского кризиса стоимости жизни.",
      "https://www.dailybread.ca/donate/", 45000000, 87, 1983, date(2024, 3, 31),
      ["food-banks", "hunger", "poverty-reduction"],
      "https://www.dailybread.ca/about-us/financials/", "annual_report", _verify_ca()),

    E("easterseals-canada", "CA", "10683-9233-RR0001", "people",
      "Easter Seals Canada", "Easter Seals Canada",
      "National federation supporting Canadians living with disabilities — equipment, programmes, advocacy.",
      "Национальная федерация, поддерживающая канадцев с инвалидностью — оборудование, программы, адвокация.",
      "Easter Seals Canada (CRA #10683-9233-RR0001, founded 1922) is the national federation of provincial Easter Seals societies serving people living with disabilities. Provides assistive equipment, accessible summer camps, life-skills programmes, post-secondary scholarships, and federal-policy advocacy on the Accessible Canada Act.",
      "Easter Seals Canada (CRA #10683-9233-RR0001, основан в 1922 году) — национальная федерация провинциальных обществ Easter Seals, обслуживающих людей с инвалидностью. Обеспечивает вспомогательное оборудование, доступные летние лагеря, программы жизненных навыков, послешкольные стипендии, федеральную адвокацию Accessible Canada Act.",
      "https://easterseals.ca/donate/", 3500000, 76, 1922, date(2024, 3, 31),
      ["disability-services"],
      "https://easterseals.ca/about-us/financials/", "annual_report", _verify_ca(), "medium"),

    # ============== Australia (3) ==============
    E("movember-foundation-au", "AU", "ABN-48-894-537-905", "people",
      "Movember Foundation", "Movember Foundation — глобальный фонд мужского здоровья",
      "Global men's-health foundation HQ — moustache-grown fundraising for prostate, testicular cancer and mental health.",
      "Глобальный штаб фонда мужского здоровья — фандрайзинг с выращиванием усов на исследования рака простаты, яичек и психического здоровья.",
      "Movember Foundation (ABN 48 894 537 905, founded 2003 in Melbourne by Travis Garone and Luke Slattery) is the global headquarters of the Movember men's-health movement. Funds ~$190M of research and programmes globally on prostate cancer, testicular cancer, and men's mental health & suicide prevention through national chapters in 20+ countries.",
      "Movember Foundation (ABN 48 894 537 905, основан в 2003 году в Мельбурне Трэвисом Гароном и Люком Слэттери) — глобальный штаб движения Movember за мужское здоровье. Финансирует ~$190 млн в год исследований и программ в мире по раку простаты, раку яичек, мужскому психическому здоровью и профилактике суицидов через национальные отделения в 20+ странах.",
      "https://au.movember.com/donate", 130000000, 79, 2003, date(2024, 4, 30),
      ["mens-health", "cancer-research", "mental-health", "suicide-prevention"],
      "https://au.movember.com/about/financials", "annual_report", _verify_au()),

    E("wilderness-society-australia", "AU", "ABN-39-411-433-094", "planet",
      "The Wilderness Society", "The Wilderness Society — Australia",
      "Australia's leading wilderness-conservation advocacy NGO — forests, climate, land-clearing.",
      "Ведущая в Австралии природоохранная организация — защита лесов, климат, расчистка земель.",
      "The Wilderness Society (ABN 39 411 433 094, founded 1976 in response to the Franklin River dam proposal in Tasmania) is one of Australia's leading wilderness-conservation NGOs. Campaigns to stop land-clearing, protect old-growth forests in Tasmania and the Great Western Woodlands, federal climate-policy advocacy. Refuses corporate funding to maintain independence.",
      "The Wilderness Society (ABN 39 411 433 094, основан в 1976 году в ответ на предложение плотины на реке Франклин в Тасмании) — одна из ведущих природоохранных НПО Австралии. Кампании по прекращению расчистки земель, защите старовозрастных лесов в Тасмании и Great Western Woodlands, федеральная адвокация климатической политики. Отказывается от корпоративного финансирования для сохранения независимости.",
      "https://www.wilderness.org.au/donate", 13000000, 76, 1976, date(2024, 6, 30),
      ["forest-protection", "climate-policy", "conservation"],
      "https://www.wilderness.org.au/about-us/our-finances", "annual_report", _verify_au(), "medium"),

    E("asrc-refugee", "AU", "ABN-71-095-068-411", "people",
      "Asylum Seeker Resource Centre (ASRC)", "Asylum Seeker Resource Centre (ASRC)",
      "Australia's largest asylum-seeker support org — Melbourne-based, ~7K people supported.",
      "Крупнейшая в Австралии организация поддержки лиц, ищущих убежища — Мельбурн, ~7 тыс. человек получают помощь.",
      "Asylum Seeker Resource Centre (ABN 71 095 068 411, founded 2001 by Kon Karapanagiotidis) is the largest asylum-seeker support organisation in Australia. Provides ~40 services to ~7K asylum seekers per year — legal aid, food bank, housing, employment, health (in-house clinic), education. Independent of government funding; explicitly refuses Australian federal-government grants.",
      "Asylum Seeker Resource Centre (ABN 71 095 068 411, основан в 2001 году Коном Карапанагиотидисом) — крупнейшая в Австралии организация поддержки лиц, ищущих убежища. Обеспечивает ~40 услуг для ~7 тыс. лиц, ищущих убежища, в год — юрпомощь, продбанк, жильё, трудоустройство, здравоохранение (внутренняя клиника), образование. Независим от государственного финансирования; принципиально отказывается от грантов федерального правительства Австралии.",
      "https://asrc.org.au/donate/", 17000000, 84, 2001, date(2024, 6, 30),
      ["asylum-seekers", "refugees", "humanitarian-medicine"],
      "https://asrc.org.au/about/financials/", "annual_report", _verify_au(), "medium"),

    # ============== Italy (3) ==============
    E("emergency-italy", "IT", "IT-97147110155", "people",
      "Emergency", "Emergency — итальянская гуманитарная медицина",
      "Italian humanitarian-medicine NGO — free surgery, war victims and civilian medical care globally.",
      "Итальянская гуманитарно-медицинская НПО — бесплатная хирургия, помощь жертвам войны и гражданским в мире.",
      "Emergency (C.F. 97147110155, founded 1994 by Gino Strada and Teresa Sarti in Milan) provides free, high-quality medical and surgical treatment to victims of war, landmines and poverty. Operates hospitals and surgical centres in Afghanistan, Sierra Leone, Sudan, Iraq, Italy. Anti-war advocacy on humanitarian grounds. Iconic among Italian humanitarian organisations.",
      "Emergency (C.F. 97147110155, основана в 1994 году Джино Страдой и Терезой Сарти в Милане) обеспечивает бесплатное, высококачественное медицинское и хирургическое лечение жертвам войны, мин и бедности. Управляет больницами и хирургическими центрами в Афганистане, Сьерра-Леоне, Судане, Ираке, Италии. Антивоенная адвокация на гуманитарной основе. Знаковая среди итальянских гуманитарных организаций.",
      "https://www.emergency.it/dona-ora/", 130000000, 86, 1994, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response"],
      "https://www.emergency.it/chi-siamo/bilancio-sociale-2023/", "annual_report", _verify_it()),

    E("avsi-italy", "IT", "IT-01059510406", "people",
      "Fondazione AVSI", "Fondazione AVSI",
      "Italian Catholic development NGO — works in ~33 countries on cooperazione e sviluppo.",
      "Итальянская католическая организация развития — работает в ~33 странах по cooperazione e sviluppo.",
      "Fondazione AVSI (C.F. 01059510406, founded 1972) is a Catholic Italian international development NGO. Works in ~33 countries on education access, child sponsorship, food security, sustainable agriculture, and humanitarian response. Implementing partner of EU, USAID, Italian Cooperation, and others.",
      "Fondazione AVSI (C.F. 01059510406, основан в 1972 году) — католическая итальянская организация международного развития. Работает в ~33 странах: доступ к образованию, спонсорство детей, продовольственная безопасность, устойчивое сельское хозяйство, гуманитарное реагирование. Имплементирующий партнёр ЕС, USAID, Italian Cooperation и других.",
      "https://www.avsi.org/it/page/sostieni-avsi/120", 90000000, 88, 1972, date(2023, 12, 31),
      ["faith-based", "humanitarian-medicine", "child-welfare"],
      "https://www.avsi.org/it/page/bilancio-sociale/", "annual_report", _verify_it()),

    E("veronesi-italy", "IT", "IT-03457800163", "people",
      "Fondazione Umberto Veronesi", "Fondazione Umberto Veronesi",
      "Italian cancer-research foundation founded by oncologist Umberto Veronesi — grants for Italian researchers.",
      "Итальянский фонд онкологических исследований, основанный онкологом Умберто Веронези — гранты для итальянских исследователей.",
      "Fondazione Umberto Veronesi (C.F. 03457800163, founded 2003 by Italian oncologist Umberto Veronesi) funds Italian medical and scientific research. Awards ~250 research grants per year to early-career Italian researchers in oncology, cardiology, neuroscience, and nutrition science. Iconic Italian scientific philanthropy organisation.",
      "Fondazione Umberto Veronesi (C.F. 03457800163, основан в 2003 году итальянским онкологом Умберто Веронези) финансирует итальянские медицинские и научные исследования. Выдаёт ~250 исследовательских грантов в год итальянским исследователям ранней карьеры в онкологии, кардиологии, нейронауках, нутрициологии. Знаковая итальянская организация научной филантропии.",
      "https://www.fondazioneveronesi.it/dona-ora", 18000000, 85, 2003, date(2023, 12, 31),
      ["cancer-research", "global-health"],
      "https://www.fondazioneveronesi.it/chi-siamo/bilancio-sociale", "annual_report", _verify_it(), "medium"),

    # ============== Spain (3) ==============
    E("aecc-spain", "ES", "ES-G28197564", "people",
      "Asociación Española Contra el Cáncer (AECC)", "AECC — Asociación Española Contra el Cáncer",
      "Spain's largest cancer charity — research funding, patient support, prevention.",
      "Крупнейшая в Испании онкологическая организация — финансирование исследований, поддержка пациентов, профилактика.",
      "AECC (NIF G28197564, founded 1953) is Spain's largest cancer charity. Funds research through Fundación Científica AECC (~€100M of grants since 2017), provides free patient services (psychological, social, palliative care) across 52 provincial branches, runs prevention campaigns and the AECC Cancer Helpline.",
      "AECC (NIF G28197564, основан в 1953 году) — крупнейшая в Испании онкологическая благотворительная организация. Финансирует исследования через Fundación Científica AECC (~€100 млн грантов с 2017 года), обеспечивает бесплатные услуги пациентам (психологические, социальные, паллиативные) в 52 провинциальных отделениях, ведёт профилактические кампании и AECC Cancer Helpline.",
      "https://www.contraelcancer.es/es/donaciones", 130000000, 84, 1953, date(2023, 12, 31),
      ["cancer-research", "global-health"],
      "https://www.contraelcancer.es/es/sobre-nosotros/transparencia/cuentas-anuales", "annual_report", _verify_es()),

    E("manos-unidas", "ES", "ES-G28567790", "people",
      "Manos Unidas", "Manos Unidas",
      "Spanish Catholic Bishops' development agency — funds projects in Africa, Asia and the Americas.",
      "Испанское католическое епископское агентство развития — финансирует проекты в Африке, Азии и Америке.",
      "Manos Unidas (NIF G28567790, founded 1959) is the official development agency of the Spanish Episcopal Conference. Funds local-partner projects across ~50 countries in Africa, Asia and the Americas in agriculture, water and sanitation, education, women's empowerment, health. Iconic annual February-Sunday fundraising appeal in Spanish parishes.",
      "Manos Unidas (NIF G28567790, основан в 1959 году) — официальное агентство развития Испанской епископальной конференции. Финансирует проекты местных партнёров в ~50 странах в Африке, Азии и Америке: сельское хозяйство, вода и санитария, образование, расширение прав женщин, здравоохранение. Знаковый ежегодный фандрайзинг в феврале в испанских приходах.",
      "https://www.manosunidas.org/colabora", 60000000, 87, 1959, date(2023, 12, 31),
      ["faith-based", "humanitarian-medicine", "poverty-reduction"],
      "https://www.manosunidas.org/transparencia", "annual_report", _verify_es()),

    E("vicente-ferrer-foundation", "ES", "ES-G09326745", "people",
      "Fundación Vicente Ferrer (RDT India)", "Fundación Vicente Ferrer — индийская работа в развитии",
      "Spanish foundation working in rural Andhra Pradesh, India — disability, women, water, agriculture.",
      "Испанский фонд, работающий в сельской Андхра-Прадеш, Индия — инвалидность, женщины, вода, сельское хозяйство.",
      "Fundación Vicente Ferrer (NIF G09326745, founded 1996 by Spanish-Indian humanitarian Vicente Ferrer; he died 2009) works exclusively in rural Andhra Pradesh, India through implementing partner RDT India. ~2.5M direct beneficiaries on disability-rights work, women's self-help groups, child education, water/sanitation, and rural-agriculture support.",
      "Fundación Vicente Ferrer (NIF G09326745, основан в 1996 году испанско-индийским гуманитаристом Висенте Феррером; он умер в 2009 году) работает исключительно в сельской Андхра-Прадеш, Индия, через имплементирующего партнёра RDT India. ~2,5 млн прямых бенефициаров: работа по правам инвалидов, женские группы самопомощи, образование детей, вода/санитария, поддержка сельского хозяйства.",
      "https://www.fundacionvicenteferrer.org/colabora", 47000000, 87, 1996, date(2023, 12, 31),
      ["disability-services", "womens-rights", "poverty-reduction"],
      "https://www.fundacionvicenteferrer.org/transparencia", "annual_report", _verify_es()),

    # ============== Belgium (3 — NEW country) ==============
    E("msf-belgium", "BE", "BE-0421-446-100", "people",
      "Médecins Sans Frontières (Operational Centre Brussels)", "MSF Belgium — Operational Centre Brussels",
      "Brussels-based operational centre of MSF — major surgical and medical operations in 30+ countries.",
      "Брюссельский операционный центр MSF — крупные хирургические и медицинские операции в 30+ странах.",
      "MSF Belgium / Operational Centre Brussels (BE 0421.446.100, founded 1980) is one of five MSF operational centres responsible for direct medical operations on the ground. Runs major surgical projects in DR Congo, Sudan, CAR, Niger, Yemen. Belgium is also home to the MSF International Office.",
      "MSF Belgium / Operational Centre Brussels (BE 0421.446.100, основан в 1980 году) — один из пяти операционных центров MSF, отвечающих за прямые медицинские операции на местах. Ведёт крупные хирургические проекты в ДРК, Судане, ЦАР, Нигере, Йемене. Бельгия также является домом для MSF International Office.",
      "https://www.msf-azg.be/nl/doneer", 320000000, 89, 1980, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response"],
      "https://www.msf-azg.be/nl/over-ons/financien", "annual_report", _verify_be()),

    E("caritas-international-be", "BE", "BE-0408-825-141", "people",
      "Caritas International Belgium", "Caritas International — бельгийское отделение",
      "Belgian Caritas member working internationally on refugees and humanitarian response.",
      "Бельгийский член Caritas, работающий международно по беженцам и гуманитарному реагированию.",
      "Caritas International Belgium (BE 0408.825.141, founded 1932) is the Belgian member of the global Caritas confederation. Focus on refugees (Belgium operates one of the largest per-capita asylum systems in Europe), international emergency response in ~25 countries, and migration policy advocacy at EU level.",
      "Caritas International Belgium (BE 0408.825.141, основан в 1932 году) — бельгийский член глобальной конфедерации Caritas. Фокус на беженцах (Бельгия имеет одну из крупнейших на душу населения систем убежища в Европе), международном экстренном реагировании в ~25 странах, адвокации миграционной политики на уровне ЕС.",
      "https://www.caritasinternational.be/fr/faire-un-don/", 45000000, 84, 1932, date(2023, 12, 31),
      ["faith-based", "refugees", "humanitarian-medicine"],
      "https://www.caritasinternational.be/fr/qui-sommes-nous/transparence-financiere/", "annual_report", _verify_be()),

    E("damien-foundation", "BE", "BE-0410-665-263", "people",
      "Damien Foundation", "Damien Foundation — бельгийская организация по борьбе с проказой",
      "Belgian NGO fighting leprosy, tuberculosis and other neglected tropical diseases in 14 countries.",
      "Бельгийская НПО, борющаяся с проказой, туберкулёзом и забытыми тропическими болезнями в 14 странах.",
      "Damien Foundation (BE 0410.665.263, founded 1964, named after Saint Damien of Molokai who served leprosy patients in Hawaii) fights leprosy, tuberculosis and other neglected tropical diseases in 14 countries (Bangladesh, India, Indonesia, DRC, Nigeria, Niger and others). Treats ~250K patients annually. Runs the iconic Belgian annual marker-pen campaign (Damienactie).",
      "Damien Foundation (BE 0410.665.263, основан в 1964 году, назван в честь Святого Дамиена де Молокая, обслуживавшего больных проказой на Гавайях) борется с проказой, туберкулёзом и забытыми тропическими болезнями в 14 странах (Бангладеш, Индия, Индонезия, ДРК, Нигерия, Нигер и др.). Лечит ~250 тыс. пациентов ежегодно. Ведёт знаковую бельгийскую ежегодную кампанию маркеров (Damienactie).",
      "https://www.damiaanactie.be/nl/doneer", 25000000, 88, 1964, date(2023, 12, 31),
      ["leprosy", "global-health", "humanitarian-medicine"],
      "https://www.damiaanactie.be/nl/over-ons/financien", "annual_report", _verify_be()),

    # ============== Denmark (3 — NEW country) ==============
    E("danchurchaid", "DK", "DK-CVR-15197718", "people",
      "Folkekirkens Nødhjælp (DanChurchAid)", "Folkekirkens Nødhjælp — DanChurchAid",
      "Danish ecumenical humanitarian NGO — emergency response, livelihoods, peacebuilding.",
      "Датская экуменическая гуманитарная НПО — экстренное реагирование, средства к существованию, миростроительство.",
      "DanChurchAid / Folkekirkens Nødhjælp (CVR 15 19 77 18, founded 1922) is one of Denmark's leading humanitarian NGOs. Works in ~25 countries on emergency response (Ukraine, Syria, Sudan, Yemen), demining and unexploded-ordnance clearance, food security, climate adaptation. Co-runs the Mine Action Group network.",
      "DanChurchAid / Folkekirkens Nødhjælp (CVR 15 19 77 18, основан в 1922 году) — одна из ведущих датских гуманитарных НПО. Работает в ~25 странах: экстренное реагирование (Украина, Сирия, Судан, Йемен), разминирование и обезвреживание неразорвавшихся боеприпасов, продовольственная безопасность, климатическая адаптация. Соведущий сети Mine Action Group.",
      "https://www.danchurchaid.org/donate", 100000000, 88, 1922, date(2023, 12, 31),
      ["faith-based", "humanitarian-medicine", "emergency-response"],
      "https://www.danchurchaid.org/about-us/financial-information", "annual_report", _verify_dk()),

    E("msf-danmark", "DK", "DK-CVR-18269204", "people",
      "Læger uden Grænser (MSF Denmark)", "Læger uden Grænser — MSF Denmark",
      "Danish section of the international MSF movement — recruits Danish medical staff, raises funds.",
      "Датская секция международного движения MSF — набирает датский медперсонал, собирает средства.",
      "Læger uden Grænser / MSF Denmark (CVR 18 26 92 04) is the Danish section of the international MSF movement. Recruits Danish medical, paramedical and logistical personnel for MSF field missions worldwide, fundraises in Denmark.",
      "Læger uden Grænser / MSF Denmark (CVR 18 26 92 04) — датская секция международного движения MSF. Набирает датский медицинский, парамедицинский и логистический персонал для полевых миссий MSF по всему миру, собирает средства в Дании.",
      "https://msf.dk/stoet/", 60000000, 89, 1993, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response"],
      "https://msf.dk/om-os/aarsrapport/", "annual_report", _verify_dk()),

    E("mary-foundation", "DK", "DK-CVR-30506960", "people",
      "Mary Foundation", "Mary Foundation — фонд королевы Дании Мэри",
      "Danish royal foundation working on bullying, domestic violence, and loneliness.",
      "Датский королевский фонд, работающий по теме буллинга, домашнего насилия и одиночества.",
      "Mary Foundation (CVR 30 50 69 60, founded 2007 by then-Crown Princess Mary of Denmark) tackles social isolation through three programmes: Free of Bullying (anti-bullying in early-years and primary schools), Break the Pattern (domestic violence response), Friend at the Workplace (loneliness reduction). Mary became Queen of Denmark in January 2024.",
      "Mary Foundation (CVR 30 50 69 60, основан в 2007 году тогда кронпринцессой Дании Мэри) борется с социальной изоляцией через три программы: Free of Bullying (антибуллинг в детских садах и начальных школах), Break the Pattern (реакция на домашнее насилие), Friend at the Workplace (уменьшение одиночества). Мэри стала королевой Дании в январе 2024 года.",
      "https://maryfonden.dk/stoet/", 8000000, 84, 2007, date(2023, 12, 31),
      ["child-protection", "domestic-violence", "mental-health"],
      "https://maryfonden.dk/om-mary-fonden/aarsrapport/", "annual_report", _verify_dk(), "medium"),
]


def _financial_row(entry: dict) -> dict:
    return {
        "year": 2023, "total_revenue_usd": entry["total_revenue_usd"],
        "program_expenses_usd": None, "admin_expenses_usd": None,
        "fundraising_expenses_usd": None, "top_executive_comp_usd": None,
        "top_executive_name": "", "source_url": entry["source_url"],
        "source_label": (
            "IRS Form 990, FY 2023 (ProPublica)" if entry["country"] == "US"
            else "Annual report & accounts (Charity Commission UK)" if entry["country"] == "GB"
            else "Annual report (org's own publication)"
        ),
    }


def _source_doc(entry: dict) -> dict:
    if entry["country"] == "US":
        return {"kind": "irs_990", "filed_date": entry["last_filed_date"],
                "label": {"en": "IRS Form 990 (FY 2023)", "ru": "Налоговая форма IRS 990 (2023)"},
                "url": entry["source_url"], "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf"}
    if entry["country"] == "GB":
        return {"kind": "annual_report", "filed_date": entry["last_filed_date"],
                "label": {"en": "Annual report & accounts (FY 2023)", "ru": "Годовой отчёт и финансовая отчётность (2023)"},
                "url": entry["source_url"], "source_label": "Charity Commission UK — accounts page",
                "file_format": "html"}
    return {"kind": "annual_report", "filed_date": entry["last_filed_date"],
            "label": {"en": "Annual report", "ru": "Годовой отчёт"},
            "url": entry["source_url"], "source_label": "Org's own annual report",
            "file_format": "html"}


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
        block = is_blocked(country=entry["country"], registration_id=entry["registration_id"],
                           cause_tags=entry["cause_slugs"],
                           name=entry["name"]["en"] + " " + entry["name"]["ru"],
                           description=entry["description"]["en"])
        if block is not None:
            print(f"[migration 0048] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
            skipped_blocked += 1
            continue

        is_stale = (date.today() - entry["last_filed_date"]).days > 730
        charity, _ = Charity.objects.update_or_create(
            country=entry["country"], registration_id=entry["registration_id"],
            defaults={
                "slug": entry["slug"], "name": entry["name"], "tagline": entry["tagline"],
                "description": entry["description"], "methodology_note": entry["methodology_note"],
                "logo_url": entry["logo_url"], "donation_url": entry["donation_url"],
                "cause_tags": entry["cause_slugs"], "size_bucket": entry["size_bucket"],
                "verification_status": "verified", "is_stale": is_stale,
                "last_filed_date": entry["last_filed_date"],
                "total_revenue_usd": entry["total_revenue_usd"],
                "program_expense_pct": entry["program_expense_pct"],
                "founded_year": entry["founded_year"], "ingestion_source": "manual_curation",
                "bucket": entry["bucket"], "hero_photo_url": entry["hero_photo_url"],
                "hero_photo_caption": entry["hero_photo_caption"],
                "hero_photo_credit": entry["hero_photo_credit"],
                "hero_photo_license": entry["hero_photo_license"],
            },
        )

        fin = _financial_row(entry)
        Financial.objects.update_or_create(
            charity=charity, year=fin["year"],
            defaults={k: v for k, v in fin.items() if k != "year"},
        )

        doc = _source_doc(entry)
        SourceDocument.objects.update_or_create(
            charity=charity, kind=doc["kind"], filed_date=doc["filed_date"],
            defaults={"label": doc["label"], "url": doc["url"],
                      "source_label": doc["source_label"], "file_format": doc["file_format"]},
        )

        upserted += 1

    all_cause_slugs: set[str] = set(NEW_CAUSES.keys())
    for entry in SEED:
        all_cause_slugs.update(entry["cause_slugs"])
    for slug in all_cause_slugs:
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    total = Charity.objects.count()
    print(f"[migration 0048] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0047_extend_country_choices_v311"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

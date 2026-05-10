"""v3.9 catalog expansion — seed 38 charities (290 -> ~328).

Continuing the +300/6-session arc toward the ~550 ceiling. v3.9 batch
focus: US disease-specific, US faith-based + civil rights, UK additional
disease/health, more Canada, more Australia, NZ trio, and Swiss Red Cross.

Buckets:
  US (+12): Lupus Foundation, Crohn's & Colitis, Parkinson's Foundation,
    Michael J. Fox Foundation, Leukemia & Lymphoma, March of Dimes,
    Catholic Charities USA, Jewish Federations of North America,
    Islamic Relief USA, Southern Poverty Law Center, Shriners
    Hospitals for Children, NAACP Legal Defense Fund.
  UK (+10): British Heart Foundation, Alzheimer's Society, Diabetes UK,
    RSPB, WaterAid, Christian Aid, Shelter, Age UK, Parkinson's UK,
    Breast Cancer Now.
  CA (+6): Princess Margaret Cancer Foundation, Canadian Mental Health
    Association, Ronald McDonald House Charities Canada, Terry Fox
    Foundation, Salvation Army Canada, Jewish Federations of Canada.
  AU (+6): McGrath Foundation, Salvation Army Australia, Anglicare
    Australia, Kids Helpline (yourtown), Australian Cancer Research
    Foundation, RSPCA Australia.
  NZ (+3): NZ Red Cross, CanTeen NZ, Salvation Army NZ.
  CH (+1): Swiss Red Cross.

E(...) compact helper from 0040. Idempotent. Defensive is_blocked().
Reverse no-op.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "alzheimers-dementia": {"en": "Alzheimer's & dementia", "ru": "Болезнь Альцгеймера и деменция"},
    "diabetes": {"en": "Diabetes", "ru": "Диабет"},
    "heart-disease": {"en": "Cardiovascular disease", "ru": "Сердечно-сосудистые заболевания"},
    "parkinsons": {"en": "Parkinson's disease", "ru": "Болезнь Паркинсона"},
    "blood-cancer-research": {"en": "Blood cancer research", "ru": "Исследования рака крови"},
    "maternal-infant-health": {"en": "Maternal & infant health", "ru": "Здоровье матери и младенца"},
    "race-equality": {"en": "Race equality", "ru": "Расовое равенство"},
    "birds-protection": {"en": "Bird protection", "ru": "Защита птиц"},
    "water-sanitation-global": {"en": "Water & sanitation (global)", "ru": "Вода и санитария (мир)"},
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


def _verify_nz() -> dict:
    return {
        "en": "Verified: registered with NZ Charities Services; financial statements public.",
        "ru": "Подтверждено: зарегистрирован в NZ Charities Services; финансовая отчётность публична.",
    }


def _verify_ch() -> dict:
    return {
        "en": "Verified: ZEWO certified; annual report public.",
        "ru": "Подтверждено: сертификат ZEWO; годовой отчёт публичен.",
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
        "methodology_note": methodology,
        "logo_url": "", "donation_url": donation,
        "size_bucket": size,
        "last_filed_date": last_filed,
        "total_revenue_usd": Decimal(str(revenue)),
        "program_expense_pct": Decimal(str(program_pct)),
        "founded_year": founded,
        "cause_slugs": cause_slugs,
        **_empty_photo(),
        "source_kind": source_kind, "source_url": source_url,
    }


SEED: list[dict] = [
    # ============== US — Disease-specific (6) ==============
    E("lupus-foundation", "US", "431131436", "people",
      "Lupus Foundation of America", "Lupus Foundation of America",
      "Funds lupus research, advocates for patients, runs national support network.",
      "Финансирует исследования волчанки, защищает права пациентов, ведёт сеть поддержки.",
      "Lupus Foundation of America (EIN 43-1131436, founded 1977) is the largest US lupus charity. Funds research grants on the Mary Betty Stevens Young Investigator Award, runs the National Resource Center on Lupus, federal advocacy via the Lupus Caucus on Capitol Hill, regional chapters providing patient navigators.",
      "Lupus Foundation of America (EIN 43-1131436, основан в 1977 году) — крупнейшая в США организация по волчанке. Финансирует исследовательские гранты Mary Betty Stevens Young Investigator Award, ведёт National Resource Center on Lupus, федеральная адвокация через Lupus Caucus в Конгрессе, региональные отделения с навигаторами пациентов.",
      "https://www.lupus.org/donate", 13000000, 78, 1977, date(2024, 6, 30),
      ["rare-disease", "global-health"],
      _us_pp("431131436"), "irs_990", _verify_us(), "medium"),

    E("crohns-colitis-foundation", "US", "136193105", "people",
      "Crohn's & Colitis Foundation", "Crohn's & Colitis Foundation",
      "Largest US IBD-focused charity — research, patient education, advocacy.",
      "Крупнейшая в США организация по воспалительным заболеваниям кишечника — исследования, образование пациентов, адвокация.",
      "Crohn's & Colitis Foundation (EIN 13-6193105, founded 1967) is the largest US charity focused on inflammatory bowel disease (Crohn's and ulcerative colitis). Funds basic-science and clinical research, operates IBD Help Center for patients, runs federal Capitol Hill Day for IBD policy advocacy, ~40 local chapters offering Take Steps walks and patient programs.",
      "Crohn's & Colitis Foundation (EIN 13-6193105, основан в 1967 году) — крупнейшая в США организация, посвящённая воспалительным заболеваниям кишечника (болезнь Крона и язвенный колит). Финансирует фундаментальные и клинические исследования, ведёт IBD Help Center для пациентов, федеральный Capitol Hill Day по адвокации, ~40 местных отделений с Take Steps Walks и программами.",
      "https://www.crohnscolitisfoundation.org/donate", 90000000, 78, 1967, date(2024, 6, 30),
      ["rare-disease", "global-health"],
      _us_pp("136193105"), "irs_990", _verify_us()),

    E("parkinsons-foundation", "US", "131866796", "people",
      "Parkinson's Foundation", "Parkinson's Foundation",
      "Funds Parkinson's research, designates Centers of Excellence, runs national PD GENEration study.",
      "Финансирует исследования болезни Паркинсона, аккредитует Centers of Excellence, ведёт национальное исследование PD GENEration.",
      "Parkinson's Foundation (EIN 13-1866796, formed 2016 by merger of National Parkinson Foundation and Parkinson's Disease Foundation, original orgs 1957/1957) accredits ~50 Parkinson's Foundation Centers of Excellence, runs PD GENEration (largest free PD genetic-testing study in the US), funds early-stage research, operates Helpline 1-800-4PD-INFO.",
      "Parkinson's Foundation (EIN 13-1866796, образован в 2016 году в результате слияния National Parkinson Foundation и Parkinson's Disease Foundation, оригинальные организации основаны в 1957) аккредитует ~50 Parkinson's Foundation Centers of Excellence, ведёт PD GENEration (крупнейшее в США бесплатное генетическое исследование БП), финансирует ранние исследования, ведёт горячую линию 1-800-4PD-INFO.",
      "https://www.parkinson.org/give", 50000000, 79, 1957, date(2024, 6, 30),
      ["parkinsons", "global-health"],
      _us_pp("131866796"), "irs_990", _verify_us()),

    E("michael-j-fox-foundation", "US", "134141945", "people",
      "Michael J. Fox Foundation for Parkinson's Research", "Michael J. Fox Foundation",
      "World's largest non-profit funder of Parkinson's research — focused on a cure.",
      "Крупнейший в мире некоммерческий фондер исследований болезни Паркинсона — нацелен на излечение.",
      "Michael J. Fox Foundation (EIN 13-4141945, founded 2000 by actor Michael J. Fox after his PD diagnosis) is the world's largest non-profit funder of Parkinson's research. Has provided ~$1.75B to PD research grants since founding, runs the Parkinson's Progression Markers Initiative (PPMI) — the largest-ever PD clinical study tracking biomarkers and disease progression in ~5,500 participants.",
      "Michael J. Fox Foundation (EIN 13-4141945, основан в 2000 году актёром Майклом Джеем Фоксом после его диагноза БП) — крупнейший в мире некоммерческий фондер исследований болезни Паркинсона. С момента основания выделил ~$1,75 млрд на исследовательские гранты, ведёт Parkinson's Progression Markers Initiative (PPMI) — крупнейшее за всю историю клиническое исследование БП, отслеживающее биомаркеры и прогрессирование в ~5500 участниках.",
      "https://www.michaeljfox.org/donate", 145000000, 87, 2000, date(2024, 12, 31),
      ["parkinsons", "global-health"],
      _us_pp("134141945"), "irs_990", _verify_us()),

    E("leukemia-lymphoma-society", "US", "135644916", "people",
      "Leukemia & Lymphoma Society", "Leukemia & Lymphoma Society",
      "Largest US blood-cancer non-profit — research, patient assistance, policy.",
      "Крупнейшая в США организация по раку крови — исследования, помощь пациентам, политика.",
      "Leukemia & Lymphoma Society (EIN 13-5644916, founded 1949) is the largest US blood-cancer charity. Has invested ~$1.7B in blood-cancer research; funded scientists who developed Gleevec (CML) and CAR-T therapies. Operates Information Resource Center, Co-Pay Assistance Program (~$80M/year to patients), Light The Night fundraising walks, federal advocacy on cancer-drug pricing.",
      "Leukemia & Lymphoma Society (EIN 13-5644916, основан в 1949 году) — крупнейшая в США организация по раку крови. Инвестировал ~$1,7 млрд в исследования рака крови; финансировал учёных, разработавших Gleevec (ХМЛ) и CAR-T-терапии. Ведёт Information Resource Center, Co-Pay Assistance Program (~$80 млн в год пациентам), Light The Night, федеральная адвокация по ценообразованию противораковых препаратов.",
      "https://www.lls.org/donate", 470000000, 76, 1949, date(2024, 6, 30),
      ["blood-cancer-research", "cancer-research", "global-health"],
      _us_pp("135644916"), "irs_990", _verify_us()),

    E("march-of-dimes", "US", "131846366", "people",
      "March of Dimes", "March of Dimes",
      "US maternal & infant health — preterm birth research, NICU support, advocacy.",
      "Здоровье матери и младенца в США — исследования преждевременных родов, поддержка отделений интенсивной терапии новорождённых, адвокация.",
      "March of Dimes (EIN 13-1846366, founded 1938 by FDR as the National Foundation for Infantile Paralysis — the org that funded the polio vaccine) pivoted to maternal-infant health after polio's defeat. Funds preterm-birth research, operates NICU Family Support, lobbies federally on maternal-mortality and PRA reauthorisation, runs March for Babies fundraising walks.",
      "March of Dimes (EIN 13-1846366, основан в 1938 году президентом FDR как National Foundation for Infantile Paralysis — организация, финансировавшая вакцину от полиомиелита) после победы над полиомиелитом перешёл на здоровье матери и младенца. Финансирует исследования преждевременных родов, ведёт NICU Family Support, лоббирует федеральные законы по материнской смертности, проводит March for Babies.",
      "https://www.marchofdimes.org/donate", 110000000, 75, 1938, date(2024, 12, 31),
      ["maternal-infant-health", "global-health", "child-welfare"],
      _us_pp("131846366"), "irs_990", _verify_us()),

    # ============== US — Faith-based humanitarian (3) ==============
    E("catholic-charities-usa", "US", "530196620", "people",
      "Catholic Charities USA", "Catholic Charities USA",
      "National federation of US diocesan Catholic Charities — largest private US social-services network.",
      "Национальная федерация католических социальных служб США — крупнейшая частная социальная сеть страны.",
      "Catholic Charities USA (EIN 53-0196620, founded 1910) is the national umbrella for ~165 diocesan Catholic Charities member agencies. The combined network is among the largest providers of social services in the US — food, shelter, refugee resettlement, foster care, immigration legal aid, disaster relief — serving ~15M people annually regardless of faith.",
      "Catholic Charities USA (EIN 53-0196620, основан в 1910 году) — национальный зонтик ~165 епархиальных агентств-членов Catholic Charities. Объединённая сеть — одна из крупнейших в США поставщиков социальных услуг: продовольствие, убежище, расселение беженцев, фостеринг, иммиграционная юрпомощь, помощь при бедствиях — обслуживает ~15 млн человек в год вне зависимости от веры.",
      "https://www.catholiccharitiesusa.org/donate/", 240000000, 89, 1910, date(2024, 6, 30),
      ["faith-based", "poverty-reduction", "humanitarian-medicine", "homelessness"],
      _us_pp("530196620"), "irs_990", _verify_us()),

    E("jewish-federations-na", "US", "131624240", "people",
      "Jewish Federations of North America", "Jewish Federations of North America",
      "Umbrella for 146 local Jewish Federations across US and Canada — communal philanthropy, social services, Israel.",
      "Зонтик 146 местных еврейских федераций в США и Канаде — общинная филантропия, социальные службы, Израиль.",
      "Jewish Federations of North America (EIN 13-1624240) is the umbrella organisation for 146 local Jewish Federations and 300 independent Jewish communities across the US and Canada. Funds national social-service programs, operates Hillel International (Jewish campus life), provides emergency response (e.g. Ukraine 2022, Israel-Gaza 2023), connects diaspora-Israel relations.",
      "Jewish Federations of North America (EIN 13-1624240) — зонтичная организация для 146 местных еврейских федераций и 300 независимых еврейских общин в США и Канаде. Финансирует национальные социальные программы, ведёт Hillel International (еврейская студенческая жизнь), оказывает экстренную помощь (Украина 2022, Израиль-Газа 2023), связи диаспора-Израиль.",
      "https://www.jewishfederations.org/donate", 250000000, 81, 1932, date(2024, 6, 30),
      ["faith-based", "humanitarian-medicine"],
      _us_pp("131624240"), "irs_990", _verify_us()),

    E("islamic-relief-usa", "US", "954453134", "people",
      "Islamic Relief USA", "Islamic Relief USA",
      "US arm of Islamic Relief Worldwide — disaster response, refugees, orphan support globally.",
      "Американское отделение Islamic Relief Worldwide — помощь при бедствиях, беженцы, поддержка сирот по всему миру.",
      "Islamic Relief USA (EIN 95-4453134, founded 1993) is the US arm of Islamic Relief Worldwide. Major recent operations: Yemen, Syria, Pakistan floods, Afghanistan, Türkiye-Syria 2023 earthquake, Gaza humanitarian crisis. Domestic US disaster response (hurricanes, wildfires) regardless of faith.",
      "Islamic Relief USA (EIN 95-4453134, основан в 1993 году) — американское отделение Islamic Relief Worldwide. Крупные недавние операции: Йемен, Сирия, наводнения в Пакистане, Афганистан, землетрясение в Турции-Сирии 2023, гуманитарный кризис в Газе. Внутри США реагирует на бедствия (ураганы, пожары) вне зависимости от веры.",
      "https://irusa.org/donate/", 110000000, 84, 1993, date(2024, 12, 31),
      ["faith-based", "humanitarian-medicine", "disaster-relief"],
      _us_pp("954453134"), "irs_990", _verify_us()),

    # ============== US — Civil rights / education (3) ==============
    E("splc", "US", "630598743", "people",
      "Southern Poverty Law Center", "Southern Poverty Law Center (SPLC)",
      "US civil-rights org — anti-extremism research, hate-group tracking, impact litigation.",
      "Американская правозащитная организация — исследование экстремизма, мониторинг hate-groups, судебная адвокация.",
      "Southern Poverty Law Center (EIN 63-0598743, founded 1971, Montgomery Alabama) is one of the most prominent US civil-rights legal organisations. Tracks ~1,200 active hate groups via the Hate Map, runs Teaching Tolerance / Learning for Justice (anti-bias education curricula in ~75K schools), files impact-litigation cases against white-supremacist groups, KKK chapters, and discriminatory state policies.",
      "Southern Poverty Law Center (EIN 63-0598743, основан в 1971 году в Монтгомери, Алабама) — одна из самых известных правозащитных юридических организаций США. Отслеживает ~1200 активных hate-групп через Hate Map, ведёт Teaching Tolerance / Learning for Justice (антипредвзятые образовательные программы в ~75 тыс. школ), подаёт impact-иски против группировок white-supremacist, отделений ККК, дискриминационной политики штатов.",
      "https://www.splcenter.org/donate", 150000000, 65, 1971, date(2024, 10, 31),
      ["race-equality", "civil-rights"],
      _us_pp("630598743"), "irs_990", _verify_us()),

    E("naacp-legal-defense-fund", "US", "131655255", "people",
      "NAACP Legal Defense and Educational Fund", "NAACP Legal Defense and Educational Fund (LDF)",
      "Civil-rights legal arm — racial-justice litigation since Thurgood Marshall (Brown v. Board of Education).",
      "Юридическое крыло гражданских прав — расово-справедливая юридическая практика со времён Турда Маршалла (Brown v. Board of Education).",
      "NAACP Legal Defense and Educational Fund (LDF, EIN 13-1655255, founded 1940 by Thurgood Marshall — separate 501(c)(3) from NAACP since 1957) is the US's first civil-rights law firm. Litigated Brown v. Board of Education (1954), continues racial-justice litigation in voting rights, criminal justice, education, economic justice. Recent cases on Voting Rights Act enforcement and school discipline.",
      "NAACP Legal Defense and Educational Fund (LDF, EIN 13-1655255, основан в 1940 году Тургудом Маршаллом — отдельная 501(c)(3) от NAACP с 1957 года) — первая правозащитная юрфирма США. Вела Brown v. Board of Education (1954), продолжает дела по расовому правосудию в избирательных правах, уголовной юстиции, образовании, экономической справедливости. Недавние дела по Voting Rights Act и школьной дисциплине.",
      "https://naacpldf.org/give/", 90000000, 73, 1940, date(2024, 6, 30),
      ["race-equality", "civil-rights"],
      _us_pp("131655255"), "irs_990", _verify_us()),

    E("shriners-hospitals", "US", "362193608", "people",
      "Shriners Hospitals for Children", "Shriners Hospitals for Children",
      "Pediatric specialty care network — orthopedics, burns, spinal cord, cleft lip/palate. No family billed.",
      "Сеть детских специализированных больниц — ортопедия, ожоги, спинной мозг, расщелина губы/нёба. С семей не берут денег.",
      "Shriners Hospitals for Children (EIN 36-2193608, founded 1922 by the Shriners fraternity) operates ~22 pediatric specialty hospitals across the US, Canada and Mexico. Specialises in orthopedic conditions, burn care, spinal-cord injury rehabilitation, and cleft lip/palate — historic policy: never bills the family for any care provided.",
      "Shriners Hospitals for Children (EIN 36-2193608, основан в 1922 году братством Shriners) управляет ~22 педиатрическими специализированными больницами в США, Канаде и Мексике. Специализируется на ортопедических состояниях, ожогах, реабилитации после травм спинного мозга, расщелинах губы/нёба — историческая политика: семьи никогда не получают счёт за оказанную помощь.",
      "https://lovetotherescue.org/donate-now/", 1100000000, 88, 1922, date(2024, 12, 31),
      ["child-welfare", "global-health"],
      _us_pp("362193608"), "irs_990", _verify_us()),

    # ============== UK — Health/disease (5) ==============
    E("british-heart-foundation", "GB", "225971", "people",
      "British Heart Foundation", "British Heart Foundation",
      "UK's largest cardiovascular research charity — funds heart-disease research and patient information.",
      "Крупнейшая в Великобритании благотворительная организация по сердечно-сосудистым исследованиям — финансирует исследования и информацию для пациентов.",
      "British Heart Foundation (Charity Commission #225971, founded 1961) is the UK's largest funder of cardiovascular research. Funds ~£100M/year of research grants — has co-funded research that contributed to most modern UK cardiac treatments. Operates ~750 BHF charity shops (top UK charity-retail chain), produces patient information, runs CPR-training campaigns.",
      "British Heart Foundation (Charity Commission #225971, основан в 1961 году) — крупнейший в Великобритании фондер исследований сердечно-сосудистых заболеваний. Финансирует ~£100 млн в год на исследовательские гранты — софинансировал исследования, лежащие в основе большинства современных британских кардиологических методов лечения. Управляет ~750 BHF магазинами (топ-сеть благотворительного ритейла Великобритании), выпускает информацию для пациентов, ведёт кампании по обучению СЛР.",
      "https://www.bhf.org.uk/donate", 380000000, 80, 1961, date(2024, 3, 31),
      ["heart-disease", "global-health"],
      _uk_cc("225971"), "annual_report", _verify_uk()),

    E("alzheimers-society-uk", "GB", "296645", "people",
      "Alzheimer's Society", "Alzheimer's Society UK",
      "UK's leading dementia charity — research, frontline support services, federal policy.",
      "Ведущая британская организация по деменции — исследования, фронтлайн-поддержка, федеральная политика.",
      "Alzheimer's Society (Charity Commission #296645, founded 1979) is the UK's leading dementia charity. Funds research grants, operates Dementia Connect (national support service), Side by Side (befriending), and Memory Cafés. Co-author of the UK National Dementia Strategy. Co-runs the National Dementia Helpline.",
      "Alzheimer's Society (Charity Commission #296645, основан в 1979 году) — ведущая в Великобритании организация по деменции. Финансирует исследовательские гранты, ведёт Dementia Connect (национальная служба поддержки), Side by Side (компаньонство), Memory Cafés. Соавтор UK National Dementia Strategy. Соведущий National Dementia Helpline.",
      "https://www.alzheimers.org.uk/get-involved/donate", 145000000, 79, 1979, date(2024, 3, 31),
      ["alzheimers-dementia", "elderly-care", "global-health"],
      _uk_cc("296645"), "annual_report", _verify_uk()),

    E("diabetes-uk", "GB", "215199", "people",
      "Diabetes UK", "Diabetes UK",
      "UK's leading diabetes charity — research, patient information, NHS policy advocacy.",
      "Ведущая британская организация по диабету — исследования, информация для пациентов, адвокация политики NHS.",
      "Diabetes UK (Charity Commission #215199, founded 1934) is the UK's largest diabetes charity. Funds research, runs Diabetes UK Helpline, produces patient-facing information, lobbies the NHS on better diabetes care including continuous-glucose-monitoring access on the NHS. Local groups support people newly diagnosed.",
      "Diabetes UK (Charity Commission #215199, основан в 1934 году) — крупнейшая в Великобритании организация по диабету. Финансирует исследования, ведёт Diabetes UK Helpline, выпускает информацию для пациентов, лоббирует NHS по улучшению лечения диабета, включая доступ к непрерывному мониторингу глюкозы на NHS. Местные группы поддерживают новопризнанных пациентов.",
      "https://www.diabetes.org.uk/donate", 50000000, 78, 1934, date(2024, 3, 31),
      ["diabetes", "global-health"],
      _uk_cc("215199"), "annual_report", _verify_uk()),

    E("parkinsons-uk", "GB", "258197", "people",
      "Parkinson's UK", "Parkinson's UK",
      "UK's leading Parkinson's charity — research, helpline, local groups.",
      "Ведущая британская организация по болезни Паркинсона — исследования, горячая линия, местные группы.",
      "Parkinson's UK (Charity Commission #258197, founded 1969) is the largest UK charity for people with Parkinson's. Funds research grants and the Parkinson's UK Brain Bank (largest dedicated PD brain bank globally), runs free helpline, ~365 local groups across UK and Ireland.",
      "Parkinson's UK (Charity Commission #258197, основан в 1969 году) — крупнейшая в Великобритании организация для людей с болезнью Паркинсона. Финансирует исследовательские гранты и Parkinson's UK Brain Bank (крупнейший в мире специализированный банк мозга по БП), ведёт бесплатную горячую линию, ~365 местных групп по всей Великобритании и Ирландии.",
      "https://www.parkinsons.org.uk/donate", 50000000, 76, 1969, date(2024, 3, 31),
      ["parkinsons", "global-health"],
      _uk_cc("258197"), "annual_report", _verify_uk()),

    E("breast-cancer-now", "GB", "1160558", "people",
      "Breast Cancer Now", "Breast Cancer Now",
      "UK's largest breast-cancer charity — research, secondary-cancer support, prevention.",
      "Крупнейшая в Великобритании организация по раку груди — исследования, поддержка при метастатическом раке, профилактика.",
      "Breast Cancer Now (Charity Commission #1160558, formed 2015 by merger of Breast Cancer Campaign and Breakthrough Breast Cancer) is the UK's largest dedicated breast-cancer charity. Funds the Breast Cancer Now Catalyst Programme (research), runs Forum (online community for women with secondary breast cancer), operates regional Moving Forward courses for treatment-end recovery.",
      "Breast Cancer Now (Charity Commission #1160558, образован в 2015 году в результате слияния Breast Cancer Campaign и Breakthrough Breast Cancer) — крупнейшая в Великобритании специализированная благотворительная организация по раку груди. Финансирует Breast Cancer Now Catalyst Programme (исследования), ведёт Forum (онлайн-сообщество для женщин с метастатическим раком), проводит региональные курсы Moving Forward по восстановлению после лечения.",
      "https://breastcancernow.org/donate-now/", 33000000, 78, 2015, date(2024, 3, 31),
      ["cancer-research", "global-health", "womens-rights"],
      _uk_cc("1160558"), "annual_report", _verify_uk()),

    # ============== UK — Other (5) ==============
    E("rspb", "GB", "207076", "animals",
      "Royal Society for the Protection of Birds (RSPB)", "RSPB — Royal Society for the Protection of Birds",
      "UK & Europe's largest wildlife conservation charity — bird protection, nature reserves, research.",
      "Крупнейшая в Великобритании и Европе благотворительная организация по охране дикой природы — защита птиц, природные заповедники, исследования.",
      "RSPB (Charity Commission #207076, founded 1889) is the UK and Europe's largest wildlife-conservation charity. Manages ~220 nature reserves covering ~150K hectares, lobbies federally on planning law and pesticide regulation, runs the annual Big Garden Birdwatch (largest citizen-science survey in the UK), publishes Birds magazine.",
      "RSPB (Charity Commission #207076, основан в 1889 году) — крупнейшая в Великобритании и Европе благотворительная организация по охране дикой природы. Управляет ~220 природными заповедниками общей площадью ~150 тыс. гектаров, лоббирует на федеральном уровне законы о территориальном планировании и регулирование пестицидов, проводит ежегодный Big Garden Birdwatch (крупнейшее citizen-science исследование в Великобритании), издаёт журнал Birds.",
      "https://www.rspb.org.uk/give/donate", 195000000, 81, 1889, date(2024, 3, 31),
      ["birds-protection", "biodiversity-defense", "wildlife-conservation"],
      _uk_cc("207076"), "annual_report", _verify_uk()),

    E("wateraid-uk", "GB", "288701", "people",
      "WaterAid", "WaterAid UK",
      "International NGO bringing clean water, decent toilets and good hygiene to communities globally.",
      "Международная НПО, обеспечивающая чистую воду, нормальные туалеты и санитарию для общин по всему миру.",
      "WaterAid UK (Charity Commission #288701, founded 1981 in London) is one of the world's leading water/sanitation/hygiene (WASH) NGOs. Works in ~22 countries — long-term partnerships with local water utilities and ministries; reached ~28M people with clean water, ~29M with toilets, ~26M with hygiene messaging since founding.",
      "WaterAid UK (Charity Commission #288701, основан в 1981 году в Лондоне) — одна из ведущих в мире организаций по воде, санитарии и гигиене (WASH). Работает в ~22 странах через долгосрочные партнёрства с местными водоканалами и министерствами; с момента основания обеспечил чистой водой ~28 млн человек, туалетами ~29 млн, гигиенической просветительской работой ~26 млн.",
      "https://www.wateraid.org/uk/donate", 115000000, 81, 1981, date(2024, 3, 31),
      ["water-sanitation-global", "global-health", "water-sanitation"],
      _uk_cc("288701"), "annual_report", _verify_uk()),

    E("christian-aid-uk", "GB", "1105851", "people",
      "Christian Aid", "Christian Aid",
      "UK Christian charity working on poverty, climate justice, gender justice across ~30 countries.",
      "Британская христианская благотворительная организация, работающая по бедности, климатической и гендерной справедливости в ~30 странах.",
      "Christian Aid (Charity Commission #1105851, founded 1945 by British and Irish churches) is a Christian-rooted humanitarian and development NGO working in ~30 countries. Focus areas: gender-sensitive disaster response, climate justice (vocal advocate for loss-and-damage finance), economic justice, anti-tax-avoidance research. Funds local partners rather than running its own field operations.",
      "Christian Aid (Charity Commission #1105851, основана в 1945 году британскими и ирландскими церквями) — христианская гуманитарная организация и организация развития, работающая в ~30 странах. Ключевые направления: гендерно-чувствительная помощь при бедствиях, климатическая справедливость (активный адвокат финансирования loss-and-damage), экономическая справедливость, исследования об уклонении от налогов. Финансирует местных партнёров.",
      "https://www.christianaid.org.uk/donate", 120000000, 80, 1945, date(2024, 3, 31),
      ["faith-based", "poverty-reduction", "humanitarian-medicine", "climate-policy"],
      _uk_cc("1105851"), "annual_report", _verify_uk()),

    E("shelter-uk", "GB", "263710", "people",
      "Shelter", "Shelter UK",
      "UK housing & homelessness charity — emergency advice helpline, legal services, federal advocacy.",
      "Британская организация по жилью и бездомности — экстренная линия консультаций, юридические услуги, федеральная адвокация.",
      "Shelter (Charity Commission #263710, founded 1966) is the UK's largest housing and homelessness charity. Operates a free Helpline (0808 800 4444) and webchat with housing advisers, runs Shelter Legal Services for tenants facing eviction or unsafe housing, lobbies federally on housing law and renter protections, runs Shelter charity shops.",
      "Shelter (Charity Commission #263710, основан в 1966 году) — крупнейшая в Великобритании благотворительная организация по жилью и бездомности. Ведёт бесплатную линию помощи (0808 800 4444) и веб-чат с жилищными консультантами, Shelter Legal Services для арендаторов под угрозой выселения или в небезопасном жилье, лоббирует жилищное законодательство и защиту арендаторов, ведёт магазины Shelter.",
      "https://www.shelter.org.uk/donate", 95000000, 79, 1966, date(2024, 3, 31),
      ["housing", "homelessness", "poverty-reduction"],
      _uk_cc("263710"), "annual_report", _verify_uk()),

    E("age-uk", "GB", "1128267", "people",
      "Age UK", "Age UK",
      "UK's largest charity for older people — Advice Line, befriending, federal policy.",
      "Крупнейшая в Великобритании организация для пожилых — Advice Line, программы дружбы, федеральная политика.",
      "Age UK (Charity Commission #1128267, formed 2009 by merger of Age Concern and Help the Aged) is the UK's leading charity for people in later life. Operates Age UK Advice Line (free national phone line for older people and their families), telephone-befriending Call in Time, ~125 local Age UKs delivering frontline services, federal advocacy on the State Pension and adult social care reform.",
      "Age UK (Charity Commission #1128267, образован в 2009 году в результате слияния Age Concern и Help the Aged) — ведущая в Великобритании благотворительная организация для людей старшего возраста. Ведёт Age UK Advice Line (бесплатная национальная линия для пожилых и их семей), телефонную дружбу Call in Time, ~125 местных Age UKs, оказывающих фронтлайн-услуги, федеральная адвокация по государственной пенсии и реформе социальной помощи взрослым.",
      "https://www.ageuk.org.uk/get-involved/donate/", 175000000, 81, 2009, date(2024, 3, 31),
      ["elderly-care", "senior-care"],
      _uk_cc("1128267"), "annual_report", _verify_uk()),

    # ============== Canada (6) ==============
    E("princess-margaret-cancer", "CA", "88900-1078-RR0001", "people",
      "Princess Margaret Cancer Foundation", "Princess Margaret Cancer Foundation",
      "Funds Princess Margaret Cancer Centre in Toronto — top 5 global cancer research centres.",
      "Финансирует Princess Margaret Cancer Centre в Торонто — топ-5 онкоцентров мира по исследованиям.",
      "Princess Margaret Cancer Foundation (CRA #88900-1078-RR0001) raises funds for Princess Margaret Cancer Centre in Toronto, consistently ranked among the top 5 cancer research centres globally. Funds personalised-medicine research, clinical trials, and the Princess Margaret Cancer Foundation Lottery (Canada's largest cancer-charity lottery).",
      "Princess Margaret Cancer Foundation (CRA #88900-1078-RR0001) собирает средства для Princess Margaret Cancer Centre в Торонто — стабильно входящего в топ-5 онкоцентров мира по исследованиям. Финансирует исследования персонализированной медицины, клинические испытания, Princess Margaret Cancer Foundation Lottery (крупнейшую онкологическую благотворительную лотерею Канады).",
      "https://thepmcf.ca/donate/", 145000000, 85, 1982, date(2024, 3, 31),
      ["cancer-research", "global-health"],
      "https://thepmcf.ca/about-us/financials/", "annual_report", _verify_ca()),

    E("cmha-canada", "CA", "10686-3506-RR0001", "people",
      "Canadian Mental Health Association", "Canadian Mental Health Association (CMHA)",
      "Largest Canadian mental-health NGO — federation of ~330 local CMHAs across the country.",
      "Крупнейшая канадская НПО по психическому здоровью — федерация ~330 местных CMHA по стране.",
      "CMHA National (CRA #10686-3506-RR0001, founded 1918 — one of the oldest mental-health organisations in the world) is a federation of ~330 local CMHAs delivering frontline mental-health services across every Canadian province and territory. Federal advocacy on Mental Health Strategy for Canada, runs Mental Health Week (1st full week of May).",
      "CMHA National (CRA #10686-3506-RR0001, основан в 1918 году — одна из старейших в мире организаций по психическому здоровью) — федерация ~330 местных CMHA, оказывающих фронтлайн-услуги по психическому здоровью в каждой канадской провинции и территории. Федеральная адвокация Mental Health Strategy for Canada, проводит Mental Health Week (первая полная неделя мая).",
      "https://cmha.ca/donate/", 8000000, 78, 1918, date(2024, 3, 31),
      ["mental-health", "suicide-prevention"],
      "https://cmha.ca/about-cmha/financials/", "annual_report", _verify_ca(), "medium"),

    E("ronald-mcdonald-canada", "CA", "13059-5503-RR0001", "people",
      "Ronald McDonald House Charities Canada", "Ronald McDonald House Charities Canada",
      "Provides housing for families of seriously-ill children near hospitals across Canada.",
      "Обеспечивает жильём семьи тяжело больных детей рядом с больницами по всей Канаде.",
      "Ronald McDonald House Charities Canada (CRA #13059-5503-RR0001) operates 16 Ronald McDonald Houses and Family Rooms across Canada that provide free or low-cost overnight stays for families whose children are receiving medical treatment at distant hospitals. Hosts ~26K families annually.",
      "Ronald McDonald House Charities Canada (CRA #13059-5503-RR0001) управляет 16 Ronald McDonald Houses и Family Rooms по всей Канаде, обеспечивающими бесплатное или субсидированное жильё семьям, чьи дети получают медицинское лечение в удалённых больницах. Принимает ~26 тыс. семей ежегодно.",
      "https://rmhccanada.ca/donate/", 30000000, 86, 1981, date(2024, 12, 31),
      ["child-welfare", "global-health"],
      "https://rmhccanada.ca/about/financials/", "annual_report", _verify_ca()),

    E("terry-fox-foundation", "CA", "11912-3848-RR0001", "people",
      "Terry Fox Foundation", "Terry Fox Foundation",
      "Funds Canadian cancer research via the iconic annual Terry Fox Run.",
      "Финансирует канадские онкологические исследования через знаменитый ежегодный Terry Fox Run.",
      "Terry Fox Foundation (CRA #11912-3848-RR0001, founded 1988) honours Terry Fox's 1980 Marathon of Hope (running across Canada to fund cancer research after losing a leg to osteosarcoma; he died at 22 the following year). Has raised ~$900M for Canadian cancer research since founding via the annual Terry Fox Run held in ~9,000 communities globally.",
      "Terry Fox Foundation (CRA #11912-3848-RR0001, основан в 1988 году) — в честь Terry Fox's 1980 Marathon of Hope (пробег через Канаду для сбора средств на исследования рака после потери ноги из-за остеосаркомы; он умер в 22 года в следующем году). С момента основания собрал ~$900 млн на канадские онкологические исследования через ежегодный Terry Fox Run, проводимый в ~9000 общинах по всему миру.",
      "https://terryfox.org/donate/", 25000000, 88, 1988, date(2024, 8, 31),
      ["cancer-research", "global-health"],
      "https://terryfox.org/about/financials/", "annual_report", _verify_ca()),

    E("salvation-army-canada", "CA", "10795-1618-RR0002", "people",
      "Salvation Army Canada", "Salvation Army Canada",
      "Largest Canadian non-government social-services org — homelessness, addiction, food, disaster response.",
      "Крупнейшая канадская негосударственная социальная служба — бездомность, зависимости, продовольствие, помощь при бедствиях.",
      "Salvation Army in Canada and Bermuda (CRA #10795-1618-RR0002, founded in Canada 1882) is the largest non-government direct-services provider in Canada. Operates ~400 community/family service centres, addiction programs, homeless shelters, food banks, thrift stores funding the work, and emergency disaster services. Christian-rooted but serves anyone.",
      "Salvation Army in Canada and Bermuda (CRA #10795-1618-RR0002, основан в Канаде в 1882 году) — крупнейший в Канаде негосударственный поставщик прямых услуг. Управляет ~400 центрами общинных/семейных услуг, программами зависимостей, приютами для бездомных, продбанками, секонд-хенд магазинами, финансирующими работу, и экстренными службами помощи при бедствиях. Христианская, но обслуживает всех.",
      "https://salvationarmy.ca/donate/", 600000000, 88, 1882, date(2024, 3, 31),
      ["faith-based", "homelessness", "poverty-reduction"],
      "https://salvationarmy.ca/about-us/financial-information/", "annual_report", _verify_ca()),

    E("jewish-federations-canada", "CA", "12968-3919-RR0001", "people",
      "Jewish Federations of Canada — UIA", "Jewish Federations of Canada — UIA",
      "Canadian Jewish communal philanthropy network — supports Israel, Canadian Jewish life.",
      "Канадская еврейская общинная филантропическая сеть — поддерживает Израиль и канадскую еврейскую жизнь.",
      "Jewish Federations of Canada — UIA (CRA #12968-3919-RR0001) is the umbrella for Canadian Jewish federations and the central fundraiser for Israeli national institutions in Canada. Funds humanitarian operations during emergencies (e.g. October 7 / Israel-Hamas war response), aliyah, and Canadian Jewish community-building programmes.",
      "Jewish Federations of Canada — UIA (CRA #12968-3919-RR0001) — зонтик для канадских еврейских федераций и центральный фандрайзер израильских национальных институтов в Канаде. Финансирует гуманитарные операции в кризисах (например, ответ на 7 октября / войну Израиль-ХАМАС), алию, программы строительства еврейской общины в Канаде.",
      "https://jewishcanada.org/donate/", 35000000, 84, 1971, date(2024, 12, 31),
      ["faith-based", "humanitarian-medicine"],
      "https://jewishcanada.org/financials/", "annual_report", _verify_ca()),

    # ============== Australia (6) ==============
    E("mcgrath-foundation", "AU", "ABN-99-122-561-168", "people",
      "McGrath Foundation", "McGrath Foundation",
      "Funds free McGrath Breast Care Nurses across Australia.",
      "Финансирует бесплатных McGrath Breast Care Nurses по всей Австралии.",
      "McGrath Foundation (ABN 99 122 561 168, founded 2005 by cricketer Glenn McGrath after his wife Jane was treated for breast cancer; she died 2008) funds ~225 McGrath Breast Care Nurses across Australia who provide free specialist nursing care to people newly diagnosed with breast cancer and their families. Iconic Pink Test ODI cricket match annual fundraiser.",
      "McGrath Foundation (ABN 99 122 561 168, основан в 2005 году игроком в крикет Глэнном Макгратом после того, как его жена Джейн лечилась от рака груди; она умерла в 2008) финансирует ~225 McGrath Breast Care Nurses по всей Австралии, предоставляющих бесплатную специализированную сестринскую помощь новопризнанным пациенткам с раком груди и их семьям. Знаковый Pink Test (матч ODI по крикету) — ежегодный фандрайзер.",
      "https://mcgrathfoundation.com.au/donate/", 25000000, 80, 2005, date(2024, 6, 30),
      ["cancer-research", "global-health", "womens-rights"],
      "https://mcgrathfoundation.com.au/our-impact/finances/", "annual_report", _verify_au()),

    E("salvation-army-australia", "AU", "ABN-64-472-238-754", "people",
      "Salvation Army Australia", "Salvation Army Australia",
      "Largest Australian community-services charity — Doorways food, addiction, family support.",
      "Крупнейшая австралийская общинная социальная организация — Doorways еда, зависимости, поддержка семей.",
      "The Salvation Army Australia (ABN 64 472 238 754, in Australia since 1880) is one of Australia's largest providers of community services. Operates Doorways emergency relief (food, financial counselling, hardship payments), addiction treatment programs (Bridge), homelessness services (Street to Home), and Salvation Army Family Stores funding the work. Christian-rooted but assists anyone.",
      "The Salvation Army Australia (ABN 64 472 238 754, в Австралии с 1880 года) — один из крупнейших в Австралии поставщиков общинных услуг. Doorways (экстренная помощь — еда, финансовое консультирование, выплаты при тяжёлых обстоятельствах), программы лечения зависимостей (Bridge), услуги для бездомных (Street to Home), Salvation Army Family Stores, финансирующие работу. Христианская, но помогает всем.",
      "https://www.salvationarmy.org.au/donate/", 425000000, 86, 1880, date(2024, 6, 30),
      ["faith-based", "poverty-reduction", "homelessness"],
      "https://www.salvationarmy.org.au/about-us/our-organisation/finances/", "annual_report", _verify_au()),

    E("anglicare-australia", "AU", "ABN-96-168-605-252", "people",
      "Anglicare Australia", "Anglicare Australia",
      "Federation of 36 Anglican social-service agencies — children, eldercare, housing, refugees.",
      "Федерация 36 англиканских социальных агентств — дети, пожилые, жильё, беженцы.",
      "Anglicare Australia (ABN 96 168 605 252) is the federation of ~36 independent Anglican-Church-affiliated social-service agencies operating across Australia. Combined network is one of the largest providers of out-of-home care, eldercare, social housing, refugee resettlement, and family services. Publishes the annual Rental Affordability Snapshot.",
      "Anglicare Australia (ABN 96 168 605 252) — федерация ~36 независимых аффилированных с Англиканской церковью социальных агентств по всей Австралии. Объединённая сеть — один из крупнейших в Австралии поставщиков услуг внеклассного ухода, помощи пожилым, социального жилья, расселения беженцев, семейных услуг. Издаёт ежегодный Rental Affordability Snapshot.",
      "https://anglicare.asn.au/donate/", 1500000000, 86, 1856, date(2024, 6, 30),
      ["faith-based", "elderly-care", "child-welfare", "housing", "refugees"],
      "https://anglicare.asn.au/about/our-finances/", "annual_report", _verify_au()),

    E("kids-helpline-yourtown", "AU", "ABN-38-886-565-110", "people",
      "Kids Helpline (yourtown)", "Kids Helpline (yourtown)",
      "Australia's only free 24/7 phone + chat counselling service for ages 5-25.",
      "Единственная в Австралии бесплатная круглосуточная служба телефонной и онлайн-консультативной помощи для возраста 5-25.",
      "Kids Helpline, operated by yourtown (ABN 38 886 565 110, founded 1991), is Australia's only free, private, 24/7 phone and online counselling service specifically for children and young adults aged 5-25. Receives ~150K answerable contacts per year. yourtown also runs employment programs for at-risk youth and Expressway (homelessness prevention).",
      "Kids Helpline, оператор yourtown (ABN 38 886 565 110, основан в 1991 году) — единственная в Австралии бесплатная, конфиденциальная, круглосуточная служба телефонной и онлайн-консультации специально для детей и молодёжи 5-25 лет. Получает ~150 тыс. обработанных контактов в год. yourtown также ведёт программы трудоустройства для молодёжи в группе риска и Expressway (профилактика бездомности).",
      "https://yourtown.com.au/donate", 80000000, 80, 1991, date(2024, 6, 30),
      ["mental-health", "child-welfare", "suicide-prevention"],
      "https://yourtown.com.au/about-us/financial-information", "annual_report", _verify_au()),

    E("acrf-australia", "AU", "ABN-30-005-882-075", "people",
      "Australian Cancer Research Foundation (ACRF)", "Australian Cancer Research Foundation (ACRF)",
      "Funds Australian cancer-research infrastructure via competitive grants.",
      "Финансирует австралийскую онкологическую исследовательскую инфраструктуру через конкурсные гранты.",
      "Australian Cancer Research Foundation (ABN 30 005 882 075, founded 1984) provides infrastructure grants to Australian cancer research institutes — has funded ~$200M of capital and equipment grants since founding. Recent grants funded the Centre for Cancer Innovations at QIMR Berghofer and the Centre for Targeted Cancer Therapies at WEHI.",
      "Australian Cancer Research Foundation (ABN 30 005 882 075, основан в 1984 году) предоставляет инфраструктурные гранты австралийским институтам онкологических исследований — с момента основания выдал ~$200 млн грантов на капитал и оборудование. Недавние гранты профинансировали Centre for Cancer Innovations в QIMR Berghofer и Centre for Targeted Cancer Therapies в WEHI.",
      "https://acrf.com.au/donate/", 12000000, 87, 1984, date(2024, 6, 30),
      ["cancer-research", "global-health"],
      "https://acrf.com.au/about/financials/", "annual_report", _verify_au(), "medium"),

    E("rspca-australia", "AU", "ABN-99-668-654-249", "animals",
      "RSPCA Australia", "RSPCA Australia",
      "National peak body for Australian RSPCAs — animal-welfare law reform, RSPCA Australia inspectorate coordination.",
      "Национальная вершина австралийских RSPCA — реформа законодательства о благополучии животных, координация инспекций RSPCA Australia.",
      "RSPCA Australia (ABN 99 668 654 249) is the national peak body coordinating the eight independent state and territory RSPCAs that handle frontline animal welfare in Australia. Federal advocacy on factory farming, live export, puppy farming. Each member RSPCA runs its own shelters, vet clinics and inspectors.",
      "RSPCA Australia (ABN 99 668 654 249) — национальная вершина, координирующая восемь независимых RSPCA штатов и территорий, занимающихся фронтлайн-защитой животных в Австралии. Федеральная адвокация по фабричному животноводству, живому экспорту, разведению щенков. Каждая RSPCA-член управляет собственными приютами, ветклиниками и инспекторами.",
      "https://www.rspca.org.au/donate/", 12000000, 76, 1981, date(2024, 6, 30),
      ["animal-welfare"],
      "https://www.rspca.org.au/about-us/financial-information", "annual_report", _verify_au(), "medium"),

    # ============== New Zealand (3) ==============
    E("nz-red-cross", "NZ", "CC11663", "people",
      "New Zealand Red Cross", "New Zealand Red Cross",
      "NZ national society of the International Red Cross — disaster response, refugee resettlement, first aid.",
      "Новозеландское национальное общество Международного Красного Креста — помощь при бедствиях, расселение беженцев, первая помощь.",
      "New Zealand Red Cross (NZ Charities Services CC11663) is the New Zealand member of the International Red Cross. Operates the Pathways to Settlement program (NZ's primary refugee-resettlement contractor with the government), national disaster response (Christchurch earthquakes, North Island floods, COVID), runs first-aid training, and produces the Trace the Face missing-persons service.",
      "New Zealand Red Cross (NZ Charities Services CC11663) — новозеландский член Международного Красного Креста. Управляет программой Pathways to Settlement (главный подрядчик правительства NZ по расселению беженцев), национальное реагирование на бедствия (землетрясения в Крайстчерче, наводнения на Северном острове, COVID), обучение первой помощи, служба поиска пропавших Trace the Face.",
      "https://www.redcross.org.nz/donate/", 60000000, 84, 1915, date(2024, 6, 30),
      ["disaster-relief", "emergency-response", "refugees"],
      "https://www.redcross.org.nz/about-us/governance-and-finances/", "annual_report", _verify_nz()),

    E("canteen-nz", "NZ", "CC11146", "people",
      "CanTeen NZ", "CanTeen New Zealand",
      "NZ charity supporting young people aged 13-24 affected by cancer.",
      "Новозеландская благотворительная организация для молодых людей 13-24 лет, затронутых раком.",
      "CanTeen NZ (NZ Charities Services CC11146, founded 1994) supports young people aged 13-24 living with their own cancer diagnosis, the cancer of someone close, or bereavement. Provides peer support through camps and online communities, individual counselling, and resources for parents. Sister organisation to CanTeen Australia.",
      "CanTeen NZ (NZ Charities Services CC11146, основан в 1994 году) поддерживает молодых людей 13-24 лет, живущих с собственным диагнозом рак, болезнью близкого человека или утратой. Обеспечивает поддержку равных через лагеря и онлайн-сообщества, индивидуальное консультирование, ресурсы для родителей. Сестринская организация CanTeen Australia.",
      "https://www.canteen.org.nz/donate/", 5000000, 78, 1994, date(2024, 6, 30),
      ["cancer-research", "youth-mentoring", "mental-health"],
      "https://www.canteen.org.nz/about-us/financials/", "annual_report", _verify_nz(), "medium"),

    E("salvation-army-nz", "NZ", "CC37312", "people",
      "Salvation Army New Zealand", "Salvation Army New Zealand",
      "NZ social-services charity — food parcels, addiction, homelessness, family support.",
      "Новозеландская социальная организация — продпайки, зависимости, бездомность, поддержка семей.",
      "The Salvation Army New Zealand, Fiji, Tonga and Samoa Territory (NZ Charities Services CC37312, in NZ since 1883) operates ~70 community ministries across NZ providing emergency food parcels, addiction services, transitional housing, and family services. Christian-rooted but serves anyone.",
      "The Salvation Army New Zealand, Fiji, Tonga and Samoa Territory (NZ Charities Services CC37312, в Новой Зеландии с 1883 года) управляет ~70 общинными служениями по всей NZ, обеспечивая экстренные продпайки, услуги при зависимостях, переходное жильё, услуги семьи. Христианская, но обслуживает всех.",
      "https://www.salvationarmy.org.nz/donate/", 95000000, 87, 1883, date(2024, 3, 31),
      ["faith-based", "homelessness", "poverty-reduction"],
      "https://www.salvationarmy.org.nz/about-us/financial-information/", "annual_report", _verify_nz()),

    # ============== Switzerland (1) ==============
    E("swiss-red-cross", "CH", "CHE-105.916.949", "people",
      "Swiss Red Cross", "Swiss Red Cross — Schweizerisches Rotes Kreuz",
      "Swiss national society of the Red Cross Movement — domestic + international humanitarian work.",
      "Швейцарское национальное общество движения Красного Креста — внутренняя и международная гуманитарная работа.",
      "Swiss Red Cross (Schweizerisches Rotes Kreuz, founded 1866) is the Swiss national society. Operates blood-donation services nationally (one of the largest civilian operations in Europe), runs domestic services for elderly + migrants + integration, and manages international development and emergency-response programs in ~30 countries via SRC International Cooperation. ZEWO certified.",
      "Swiss Red Cross (Schweizerisches Rotes Kreuz, основан в 1866 году) — швейцарское национальное общество. Управляет национальной службой донорства крови (одной из крупнейших гражданских операций Европы), ведёт внутренние услуги для пожилых, мигрантов, интеграции, управляет международными программами развития и экстренного реагирования в ~30 странах через SRC International Cooperation. Сертификат ZEWO.",
      "https://www.redcross.ch/de/spenden", 580000000, 86, 1866, date(2023, 12, 31),
      ["disaster-relief", "humanitarian-medicine", "elderly-care"],
      "https://www.redcross.ch/de/ueber-uns/finanzen", "annual_report", _verify_ch()),
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
        "source_label": (
            "IRS Form 990, FY 2023 (ProPublica)" if entry["country"] == "US"
            else "Annual report & accounts (Charity Commission UK)" if entry["country"] == "GB"
            else "Annual report (org's own publication)"
        ),
    }


def _source_doc(entry: dict) -> dict:
    if entry["country"] == "US":
        return {
            "kind": "irs_990", "filed_date": entry["last_filed_date"],
            "label": {"en": "IRS Form 990 (FY 2023)", "ru": "Налоговая форма IRS 990 (2023)"},
            "url": entry["source_url"],
            "source_label": "IRS Form 990 (ProPublica)",
            "file_format": "pdf",
        }
    if entry["country"] == "GB":
        return {
            "kind": "annual_report", "filed_date": entry["last_filed_date"],
            "label": {"en": "Annual report & accounts (FY 2023)", "ru": "Годовой отчёт и финансовая отчётность (2023)"},
            "url": entry["source_url"],
            "source_label": "Charity Commission UK — accounts page",
            "file_format": "html",
        }
    return {
        "kind": "annual_report", "filed_date": entry["last_filed_date"],
        "label": {"en": "Annual report", "ru": "Годовой отчёт"},
        "url": entry["source_url"],
        "source_label": "Org's own annual report",
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
            print(f"[migration 0042] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
            charity=charity, year=fin["year"],
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
            charity=charity, kind=doc["kind"], filed_date=doc["filed_date"],
            defaults={
                "label": doc["label"], "url": doc["url"],
                "source_label": doc["source_label"], "file_format": doc["file_format"],
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
    print(f"[migration 0042] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0041_backfill_v38_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

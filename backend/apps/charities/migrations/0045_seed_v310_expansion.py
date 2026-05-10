"""v3.10 catalog expansion — seed 40 charities (328 -> ~368).

4th batch of the +300/6-session arc. v3.10 focus: continental Europe
expansion (Italy, Spain, Ireland, Norway — 4 new countries via 0044
schema migration), more US Hispanic/disease/anti-trafficking, more UK
cause-specific cancer + youth mental health, more CA/AU/NZ.

New countries: Italy (IT), Spain (ES), Ireland (IE), Norway (NO).

Buckets:
  US (+9): NF1 / Children's Tumor Foundation, ALS-TDI, Sickle Cell Disease
    Association, UnidosUS, Hispanic Federation, MALDEF, Polaris Project,
    Stop Soldier Suicide, Bob Woodruff Foundation.
  UK (+6): CAFOD, Tearfund, YoungMinds, Pancreatic Cancer UK,
    Bowel Cancer UK, Woodland Trust.
  CA (+4): UNICEF Canada, Plan International Canada, Kids Help Phone,
    Oxfam Canada.
  AU (+3): Lifeline Australia, Black Dog Institute, OzHarvest.
  Italy (+6): Save the Children Italia, AIRC, Fondazione Telethon,
    Caritas Italiana, ActionAid Italia, Lega del Filo d'Oro.
  Spain (+6): Cáritas Española, MSF España, Fundación ANAR,
    Save the Children España, Médicos del Mundo España, Greenpeace España.
  Ireland (+3): Irish Red Cross, Trócaire, Concern Worldwide.
  Norway (+3): Redd Barna, Norwegian Refugee Council, SOS-barnebyer Norge.

Idempotent. Defensive is_blocked(). Reverse no-op.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "neurofibromatosis": {"en": "Neurofibromatosis research", "ru": "Исследования нейрофиброматоза"},
    "sickle-cell": {"en": "Sickle cell disease", "ru": "Серповидноклеточная анемия"},
    "hispanic-rights": {"en": "Hispanic / Latino civil rights", "ru": "Гражданские права испаноязычных / латиноамериканцев"},
    "anti-trafficking": {"en": "Anti-human-trafficking", "ru": "Борьба с торговлей людьми"},
    "youth-mental-health": {"en": "Youth mental health", "ru": "Психическое здоровье молодёжи"},
    "deafblind": {"en": "Deafblind support", "ru": "Поддержка слепоглухих"},
    "food-rescue": {"en": "Food rescue", "ru": "Спасение еды от утилизации"},
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


def _verify_ie() -> dict:
    return {
        "en": "Verified: registered with the Charities Regulator of Ireland; annual report public.",
        "ru": "Подтверждено: зарегистрировано в Charities Regulator Ирландии; годовой отчёт публичен.",
    }


def _verify_no() -> dict:
    return {
        "en": "Verified: registered with Brønnøysundregistrene; Innsamlingskontrollen (donor-protection registry) member; annual report public.",
        "ru": "Подтверждено: зарегистрировано в Brønnøysundregistrene; член Innsamlingskontrollen (реестр защиты доноров); годовой отчёт публичен.",
    }


def _empty_photo() -> dict:
    return {
        "hero_photo_url": "", "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "", "hero_photo_license": "",
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
        "founded_year": founded, "cause_slugs": cause_slugs,
        **_empty_photo(),
        "source_kind": source_kind, "source_url": source_url,
    }


SEED: list[dict] = [
    # ============== US (9) ==============
    E("childrens-tumor-foundation", "US", "133727593", "people",
      "Children's Tumor Foundation", "Children's Tumor Foundation",
      "Funds neurofibromatosis (NF) research — venture-philanthropy model accelerating drug development.",
      "Финансирует исследования нейрофиброматоза (NF) — венчурно-филантропическая модель ускорения разработки лекарств.",
      "Children's Tumor Foundation (CTF, EIN 13-3727593, founded 1978) is the largest US foundation focused on neurofibromatosis. Funds ~$15M/year of NF research, runs the NF Clinic Network (~70 affiliated clinics), launched the NF Therapeutic Acceleration Program drug-development portfolio. Model emulates Cystic Fibrosis Foundation's venture-philanthropy approach.",
      "Children's Tumor Foundation (CTF, EIN 13-3727593, основан в 1978 году) — крупнейший в США фонд, посвящённый нейрофиброматозу. Финансирует ~$15 млн в год на NF-исследования, управляет NF Clinic Network (~70 аффилированных клиник), запустил портфель разработки лекарств NF Therapeutic Acceleration Program. Модель повторяет венчурно-филантропический подход Cystic Fibrosis Foundation.",
      "https://www.ctf.org/donate", 24000000, 80, 1978, date(2024, 9, 30),
      ["neurofibromatosis", "rare-disease"],
      _us_pp("133727593"), "irs_990", _verify_us(), "medium"),

    E("als-tdi", "US", "043267247", "people",
      "ALS Therapy Development Institute", "ALS Therapy Development Institute",
      "First non-profit biotech 100% focused on ALS drug discovery — pre-clinical research.",
      "Первая некоммерческая биотех-организация, на 100% сосредоточенная на разработке лекарств от БАС — доклинические исследования.",
      "ALS Therapy Development Institute (ALS-TDI, EIN 04-3267247, founded 1999) is the world's first non-profit biotech focused entirely on ALS drug discovery. Operates a 26K-sqft Cambridge Massachusetts lab; runs the largest ALS pre-clinical mouse-model studies in the world; pioneered Precision Medicine Program tracking voice/movement biomarkers in 600+ ALS patients longitudinally.",
      "ALS Therapy Development Institute (ALS-TDI, EIN 04-3267247, основан в 1999 году) — первая в мире некоммерческая биотех-организация, полностью сосредоточенная на разработке лекарств от БАС. Управляет лабораторией площадью ~26 тыс. кв. футов в Кембридже, Массачусетс; ведёт крупнейшие в мире доклинические исследования БАС на мышиных моделях; пионер программы Precision Medicine, отслеживающей биомаркеры голоса/движения у 600+ пациентов с БАС лонгитюдно.",
      "https://www.als.net/donate/", 12000000, 78, 1999, date(2024, 12, 31),
      ["rare-disease", "global-health"],
      _us_pp("043267247"), "irs_990", _verify_us(), "medium"),

    E("sickle-cell-disease-association", "US", "237378655", "people",
      "Sickle Cell Disease Association of America", "Sickle Cell Disease Association of America",
      "National federation supporting people with sickle cell disease — research, advocacy, education.",
      "Национальная федерация, поддерживающая людей с серповидноклеточной анемией — исследования, адвокация, образование.",
      "Sickle Cell Disease Association of America (SCDAA, EIN 23-7378655, founded 1971) is the federation of ~50 community-based US member organisations serving sickle cell patients. Federal advocacy on the Sickle Cell Disease Treatment Demonstration Program, sickle cell trait newborn screening, and access to gene therapies (Casgevy / Lyfgenia approved 2023).",
      "Sickle Cell Disease Association of America (SCDAA, EIN 23-7378655, основан в 1971 году) — федерация ~50 общинных US организаций-членов, обслуживающих пациентов с серповидноклеточной анемией. Федеральная адвокация по Sickle Cell Disease Treatment Demonstration Program, скринингу новорождённых на серповидноклеточный признак, доступу к генным терапиям (Casgevy / Lyfgenia одобрены в 2023 году).",
      "https://www.sicklecelldisease.org/donate/", 5500000, 76, 1971, date(2024, 9, 30),
      ["sickle-cell", "rare-disease", "race-equality"],
      _us_pp("237378655"), "irs_990", _verify_us(), "medium"),

    E("unidosus", "US", "860212873", "people",
      "UnidosUS", "UnidosUS — крупнейшая в США латиноамериканская организация",
      "Largest US Hispanic civil-rights & advocacy org (formerly NCLR — National Council of La Raza).",
      "Крупнейшая в США латиноамериканская правозащитная организация (раньше называлась NCLR — National Council of La Raza).",
      "UnidosUS (EIN 86-0212873, founded 1968 as the Southwest Council of La Raza, renamed 2017) is the largest US Hispanic civil-rights and advocacy organisation. Combines federal policy advocacy, an Affiliate Network of ~280 Hispanic-serving community organisations, signature programs in education, workforce, housing, immigration, and health.",
      "UnidosUS (EIN 86-0212873, основан в 1968 году как Southwest Council of La Raza, переименован в 2017 году) — крупнейшая в США правозащитная и адвокационная организация испаноязычных. Объединяет федеральную адвокацию политики, Affiliate Network из ~280 общинных организаций, обслуживающих испаноязычное население, ключевые программы в образовании, рабочей силе, жилье, иммиграции, здравоохранении.",
      "https://unidosus.org/donate/", 80000000, 84, 1968, date(2024, 6, 30),
      ["hispanic-rights", "civil-rights", "education"],
      _us_pp("860212873"), "irs_990", _verify_us()),

    E("hispanic-federation", "US", "133573852", "people",
      "Hispanic Federation", "Hispanic Federation",
      "NYC-area Latino civil-rights and community-based grant-making — also Puerto Rico-Maria response.",
      "Нью-йоркская латиноамериканская правозащитная и грантодающая организация — также реагировала на ураган Мария на Пуэрто-Рико.",
      "Hispanic Federation (EIN 13-3573852, founded 1990) is the largest Hispanic non-profit grant-maker on the East Coast US. Funds ~100 Latino-serving community organisations in the NYC region annually. Led private-sector Hurricane Maria recovery in Puerto Rico (2017+); UNIDOS Disaster Relief Fund continues for post-Maria + 2020 earthquakes.",
      "Hispanic Federation (EIN 13-3573852, основан в 1990 году) — крупнейший латиноамериканский некоммерческий грантодатель на восточном побережье США. Ежегодно финансирует ~100 общинных латиноамериканских организаций в районе Нью-Йорка. Возглавлял частный сектор восстановления Пуэрто-Рико после урагана Мария (2017+); фонд UNIDOS Disaster Relief Fund продолжается на пост-Мария + 2020 землетрясения.",
      "https://www.hispanicfederation.org/donate/", 35000000, 89, 1990, date(2024, 6, 30),
      ["hispanic-rights", "disaster-relief"],
      _us_pp("133573852"), "irs_990", _verify_us(), "medium"),

    E("maldef", "US", "741563270", "people",
      "Mexican American Legal Defense and Educational Fund (MALDEF)", "MALDEF",
      "Latino civil rights legal organisation — voting rights, education access, immigrants' rights.",
      "Латиноамериканская правозащитная юридическая организация — избирательные права, доступ к образованию, права иммигрантов.",
      "MALDEF (EIN 74-1563270, founded 1968 in San Antonio Texas) is the leading Latino civil-rights legal organisation in the US. Litigates landmark cases on voting rights, education access, employment discrimination, immigration. Currently challenging multiple state-level voting-rights restrictions.",
      "MALDEF (EIN 74-1563270, основан в 1968 году в Сан-Антонио, Техас) — ведущая латиноамериканская правозащитная юридическая организация США. Ведёт ключевые дела по избирательным правам, доступу к образованию, дискриминации в трудоустройстве, иммиграции. В настоящее время оспаривает множество ограничений избирательных прав на уровне штатов.",
      "https://www.maldef.org/donate/", 8000000, 74, 1968, date(2024, 6, 30),
      ["hispanic-rights", "civil-rights"],
      _us_pp("741563270"), "irs_990", _verify_us(), "medium"),

    E("polaris-project", "US", "030391561", "people",
      "Polaris Project", "Polaris Project",
      "Operates the US National Human Trafficking Hotline + research on trafficking patterns.",
      "Управляет Национальной горячей линией США по торговле людьми + исследования паттернов трафикинга.",
      "Polaris Project (EIN 03-0391561, founded 2002) operates the US National Human Trafficking Hotline (1-888-373-7888) — 24/7, multilingual, free. Connects survivors with services, builds the BeFree Textline (text 233733), and produces research on human-trafficking patterns. Has handled ~410K interactions identifying ~85K victims and survivors since founding.",
      "Polaris Project (EIN 03-0391561, основан в 2002 году) управляет Национальной горячей линией США по торговле людьми (1-888-373-7888) — круглосуточно, на нескольких языках, бесплатно. Связывает выживших с услугами, ведёт BeFree Textline (текст 233733), выпускает исследования паттернов трафикинга. С момента основания обработал ~410 тыс. взаимодействий, выявил ~85 тыс. жертв и выживших.",
      "https://polarisproject.org/donate/", 12000000, 80, 2002, date(2024, 12, 31),
      ["anti-trafficking", "civil-rights"],
      _us_pp("030391561"), "irs_990", _verify_us(), "medium"),

    E("stop-soldier-suicide", "US", "270488082", "people",
      "Stop Soldier Suicide", "Stop Soldier Suicide",
      "Veteran-founded nonprofit providing case management for at-risk veterans and active-duty military.",
      "Некоммерческая организация, основанная ветеранами, ведущая case-management для ветеранов и военнослужащих в группе риска.",
      "Stop Soldier Suicide (EIN 27-0488082, founded 2010 by three Army veterans) provides 1-on-1 case management to military service members, veterans and their families at risk of suicide. Focus: warm handoff to mental-health and crisis resources, not just hotline. ~50K people served. Deploying advanced predictive-analytics on suicide-risk indicators.",
      "Stop Soldier Suicide (EIN 27-0488082, основан в 2010 году тремя армейскими ветеранами) обеспечивает индивидуальный case-management для военнослужащих, ветеранов и их семей в группе риска суицида. Фокус: тёплая передача на услуги психического здоровья и кризисные ресурсы, не просто линия помощи. Помогли ~50 тыс. человек. Внедряют продвинутую предиктивную аналитику индикаторов суицидального риска.",
      "https://stopsoldiersuicide.org/donate", 13000000, 76, 2010, date(2024, 12, 31),
      ["veterans", "suicide-prevention", "mental-health"],
      _us_pp("270488082"), "irs_990", _verify_us(), "medium"),

    E("bob-woodruff-foundation", "US", "208853847", "people",
      "Bob Woodruff Foundation", "Bob Woodruff Foundation",
      "Funds local-level vetted programs for post-9/11 veterans, service members and their families.",
      "Финансирует местные проверенные программы для ветеранов после 9/11, военнослужащих и их семей.",
      "Bob Woodruff Foundation (EIN 20-8853847, founded 2006 after ABC anchor Bob Woodruff was severely injured in Iraq) funds vetted, evidence-based local programs that help post-9/11 veterans and military families with employment, education, mental health, rehab and family support. Issues ~$10-12M/year in grants.",
      "Bob Woodruff Foundation (EIN 20-8853847, основан в 2006 году после того, как ведущий ABC Боб Вудраф был тяжело ранен в Ираке) финансирует проверенные, evidence-based местные программы, помогающие ветеранам после 9/11 и военным семьям в трудоустройстве, образовании, психическом здоровье, реабилитации, поддержке семей. Ежегодно выдаёт ~$10-12 млн грантов.",
      "https://bobwoodrufffoundation.org/donate/", 14000000, 78, 2006, date(2024, 12, 31),
      ["veterans", "mental-health"],
      _us_pp("208853847"), "irs_990", _verify_us(), "medium"),

    # ============== UK (6) ==============
    E("cafod", "GB", "1160384", "people",
      "Catholic Agency for Overseas Development (CAFOD)", "CAFOD — Catholic Agency for Overseas Development",
      "UK Catholic international development agency — emergency relief, long-term programmes, advocacy.",
      "Британское католическое агентство международного развития — экстренная помощь, долгосрочные программы, адвокация.",
      "CAFOD (Charity Commission #1160384, founded 1962, the official Catholic aid agency for England and Wales) works in ~40 countries on emergency relief (Ukraine, Gaza, Sudan, climate disasters), long-term development partnerships with local Catholic and secular partners, and UK-side advocacy on debt relief, climate finance, and tax justice.",
      "CAFOD (Charity Commission #1160384, основан в 1962 году, официальное католическое агентство помощи Англии и Уэльса) работает в ~40 странах: экстренная помощь (Украина, Газа, Судан, климатические бедствия), долгосрочные партнёрства развития с местными католическими и светскими партнёрами, адвокация в Великобритании по списанию долгов, климатическому финансированию, налоговой справедливости.",
      "https://cafod.org.uk/give", 95000000, 88, 1962, date(2024, 3, 31),
      ["faith-based", "humanitarian-medicine", "poverty-reduction"],
      _uk_cc("1160384"), "annual_report", _verify_uk()),

    E("tearfund", "GB", "265464", "people",
      "Tearfund", "Tearfund",
      "UK Christian relief and development charity — works through local churches in ~50 countries.",
      "Британская христианская гуманитарная и организация развития — работает через местные церкви в ~50 странах.",
      "Tearfund (Charity Commission #265464, founded 1968) is a British evangelical Christian relief and development charity. Works through local churches in ~50 countries on disaster response (Türkiye-Syria 2023, Yemen, DRC), long-term programs on water/sanitation, sustainable livelihoods, and economic empowerment.",
      "Tearfund (Charity Commission #265464, основан в 1968 году) — британская евангельская христианская гуманитарная организация и организация развития. Работает через местные церкви в ~50 странах: реагирование на бедствия (Турция-Сирия 2023, Йемен, ДРК), долгосрочные программы по воде/санитарии, устойчивым средствам к существованию, экономическому расширению прав.",
      "https://www.tearfund.org/donate", 105000000, 86, 1968, date(2024, 3, 31),
      ["faith-based", "humanitarian-medicine", "poverty-reduction"],
      _uk_cc("265464"), "annual_report", _verify_uk()),

    E("youngminds", "GB", "1016968", "people",
      "YoungMinds", "YoungMinds",
      "UK youth-mental-health charity — Parents Helpline, training, federal CYP-mental-health policy.",
      "Британская молодёжная организация по психическому здоровью — Parents Helpline, обучение, федеральная политика CYP.",
      "YoungMinds (Charity Commission #1016968, founded 1992) is the UK's leading children & young people's (CYP) mental-health charity. Operates the Parents Helpline (free advice line for parents worried about their child), runs school-based training, federal advocacy on the CYP Mental Health Standards, and the Youth Activists peer-support network.",
      "YoungMinds (Charity Commission #1016968, основан в 1992 году) — ведущая в Великобритании благотворительная организация по психическому здоровью детей и молодёжи (CYP). Управляет Parents Helpline (бесплатная линия консультаций для родителей, обеспокоенных за своего ребёнка), ведёт обучение в школах, федеральную адвокацию CYP Mental Health Standards, сеть Youth Activists.",
      "https://www.youngminds.org.uk/about-us/donate/", 12000000, 78, 1992, date(2024, 3, 31),
      ["youth-mental-health", "mental-health", "child-welfare"],
      _uk_cc("1016968"), "annual_report", _verify_uk(), "medium"),

    E("pancreatic-cancer-uk", "GB", "1112708", "people",
      "Pancreatic Cancer UK", "Pancreatic Cancer UK",
      "UK's leading pancreatic cancer charity — research, support line, awareness.",
      "Ведущая британская организация по раку поджелудочной железы — исследования, линия поддержки, информирование.",
      "Pancreatic Cancer UK (Charity Commission #1112708, founded 1996) is the UK's leading pancreatic cancer charity. Funds research grants (the only UK charity dedicated solely to PC research), runs the only specialist UK Pancreatic Cancer Support Line, lobbies for earlier diagnosis. PC has the lowest survival rate of all common cancers (~7% 5-year survival).",
      "Pancreatic Cancer UK (Charity Commission #1112708, основана в 1996 году) — ведущая британская организация по раку поджелудочной железы. Финансирует исследовательские гранты (единственная британская благотворительная организация, посвящённая исключительно исследованиям PC), ведёт единственную специализированную в Великобритании Pancreatic Cancer Support Line, лоббирует более раннюю диагностику. PC имеет самый низкий показатель выживаемости среди всех распространённых видов рака (~7% 5-летняя выживаемость).",
      "https://www.pancreaticcancer.org.uk/donate", 12000000, 76, 1996, date(2024, 3, 31),
      ["cancer-research", "global-health"],
      _uk_cc("1112708"), "annual_report", _verify_uk(), "medium"),

    E("bowel-cancer-uk", "GB", "1071038", "people",
      "Bowel Cancer UK", "Bowel Cancer UK",
      "UK's leading bowel cancer charity — research, support, screening advocacy.",
      "Ведущая британская организация по раку кишечника — исследования, поддержка, адвокация скрининга.",
      "Bowel Cancer UK (Charity Commission #1071038, founded 1987 as Beating Bowel Cancer; merged 2017) is the UK's leading bowel cancer charity. Funds research, runs Patients & Family helpline + online community, advocates for FIT-test bowel cancer screening rollout, lower screening start age, and improved access to genetics testing.",
      "Bowel Cancer UK (Charity Commission #1071038, основан в 1987 году как Beating Bowel Cancer; объединились в 2017 году) — ведущая британская организация по раку кишечника. Финансирует исследования, ведёт Patients & Family helpline + онлайн-сообщество, лоббирует развёртывание FIT-теста для скрининга, более низкий возраст начала скрининга, улучшенный доступ к генетическому тестированию.",
      "https://www.bowelcanceruk.org.uk/donate-now/", 7500000, 78, 1987, date(2024, 3, 31),
      ["cancer-research", "global-health"],
      _uk_cc("1071038"), "annual_report", _verify_uk(), "medium"),

    E("woodland-trust", "GB", "294344", "planet",
      "Woodland Trust", "Woodland Trust",
      "UK's largest woodland conservation charity — protects native woods, plants new ones.",
      "Крупнейшая в Великобритании организация по защите лесов — защищает родные леса, сажает новые.",
      "Woodland Trust (Charity Commission #294344, founded 1972) is the UK's largest woodland-conservation charity. Manages ~1,000 woodland sites covering ~30K hectares, plants ~50M trees per decade, runs Big Climate Fightback campaigns, advocates for ancient-woodland legal protection. Ancient woodland covers only ~2.5% of UK land area.",
      "Woodland Trust (Charity Commission #294344, основан в 1972 году) — крупнейшая в Великобритании благотворительная организация по защите лесов. Управляет ~1000 лесными участками общей площадью ~30 тыс. гектаров, сажает ~50 млн деревьев за десятилетие, ведёт кампании Big Climate Fightback, лоббирует юридическую защиту древних лесов. Древние леса покрывают лишь ~2,5% территории Великобритании.",
      "https://www.woodlandtrust.org.uk/give-money/", 100000000, 78, 1972, date(2024, 3, 31),
      ["forest-protection", "conservation", "biodiversity-defense"],
      _uk_cc("294344"), "annual_report", _verify_uk()),

    # ============== Canada (4) ==============
    E("unicef-canada", "CA", "12200-9128-RR0001", "people",
      "UNICEF Canada", "UNICEF Canada",
      "Canadian National Committee for UNICEF — funds global UNICEF programmes.",
      "Канадский национальный комитет UNICEF — финансирует глобальные программы UNICEF.",
      "UNICEF Canada (CRA #12200-9128-RR0001) is the Canadian National Committee for UNICEF — one of 33 national committees that raise funds for UNICEF's global child-survival, education, child protection and emergency-relief programs. Currently emphasising Sudan crisis, Gaza, and Pacific climate-disaster response.",
      "UNICEF Canada (CRA #12200-9128-RR0001) — канадский национальный комитет UNICEF, один из 33 национальных комитетов, собирающих средства для глобальных программ UNICEF в области выживания детей, образования, защиты детей и экстренной помощи. Текущий фокус: кризис в Судане, Газа, климатические бедствия в Тихоокеанском регионе.",
      "https://www.unicef.ca/en/donate", 65000000, 84, 1955, date(2024, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.ca/en/about-us/financial-statements", "annual_report", _verify_ca()),

    E("plan-international-canada", "CA", "11892-8993-RR0001", "people",
      "Plan International Canada", "Plan International Canada",
      "Canadian arm of Plan International — children's rights and gender equality globally.",
      "Канадское отделение Plan International — права детей и гендерное равенство по всему миру.",
      "Plan International Canada (CRA #11892-8993-RR0001) is the Canadian arm of Plan International, focused on children's rights with strong emphasis on gender equality. Operates in ~50 countries: education access, child protection, sexual & reproductive health, adolescent girls' programmes (Because I am a Girl), emergency response.",
      "Plan International Canada (CRA #11892-8993-RR0001) — канадское отделение Plan International, сосредоточенное на правах детей с сильным акцентом на гендерное равенство. Работает в ~50 странах: доступ к образованию, защита детей, сексуальное и репродуктивное здоровье, программы для девочек-подростков (Because I am a Girl), экстренное реагирование.",
      "https://plancanada.ca/donate/", 240000000, 86, 1969, date(2024, 6, 30),
      ["child-welfare", "womens-rights", "humanitarian-medicine"],
      "https://plancanada.ca/about/financials/", "annual_report", _verify_ca()),

    E("kids-help-phone-canada", "CA", "13075-9743-RR0001", "people",
      "Kids Help Phone", "Kids Help Phone — Канадская молодёжная линия",
      "Canada's only national 24/7 e-mental-health service for young people — phone, text, online.",
      "Единственная в Канаде национальная круглосуточная электронная служба психического здоровья для молодёжи — телефон, текст, онлайн.",
      "Kids Help Phone (CRA #13075-9743-RR0001, founded 1989) is Canada's only national 24/7 e-mental-health service for young people aged 5-29 — phone (1-800-668-6868), text (CONNECT to 686868), online live chat. Available in English and French. Counsellors are trained mental-health professionals; calls are confidential.",
      "Kids Help Phone (CRA #13075-9743-RR0001, основан в 1989 году) — единственная в Канаде национальная круглосуточная электронная служба психического здоровья для молодёжи 5-29 лет — телефон (1-800-668-6868), текст (CONNECT на 686868), онлайн-чат. Доступна на английском и французском. Консультанты — обученные специалисты в области психического здоровья; звонки конфиденциальны.",
      "https://kidshelpphone.ca/donate/", 50000000, 78, 1989, date(2024, 12, 31),
      ["youth-mental-health", "mental-health", "suicide-prevention"],
      "https://kidshelpphone.ca/about/financials/", "annual_report", _verify_ca()),

    E("oxfam-canada", "CA", "12952-1683-RR0001", "people",
      "Oxfam Canada", "Oxfam Canada",
      "Canadian member of Oxfam confederation — feminist approach to ending poverty and injustice.",
      "Канадский член конфедерации Oxfam — феминистский подход к прекращению бедности и несправедливости.",
      "Oxfam Canada (CRA #12952-1683-RR0001, founded 1963) is the Canadian member of Oxfam International. Distinct feminist approach: gender-just emergency response, sexual & reproductive health & rights, women's economic empowerment. Programs in ~25 countries; Canadian advocacy on aid budget, climate finance, and inequality.",
      "Oxfam Canada (CRA #12952-1683-RR0001, основан в 1963 году) — канадский член Oxfam International. Особый феминистский подход: гендерно-справедливое экстренное реагирование, сексуальное и репродуктивное здоровье и права, экономическое расширение прав женщин. Программы в ~25 странах; адвокация в Канаде по бюджету помощи, климатическому финансированию, неравенству.",
      "https://www.oxfam.ca/donate/", 35000000, 80, 1963, date(2024, 3, 31),
      ["poverty-reduction", "womens-rights", "humanitarian-medicine"],
      "https://www.oxfam.ca/about/financials/", "annual_report", _verify_ca()),

    # ============== Australia (3) ==============
    E("lifeline-australia", "AU", "ABN-84-081-031-263", "people",
      "Lifeline Australia", "Lifeline Australia",
      "Australia's national crisis support and suicide prevention service — 13 11 14, 24/7.",
      "Национальная служба кризисной поддержки и профилактики суицидов Австралии — 13 11 14, круглосуточно.",
      "Lifeline Australia (ABN 84 081 031 263, founded 1963 by Reverend Sir Alan Walker) operates Australia's national crisis support and suicide-prevention service: 13 11 14 phone line, online chat, text. ~40 local Lifeline Centres deliver frontline counselling. Receives ~3,500 contacts per day. Independent of government clinical mental-health services but referrer-friendly.",
      "Lifeline Australia (ABN 84 081 031 263, основан в 1963 году преподобным сэром Аланом Уокером) управляет национальной службой кризисной поддержки и профилактики суицидов Австралии: телефон 13 11 14, онлайн-чат, текст. ~40 местных центров Lifeline оказывают консультации на фронтлайне. Получает ~3500 контактов в день. Независим от государственных клинических служб психического здоровья, но дружественен к направлениям.",
      "https://www.lifeline.org.au/donate/", 85000000, 80, 1963, date(2024, 6, 30),
      ["mental-health", "suicide-prevention"],
      "https://www.lifeline.org.au/about/financial-information/", "annual_report", _verify_au()),

    E("black-dog-institute", "AU", "ABN-12-115-954-197", "people",
      "Black Dog Institute", "Black Dog Institute",
      "Mental-health research and clinical services — affiliated with UNSW Sydney.",
      "Исследования и клинические услуги в области психического здоровья — аффилированный с UNSW Сидней.",
      "Black Dog Institute (ABN 12 115 954 197, founded 2002) is a translational mental-health research institute affiliated with UNSW Sydney. Operates clinical services for mood disorders, runs research studies on suicide prevention, online CBT (myCompass), and workplace mental health. Co-developed Australia's national clinical guidelines for depression management.",
      "Black Dog Institute (ABN 12 115 954 197, основан в 2002 году) — трансляционный исследовательский институт в области психического здоровья, аффилированный с UNSW Сидней. Управляет клиническими услугами для расстройств настроения, ведёт исследования по профилактике суицида, онлайн-КПТ (myCompass), психическому здоровью на рабочем месте. Сооснователь национальных клинических рекомендаций Австралии по лечению депрессии.",
      "https://www.blackdoginstitute.org.au/donate/", 30000000, 82, 2002, date(2024, 6, 30),
      ["mental-health", "suicide-prevention"],
      "https://www.blackdoginstitute.org.au/about-us/governance-financials/", "annual_report", _verify_au()),

    E("oz-harvest", "AU", "ABN-46-219-805-214", "people",
      "OzHarvest", "OzHarvest",
      "Australia's leading food-rescue organisation — diverts 200+ tons of surplus food per week.",
      "Ведущая в Австралии организация по спасению еды — отводит 200+ тонн излишков еды в неделю.",
      "OzHarvest (ABN 46 219 805 214, founded 2004 by Ronni Kahn) rescues quality surplus food from ~2,500 commercial outlets across Australia (supermarkets, restaurants, cafés, airlines) and delivers it to ~1,800 charities feeding people experiencing food insecurity. Diverts ~200 tons per week — equivalent to ~600K meals.",
      "OzHarvest (ABN 46 219 805 214, основан в 2004 году Ронни Каном) спасает качественные излишки еды из ~2500 коммерческих точек по всей Австралии (супермаркеты, рестораны, кафе, авиакомпании) и доставляет их ~1800 благотворительным организациям, кормящим людей в продовольственной нужде. Отводит ~200 тонн в неделю — эквивалент ~600 тыс. блюд.",
      "https://www.ozharvest.org/donate/", 32000000, 87, 2004, date(2024, 6, 30),
      ["food-rescue", "food-banks", "hunger"],
      "https://www.ozharvest.org/financials/", "annual_report", _verify_au()),

    # ============== Italy (6) ==============
    E("save-the-children-italia", "IT", "IT-97227450158", "people",
      "Save the Children Italia", "Save the Children Italia",
      "Italian member of Save the Children International — child rights, education, refugees.",
      "Итальянский член Save the Children International — права детей, образование, беженцы.",
      "Save the Children Italia (C.F. 97227450158, founded 1998) is the Italian member of Save the Children International. Domestic Italy programmes on child poverty (Italy's Atlas of Childhood Poverty), educational inequality (Illuminiamo il Futuro), and refugee/migrant children at the Mediterranean Sea border. International funding via STC International.",
      "Save the Children Italia (C.F. 97227450158, основан в 1998 году) — итальянский член Save the Children International. Внутренние программы в Италии по детской бедности (Atlas of Childhood Poverty), образовательному неравенству (Illuminiamo il Futuro), детям-беженцам и мигрантам на средиземноморской границе. Международное финансирование через STC International.",
      "https://www.savethechildren.it/dona", 95000000, 86, 1998, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "refugees"],
      "https://www.savethechildren.it/cosa-facciamo/bilancio-trasparenza", "annual_report", _verify_it()),

    E("airc-italy", "IT", "IT-80051890152", "people",
      "Fondazione AIRC per la Ricerca sul Cancro", "AIRC — Fondazione AIRC per la Ricerca sul Cancro",
      "Italy's leading cancer research foundation — funds Italian cancer scientists and clinical trials.",
      "Ведущий итальянский фонд онкологических исследований — финансирует итальянских онкологических учёных и клинические испытания.",
      "Fondazione AIRC (C.F. 80051890152, founded 1965) is Italy's largest cancer research charity. Funds ~5,000 Italian cancer researchers across ~700 projects and ~150 clinical trials. Iconic Le Arance della Salute (Oranges of Health) annual fundraising campaign in Italian piazzas.",
      "Fondazione AIRC (C.F. 80051890152, основан в 1965 году) — крупнейшая в Италии благотворительная организация по онкологическим исследованиям. Финансирует ~5000 итальянских онкологических исследователей в ~700 проектах и ~150 клинических испытаниях. Знаковая ежегодная фандрайзинговая кампания Le Arance della Salute (Апельсины здоровья) на итальянских площадях.",
      "https://www.airc.it/sostienici", 145000000, 84, 1965, date(2023, 12, 31),
      ["cancer-research", "global-health"],
      "https://www.airc.it/chi-siamo/bilancio", "annual_report", _verify_it()),

    E("telethon-italy", "IT", "IT-04879781005", "people",
      "Fondazione Telethon", "Fondazione Telethon",
      "Italian rare-disease research foundation — pioneered gene therapy with Strimvelis (ADA-SCID).",
      "Итальянский фонд исследований редких болезней — пионер генной терапии со Strimvelis (ADA-SCID).",
      "Fondazione Telethon (C.F. 04879781005, founded 1990) funds Italian research into genetic rare diseases. Funded development of Strimvelis (gene therapy for ADA-SCID, approved EU 2016) at the Telethon-supported San Raffaele Telethon Institute (TIGET, Milan). Annual TV Telethon fundraising marathon.",
      "Fondazione Telethon (C.F. 04879781005, основан в 1990 году) финансирует итальянские исследования генетических редких заболеваний. Финансировал разработку Strimvelis (генная терапия ADA-SCID, одобрена в ЕС в 2016 году) в Telethon-поддерживаемом институте San Raffaele Telethon Institute (TIGET, Милан). Ежегодный телевизионный телетон-фандрайзинг.",
      "https://www.telethon.it/dona", 60000000, 88, 1990, date(2023, 12, 31),
      ["rare-disease", "global-health"],
      "https://www.telethon.it/chi-siamo/trasparenza/bilancio", "annual_report", _verify_it()),

    E("caritas-italiana", "IT", "IT-80102590587", "people",
      "Caritas Italiana", "Caritas Italiana",
      "Italian Catholic Bishops' Conference humanitarian arm — domestic poverty, international cooperation.",
      "Гуманитарное крыло Конференции католических епископов Италии — внутренняя бедность, международное сотрудничество.",
      "Caritas Italiana (C.F. 80102590587, founded 1971) is the humanitarian arm of the Italian Catholic Bishops' Conference (CEI). Coordinates ~220 diocesan Caritas across Italy on domestic anti-poverty work, refugees and migrants reception, plus international development and emergency response (Ukraine, Syria, Sudan).",
      "Caritas Italiana (C.F. 80102590587, основан в 1971 году) — гуманитарное крыло Конференции католических епископов Италии (CEI). Координирует ~220 епархиальных Caritas по всей Италии: внутренняя борьба с бедностью, приём беженцев и мигрантов, плюс международное развитие и экстренное реагирование (Украина, Сирия, Судан).",
      "https://www.caritas.it/dona", 85000000, 89, 1971, date(2023, 12, 31),
      ["faith-based", "poverty-reduction", "humanitarian-medicine"],
      "https://www.caritas.it/chi-siamo/trasparenza/", "annual_report", _verify_it()),

    E("actionaid-italia", "IT", "IT-09686720153", "people",
      "ActionAid Italia", "ActionAid Italia",
      "Italian member of ActionAid International — child sponsorship, gender justice, food rights.",
      "Итальянский член ActionAid International — спонсорство детей, гендерная справедливость, продовольственные права.",
      "ActionAid Italia (C.F. 09686720153, founded 1989) is the Italian member of ActionAid International, an Africa-headquartered (Johannesburg) federation. Italian-domestic anti-poverty programs (food poverty in Italy, women's empowerment), plus international child-sponsorship and program work in ~25 countries.",
      "ActionAid Italia (C.F. 09686720153, основан в 1989 году) — итальянский член ActionAid International, федерации со штаб-квартирой в Африке (Йоханнесбург). Внутренние антибедные программы в Италии (продовольственная бедность в Италии, расширение прав женщин), плюс международное спонсорство детей и программная работа в ~25 странах.",
      "https://www.actionaid.it/sostienici", 65000000, 82, 1989, date(2023, 12, 31),
      ["child-welfare", "poverty-reduction", "womens-rights"],
      "https://www.actionaid.it/chi-siamo/trasparenza-bilanci", "annual_report", _verify_it()),

    E("lega-del-filo-doro", "IT", "IT-80003150421", "people",
      "Lega del Filo d'Oro", "Lega del Filo d'Oro — итальянский фонд слепоглухих",
      "Italian foundation for deafblind children and adults — rehabilitation, education, family support.",
      "Итальянский фонд для слепоглухих детей и взрослых — реабилитация, образование, поддержка семей.",
      "Lega del Filo d'Oro (C.F. 80003150421, founded 1964) is Italy's primary organisation for deafblind people and people with multi-sensory disabilities. Operates 5 national centres for early intervention, education, rehabilitation, residential care, and family support. ~50K people supported in their lifetime.",
      "Lega del Filo d'Oro (C.F. 80003150421, основан в 1964 году) — основная итальянская организация для слепоглухих и людей с мульти-сенсорными нарушениями. Управляет 5 национальными центрами раннего вмешательства, образования, реабилитации, резиденциального ухода и поддержки семей. ~50 тыс. человек получили помощь за всю историю.",
      "https://www.legadelfilodoro.it/dona", 50000000, 86, 1964, date(2023, 12, 31),
      ["deafblind", "disability-services"],
      "https://www.legadelfilodoro.it/it/trasparenza/bilancio", "annual_report", _verify_it()),

    # ============== Spain (6) ==============
    E("caritas-espanola", "ES", "ES-R2800023H", "people",
      "Cáritas Española", "Cáritas Española",
      "Spanish Catholic Bishops' Conference social-services confederation — Spain's largest welfare network.",
      "Конфедерация социальных служб Конференции католических епископов Испании — крупнейшая социальная сеть Испании.",
      "Cáritas Española (NIF R2800023H, founded 1947) is the social-services confederation of the Spanish Episcopal Conference, with ~70 diocesan Cáritas plus regional federations. ~80K paid staff and volunteers serve ~3M people annually across Spain — homelessness, food, employment, immigration, addictions. Plus international cooperation in ~50 countries.",
      "Cáritas Española (NIF R2800023H, основан в 1947 году) — конфедерация социальных служб Испанской епископальной конференции, ~70 епархиальных Cáritas плюс региональные федерации. ~80 тыс. оплачиваемых сотрудников и добровольцев обслуживают ~3 млн человек ежегодно в Испании — бездомность, питание, трудоустройство, иммиграция, зависимости. Плюс международное сотрудничество в ~50 странах.",
      "https://www.caritas.es/donativos/", 480000000, 88, 1947, date(2023, 12, 31),
      ["faith-based", "homelessness", "poverty-reduction", "humanitarian-medicine"],
      "https://www.caritas.es/quienes-somos/transparencia/", "annual_report", _verify_es()),

    E("msf-espana", "ES", "ES-G81031440", "people",
      "Médicos Sin Fronteras España", "Médicos Sin Fronteras España",
      "Spanish section of MSF — recruits Spanish medical staff, raises funds for global emergencies.",
      "Испанская секция MSF — набирает испанский медперсонал, собирает средства для глобальных кризисов.",
      "Médicos Sin Fronteras España (NIF G81031440, founded 1986) is the Spanish section of the international MSF movement. Recruits Spanish medical, paramedical and logistical staff for MSF projects worldwide, fundraises in Spain. Operational responsibility for Spanish-language Latin America projects.",
      "Médicos Sin Fronteras España (NIF G81031440, основан в 1986 году) — испанская секция международного движения MSF. Набирает испанский медицинский, парамедицинский и логистический персонал для проектов MSF по всему миру, собирает средства в Испании. Операционная ответственность за испаноязычные проекты в Латинской Америке.",
      "https://www.msf.es/dona", 165000000, 88, 1986, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response"],
      "https://www.msf.es/conocenos/transparencia", "annual_report", _verify_es()),

    E("anar-spain", "ES", "ES-G80157014", "people",
      "Fundación ANAR", "Fundación ANAR — испанская детская правозащитная организация",
      "Spanish foundation operating Europe's longest-running children's rights helpline.",
      "Испанский фонд, ведущий старейшую в Европе детскую правозащитную линию помощи.",
      "Fundación ANAR (NIF G80157014, founded 1970 as Ayuda a Niños y Adolescentes en Riesgo) operates the ANAR Helpline (900 20 20 10) — free, anonymous, 24/7 — Europe's longest-running children's rights helpline. ~600K calls handled per year. Also runs an adult-helpline for adults concerned about children. Publishes annual ANAR Report on child abuse trends in Spain.",
      "Fundación ANAR (NIF G80157014, основан в 1970 году как Ayuda a Niños y Adolescentes en Riesgo) ведёт ANAR Helpline (900 20 20 10) — бесплатную, анонимную, круглосуточную — старейшую в Европе детскую правозащитную линию. ~600 тыс. звонков в год. Также ведёт линию для взрослых, обеспокоенных детьми. Публикует ежегодный ANAR Report по тенденциям насилия над детьми в Испании.",
      "https://www.anar.org/donaciones/", 12000000, 84, 1970, date(2023, 12, 31),
      ["child-protection", "child-welfare", "mental-health"],
      "https://www.anar.org/transparencia/", "annual_report", _verify_es(), "medium"),

    E("save-the-children-espana", "ES", "ES-G79362497", "people",
      "Save the Children España", "Save the Children España",
      "Spanish member of Save the Children International — domestic child poverty + international.",
      "Испанский член Save the Children International — внутренняя детская бедность + международное.",
      "Save the Children España (NIF G79362497, founded 1997) is the Spanish member of Save the Children International. Domestic Spain programs on child poverty (which affects ~33% of Spanish children), school dropout, refugee and migrant children, and gender-based violence prevention.",
      "Save the Children España (NIF G79362497, основан в 1997 году) — испанский член Save the Children International. Внутренние программы в Испании по детской бедности (затрагивает ~33% испанских детей), школьному отсеву, детям-беженцам и мигрантам, профилактике гендерного насилия.",
      "https://www.savethechildren.es/colabora", 90000000, 84, 1997, date(2023, 12, 31),
      ["child-welfare", "poverty-reduction", "refugees"],
      "https://www.savethechildren.es/transparencia", "annual_report", _verify_es()),

    E("medicos-del-mundo-espana", "ES", "ES-G79408852", "people",
      "Médicos del Mundo España", "Médicos del Mundo España",
      "Spanish section of Médecins du Monde — health for excluded populations in Spain and globally.",
      "Испанская секция Médecins du Monde — медицина для исключённых групп в Испании и в мире.",
      "Médicos del Mundo España (NIF G79408852, founded 1990) is the Spanish section of the Médecins du Monde international network. Domestic Spain clinics serve undocumented migrants, sex workers, drug users, and homeless people; international programmes in ~25 countries on humanitarian and primary-health-care access.",
      "Médicos del Mundo España (NIF G79408852, основан в 1990 году) — испанская секция международной сети Médecins du Monde. Внутренние клиники в Испании обслуживают недокументированных мигрантов, секс-работников, наркопотребителей, бездомных; международные программы в ~25 странах по гуманитарному и первичному медицинскому доступу.",
      "https://www.medicosdelmundo.org/colabora/dona", 45000000, 82, 1990, date(2023, 12, 31),
      ["humanitarian-medicine", "global-health"],
      "https://www.medicosdelmundo.org/quienes-somos/transparencia", "annual_report", _verify_es()),

    E("greenpeace-espana", "ES", "ES-G28491050", "planet",
      "Greenpeace España", "Greenpeace España",
      "Spanish national office of Greenpeace — climate, oceans, agriculture, energy.",
      "Испанское национальное отделение Greenpeace — климат, океаны, сельское хозяйство, энергия.",
      "Greenpeace España (NIF G28491050, founded 1984) is the Spanish national office of Greenpeace International. Campaigns on climate change, ocean protection (Mediterranean and Cantabrian Sea), industrial agriculture reform, energy transition. Like other Greenpeace nationals, refuses government and corporate funding.",
      "Greenpeace España (NIF G28491050, основан в 1984 году) — испанское национальное отделение Greenpeace International. Кампании по изменению климата, защите океанов (Средиземное и Кантабрийское моря), реформе промышленного сельского хозяйства, энергетическому переходу. Как другие национальные офисы Greenpeace, отказывается от государственного и корпоративного финансирования.",
      "https://es.greenpeace.org/es/colabora/hazte-socio/", 25000000, 75, 1984, date(2023, 12, 31),
      ["climate", "oceans", "environment"],
      "https://es.greenpeace.org/es/quienes-somos/transparencia/", "annual_report", _verify_es()),

    # ============== Ireland (3) ==============
    E("irish-red-cross", "IE", "IE-CHY-3950", "people",
      "Irish Red Cross", "Irish Red Cross",
      "Irish national society of the International Red Cross — domestic emergency + international.",
      "Ирландское национальное общество Международного Красного Креста — внутренняя экстренная помощь + международное.",
      "Irish Red Cross (CHY 3950, RCN 20003729, founded 1939) is the Irish national society of the International Red Cross Movement. Operates ambulance and first-aid services across Ireland, refugee resettlement (post-2022 Ukraine response), and international Disaster Relief Appeal funding.",
      "Irish Red Cross (CHY 3950, RCN 20003729, основан в 1939 году) — ирландское национальное общество Международного движения Красного Креста. Управляет службами скорой помощи и первой помощи по всей Ирландии, расселение беженцев (ответ на Украину после 2022 года), международное финансирование Disaster Relief Appeal.",
      "https://www.redcross.ie/donate/", 35000000, 84, 1939, date(2023, 12, 31),
      ["emergency-response", "disaster-relief", "refugees"],
      "https://www.redcross.ie/about-us/governance-and-financials/", "annual_report", _verify_ie()),

    E("trocaire", "IE", "IE-CHY-5883", "people",
      "Trócaire", "Trócaire",
      "Irish Catholic agency for international development — emergency + long-term partnerships.",
      "Ирландское католическое агентство международного развития — экстренная помощь + долгосрочные партнёрства.",
      "Trócaire (CHY 5883, RCN 20009601, founded 1973 by Irish Catholic Bishops' Conference) is the official overseas-development agency of the Catholic Church in Ireland. Works in ~20 countries on long-term development (women's empowerment, climate justice, livelihoods) plus emergency response. Iconic annual Trócaire Lenten Box fundraising campaign in Ireland.",
      "Trócaire (CHY 5883, RCN 20009601, основан в 1973 году ирландской Конференцией католических епископов) — официальное зарубежное агентство развития Католической церкви в Ирландии. Работает в ~20 странах: долгосрочное развитие (расширение прав женщин, климатическая справедливость, средства к существованию) плюс экстренное реагирование. Знаковая ежегодная кампания Trócaire Lenten Box в Ирландии.",
      "https://www.trocaire.org/donate/", 80000000, 86, 1973, date(2024, 2, 29),
      ["faith-based", "humanitarian-medicine", "poverty-reduction"],
      "https://www.trocaire.org/about-us/financials-and-reports/", "annual_report", _verify_ie()),

    E("concern-worldwide", "IE", "IE-CHY-5745", "people",
      "Concern Worldwide", "Concern Worldwide",
      "Ireland-headquartered international humanitarian NGO — extreme poverty + emergency response in ~25 countries.",
      "Международная гуманитарная НПО со штаб-квартирой в Ирландии — крайняя бедность + экстренная помощь в ~25 странах.",
      "Concern Worldwide (CHY 5745, RCN 20009090, founded 1968 in response to the Biafra famine) is one of the largest international humanitarian NGOs headquartered in Ireland. Works in ~25 countries reaching the world's poorest people through long-term programmes, emergency response, and policy advocacy. Co-publisher of the annual Global Hunger Index.",
      "Concern Worldwide (CHY 5745, RCN 20009090, основана в 1968 году в ответ на голод в Биафре) — одна из крупнейших международных гуманитарных НПО со штаб-квартирой в Ирландии. Работает в ~25 странах, помогая беднейшим людям мира через долгосрочные программы, экстренное реагирование и политическую адвокацию. Соиздатель ежегодного Global Hunger Index.",
      "https://www.concern.net/donate", 200000000, 89, 1968, date(2023, 12, 31),
      ["humanitarian-medicine", "poverty-reduction", "emergency-response"],
      "https://www.concern.net/about/financial-information", "annual_report", _verify_ie()),

    # ============== Norway (3) ==============
    E("redd-barna", "NO", "NO-956350174", "people",
      "Redd Barna (Save the Children Norway)", "Redd Barna — норвежское отделение Save the Children",
      "Norwegian member of Save the Children International — child rights, emergency, advocacy.",
      "Норвежский член Save the Children International — права детей, экстренная помощь, адвокация.",
      "Redd Barna (Org 956 350 174, founded 1946) is the Norwegian member of Save the Children International. Norway has long been a major donor government for international children's-rights work — Redd Barna leverages public-private partnerships with Norwegian government aid agency Norad. International programs in ~25 countries plus Norwegian-domestic work.",
      "Redd Barna (Org 956 350 174, основан в 1946 году) — норвежский член Save the Children International. Норвегия давно является крупным донорским правительством для международной работы по правам детей — Redd Barna использует государственно-частные партнёрства с норвежским агентством международного развития Norad. Международные программы в ~25 странах плюс работа внутри Норвегии.",
      "https://www.reddbarna.no/gi-gave/", 110000000, 88, 1946, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "child-protection"],
      "https://www.reddbarna.no/om-oss/arsrapport-og-regnskap/", "annual_report", _verify_no()),

    E("norwegian-refugee-council", "NO", "NO-977538142", "people",
      "Norwegian Refugee Council (NRC)", "Norwegian Refugee Council (NRC) — Flyktninghjelpen",
      "Independent humanitarian org for displaced people — operates in ~40 conflict-affected countries.",
      "Независимая гуманитарная организация для перемещённых лиц — работает в ~40 странах, затронутых конфликтами.",
      "Norwegian Refugee Council (Org 977 538 142, founded 1946 to help post-WWII refugees) is one of the world's largest humanitarian organisations focused exclusively on displacement. Operates in ~40 countries (Ukraine, Sudan, Syria, Afghanistan, Yemen, Colombia, Myanmar, DRC) providing emergency shelter, food security, water, education in emergencies, legal information, and camp management. Runs the Internal Displacement Monitoring Centre.",
      "Norwegian Refugee Council (Org 977 538 142, основан в 1946 году для помощи послевоенным беженцам) — одна из крупнейших в мире гуманитарных организаций, исключительно сосредоточенная на перемещении. Работает в ~40 странах (Украина, Судан, Сирия, Афганистан, Йемен, Колумбия, Мьянма, ДРК), обеспечивая экстренное жильё, продовольственную безопасность, воду, образование в чрезвычайных ситуациях, юридическую информацию и управление лагерями. Ведёт Internal Displacement Monitoring Centre.",
      "https://www.nrc.no/donate/", 920000000, 91, 1946, date(2023, 12, 31),
      ["refugees", "humanitarian-medicine", "emergency-response"],
      "https://www.nrc.no/about-us/our-organisation/", "annual_report", _verify_no()),

    E("sos-barnebyer-norge", "NO", "NO-952357968", "people",
      "SOS-barnebyer Norge", "SOS-barnebyer Norge",
      "Norwegian member of SOS Children's Villages — orphan care + family-strengthening worldwide.",
      "Норвежский член SOS Children's Villages — забота о сиротах + укрепление семей по всему миру.",
      "SOS-barnebyer Norge (Org 952 357 968, founded 1965) is the Norwegian member federation of SOS Children's Villages International. Funds family-based care for children without parental care across ~135 countries. Norway is one of the largest per-capita donors to SOS Children's Villages globally.",
      "SOS-barnebyer Norge (Org 952 357 968, основан в 1965 году) — норвежская федерация-член SOS Children's Villages International. Финансирует семейную опеку детей без родительской заботы в ~135 странах. Норвегия — один из крупнейших по показателю на душу населения доноров SOS Children's Villages в мире.",
      "https://www.sos-barnebyer.no/gi-gave/", 75000000, 86, 1965, date(2023, 12, 31),
      ["child-welfare", "child-protection"],
      "https://www.sos-barnebyer.no/om-oss/regnskap-arsrapport/", "annual_report", _verify_no()),
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
            print(f"[migration 0045] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
    print(f"[migration 0045] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0044_extend_country_choices_v310"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

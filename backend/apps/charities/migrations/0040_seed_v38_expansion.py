"""v3.8 catalog expansion — seed 40 charities (250 -> ~290).

Goal: backfill underrepresented cause-tags + scale UK, plus more
Canada / Australia / NZ to balance the regional filter.

Cause-tag gaps targeted:
  - veterans (was 0): +5 US (Wounded Warrior, DAV, T2T, Folds of Honor, IAVA)
  - lgbtq-youth (was 0 explicit): +5 (Trans Lifeline, GLSEN, PFLAG, NCLR,
    Family Equality)
  - domestic-violence (was tagged via womens-rights): +3 (RAINN, NNEDV,
    Futures Without Violence)
  - elderly-care (was 4 senior-care): +3 (NCoA, OATS, Volunteers of America)
  - youth-mentoring (was 0): +3 (Boys & Girls Clubs America,
    Big Brothers Big Sisters US/CA)
  - food-banks (was 0 explicit): +2 (Trussell Trust UK, Foodbank Australia)
  - rare-disease (was 0): +1 (Cystic Fibrosis Foundation)

UK +10: NSPCC, Barnardo's, Trussell Trust, Dogs Trust, Cats Protection,
Action for Children, Help for Heroes, CALM, Battersea Dogs & Cats Home,
Joseph Rowntree Foundation.

Canada +5: CAMH Foundation, Make-A-Wish Canada, Boys & Girls Clubs of
Canada, Big Brothers Big Sisters of Canada, WWF-Canada.

Australia +3: Foodbank Australia, Caritas Australia, St Vincent de Paul
Society (Vinnies) Australia.

Idempotent. Defensive `is_blocked()` per entry. Reverse no-op.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "veterans": {"en": "Veterans & military families", "ru": "Ветераны и семьи военнослужащих"},
    "lgbtq-youth": {"en": "LGBTQ+ youth & families", "ru": "ЛГБТ+ молодёжь и семьи"},
    "domestic-violence": {"en": "Domestic & sexual violence prevention", "ru": "Профилактика домашнего и сексуального насилия"},
    "elderly-care": {"en": "Elderly care", "ru": "Помощь пожилым"},
    "youth-mentoring": {"en": "Youth mentoring", "ru": "Менторство молодёжи"},
    "food-banks": {"en": "Food banks & food security", "ru": "Продовольственные банки и продбезопасность"},
    "rare-disease": {"en": "Rare disease research", "ru": "Исследования редких заболеваний"},
    "child-protection": {"en": "Child protection", "ru": "Защита детей"},
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
        "en": "Verified: registered with ACNC (Australian Charities and Not-for-profits Commission); annual information statement public.",
        "ru": "Подтверждено: зарегистрирован в ACNC (регулятор Австралии); ежегодное info-statement публично.",
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


# Compact entry helper
def E(slug, country, regid, bucket, name_en, name_ru, tagline_en, tagline_ru,
      desc_en, desc_ru, donation, revenue, program_pct, founded, last_filed,
      cause_slugs, source_url, source_kind, methodology, size="large"):
    return {
        "slug": slug,
        "country": country,
        "registration_id": regid,
        "bucket": bucket,
        "name": {"en": name_en, "ru": name_ru},
        "tagline": {"en": tagline_en, "ru": tagline_ru},
        "description": {"en": desc_en, "ru": desc_ru},
        "methodology_note": methodology,
        "logo_url": "",
        "donation_url": donation,
        "size_bucket": size,
        "last_filed_date": last_filed,
        "total_revenue_usd": Decimal(str(revenue)),
        "program_expense_pct": Decimal(str(program_pct)),
        "founded_year": founded,
        "cause_slugs": cause_slugs,
        **_empty_photo(),
        "source_kind": source_kind,
        "source_url": source_url,
    }


SEED: list[dict] = [
    # ============== US LGBTQ+ (5) ==============
    E("trans-lifeline", "US", "473159768", "people",
      "Trans Lifeline", "Trans Lifeline",
      "Peer-support crisis hotline run by and for trans people in the US and Canada.",
      "Линия экстренной поддержки от равных, ведомая трансгендерными людьми, для США и Канады.",
      "Trans Lifeline (EIN 47-3159768, founded 2014) is a peer-support crisis hotline staffed entirely by trans operators, plus a microgrants program for legal name changes and ID documents. Refuses non-consensual emergency-services intervention — never calls police on callers. Serves the US and Canada.",
      "Trans Lifeline (EIN 47-3159768, основан в 2014 году) — кризисная линия поддержки от равных, на которой работают исключительно трансгендерные операторы, плюс программа микрогрантов для смены имени и документов. Принципиально не подключает экстренные службы без согласия — никогда не вызывает полицию к звонящим. Обслуживает США и Канаду.",
      "https://translifeline.org/donate/", 4500000, 80, 2014, date(2024, 6, 30),
      ["lgbtq-youth", "mental-health", "suicide-prevention"],
      _us_pp("473159768"), "irs_990", _verify_us(), "medium"),

    E("glsen", "US", "043234202", "people",
      "GLSEN", "GLSEN — права ЛГБТ+ в школах США",
      "Creates safer K-12 schools for LGBTQ+ students through research, policy and student-led GSAs.",
      "Создаёт безопасные школы для ЛГБТ+ учеников через исследования, политику и ученические клубы GSA.",
      "GLSEN (EIN 04-3234202, founded 1990) works to ensure K-12 schools across the US are safe for LGBTQ+ students. Publishes the biennial National School Climate Survey, supports ~7,000 student-led Gay-Straight Alliances / Genders & Sexualities Alliances, trains educators, and pushes anti-bullying policy.",
      "GLSEN (EIN 04-3234202, основан в 1990 году) работает над тем, чтобы школы (K-12) в США были безопасны для ЛГБТ+ учеников. Публикует ежегодное исследование школьного климата, поддерживает ~7000 ученических клубов GSA, обучает учителей, лоббирует антибуллинговую политику.",
      "https://www.glsen.org/donate", 8500000, 75, 1990, date(2024, 6, 30),
      ["lgbtq-youth", "civil-rights", "education"],
      _us_pp("043234202"), "irs_990", _verify_us()),

    E("pflag", "US", "237434210", "people",
      "PFLAG", "PFLAG — поддержка семей ЛГБТ+",
      "Largest US org of LGBTQ+ people, parents, families and allies — local chapter network.",
      "Крупнейшая в США организация ЛГБТ+ людей, родителей, семей и союзников — сеть местных отделений.",
      "PFLAG (EIN 23-7434210, founded 1973) is the largest US organisation of LGBTQ+ people, their parents, families and allies. Runs ~400 local chapters that hold support meetings for families with newly-out LGBTQ+ members; advocates federally on inclusive education, employment non-discrimination, and trans-affirming healthcare.",
      "PFLAG (EIN 23-7434210, основан в 1973 году) — крупнейшая в США организация ЛГБТ+ людей, их родителей, семей и союзников. Управляет ~400 местными отделениями, проводящими встречи поддержки для семей со впервые открывшимися ЛГБТ+ родственниками; лоббирует федеральные законы по инклюзивному образованию, антидискриминации в трудоустройстве, трансгендерной медицине.",
      "https://pflag.org/donate/", 7500000, 76, 1973, date(2024, 9, 30),
      ["lgbtq-youth", "civil-rights"],
      _us_pp("237434210"), "irs_990", _verify_us(), "medium"),

    E("nclr", "US", "942478839", "people",
      "National Center for Lesbian Rights (NCLR)", "National Center for Lesbian Rights (NCLR)",
      "Legal advocacy for LGBTQ+ rights — courtroom litigation and legislative campaigns since 1977.",
      "Юридическая адвокация прав ЛГБТ+ — судебные процессы и законодательные кампании с 1977 года.",
      "NCLR (EIN 94-2478839, founded 1977) is one of the oldest LGBTQ+ legal-advocacy organisations in the US. Litigates landmark cases on employment, family, immigration, sports inclusion, and trans-rights; runs federal & state legislative-policy campaigns; provides direct legal help via a national hotline.",
      "NCLR (EIN 94-2478839, основан в 1977 году) — одна из старейших организаций США по правовой защите прав ЛГБТ+. Ведёт ключевые судебные дела по трудоустройству, семье, иммиграции, спортивной инклюзии, трансгендерным правам; ведёт федеральные и штатные законодательные кампании; оказывает юридическую помощь через национальную горячую линию.",
      "https://www.nclrights.org/donate/", 9500000, 78, 1977, date(2024, 6, 30),
      ["lgbtq-youth", "civil-rights"],
      _us_pp("942478839"), "irs_990", _verify_us(), "medium"),

    E("family-equality", "US", "043106090", "people",
      "Family Equality", "Family Equality",
      "Advances equality for LGBTQ+ families through advocacy, education and community.",
      "Продвигает равенство для ЛГБТ+ семей через адвокацию, образование и сообщество.",
      "Family Equality (EIN 04-3106090, founded 1979) advances legal and lived equality for LGBTQ+ parents and their children. Runs Family Week (largest annual gathering of LGBTQ+ families in the US), advocates for adoption + foster-care non-discrimination, supports families through pregnancy and adoption journeys.",
      "Family Equality (EIN 04-3106090, основан в 1979 году) продвигает юридическое и фактическое равенство для ЛГБТ+ родителей и их детей. Проводит Family Week (крупнейший в США ежегодный сбор ЛГБТ+ семей), лоббирует антидискриминацию в усыновлении и фостерной опеке, сопровождает семьи в беременности и усыновлении.",
      "https://www.familyequality.org/donate/", 4200000, 75, 1979, date(2024, 6, 30),
      ["lgbtq-youth", "child-welfare"],
      _us_pp("043106090"), "irs_990", _verify_us(), "medium"),

    # ============== US Veterans (5) ==============
    E("wounded-warrior-project", "US", "202370934", "people",
      "Wounded Warrior Project", "Wounded Warrior Project",
      "Programs for post-9/11 veterans — mental health, physical health, financial wellness, peer connection.",
      "Программы для ветеранов после 9/11 — психическое здоровье, физическое здоровье, финансовое благополучие, сообщество.",
      "Wounded Warrior Project (EIN 20-2370934, founded 2003) is one of the largest US veteran-services charities. Operates Combat Stress Recovery (mental-health), Independence Program (severely-wounded long-term care), Warriors to Work (employment), peer-support groups, and adaptive sports. Reaches ~200K post-9/11 wounded veterans and their families.",
      "Wounded Warrior Project (EIN 20-2370934, основан в 2003 году) — одна из крупнейших в США организаций помощи ветеранам. Программы Combat Stress Recovery (психическое здоровье), Independence Program (долгосрочный уход за тяжело раненными), Warriors to Work (трудоустройство), группы поддержки от равных, адаптивный спорт. Охватывает ~200 тыс. ветеранов после 9/11 и их семьи.",
      "https://www.woundedwarriorproject.org/donate", 290000000, 73, 2003, date(2024, 9, 30),
      ["veterans", "mental-health", "disability-services"],
      _us_pp("202370934"), "irs_990", _verify_us()),

    E("dav-charitable-trust", "US", "521516672", "people",
      "DAV Charitable Service Trust", "DAV — Disabled American Veterans Charitable Service Trust",
      "Funds programs for ill and injured American veterans across all eras.",
      "Финансирует программы для больных и раненых американских ветеранов всех эпох.",
      "DAV Charitable Service Trust (EIN 52-1516672, founded 1986) is the charitable arm of Disabled American Veterans. Funds homeless-veteran outreach, transportation to VA medical centers, employment programs, and disaster relief for veterans. DAV itself was founded in 1920 by WWI veterans.",
      "DAV Charitable Service Trust (EIN 52-1516672, основан в 1986 году) — благотворительное крыло Disabled American Veterans. Финансирует помощь бездомным ветеранам, транспорт до медцентров VA, программы трудоустройства, помощь при стихийных бедствиях. Сама DAV основана в 1920 году ветеранами Первой мировой.",
      "https://www.dav.org/donate/", 90000000, 79, 1920, date(2024, 6, 30),
      ["veterans", "disability-services"],
      _us_pp("521516672"), "irs_990", _verify_us()),

    E("tunnel-to-towers", "US", "020599710", "people",
      "Tunnel to Towers Foundation", "Tunnel to Towers Foundation",
      "Pays off mortgages for fallen first-responder & catastrophically-injured veteran families.",
      "Погашает ипотеки семьям погибших первых-реагирующих и тяжело раненых ветеранов.",
      "Tunnel to Towers Foundation (EIN 02-0599710, founded 2001 in memory of FDNY firefighter Stephen Siller killed on 9/11) builds and pays off mortgages on smart, accessible homes for catastrophically-injured veterans and gold-star families of fallen first-responders.",
      "Tunnel to Towers Foundation (EIN 02-0599710, основан в 2001 году в память о пожарном FDNY Стивене Силлере, погибшем 11 сентября) строит и погашает ипотеки на умные, доступные дома для тяжело раненых ветеранов и семей погибших первых-реагирующих.",
      "https://t2t.org/donate/", 300000000, 92, 2001, date(2024, 12, 31),
      ["veterans", "housing"],
      _us_pp("020599710"), "irs_990", _verify_us()),

    E("folds-of-honor", "US", "261316983", "people",
      "Folds of Honor", "Folds of Honor",
      "Education scholarships for spouses and children of fallen and disabled US military.",
      "Образовательные стипендии супругам и детям павших и раненых американских военных.",
      "Folds of Honor (EIN 26-1316983, founded 2007) provides educational scholarships to the spouses and children of fallen or disabled US service members. Has awarded ~50K scholarships covering K-12 private school, undergraduate, and trade-school tuition.",
      "Folds of Honor (EIN 26-1316983, основан в 2007 году) предоставляет образовательные стипендии супругам и детям павших или раненых американских военнослужащих. Выдала ~50 тыс. стипендий, покрывающих частные школы K-12, бакалавриат и профобучение.",
      "https://foldsofhonor.org/donate/", 50000000, 81, 2007, date(2024, 12, 31),
      ["veterans", "education"],
      _us_pp("261316983"), "irs_990", _verify_us()),

    E("iava", "US", "200583093", "people",
      "Iraq and Afghanistan Veterans of America", "IAVA — Iraq and Afghanistan Veterans of America",
      "Advocacy and direct services for post-9/11 veterans — VA reform, mental health, women veterans.",
      "Адвокация и прямая помощь ветеранам после 9/11 — реформа VA, психическое здоровье, женщины-ветераны.",
      "IAVA (EIN 20-0583093, founded 2004) is the largest non-partisan post-9/11 veterans organisation in the US. Advocates for VA accountability, suicide-prevention legislation, women-veteran health services. Runs Quick Reaction Force — direct case-management for veterans in crisis.",
      "IAVA (EIN 20-0583093, основан в 2004 году) — крупнейшая беспартийная организация ветеранов после 9/11 в США. Лоббирует подотчётность VA, законы о профилактике суицида, медицину для женщин-ветеранов. Quick Reaction Force — прямой кейс-менеджмент для ветеранов в кризисе.",
      "https://iava.org/donate/", 7800000, 75, 2004, date(2024, 12, 31),
      ["veterans", "mental-health"],
      _us_pp("200583093"), "irs_990", _verify_us(), "medium"),

    # ============== US Domestic / Sexual Violence (3) ==============
    E("rainn", "US", "521801260", "people",
      "RAINN", "RAINN — Rape, Abuse & Incest National Network",
      "Largest US anti-sexual-violence org — operates the National Sexual Assault Hotline.",
      "Крупнейшая в США антинасильственная организация — ведёт Национальную линию помощи жертвам сексуального насилия.",
      "RAINN (EIN 52-1801260, founded 1994) operates the National Sexual Assault Hotline (1-800-656-HOPE) and online chat in partnership with ~1,000 local sexual-assault service providers. Trains military and DoD personnel through Safe Helpline; advocates federally on victim rights and Title IX enforcement.",
      "RAINN (EIN 52-1801260, основан в 1994 году) ведёт Национальную линию помощи жертвам сексуального насилия (1-800-656-HOPE) и онлайн-чат в партнёрстве с ~1000 местных провайдеров. Обучает военных и сотрудников DoD через Safe Helpline; лоббирует на федеральном уровне права жертв и Title IX.",
      "https://www.rainn.org/donate", 22000000, 80, 1994, date(2024, 6, 30),
      ["domestic-violence", "womens-rights", "civil-rights"],
      _us_pp("521801260"), "irs_990", _verify_us()),

    E("nnedv", "US", "521973408", "people",
      "National Network to End Domestic Violence", "NNEDV — National Network to End Domestic Violence",
      "Federation of US state DV coalitions — policy, technology safety, financial empowerment.",
      "Федерация коалиций штатов США против домашнего насилия — политика, цифровая безопасность, финансовая независимость.",
      "NNEDV (EIN 52-1973408, founded 1990) is the leading US federation of 56 state and territory domestic-violence coalitions. Operates the Safety Net Project (digital-abuse and tech-safety expertise), Allstate Foundation Moving Ahead (financial empowerment), and federal policy advocacy on VAWA and FVPSA reauthorization.",
      "NNEDV (EIN 52-1973408, основан в 1990 году) — ведущая в США федерация коалиций 56 штатов и территорий против домашнего насилия. Проект Safety Net (цифровое насилие и tech-safety), Allstate Foundation Moving Ahead (финансовая независимость), федеральная адвокация по реавторизации VAWA и FVPSA.",
      "https://nnedv.org/donate/", 16000000, 78, 1990, date(2024, 9, 30),
      ["domestic-violence", "womens-rights"],
      _us_pp("521973408"), "irs_990", _verify_us(), "medium"),

    E("futures-without-violence", "US", "943110750", "people",
      "Futures Without Violence", "Futures Without Violence",
      "Health, justice and education programs to end gender-based violence in the US and globally.",
      "Программы в области здравоохранения, правосудия и образования для прекращения гендерного насилия в США и в мире.",
      "Futures Without Violence (EIN 94-3110750, founded 1980) develops public-health, justice-system and youth-prevention programs to end domestic violence and child abuse. Trains medical providers to recognise IPV, runs Children Exposed to Violence programs, federal advocacy on VAWA.",
      "Futures Without Violence (EIN 94-3110750, основан в 1980 году) разрабатывает программы общественного здравоохранения, юстиции и профилактики среди молодёжи для прекращения домашнего насилия и насилия над детьми. Обучает врачей распознавать IPV, ведёт программы для детей, ставших свидетелями насилия, федеральная адвокация по VAWA.",
      "https://www.futureswithoutviolence.org/donate/", 18000000, 79, 1980, date(2024, 9, 30),
      ["domestic-violence", "womens-rights", "child-welfare"],
      _us_pp("943110750"), "irs_990", _verify_us(), "medium"),

    # ============== US Elderly (3) ==============
    E("ncoa", "US", "131932384", "people",
      "National Council on Aging", "National Council on Aging (NCoA)",
      "US senior advocacy + benefits enrolment + economic-security programs.",
      "Адвокация прав пожилых США + регистрация в льготы + программы экономической безопасности.",
      "NCoA (EIN 13-1932384, founded 1950) is one of the oldest US aging-services organisations. Operates BenefitsCheckUp (helps seniors find and enrol in ~2,000 federal/state/local benefits programs), advocates federally on Medicare and Social Security, runs falls-prevention and chronic-disease self-management programs.",
      "NCoA (EIN 13-1932384, основан в 1950 году) — одна из старейших в США организаций помощи пожилым. Управляет BenefitsCheckUp (помогает пенсионерам найти и оформить ~2000 федеральных/штатных/местных льгот), лоббирует Medicare и Social Security, ведёт программы профилактики падений и самоуправления хроническими заболеваниями.",
      "https://www.ncoa.org/donate", 36000000, 78, 1950, date(2024, 6, 30),
      ["elderly-care", "senior-care"],
      _us_pp("131932384"), "irs_990", _verify_us()),

    E("oats-tech", "US", "134205586", "people",
      "Older Adults Technology Services (OATS)", "Older Adults Technology Services (OATS)",
      "Trains older adults in digital skills via Senior Planet community tech centers.",
      "Обучает пожилых людей цифровым навыкам через сеть Senior Planet community-центров.",
      "OATS (EIN 13-4205586, founded 2004), now part of AARP, operates Senior Planet — a network of community tech centers and online classes that teach digital skills to adults 60+. Closes the digital divide for ~25K seniors per year through hands-on training and a national online platform.",
      "OATS (EIN 13-4205586, основан в 2004 году), сейчас часть AARP, ведёт Senior Planet — сеть общинных tech-центров и онлайн-классов, обучающих цифровым навыкам взрослых 60+. Сокращает цифровой разрыв для ~25 тыс. пенсионеров в год через очные занятия и национальную онлайн-платформу.",
      "https://seniorplanet.org/give/", 11000000, 80, 2004, date(2024, 12, 31),
      ["elderly-care", "senior-care"],
      _us_pp("134205586"), "irs_990", _verify_us(), "medium"),

    E("volunteers-of-america", "US", "132584129", "people",
      "Volunteers of America", "Volunteers of America",
      "Faith-based US service org — homeless veterans, seniors, ex-offenders, children with disabilities.",
      "Религиозная американская служебная организация — бездомные ветераны, пожилые, экс-заключённые, дети с инвалидностью.",
      "Volunteers of America (EIN 13-2584129, founded 1896) runs ~24K affordable senior housing units, transitional housing for homeless veterans, behavioural-health programs, re-entry services for formerly incarcerated people, and developmental-disability services for ~1.5M people annually across 46 states.",
      "Volunteers of America (EIN 13-2584129, основана в 1896 году) управляет ~24 тыс. единицами доступного жилья для пожилых, переходным жильём для бездомных ветеранов, программами поведенческого здоровья, услугами реинтеграции для бывших заключённых, услугами для людей с нарушениями развития для ~1,5 млн человек ежегодно в 46 штатах.",
      "https://www.voa.org/donate", 1100000000, 87, 1896, date(2024, 6, 30),
      ["elderly-care", "veterans", "homelessness", "disability-services"],
      _us_pp("132584129"), "irs_990", _verify_us()),

    # ============== US Children & Youth Mentoring (3) ==============
    E("boys-girls-clubs-america", "US", "135562976", "people",
      "Boys & Girls Clubs of America", "Boys & Girls Clubs of America",
      "National federation of after-school clubs serving ~4M young people across 5,000+ club sites.",
      "Национальная федерация after-school клубов, обслуживающая ~4 млн подростков в 5000+ клубных точках.",
      "Boys & Girls Clubs of America (EIN 13-5562976, founded 1860 / national org 1906) is the federation that supports ~5,000 independently-chartered local Boys & Girls Clubs across the US, serving ~4M young people aged 6-18 with after-school academic enrichment, mentoring, sports, and youth-leadership programs.",
      "Boys & Girls Clubs of America (EIN 13-5562976, основан в 1860 году / национальная организация в 1906) — федерация ~5000 независимо-учреждённых местных клубов Boys & Girls по всей территории США, обслуживающая ~4 млн подростков 6-18 лет: внеклассная учебная программа, менторство, спорт, лидерство.",
      "https://www.bgca.org/donate", 215000000, 76, 1860, date(2024, 12, 31),
      ["youth-mentoring", "child-welfare", "education"],
      _us_pp("135562976"), "irs_990", _verify_us()),

    E("big-brothers-big-sisters-america", "US", "135605455", "people",
      "Big Brothers Big Sisters of America", "Big Brothers Big Sisters of America",
      "1-to-1 youth mentoring — matches adult volunteers (Bigs) with children 6-18 (Littles).",
      "Менторство 1-на-1 — пары взрослых волонтёров (Bigs) с детьми 6-18 (Littles).",
      "Big Brothers Big Sisters of America (EIN 13-5605455, founded 1904) is the largest US youth-mentoring network. Operates ~230 affiliated local agencies that match adult volunteers (Bigs) with children aged 6-18 (Littles) for long-term 1-to-1 mentoring relationships. Currently ~140K active matches.",
      "Big Brothers Big Sisters of America (EIN 13-5605455, основан в 1904 году) — крупнейшая в США сеть менторства молодёжи. ~230 аффилированных местных агентств подбирают взрослых волонтёров (Bigs) с детьми 6-18 (Littles) для долгосрочного менторства 1-на-1. Сейчас ~140 тыс. активных пар.",
      "https://www.bbbs.org/donate/", 26000000, 79, 1904, date(2024, 12, 31),
      ["youth-mentoring", "child-welfare"],
      _us_pp("135605455"), "irs_990", _verify_us()),

    E("boys-town", "US", "470376606", "people",
      "Boys Town", "Boys Town",
      "Faith-based but inclusive integrated child and family services — residential, behavioural, healthcare.",
      "Религиозная, но инклюзивная интегрированная служба для детей и семей — резиденциальная, поведенческая, медицинская.",
      "Boys Town (EIN 47-0376606, founded 1917 by Father Edward Flanagan) provides direct care to ~700K children and families annually. Operates the Boys Town National Hotline, residential homes, foster-care services, in-home family services, and the Boys Town National Research Hospital (specialty care for children's deafness, hereditary disease).",
      "Boys Town (EIN 47-0376606, основан в 1917 году отцом Эдвардом Фланаганом) оказывает прямую помощь ~700 тыс. детей и семей ежегодно. Национальная горячая линия Boys Town, резиденциальные дома, фостерная опека, услуги семьи на дому, исследовательская больница Boys Town National (специализированная помощь детям при глухоте, наследственных заболеваниях).",
      "https://www.boystown.org/give", 470000000, 81, 1917, date(2024, 12, 31),
      ["youth-mentoring", "child-welfare", "global-health"],
      _us_pp("470376606"), "irs_990", _verify_us()),

    # ============== US Refugees (2) ==============
    E("lirs", "US", "135564422", "people",
      "Lutheran Immigration and Refugee Service (LIRS)", "Lutheran Immigration and Refugee Service (LIRS)",
      "US refugee resettlement, asylum legal services, and unaccompanied-minor case management.",
      "Расселение беженцев в США, юридическая помощь по asylum, и опека несовершеннолетних без сопровождения.",
      "LIRS (EIN 13-5564422, founded 1939) is one of nine national refugee-resettlement agencies authorized by the US State Department. Resettles refugees admitted to the US, runs asylum legal-services, and provides case management for unaccompanied refugee minors. Network of ~50 affiliated local resettlement offices.",
      "LIRS (EIN 13-5564422, основан в 1939 году) — одно из девяти национальных агентств по расселению беженцев, авторизованных Госдепартаментом США. Расселяет принятых в США беженцев, ведёт юридические службы asylum, обеспечивает опеку несовершеннолетних беженцев без сопровождения. Сеть из ~50 аффилированных местных офисов.",
      "https://www.lirs.org/donate/", 80000000, 88, 1939, date(2024, 9, 30),
      ["refugees", "humanitarian-medicine"],
      _us_pp("135564422"), "irs_990", _verify_us()),

    E("uscri", "US", "131623891", "people",
      "US Committee for Refugees and Immigrants (USCRI)", "USCRI — US Committee for Refugees and Immigrants",
      "Refugee resettlement + global advocacy via World Refugee Survey.",
      "Расселение беженцев + глобальная адвокация через World Refugee Survey.",
      "USCRI (EIN 13-1623891, founded 1911 as the National Institute on Immigrant Welfare) resettles refugees in the US through a network of field offices and publishes the annual World Refugee Survey — the most widely-cited US-published assessment of refugee conditions worldwide. Also runs unaccompanied-minor case management.",
      "USCRI (EIN 13-1623891, основан в 1911 году как National Institute on Immigrant Welfare) расселяет беженцев в США через сеть полевых офисов и публикует ежегодный World Refugee Survey — самую цитируемую в США оценку условий беженцев в мире. Также ведёт опеку несовершеннолетних без сопровождения.",
      "https://refugees.org/donate/", 70000000, 86, 1911, date(2024, 9, 30),
      ["refugees", "civil-rights"],
      _us_pp("131623891"), "irs_990", _verify_us()),

    # ============== US Disease (1) ==============
    E("cystic-fibrosis-foundation", "US", "131930701", "people",
      "Cystic Fibrosis Foundation", "Cystic Fibrosis Foundation",
      "Funded the venture-philanthropy R&D pipeline that produced Trikafta (CF therapy).",
      "Финансировал венчурно-филантропический R&D-конвейер, давший Trikafta (терапия муковисцидоза).",
      "Cystic Fibrosis Foundation (EIN 13-1930701, founded 1955) pioneered the venture-philanthropy model — funded Vertex Pharmaceuticals' research that produced Kalydeco, Orkambi, Symdeko and Trikafta. CF was once an under-10 mortality disease; people born with CF today have a median predicted lifespan of ~50 years. Funds research, accredits CF Care Centers, runs patient registry.",
      "Cystic Fibrosis Foundation (EIN 13-1930701, основан в 1955 году) разработал модель венчурной филантропии — финансировал исследования Vertex Pharmaceuticals, которые дали Kalydeco, Orkambi, Symdeko и Trikafta. Раньше муковисцидоз был болезнью с детской смертностью; сегодня медианная прогнозируемая продолжительность жизни ~50 лет. Финансирует исследования, аккредитует CF-центры, ведёт реестр пациентов.",
      "https://www.cff.org/donate", 280000000, 81, 1955, date(2024, 12, 31),
      ["rare-disease", "global-health"],
      _us_pp("131930701"), "irs_990", _verify_us()),

    # ============== UK (10) ==============
    E("nspcc", "GB", "216401", "people",
      "NSPCC", "NSPCC — National Society for the Prevention of Cruelty to Children",
      "UK's leading child-protection charity — Childline, prevention programs, policy.",
      "Ведущая британская организация по защите детей — Childline, программы профилактики, политика.",
      "NSPCC (Charity Commission #216401, founded 1884) is the UK's leading child-protection charity. Operates Childline (free 24/7 children's counselling helpline since 1986), runs prevention programs in schools (Speak Out Stay Safe), provides therapy to children who have experienced abuse, and campaigns federally for stronger child-protection law.",
      "NSPCC (Charity Commission #216401, основан в 1884 году) — ведущая британская благотворительная организация по защите детей. Управляет Childline (бесплатная круглосуточная детская линия консультирования с 1986 года), ведёт программы профилактики в школах (Speak Out Stay Safe), оказывает терапию детям, пережившим насилие, лоббирует более сильное законодательство по защите детей.",
      "https://www.nspcc.org.uk/donate-now/", 165000000, 80, 1884, date(2024, 3, 31),
      ["child-protection", "child-welfare", "mental-health"],
      _uk_cc("216401"), "annual_report", _verify_uk()),

    E("barnardos", "GB", "216250", "people",
      "Barnardo's", "Barnardo's",
      "UK's largest children's charity — fostering, adoption, family support, child sexual exploitation services.",
      "Крупнейшая британская детская благотворительная организация — фостеринг, усыновление, поддержка семей, помощь жертвам сексуальной эксплуатации.",
      "Barnardo's (Charity Commission #216250, founded 1866 by Thomas Barnardo) is the UK's largest children's charity. Runs ~800 services including fostering, adoption, family-support, services for children sexually exploited or trafficked, and support for care-leavers. Reaches ~370K children, young people and families annually.",
      "Barnardo's (Charity Commission #216250, основан в 1866 году Томасом Барнардо) — крупнейшая британская детская благотворительная организация. Управляет ~800 услугами: фостерное воспитание, усыновление, поддержка семей, помощь детям, подвергшимся сексуальной эксплуатации или торговле людьми, поддержка выпускников системы опеки. Охват ~370 тыс. детей, молодёжи и семей ежегодно.",
      "https://www.barnardos.org.uk/donate", 410000000, 86, 1866, date(2024, 3, 31),
      ["child-welfare", "child-protection"],
      _uk_cc("216250"), "annual_report", _verify_uk()),

    E("trussell-trust", "GB", "1110522", "people",
      "Trussell Trust", "Trussell Trust",
      "UK's largest food-bank network — ~1,400 community food banks in partnership with churches.",
      "Крупнейшая в Великобритании сеть продбанков — ~1400 общинных продбанков в партнёрстве с церквями.",
      "Trussell Trust (Charity Commission #1110522, founded 1997) supports the UK's largest network of food banks — ~1,400 community-run food banks (mostly church-based) that distribute emergency food to people referred by frontline professionals. Distributed ~3.1M emergency-food parcels in the year ending March 2024 — record demand reflects UK cost-of-living pressure.",
      "Trussell Trust (Charity Commission #1110522, основан в 1997 году) поддерживает крупнейшую в Великобритании сеть продбанков — ~1400 общинных продбанков (в основном при церквях), распределяющих экстренную еду людям по направлению фронтлайн-специалистов. Выдал ~3,1 млн пакетов экстренной помощи за год, закончившийся в марте 2024 — рекордный спрос отражает кризис стоимости жизни в Великобритании.",
      "https://www.trusselltrust.org/make-a-donation/", 18000000, 84, 1997, date(2024, 3, 31),
      ["food-banks", "hunger", "poverty-reduction"],
      _uk_cc("1110522"), "annual_report", _verify_uk(), "medium"),

    E("dogs-trust", "GB", "227523", "animals",
      "Dogs Trust", "Dogs Trust",
      "UK's largest dog welfare charity — runs 21 rehoming centres + the Hope Project for homeless dog-owners.",
      "Крупнейшая в Великобритании организация по защите собак — управляет 21 центром передержки + Hope Project для бездомных владельцев собак.",
      "Dogs Trust (Charity Commission #227523, founded 1891 as the National Canine Defence League) is the UK's largest dog welfare charity. Runs 21 rehoming centres across the UK and Ireland, finds new homes for ~14K dogs annually, and operates Hope Project (free vet care for the dogs of homeless people) and Freedom Project (fostering for dogs of domestic-abuse survivors).",
      "Dogs Trust (Charity Commission #227523, основан в 1891 году как National Canine Defence League) — крупнейшая в Великобритании организация по защите собак. Управляет 21 центром передержки в Великобритании и Ирландии, находит новые дома ~14 тыс. собак ежегодно, ведёт Hope Project (бесплатный ветуход для собак бездомных) и Freedom Project (фостеринг для собак переживших домашнее насилие).",
      "https://www.dogstrust.org.uk/donate", 175000000, 80, 1891, date(2024, 3, 31),
      ["animal-welfare"],
      _uk_cc("227523"), "annual_report", _verify_uk()),

    E("cats-protection", "GB", "203644", "animals",
      "Cats Protection", "Cats Protection",
      "UK's leading cat charity — homing, neutering programs, and welfare advocacy.",
      "Ведущая британская кошачья благотворительная организация — пристройство, программы стерилизации, адвокация благополучия.",
      "Cats Protection (Charity Commission #203644, founded 1927) is the UK's largest cat charity. Operates ~250 volunteer-run branches and 36 adoption centres, helps ~157K cats and kittens annually through homing, free or low-cost neutering for low-income owners, and microchipping. Co-leads the Cat Welfare Group lobbying for the new Animal Welfare (Kept Animals) Bill.",
      "Cats Protection (Charity Commission #203644, основан в 1927 году) — крупнейшая в Великобритании кошачья благотворительная организация. Управляет ~250 волонтёрскими отделениями и 36 центрами усыновления, помогает ~157 тыс. кошек и котят ежегодно через пристройство, бесплатную или субсидированную стерилизацию для малоимущих владельцев, чипирование. Соруководит Cat Welfare Group, лоббирующей новый Animal Welfare (Kept Animals) Bill.",
      "https://www.cats.org.uk/donate", 80000000, 78, 1927, date(2024, 3, 31),
      ["animal-welfare"],
      _uk_cc("203644"), "annual_report", _verify_uk()),

    E("action-for-children", "GB", "1097940", "people",
      "Action for Children", "Action for Children",
      "UK children's charity — early-intervention services, fostering, adoption, child-protection campaigns.",
      "Британская детская благотворительная организация — раннее вмешательство, фостеринг, усыновление, кампании по защите детей.",
      "Action for Children (Charity Commission #1097940, founded 1869 as the National Children's Home) protects and supports vulnerable children and young people in the UK. Runs ~470 services including children's centres, fostering, adoption, mental-health support, and youth-homelessness prevention. Reaches ~604K children, young people and families per year.",
      "Action for Children (Charity Commission #1097940, основана в 1869 году как National Children's Home) защищает и поддерживает уязвимых детей и молодёжь в Великобритании. Управляет ~470 услугами: детские центры, фостеринг, усыновление, поддержка психического здоровья, профилактика молодёжной бездомности. Охват ~604 тыс. детей, молодёжи и семей в год.",
      "https://www.actionforchildren.org.uk/support-us/donate/", 200000000, 87, 1869, date(2024, 3, 31),
      ["child-welfare", "child-protection"],
      _uk_cc("1097940"), "annual_report", _verify_uk()),

    E("help-for-heroes", "GB", "1120920", "people",
      "Help for Heroes", "Help for Heroes",
      "UK veteran-services charity — recovery support for British wounded service personnel and their families.",
      "Британская организация поддержки ветеранов — восстановление для раненых британских военнослужащих и их семей.",
      "Help for Heroes (Charity Commission #1120920, founded 2007) provides recovery support to British military veterans wounded in service. Runs Recovery Centres, individual care plans, mental-health support (Hidden Wounds), and family support. Supports ~30K wounded veterans and their loved ones to date.",
      "Help for Heroes (Charity Commission #1120920, основан в 2007 году) обеспечивает поддержку восстановления британских военных ветеранов, раненых на службе. Центры восстановления, индивидуальные планы помощи, поддержка психического здоровья (Hidden Wounds), помощь семьям. Помог ~30 тыс. раненых ветеранов и их близких на текущий момент.",
      "https://www.helpforheroes.org.uk/donate/", 28000000, 76, 2007, date(2024, 9, 30),
      ["veterans", "mental-health", "disability-services"],
      _uk_cc("1120920"), "annual_report", _verify_uk(), "medium"),

    E("calm-uk", "GB", "1110621", "people",
      "Campaign Against Living Miserably (CALM)", "CALM — Campaign Against Living Miserably (UK)",
      "Suicide prevention campaigns + free helpline for men in crisis.",
      "Кампании по профилактике суицида + бесплатная линия помощи мужчинам в кризисе.",
      "CALM (Charity Commission #1110621, founded 2006) is the UK's leading suicide-prevention charity for men. Operates a free helpline and webchat 5pm-midnight 365 days a year, runs cultural campaigns to challenge the stigma of male emotional vulnerability. Suicide is the largest cause of death for UK men under 50.",
      "CALM (Charity Commission #1110621, основан в 2006 году) — ведущая в Великобритании организация по профилактике суицида среди мужчин. Бесплатная линия помощи и веб-чат с 17:00 до полуночи 365 дней в году, культурные кампании против стигмы мужской эмоциональной уязвимости. Суицид — главная причина смерти британских мужчин до 50 лет.",
      "https://www.thecalmzone.net/donate", 10500000, 75, 2006, date(2024, 3, 31),
      ["mental-health", "suicide-prevention"],
      _uk_cc("1110621"), "annual_report", _verify_uk(), "medium"),

    E("battersea-dogs-cats", "GB", "206394", "animals",
      "Battersea Dogs & Cats Home", "Battersea Dogs & Cats Home",
      "Iconic UK rescue centre — rescues, rehabilitates and rehomes dogs and cats since 1860.",
      "Знаковый британский приют — спасает, реабилитирует и пристраивает собак и кошек с 1860 года.",
      "Battersea Dogs & Cats Home (Charity Commission #206394, founded 1860) operates three London-area centres that take in unwanted, lost or abandoned dogs and cats — ~3,500 rehomed annually plus ~3,000 reunited with owners. Runs the Battersea Academy training behavioural advisors, advocates federally for animal-welfare law.",
      "Battersea Dogs & Cats Home (Charity Commission #206394, основан в 1860 году) управляет тремя центрами в районе Лондона, принимающими ненужных, потерянных или брошенных собак и кошек — ~3500 пристроены ежегодно плюс ~3000 воссоединены с владельцами. Battersea Academy готовит специалистов по поведению, лоббирует на федеральном уровне законы по защите животных.",
      "https://www.battersea.org.uk/donate", 50000000, 76, 1860, date(2024, 3, 31),
      ["animal-welfare"],
      _uk_cc("206394"), "annual_report", _verify_uk()),

    E("joseph-rowntree-foundation", "GB", "210169", "people",
      "Joseph Rowntree Foundation", "Joseph Rowntree Foundation",
      "Independent UK think-tank and funder working to solve UK poverty.",
      "Независимый британский think-tank и грантодатель, работающий над решением проблемы бедности в Великобритании.",
      "Joseph Rowntree Foundation (Charity Commission #210169, founded 1904 by York chocolate-maker Joseph Rowntree) is one of the UK's leading social-policy charities. Funds independent research on UK poverty (including the influential Minimum Income Standard and annual UK Poverty report), funds anti-poverty programmes, and runs Joseph Rowntree Housing Trust providing affordable housing in York.",
      "Joseph Rowntree Foundation (Charity Commission #210169, основан в 1904 году йоркским шоколатье Джозефом Раунтри) — одна из ведущих социально-политических благотворительных организаций Великобритании. Финансирует независимые исследования бедности в Великобритании (включая влиятельный Minimum Income Standard и ежегодный отчёт UK Poverty), финансирует программы борьбы с бедностью, ведёт Joseph Rowntree Housing Trust (доступное жильё в Йорке).",
      "https://www.jrf.org.uk/our-work/donate", 25000000, 78, 1904, date(2024, 12, 31),
      ["poverty-reduction", "housing"],
      _uk_cc("210169"), "annual_report", _verify_uk()),

    # ============== Canada (5) ==============
    E("camh-foundation", "CA", "11892-9941-RR0001", "people",
      "CAMH Foundation", "CAMH Foundation — фонд центра психиатрии в Торонто",
      "Funds the Centre for Addiction and Mental Health — Canada's largest mental-health teaching hospital.",
      "Финансирует Centre for Addiction and Mental Health — крупнейшую в Канаде учебную психиатрическую больницу.",
      "CAMH Foundation (CRA #11892-9941-RR0001) raises and stewards funds for the Centre for Addiction and Mental Health (CAMH), Canada's largest mental-health and addiction teaching hospital. CAMH treats ~37K patients annually and runs one of the world's largest mental-health research programs.",
      "CAMH Foundation (CRA #11892-9941-RR0001) собирает и управляет средствами для Centre for Addiction and Mental Health (CAMH) — крупнейшей в Канаде учебной психиатрической больницы по психическому здоровью и зависимостям. CAMH лечит ~37 тыс. пациентов ежегодно и ведёт одну из крупнейших в мире программ исследований психического здоровья.",
      "https://www.camhfoundation.ca/donate", 95000000, 82, 1979, date(2024, 3, 31),
      ["mental-health", "global-health"],
      "https://www.camhfoundation.ca/about-us/financials", "annual_report", _verify_ca()),

    E("make-a-wish-canada", "CA", "10729-7011-RR0001", "people",
      "Make-A-Wish Canada", "Make-A-Wish Canada",
      "Grants wishes to Canadian children with critical illnesses.",
      "Исполняет желания канадских детей с тяжёлыми заболеваниями.",
      "Make-A-Wish Canada (CRA #10729-7011-RR0001, founded 1983) grants the wishes of Canadian children aged 3-17 with critical illnesses. Operates as the Canadian chapter of Make-A-Wish International. Has granted ~38K wishes to date — typically a trip, a meeting with a hero, or a special experience tailored to the child.",
      "Make-A-Wish Canada (CRA #10729-7011-RR0001, основан в 1983 году) исполняет желания канадских детей 3-17 лет с тяжёлыми заболеваниями. Работает как канадское отделение Make-A-Wish International. Исполнила ~38 тыс. желаний — обычно поездка, встреча с героем или особый опыт, подобранный для ребёнка.",
      "https://makeawish.ca/donate/", 26000000, 76, 1983, date(2024, 8, 31),
      ["child-welfare", "global-health"],
      "https://makeawish.ca/about-us/financials/", "annual_report", _verify_ca()),

    E("boys-girls-clubs-canada", "CA", "11881-1306-RR0001", "people",
      "Boys & Girls Clubs of Canada", "Boys & Girls Clubs of Canada",
      "Federation of ~590 Canadian after-school clubs serving ~200K young people annually.",
      "Федерация ~590 канадских after-school клубов, обслуживающая ~200 тыс. подростков ежегодно.",
      "Boys & Girls Clubs of Canada (CRA #11881-1306-RR0001, founded 1900) is the federation of ~590 local Canadian Boys & Girls Clubs. Provides ~200K children and youth annually with after-school programs, mentoring, mental-health support, leadership development. Independent from the US BGCA but shares brand and methodology.",
      "Boys & Girls Clubs of Canada (CRA #11881-1306-RR0001, основан в 1900 году) — федерация ~590 местных канадских Boys & Girls Clubs. Ежегодно обеспечивает ~200 тыс. детей и молодёжи внеклассными программами, менторством, поддержкой психического здоровья, лидерством. Независим от US BGCA, но делит бренд и методологию.",
      "https://www.bgccan.com/en/donate/", 5500000, 78, 1900, date(2024, 6, 30),
      ["youth-mentoring", "child-welfare"],
      "https://www.bgccan.com/en/about-us/financials/", "annual_report", _verify_ca(), "medium"),

    E("big-brothers-big-sisters-canada", "CA", "10684-7635-RR0001", "people",
      "Big Brothers Big Sisters of Canada", "Big Brothers Big Sisters of Canada",
      "1-to-1 youth mentoring across ~100 Canadian agencies — ~31K active matches.",
      "Менторство молодёжи 1-на-1 в ~100 канадских агентствах — ~31 тыс. активных пар.",
      "Big Brothers Big Sisters of Canada (CRA #10684-7635-RR0001, founded 1913) is the federation of ~100 affiliated local agencies that match adult volunteers (Bigs) with children aged 6-18 (Littles) for long-term 1-to-1 mentoring. ~31K active matches across Canada.",
      "Big Brothers Big Sisters of Canada (CRA #10684-7635-RR0001, основан в 1913 году) — федерация ~100 аффилированных местных агентств, подбирающих взрослых волонтёров (Bigs) с детьми 6-18 (Littles) для долгосрочного менторства 1-на-1. ~31 тыс. активных пар по всей Канаде.",
      "https://bigbrothersbigsisters.ca/donate/", 4500000, 80, 1913, date(2024, 6, 30),
      ["youth-mentoring", "child-welfare"],
      "https://bigbrothersbigsisters.ca/financial-statements/", "annual_report", _verify_ca(), "medium"),

    E("wwf-canada", "CA", "11930-4954-RR0001", "planet",
      "WWF-Canada", "WWF-Canada",
      "Canadian arm of WWF — Arctic conservation, freshwater, climate, species at risk.",
      "Канадское отделение WWF — Арктика, пресные воды, климат, виды под угрозой.",
      "WWF-Canada (CRA #11930-4954-RR0001, founded 1967) is the Canadian national office of the WWF International network. Focus areas: Arctic and high-Arctic conservation, freshwater systems (Mackenzie, Lake Winnipeg), climate, and species-at-risk recovery (caribou, beluga, Atlantic salmon).",
      "WWF-Canada (CRA #11930-4954-RR0001, основан в 1967 году) — канадское национальное отделение сети WWF International. Ключевые направления: сохранение Арктики и Высокой Арктики, пресноводные системы (Маккензи, озеро Виннипег), климат, восстановление видов под угрозой (карибу, белуха, атлантический лосось).",
      "https://wwf.ca/donate/", 28000000, 78, 1967, date(2024, 6, 30),
      ["conservation", "biodiversity-defense", "wildlife-conservation", "climate"],
      "https://wwf.ca/about-us/financials/", "annual_report", _verify_ca()),

    # ============== Australia (3) ==============
    E("foodbank-australia", "AU", "ABN-58-073-579-254", "people",
      "Foodbank Australia", "Foodbank Australia",
      "Australia's largest food-relief org — supplies surplus food to ~2,950 charity partners.",
      "Крупнейшая в Австралии продпомощь — поставляет излишки продовольствия ~2950 благотворительным партнёрам.",
      "Foodbank Australia (ABN 58 073 579 254, founded 1992) is Australia's largest food-relief organisation. Sources surplus food and groceries from manufacturers, retailers and farmers; distributes through ~2,950 charity partners that feed ~3.4M people annually. Operates state-level Foodbank affiliates plus a national hub.",
      "Foodbank Australia (ABN 58 073 579 254, основан в 1992 году) — крупнейшая в Австралии организация продовольственной помощи. Получает излишки продуктов от производителей, ритейлеров и фермеров; распределяет через ~2950 благотворительных партнёров, кормящих ~3,4 млн человек ежегодно. Работает через филиалы Foodbank на уровне штатов плюс национальный хаб.",
      "https://www.foodbank.org.au/donate-money/", 90000000, 91, 1992, date(2024, 6, 30),
      ["food-banks", "hunger", "food-security"],
      "https://www.foodbank.org.au/about-us/governance-financials/", "annual_report", _verify_au()),

    E("caritas-australia", "AU", "ABN-90-970-605-069", "people",
      "Caritas Australia", "Caritas Australia",
      "Australian Catholic agency for international aid — Project Compassion fundraising campaign.",
      "Австралийское католическое агентство международной помощи — кампания Project Compassion.",
      "Caritas Australia (ABN 90 970 605 069) is the Australian Catholic Church's international-aid and development agency, member of the global Caritas Internationalis confederation. Works in ~30 countries on disaster relief, education, health and livelihoods. The annual Project Compassion Lenten appeal is one of Australia's largest annual charity campaigns.",
      "Caritas Australia (ABN 90 970 605 069) — австралийское агентство Католической церкви по международной помощи и развитию, член глобальной конфедерации Caritas Internationalis. Работает в ~30 странах: помощь при стихийных бедствиях, образование, здравоохранение, средства к существованию. Ежегодная кампания Project Compassion в Великий пост — одна из крупнейших ежегодных благотворительных кампаний Австралии.",
      "https://www.caritas.org.au/donate/", 65000000, 84, 1964, date(2024, 6, 30),
      ["humanitarian-medicine", "disaster-relief", "faith-based"],
      "https://www.caritas.org.au/about/financials/", "annual_report", _verify_au()),

    E("vinnies-australia", "AU", "ABN-50-748-098-845", "people",
      "St Vincent de Paul Society Australia (Vinnies)", "Vinnies — St Vincent de Paul Society Australia",
      "Catholic-rooted social-services federation — homelessness, financial hardship, op-shops nationwide.",
      "Католически-укоренённая социальная федерация — бездомность, финансовые трудности, op-shops по всей стране.",
      "St Vincent de Paul Society Australia (ABN 50 748 098 845, founded 1881) — known as 'Vinnies' — runs a national network of homelessness services, food relief, financial-counselling, refugee and migrant support, plus ~660 'Vinnies' second-hand shops that fund the work. ~60K volunteer members across Australia. Federation of seven state/territory entities.",
      "St Vincent de Paul Society Australia (ABN 50 748 098 845, основано в 1881 году) — известно как 'Vinnies' — управляет национальной сетью услуг для бездомных, продовольственной помощи, финансового консультирования, поддержки беженцев и мигрантов, плюс ~660 секонд-хендов 'Vinnies', финансирующих работу. ~60 тыс. волонтёров по всей Австралии. Федерация семи структур штатов/территорий.",
      "https://www.vinnies.org.au/donate", 800000000, 86, 1881, date(2024, 6, 30),
      ["homelessness", "poverty-reduction", "faith-based"],
      "https://www.vinnies.org.au/about-us/governance/", "annual_report", _verify_au()),
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
            print(f"[migration 0040] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
    print(f"[migration 0040] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0039_backfill_v37_geo_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

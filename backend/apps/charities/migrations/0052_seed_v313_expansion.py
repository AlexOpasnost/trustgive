"""v3.13 catalog expansion — seed 36 charities (436 -> ~472).

7th batch of the +300/6-session arc. v3.13 = breadth pass:
  US (12): lung, alzheimer's research, blind, children's media, youth
    development, peace, philanthropic infra, torture survivors,
    women's global, microfinance, veteran-led disaster, in-kind logistics.
  UK (8): HIV legacy, Jewish humanitarian, bereavement care, age
    international, pet welfare, disaster shelter, animal welfare,
    blood-cancer registry.
  Germany (5): DKMS bone marrow, WWF DE, Tafel food banks, Malteser,
    Arbeiterwohlfahrt (AWO).
  Netherlands (3): nature conservation, forgotten children,
    refugees nl.
  Sweden (1): Cancerfonden.
  France (2): Secours Populaire, Petits Frères des Pauvres.
  Switzerland (1): Pro Senectute (elderly).
  Italy (2): Istituto Clinico Humanitas, Fondazione Mediolanum.
  Spain (2): Ayuda en Acción, Intermón Oxfam (the original Spanish Oxfam).

No new countries.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "lung-disease": {"en": "Lung disease & tobacco control", "ru": "Заболевания лёгких и табачный контроль"},
    "blindness-low-vision": {"en": "Blindness & low vision", "ru": "Слепота и слабовидение"},
    "childrens-media": {"en": "Children's educational media", "ru": "Детские образовательные медиа"},
    "youth-development": {"en": "Youth development", "ru": "Развитие молодёжи"},
    "peace-disarmament": {"en": "Peace & disarmament", "ru": "Мир и разоружение"},
    "philanthropic-infrastructure": {"en": "Philanthropic-sector infrastructure", "ru": "Инфраструктура филантропического сектора"},
    "torture-rehabilitation": {"en": "Torture-survivor rehabilitation", "ru": "Реабилитация переживших пытки"},
    "global-womens-rights": {"en": "Global women's rights", "ru": "Глобальные права женщин"},
    "microfinance": {"en": "Microfinance & financial inclusion", "ru": "Микрофинансирование и финансовая инклюзия"},
    "in-kind-logistics": {"en": "In-kind donation logistics", "ru": "Логистика in-kind пожертвований"},
    "bereavement": {"en": "Bereavement support", "ru": "Поддержка переживших утрату"},
    "blood-stem-cell-registry": {"en": "Blood-stem-cell donor registries", "ru": "Реестры доноров стволовых клеток крови"},
    "knights-of-malta-medical": {"en": "Order of Malta medical aid", "ru": "Медицинская помощь Мальтийского ордена"},
    "german-labor-welfare": {"en": "German labour-movement social welfare", "ru": "Социальное обеспечение немецкого рабочего движения"},
    "nature-conservation-nl": {"en": "Dutch nature reserves", "ru": "Голландские природные заповедники"},
    "swedish-cancer-research": {"en": "Swedish cancer research", "ru": "Шведские онкологические исследования"},
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


def _verify_de() -> dict:
    return {
        "en": "Verified: German gemeinnützige organisation; DZI Spendensiegel or equivalent annual report public.",
        "ru": "Подтверждено: немецкая некоммерческая организация; сертификат DZI Spendensiegel или эквивалентный годовой отчёт публичен.",
    }


def _verify_nl() -> dict:
    return {
        "en": "Verified: CBF Erkend; ANBI status; annual report public.",
        "ru": "Подтверждено: CBF Erkend; ANBI статус; годовой отчёт публичен.",
    }


def _verify_se() -> dict:
    return {
        "en": "Verified: 90-konto certified by Svensk Insamlingskontroll.",
        "ru": "Подтверждено: сертификат 90-konto от Svensk Insamlingskontroll.",
    }


def _verify_fr() -> dict:
    return {
        "en": "Verified: Don en Confiance / Comité de la Charte certified; annual report public.",
        "ru": "Подтверждено: сертификат Don en Confiance / Comité de la Charte; годовой отчёт публичен.",
    }


def _verify_ch() -> dict:
    return {
        "en": "Verified: ZEWO certified; annual report public.",
        "ru": "Подтверждено: сертификат ZEWO; годовой отчёт публичен.",
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
    E("american-lung-association", "US", "131632524", "people",
      "American Lung Association", "American Lung Association",
      "Lung-health research, tobacco-control advocacy, asthma & COPD patient programmes.",
      "Исследования здоровья лёгких, антитабачная адвокация, программы для пациентов с астмой и ХОБЛ.",
      "American Lung Association (EIN 13-1632524, founded 1904 as the National Association for the Study and Prevention of Tuberculosis) is the leading US lung-health charity. Funds research grants, runs Better Breathers Clubs for COPD/emphysema, advocates federally for clean-air rules + tobacco regulation. Iconic Christmas Seals annual fundraising campaign.",
      "American Lung Association (EIN 13-1632524, основан в 1904 году как National Association for the Study and Prevention of Tuberculosis) — ведущая в США благотворительная организация по здоровью лёгких. Финансирует исследовательские гранты, ведёт Better Breathers Clubs для ХОБЛ/эмфиземы, лоббирует на федеральном уровне правила чистого воздуха и табачное регулирование. Знаковая ежегодная фандрайзинговая кампания Christmas Seals.",
      "https://www.lung.org/donate", 100000000, 78, 1904, date(2024, 6, 30),
      ["lung-disease", "global-health"],
      _us_pp("131632524"), "irs_990", _verify_us()),

    E("cure-alzheimers-fund", "US", "522348320", "people",
      "Cure Alzheimer's Fund", "Cure Alzheimer's Fund",
      "Alzheimer's research-only charity — 100% of donations go to research.",
      "Благотворительный фонд исключительно по исследованиям Альцгеймера — 100% пожертвований идёт на науку.",
      "Cure Alzheimer's Fund (EIN 52-2348320, founded 2004) operates on a 100% donations-to-research model — all admin and fundraising overhead is paid by a separate group of founder donors. Funds Alzheimer's research grants worldwide; pioneered the 'Alzheimer's Genome Project' identifying disease-relevant genes.",
      "Cure Alzheimer's Fund (EIN 52-2348320, основан в 2004 году) работает по модели «100% пожертвований на исследования» — все административные и фандрайзинговые накладные оплачиваются отдельной группой доноров-основателей. Финансирует исследовательские гранты по болезни Альцгеймера по всему миру; пионер Alzheimer's Genome Project, выявившего гены, связанные с болезнью.",
      "https://curealz.org/donate/", 35000000, 99, 2004, date(2024, 12, 31),
      ["alzheimers-dementia", "global-health"],
      _us_pp("522348320"), "irs_990", _verify_us()),

    E("american-foundation-for-blind", "US", "131623345", "people",
      "American Foundation for the Blind (AFB)", "American Foundation for the Blind (AFB)",
      "Leading US blindness-policy organisation — Helen Keller's professional home for 44 years.",
      "Ведущая в США организация по политике защиты прав слепых — профессиональный дом Хелен Келлер в течение 44 лет.",
      "American Foundation for the Blind (EIN 13-1623345, founded 1921) is one of the oldest US blindness-services organisations. Helen Keller served as AFB's spokesperson for 44 years. Today: federal policy advocacy on disability employment + tech accessibility, research-based content for blindness professionals, blindness statistics + the Visual Impairment Quarterly journal.",
      "American Foundation for the Blind (EIN 13-1623345, основан в 1921 году) — одна из старейших в США организаций по обслуживанию слепых. Хелен Келлер была пресс-секретарём AFB в течение 44 лет. Сегодня: федеральная адвокация политики занятости инвалидов и доступности технологий, ресурсы для специалистов по слепоте, статистика слепоты + журнал Visual Impairment Quarterly.",
      "https://www.afb.org/donate", 4500000, 76, 1921, date(2024, 6, 30),
      ["blindness-low-vision", "disability-services"],
      _us_pp("131623345"), "irs_990", _verify_us(), "medium"),

    E("sesame-workshop", "US", "131973898", "people",
      "Sesame Workshop", "Sesame Workshop",
      "Producer of Sesame Street + international children's educational TV in 150+ countries.",
      "Производитель Sesame Street + международного детского образовательного ТВ в 150+ странах.",
      "Sesame Workshop (EIN 13-1973898, founded 1968 as Children's Television Workshop) produces Sesame Street and operates international co-productions in 150+ countries (Rechov Sumsum in Israel, Zhima Jie in China, Sisimpur in Bangladesh). Mission-driven children's media on early literacy, numeracy, social-emotional learning, and topics like refugees (post-Syria) and special needs.",
      "Sesame Workshop (EIN 13-1973898, основан в 1968 году как Children's Television Workshop) выпускает Sesame Street и ведёт международные совместные производства в 150+ странах (Rechov Sumsum в Израиле, Zhima Jie в Китае, Sisimpur в Бангладеш). Миссионерские детские медиа по ранней грамотности, счёту, социально-эмоциональному обучению и темам как беженцы (после Сирии) и особые потребности.",
      "https://www.sesameworkshop.org/donate", 220000000, 80, 1968, date(2024, 6, 30),
      ["childrens-media", "education", "child-welfare"],
      _us_pp("131973898"), "irs_990", _verify_us()),

    E("national-4-h-council", "US", "521265758", "people",
      "National 4-H Council", "National 4-H Council",
      "Largest US youth-development non-profit — STEM, healthy living, civic engagement.",
      "Крупнейшая в США некоммерческая организация развития молодёжи — STEM, здоровый образ жизни, гражданская активность.",
      "National 4-H Council (EIN 52-1265758, founded 1976) supports the 4-H movement — the largest US positive-youth-development organisation, reaching ~6M youth annually through partnerships with USDA Cooperative Extension at land-grant universities. Programmes on STEM (40% of activities), agriculture, healthy living, civic leadership. Council is the national private-philanthropy partner.",
      "National 4-H Council (EIN 52-1265758, основан в 1976 году) поддерживает движение 4-H — крупнейшую в США организацию позитивного развития молодёжи, охватывающую ~6 млн молодёжи ежегодно через партнёрства с USDA Cooperative Extension в land-grant университетах. Программы STEM (40% активностей), сельское хозяйство, здоровый образ жизни, гражданское лидерство. Совет — национальный частный филантропический партнёр.",
      "https://4-h.org/donate/", 60000000, 81, 1976, date(2024, 9, 30),
      ["youth-development", "education", "youth-mentoring"],
      _us_pp("521265758"), "irs_990", _verify_us()),

    E("national-ffa-foundation", "US", "237340496", "people",
      "National FFA Foundation", "National FFA Foundation",
      "Funds US Future Farmers of America — agricultural-education youth org, ~1M members.",
      "Финансирует Future Farmers of America — молодёжную организацию аграрного образования США, ~1 млн членов.",
      "National FFA Foundation (EIN 23-7340496) is the philanthropic arm of National FFA Organization (Future Farmers of America) — a US youth org with ~1M members in middle and high school agriculture-education programmes. Funds chapter scholarships, leadership conferences, and the National FFA Convention. Partners with the National Association of Agricultural Educators.",
      "National FFA Foundation (EIN 23-7340496) — филантропическое крыло National FFA Organization (Future Farmers of America) — молодёжной организации США с ~1 млн членов в программах сельскохозяйственного образования в средней и старшей школе. Финансирует стипендии отделений, конференции лидерства, National FFA Convention. Партнёр National Association of Agricultural Educators.",
      "https://www.ffa.org/give/", 26000000, 86, 1944, date(2024, 8, 31),
      ["youth-development", "education"],
      _us_pp("237340496"), "irs_990", _verify_us(), "medium"),

    E("ploughshares-fund", "US", "942764520", "people",
      "Ploughshares Fund", "Ploughshares Fund",
      "Public foundation funding nuclear-weapons-elimination grants since 1981.",
      "Публичный фонд, финансирующий гранты по ликвидации ядерного оружия с 1981 года.",
      "Ploughshares Fund (EIN 94-2764520, founded 1981 by Sally Lilienthal) is a public grant-making foundation focused exclusively on reducing nuclear-weapons risk. Funds ~$10-15M/year of grants to ~70 grantee organisations (Federation of American Scientists, Union of Concerned Scientists, Arms Control Association). Federal policy advocacy on arms control + Iran deal preservation.",
      "Ploughshares Fund (EIN 94-2764520, основан в 1981 году Sally Lilienthal) — публичный грантодающий фонд, исключительно сосредоточенный на снижении ядерных рисков. Финансирует ~$10-15 млн в год грантов ~70 организациям-грантополучателям (Federation of American Scientists, Union of Concerned Scientists, Arms Control Association). Федеральная адвокация контроля над вооружениями + сохранения иранской ядерной сделки.",
      "https://ploughshares.org/donate", 12000000, 78, 1981, date(2024, 12, 31),
      ["peace-disarmament", "civil-rights"],
      _us_pp("942764520"), "irs_990", _verify_us(), "medium"),

    E("independent-sector", "US", "521203782", "people",
      "Independent Sector", "Independent Sector",
      "US national membership coalition for charities and grant-makers — Capitol Hill advocacy.",
      "Национальная американская членская коалиция благотворительных организаций и грантодателей — адвокация в Конгрессе.",
      "Independent Sector (EIN 52-1203782, founded 1980) is the national US umbrella coalition of charitable non-profits, foundations and corporate giving programmes. Advocates federally on tax policy affecting non-profits (universal charitable deduction, foundation payout rules), produces the biennial 'Health of the US Nonprofit Sector' report, and convenes sector-wide standards.",
      "Independent Sector (EIN 52-1203782, основан в 1980 году) — национальная американская зонтичная коалиция благотворительных НПО, фондов и программ корпоративных пожертвований. Лоббирует на федеральном уровне налоговую политику, затрагивающую НПО (универсальный благотворительный вычет, правила выплат фондов), выпускает биеннале-отчёт Health of the US Nonprofit Sector, объединяет общесекторные стандарты.",
      "https://independentsector.org/give/", 16000000, 76, 1980, date(2024, 6, 30),
      ["philanthropic-infrastructure"],
      _us_pp("521203782"), "irs_990", _verify_us(), "medium"),

    E("center-for-victims-of-torture", "US", "411768932", "people",
      "Center for Victims of Torture (CVT)", "Center for Victims of Torture (CVT)",
      "Largest US torture-rehabilitation org — psychological, physical, social rehab for torture survivors.",
      "Крупнейшая в США организация реабилитации жертв пыток — психологическая, физическая, социальная реабилитация переживших пытки.",
      "Center for Victims of Torture (EIN 41-1768932, founded 1985 in Minneapolis) is the largest US organisation specifically rehabilitating torture survivors. Operates US healing-centres in Minnesota and Georgia, plus international centres in Jordan (Syrian refugees), Ethiopia (Eritrean and others), DR Congo and Uganda. Federal advocacy for the Torture Victims Relief Act.",
      "Center for Victims of Torture (EIN 41-1768932, основан в 1985 году в Миннеаполисе) — крупнейшая в США организация, специально реабилитирующая переживших пытки. Управляет US healing-центрами в Миннесоте и Джорджии, плюс международные центры в Иордании (сирийские беженцы), Эфиопии (эритрейцы и др.), ДРК и Уганде. Федеральная адвокация Torture Victims Relief Act.",
      "https://www.cvt.org/donate", 35000000, 86, 1985, date(2024, 6, 30),
      ["torture-rehabilitation", "refugees", "humanitarian-medicine"],
      _us_pp("411768932"), "irs_990", _verify_us()),

    E("global-fund-for-women", "US", "770155782", "people",
      "Global Fund for Women", "Global Fund for Women",
      "Public foundation funding women's-rights movements in ~175 countries — flexible, trust-based grants.",
      "Публичный фонд, финансирующий женские правозащитные движения в ~175 странах — гибкие гранты на основе доверия.",
      "Global Fund for Women (EIN 77-0155782, founded 1987) is a public grant-making foundation supporting women's-rights movements globally. Has made ~12K grants to ~5K women-led groups in ~175 countries since founding. Trust-based philanthropy approach — flexible, multi-year, general-operating grants. Focus areas: gender-based violence, economic empowerment, sexual & reproductive rights.",
      "Global Fund for Women (EIN 77-0155782, основан в 1987 году) — публичный грантодающий фонд, поддерживающий женские правозащитные движения по всему миру. С момента основания выдал ~12 тыс. грантов ~5 тыс. женских групп в ~175 странах. Подход trust-based philanthropy — гибкие, многолетние, общеоперационные гранты. Ключевые направления: гендерное насилие, экономическое расширение прав, сексуальные и репродуктивные права.",
      "https://www.globalfundforwomen.org/donate/", 25000000, 84, 1987, date(2024, 12, 31),
      ["global-womens-rights", "womens-rights", "civil-rights"],
      _us_pp("770155782"), "irs_990", _verify_us()),

    E("team-rubicon", "US", "271720480", "people",
      "Team Rubicon", "Team Rubicon",
      "Veteran-led US disaster-response NGO — deploys to disasters domestically + globally.",
      "Американская НПО реагирования на бедствия, ведомая ветеранами — развёртывание на бедствия в США и в мире.",
      "Team Rubicon (EIN 27-1720480, founded 2010 by Marine Corps veterans Jake Wood and William McNulty after the Haiti earthquake) deploys veteran-led teams to natural disasters worldwide. ~150K registered Greyshirts (~80% veterans) responded to ~1,500+ disaster operations. Re-purposes military skills (logistics, leadership, austere-environment work) for humanitarian response.",
      "Team Rubicon (EIN 27-1720480, основан в 2010 году ветеранами Корпуса морской пехоты Джейком Вудом и Уильямом Макналти после землетрясения на Гаити) развёртывает команды, ведомые ветеранами, на стихийные бедствия по всему миру. ~150 тыс. зарегистрированных Greyshirts (~80% ветеранов) реагировали на ~1500+ операций. Перепрофилирует военные навыки (логистика, лидерство, работа в суровых условиях) для гуманитарного реагирования.",
      "https://teamrubiconusa.org/donate/", 70000000, 84, 2010, date(2024, 12, 31),
      ["disaster-relief", "veterans", "emergency-response"],
      _us_pp("271720480"), "irs_990", _verify_us()),

    E("good360", "US", "237081820", "people",
      "Good360", "Good360",
      "Largest US in-kind goods distributor for non-profits — diverts surplus merchandise from retailers.",
      "Крупнейший в США дистрибьютор товаров in-kind для НПО — отвлекает излишки товаров от ритейлеров.",
      "Good360 (EIN 23-7081820, founded 1983 by Procter & Gamble) is the largest US distributor of in-kind product donations from companies to verified non-profits. Distributes ~$650M of donated retail goods per year to ~30K non-profits (Habitat for Humanity affiliates, schools, disaster-response orgs). Saves brands tax-deductible inventory write-offs while serving non-profits.",
      "Good360 (EIN 23-7081820, основан в 1983 году Procter & Gamble) — крупнейший в США дистрибьютор натуральных пожертвований от компаний верифицированным НПО. Ежегодно распределяет ~$650 млн пожертвованных розничных товаров ~30 тыс. НПО (отделения Habitat for Humanity, школы, организации реагирования на бедствия). Экономит брендам налоговые вычеты на списания запасов, обслуживая НПО.",
      "https://good360.org/donate/", 720000000, 96, 1983, date(2024, 6, 30),
      ["in-kind-logistics", "poverty-reduction"],
      _us_pp("237081820"), "irs_990", _verify_us()),

    # ============== UK (8) ==============
    E("terrence-higgins-trust", "GB", "288527", "people",
      "Terrence Higgins Trust", "Terrence Higgins Trust",
      "UK's leading HIV charity — founded in memory of one of the first UK AIDS deaths.",
      "Ведущая британская организация по ВИЧ — основана в память об одной из первых смертей от СПИДа в Великобритании.",
      "Terrence Higgins Trust (Charity Commission #288527, founded 1982 in memory of Terry Higgins, one of the first UK AIDS deaths) is the UK's leading HIV charity. Runs THT Direct helpline, HIV testing services, PrEP and PEP advocacy on the NHS, sexual-health information. Co-led campaign that achieved 'undetectable = untransmittable' (U=U) policy adoption by the NHS.",
      "Terrence Higgins Trust (Charity Commission #288527, основан в 1982 году в память о Терри Хиггинсе, одной из первых смертей от СПИДа в Великобритании) — ведущая в Великобритании организация по ВИЧ. Ведёт THT Direct helpline, услуги тестирования на ВИЧ, адвокация PrEP и PEP в NHS, информация о сексуальном здоровье. Соруководил кампанией, достигшей принятия NHS политики 'undetectable = untransmittable' (U=U).",
      "https://www.tht.org.uk/donate-to-tht", 22000000, 78, 1982, date(2024, 3, 31),
      ["hiv-aids", "lgbtq-youth", "global-health"],
      _uk_cc("288527"), "annual_report", _verify_uk()),

    E("world-jewish-relief", "GB", "290767", "people",
      "World Jewish Relief", "World Jewish Relief",
      "UK Jewish humanitarian charity — emergency response, livelihoods, Ukraine, Israel.",
      "Британская еврейская гуманитарная организация — экстренное реагирование, средства к существованию, Украина, Израиль.",
      "World Jewish Relief (Charity Commission #290767, founded 1933 by British Jews to evacuate German Jewish refugees) is the UK Jewish community's international humanitarian agency. Current operations: Ukraine humanitarian response (since 2022), Israel-Gaza response, livelihoods programmes in 15 countries, refugee resettlement in the UK including Afghan and Ukrainian arrivals.",
      "World Jewish Relief (Charity Commission #290767, основан в 1933 году британскими евреями для эвакуации немецких еврейских беженцев) — международное гуманитарное агентство британской еврейской общины. Текущие операции: украинский гуманитарный ответ (с 2022 года), реакция на Израиль-Газа, программы средств к существованию в 15 странах, расселение беженцев в Великобритании, включая прибывших из Афганистана и Украины.",
      "https://www.worldjewishrelief.org/donate/", 30000000, 84, 1933, date(2023, 12, 31),
      ["faith-based", "refugees", "humanitarian-medicine"],
      _uk_cc("290767"), "annual_report", _verify_uk()),

    E("cruse-bereavement", "GB", "208078", "people",
      "Cruse Bereavement Support", "Cruse Bereavement Support",
      "UK bereavement-support charity — free helpline + face-to-face counselling.",
      "Британская организация поддержки переживших утрату — бесплатная линия помощи + очное консультирование.",
      "Cruse Bereavement Support (Charity Commission #208078, founded 1959) is the UK's largest bereavement charity. Operates a free helpline (0808 808 1677), online live chat, ~5K trained volunteer bereavement workers offering free face-to-face support across England, Wales and Northern Ireland. Specialist youth service: Cruse for Children & Young People.",
      "Cruse Bereavement Support (Charity Commission #208078, основан в 1959 году) — крупнейшая в Великобритании организация поддержки переживших утрату. Управляет бесплатной линией помощи (0808 808 1677), онлайн-чатом, ~5 тыс. обученных волонтёров-работников по утрате, предлагающих бесплатную очную поддержку в Англии, Уэльсе и Северной Ирландии. Специализированная молодёжная служба: Cruse for Children & Young People.",
      "https://www.cruse.org.uk/donate", 8000000, 76, 1959, date(2024, 3, 31),
      ["bereavement", "mental-health"],
      _uk_cc("208078"), "annual_report", _verify_uk(), "medium"),

    E("age-international", "GB", "1128267", "people",
      "Age International", "Age International",
      "International arm of Age UK — older people's rights and humanitarian work globally.",
      "Международное крыло Age UK — права пожилых и гуманитарная работа в мире.",
      "Age International (operating under Age UK's Charity Commission #1128267) is the international arm of Age UK. Works in ~45 countries through HelpAge International network on emergency response (older people in disasters), pensions advocacy, and elder healthcare. UK government Disasters Emergency Committee (DEC) member.",
      "Age International (работает под Age UK's Charity Commission #1128267) — международное крыло Age UK. Работает в ~45 странах через сеть HelpAge International: экстренное реагирование (пожилые в бедствиях), адвокация пенсий, гериатрическое здравоохранение. Член Disasters Emergency Committee (DEC) британского правительства.",
      "https://www.ageinternational.org.uk/donate/", 10000000, 80, 2012, date(2024, 3, 31),
      ["elderly-care", "humanitarian-medicine", "senior-care"],
      _uk_cc("1128267"), "annual_report", _verify_uk(), "medium"),

    E("blue-cross-uk", "GB", "224392", "animals",
      "Blue Cross (UK)", "Blue Cross (UK)",
      "UK pet charity — pet hospitals, rehoming, pet-bereavement support, equine welfare.",
      "Британская организация защиты домашних животных — ветклиники, пристройство, поддержка при утрате питомца, лошадиное благополучие.",
      "Blue Cross (Charity Commission #224392, founded 1897 as Our Dumb Friends League) is one of the UK's oldest animal-welfare charities. Operates 4 pet hospitals (low-cost vet care for pet owners on welfare), ~12 rehoming centres for dogs/cats/horses, the UK's first pet-bereavement support service, and the Blue Cross Equine Welfare programme.",
      "Blue Cross (Charity Commission #224392, основан в 1897 году как Our Dumb Friends League) — одна из старейших британских организаций по благополучию животных. Управляет 4 ветеринарными больницами (дешёвый ветуход для владельцев питомцев на пособиях), ~12 центрами пристройства для собак/кошек/лошадей, первой в Великобритании службой поддержки при утрате питомца, программой Blue Cross Equine Welfare.",
      "https://www.bluecross.org.uk/donate", 45000000, 80, 1897, date(2024, 3, 31),
      ["animal-welfare"],
      _uk_cc("224392"), "annual_report", _verify_uk()),

    E("shelterbox", "GB", "1096479", "people",
      "ShelterBox", "ShelterBox",
      "Disaster-relief charity providing emergency shelter and tools after disasters worldwide.",
      "Организация помощи при бедствиях, предоставляющая экстренное жильё и инструменты после катастроф.",
      "ShelterBox (Charity Commission #1096479, founded 2000 in Cornwall) provides emergency shelter and household tools after natural disasters and conflict displacement. Pioneered the 'ShelterBox' — a large green box containing a family-sized tent, water-purification tools, blankets, cooking kit, mosquito nets. Deployed in ~100+ countries since founding.",
      "ShelterBox (Charity Commission #1096479, основан в 2000 году в Корнуолле) обеспечивает экстренное жильё и хозяйственные инструменты после стихийных бедствий и конфликтного перемещения. Пионер ShelterBox — большой зелёный ящик, содержащий семейную палатку, инструменты очистки воды, одеяла, набор для готовки, противомоскитные сетки. Развёрнут в ~100+ странах с момента основания.",
      "https://www.shelterbox.org/donate/", 35000000, 80, 2000, date(2024, 3, 31),
      ["disaster-relief", "emergency-response", "refugees"],
      _uk_cc("1096479"), "annual_report", _verify_uk()),

    E("ifaw-uk", "GB", "1024806", "animals",
      "International Fund for Animal Welfare (IFAW) UK", "International Fund for Animal Welfare (IFAW) UK",
      "UK arm of global animal welfare org — wildlife crime, marine mammals, disaster rescue.",
      "Британское крыло глобальной организации защиты животных — преступления против дикой природы, морские млекопитающие, спасение при бедствиях.",
      "International Fund for Animal Welfare (Charity Commission #1024806) is one of the largest global animal-welfare NGOs (HQ Yarmouth, US Massachusetts; UK office is a separate legal entity). Operations in ~40 countries: wildlife-crime investigations and prosecutor support, marine-mammal stranding response, post-disaster animal rescue (e.g. Australian bushfires, Ukraine), elephant orphanage operations.",
      "International Fund for Animal Welfare (Charity Commission #1024806) — одна из крупнейших глобальных НПО по защите животных (штаб-квартира в Ярмуте, штат Массачусетс; британский офис — отдельное юрлицо). Операции в ~40 странах: расследования преступлений против дикой природы и поддержка прокуроров, реагирование на выбросы морских млекопитающих, спасение животных после бедствий (австралийские пожары, Украина), приюты для слонят.",
      "https://www.ifaw.org/uk/donate", 85000000, 82, 1969, date(2024, 6, 30),
      ["wildlife-conservation", "marine-mammal-protection", "animal-welfare"],
      _uk_cc("1024806"), "annual_report", _verify_uk()),

    E("dkms-uk", "GB", "1150056", "people",
      "DKMS UK", "DKMS UK — реестр доноров костного мозга",
      "UK arm of DKMS — world's largest blood-stem-cell donor registry, originally German.",
      "Британское крыло DKMS — крупнейший в мире реестр доноров стволовых клеток крови, изначально немецкий.",
      "DKMS UK (Charity Commission #1150056, UK arm founded 2013) is the UK national office of DKMS — the world's largest blood-stem-cell donor registry, originally founded in Germany 1991. Operates the UK donor drives, matches UK donors to anywhere-in-the-world recipients, runs DKMS Patients Programme financial support. Global registry has 11M+ registered donors.",
      "DKMS UK (Charity Commission #1150056, британское крыло основано в 2013 году) — британское национальное отделение DKMS — крупнейшего в мире реестра доноров стволовых клеток крови, изначально основанного в Германии в 1991 году. Управляет британскими donor drives, сопоставляет британских доноров с реципиентами по всему миру, ведёт DKMS Patients Programme финансовой поддержки. Глобальный реестр имеет 11+ млн зарегистрированных доноров.",
      "https://www.dkms.org.uk/donate", 18000000, 85, 2013, date(2024, 3, 31),
      ["blood-stem-cell-registry", "blood-cancer-research", "global-health"],
      _uk_cc("1150056"), "annual_report", _verify_uk()),

    # ============== Germany (5) ==============
    E("dkms-deutschland", "DE", "DE-DKMS-1991", "people",
      "DKMS Deutschland", "DKMS Deutschland",
      "World's largest blood-stem-cell donor registry — German HQ, founded 1991.",
      "Крупнейший в мире реестр доноров стволовых клеток крови — немецкая штаб-квартира, основан в 1991 году.",
      "DKMS Deutschland (Tübingen, founded 1991 by Peter Harf after his wife died of leukaemia for lack of a matching donor) is the world's largest blood-stem-cell donor registry. ~11M+ donors registered globally across DE/US/UK/PL/IN/ZA/CL national arms. ~95K donor matches facilitated to date.",
      "DKMS Deutschland (Тюбинген, основан в 1991 году Петером Харфом после смерти его жены от лейкемии из-за отсутствия подходящего донора) — крупнейший в мире реестр доноров стволовых клеток крови. ~11+ млн доноров зарегистрировано глобально в национальных крыльях DE/US/UK/PL/IN/ZA/CL. ~95 тыс. матчей доноров облегчено на текущий момент.",
      "https://www.dkms.de/spenden", 180000000, 89, 1991, date(2023, 12, 31),
      ["blood-stem-cell-registry", "blood-cancer-research", "global-health"],
      "https://www.dkms.de/spenden/jahresbericht", "annual_report", _verify_de()),

    E("wwf-deutschland", "DE", "DE-WWF-1963", "planet",
      "WWF Deutschland", "WWF Deutschland",
      "German national office of WWF — climate, biodiversity, forests, oceans.",
      "Немецкое национальное отделение WWF — климат, биоразнообразие, леса, океаны.",
      "WWF Deutschland (founded 1963 in Frankfurt) is the German national office of the WWF International network. ~620K supporters; ~€100M annual budget. Major focus: Amazon and Congo Basin forest protection, EU climate policy, baltic-sea protection, marine fisheries reform. DZI Spendensiegel certified.",
      "WWF Deutschland (основан в 1963 году во Франкфурте) — немецкое национальное отделение сети WWF International. ~620 тыс. сторонников; ~€100 млн годовой бюджет. Основной фокус: защита лесов Амазонии и Конго, климатическая политика ЕС, защита Балтийского моря, реформа морских рыбных промыслов. Сертифицирован DZI Spendensiegel.",
      "https://www.wwf.de/spenden", 110000000, 81, 1963, date(2023, 12, 31),
      ["conservation", "climate", "biodiversity-defense"],
      "https://www.wwf.de/ueber-uns/transparenz/", "annual_report", _verify_de()),

    E("tafel-deutschland", "DE", "DE-TAFEL-1995", "people",
      "Tafel Deutschland", "Tafel Deutschland",
      "Federation of ~960 local food banks across Germany — distributing surplus food.",
      "Федерация ~960 местных продбанков по всей Германии — распределение излишков еды.",
      "Tafel Deutschland (founded 1995, federation since 1996) is the umbrella federation of ~960 local Tafeln (food banks) across Germany. ~60K volunteer staff distribute surplus food from retailers and manufacturers to ~2M people in need. Iconic German civil-society response to food insecurity — partnered with retailers (Edeka, Rewe, Aldi).",
      "Tafel Deutschland (основан в 1995 году, федерация с 1996 года) — зонтичная федерация ~960 местных Tafeln (продбанков) по всей Германии. ~60 тыс. волонтёров распределяют излишки еды от ритейлеров и производителей ~2 млн нуждающимся. Знаковый немецкий гражданско-общественный ответ на продовольственную незащищённость — партнёры с ритейлерами (Edeka, Rewe, Aldi).",
      "https://www.tafel.de/spenden", 25000000, 90, 1995, date(2023, 12, 31),
      ["food-banks", "hunger", "poverty-reduction"],
      "https://www.tafel.de/ueber-uns/transparenz/", "annual_report", _verify_de()),

    E("malteser-deutschland", "DE", "DE-MALTESER-1953", "people",
      "Malteser Hilfsdienst (Germany)", "Malteser Hilfsdienst",
      "German member of the Order of Malta — disaster response, first aid, dementia services.",
      "Немецкий член Мальтийского ордена — реагирование на бедствия, первая помощь, услуги при деменции.",
      "Malteser Hilfsdienst (founded 1953 in Cologne) is the German member of the Order of Malta. Provides ambulance and emergency response, first-aid training (~1M people trained annually), dementia services, refugee reception, and international humanitarian work via Malteser International (~25 countries). DZI Spendensiegel certified.",
      "Malteser Hilfsdienst (основан в 1953 году в Кёльне) — немецкий член Мальтийского ордена. Обеспечивает скорую помощь и экстренное реагирование, обучение первой помощи (~1 млн человек ежегодно), услуги при деменции, приём беженцев и международную гуманитарную работу через Malteser International (~25 стран). Сертифицирован DZI Spendensiegel.",
      "https://www.malteser.de/spenden", 320000000, 88, 1953, date(2023, 12, 31),
      ["knights-of-malta-medical", "humanitarian-medicine", "disaster-relief"],
      "https://www.malteser.de/ueber-uns/zahlen-und-fakten.html", "annual_report", _verify_de()),

    E("awo-deutschland", "DE", "DE-AWO-1919", "people",
      "Arbeiterwohlfahrt (AWO)", "Arbeiterwohlfahrt (AWO)",
      "Largest German social-services federation rooted in the labour movement — ~14K facilities.",
      "Крупнейшая социальная федерация Германии, корнями в рабочем движении — ~14 тыс. учреждений.",
      "Arbeiterwohlfahrt (AWO, founded 1919 by SPD politician Marie Juchacz) is one of Germany's largest welfare federations alongside Caritas and Diakonie. ~14K facilities — daycare centres, eldercare, mental-health support, migration services, addiction help. ~225K paid staff and ~70K volunteers. Rooted in the German workers' movement, secular.",
      "Arbeiterwohlfahrt (AWO, основан в 1919 году политиком SPD Мари Юхач) — одна из крупнейших социальных федераций Германии наряду с Caritas и Diakonie. ~14 тыс. учреждений — детские сады, уход за пожилыми, поддержка психического здоровья, миграционные услуги, помощь при зависимостях. ~225 тыс. оплачиваемых сотрудников и ~70 тыс. волонтёров. Корни в немецком рабочем движении, светский.",
      "https://www.awo.org/spenden", 200000000, 88, 1919, date(2023, 12, 31),
      ["german-labor-welfare", "elderly-care", "child-welfare", "mental-health"],
      "https://www.awo.org/wirueberuns/finanzen", "annual_report", _verify_de()),

    # ============== Netherlands (3) ==============
    E("natuurmonumenten", "NL", "RSIN-002816579", "planet",
      "Vereniging Natuurmonumenten", "Vereniging Natuurmonumenten",
      "Dutch nature-conservation membership association — owns and manages ~110K hectares of nature reserves.",
      "Голландская членская природоохранная ассоциация — владеет и управляет ~110 тыс. гектарами природных заповедников.",
      "Vereniging Natuurmonumenten (RSIN 002816579, founded 1905) is the leading Dutch nature-conservation membership organisation. Owns and manages ~110K hectares of nature reserves (~3% of the Netherlands), including the iconic Veluwe, Naardermeer (the Netherlands' first nature reserve, purchased 1906), and de Loonse en Drunense Duinen. ~880K members. CBF Erkend.",
      "Vereniging Natuurmonumenten (RSIN 002816579, основан в 1905 году) — ведущая голландская членская природоохранная организация. Владеет и управляет ~110 тыс. гектарами природных заповедников (~3% территории Нидерландов), включая знаковые Велуве, Наардермеер (первый природный заповедник Нидерландов, куплен в 1906 году) и de Loonse en Drunense Duinen. ~880 тыс. членов. CBF Erkend.",
      "https://www.natuurmonumenten.nl/over-ons/doneer", 110000000, 81, 1905, date(2024, 3, 31),
      ["nature-conservation-nl", "conservation", "biodiversity-defense"],
      "https://www.natuurmonumenten.nl/over-ons/jaarverslag", "annual_report", _verify_nl()),

    E("het-vergeten-kind", "NL", "RSIN-815038996", "people",
      "Het Vergeten Kind", "Het Vergeten Kind — голландский фонд «забытых детей»",
      "Dutch foundation supporting children growing up in unsafe situations in the Netherlands.",
      "Голландский фонд, поддерживающий детей, растущих в небезопасных условиях в Нидерландах.",
      "Het Vergeten Kind (RSIN 815038996, founded 2004) raises Dutch public awareness for the ~45K children growing up in unsafe situations in the Netherlands (women's shelters, foster care, asylum-seeker centres). Funds resource bags, summer camps, structural programmes inside shelters. CBF Erkend.",
      "Het Vergeten Kind (RSIN 815038996, основан в 2004 году) повышает осведомлённость голландской общественности о ~45 тыс. детей, растущих в небезопасных условиях в Нидерландах (женские приюты, фостерные семьи, центры лиц, ищущих убежища). Финансирует resource bags, летние лагеря, структурные программы внутри приютов. CBF Erkend.",
      "https://www.hetvergetenkind.nl/doneer/", 12000000, 80, 2004, date(2024, 3, 31),
      ["child-protection", "child-welfare", "domestic-violence"],
      "https://www.hetvergetenkind.nl/over-ons/financiele-informatie/", "annual_report", _verify_nl(), "medium"),

    E("vluchtelingenwerk-nl", "NL", "RSIN-002959419", "people",
      "VluchtelingenWerk Nederland", "VluchtelingenWerk Nederland — Голландский совет по делам беженцев",
      "Dutch Refugee Council — supports asylum seekers and refugees in the Netherlands.",
      "Голландский совет по делам беженцев — поддерживает лиц, ищущих убежища, и беженцев в Нидерландах.",
      "VluchtelingenWerk Nederland (RSIN 002959419, founded 1979) is the Dutch national refugee council. Operates volunteer-staffed offices at ~50 asylum-seeker centres (AZCs) plus 200+ local refugee-integration offices. Legal advice, language buddies, employment support, family-reunification support. CBF Erkend.",
      "VluchtelingenWerk Nederland (RSIN 002959419, основан в 1979 году) — голландский национальный совет по делам беженцев. Управляет офисами с волонтёрами в ~50 центрах лиц, ищущих убежища (AZC), плюс 200+ местных офисов интеграции беженцев. Юрпомощь, языковые партнёры, поддержка трудоустройства, поддержка воссоединения семей. CBF Erkend.",
      "https://www.vluchtelingenwerk.nl/doneer", 75000000, 84, 1979, date(2024, 3, 31),
      ["refugees", "asylum-seekers", "humanitarian-medicine"],
      "https://www.vluchtelingenwerk.nl/over-ons/jaarverslagen", "annual_report", _verify_nl()),

    # ============== Sweden (1) ==============
    E("cancerfonden", "SE", "SE-802005-3370", "people",
      "Cancerfonden (Swedish Cancer Society)", "Cancerfonden — Шведское онкологическое общество",
      "Sweden's largest non-profit cancer research funder — ~$60M/year in research grants.",
      "Крупнейший в Швеции некоммерческий фондер онкологических исследований — ~$60 млн в год грантов.",
      "Cancerfonden (org-nr 802005-3370, founded 1951) is Sweden's largest non-profit cancer-research funder. Awards ~$60M/year of research grants to Swedish cancer scientists. Iconic Rosa Bandet (Pink Ribbon, since 2003) and Mustaschkampen (Movember Sweden) fundraising campaigns. 90-konto certified.",
      "Cancerfonden (org-nr 802005-3370, основан в 1951 году) — крупнейший в Швеции некоммерческий фондер онкологических исследований. Выдаёт ~$60 млн в год грантов шведским онкологическим учёным. Знаковые фандрайзинговые кампании Rosa Bandet (Pink Ribbon, с 2003 года) и Mustaschkampen (шведский Movember). Сертификат 90-konto.",
      "https://www.cancerfonden.se/ge-en-gava", 100000000, 82, 1951, date(2023, 12, 31),
      ["swedish-cancer-research", "cancer-research", "global-health"],
      "https://www.cancerfonden.se/om-cancerfonden/finansiell-information", "annual_report", _verify_se()),

    # ============== France (2) ==============
    E("secours-populaire", "FR", "FR-RNA-W751064167", "people",
      "Secours Populaire Français", "Secours Populaire Français",
      "Largest French anti-poverty NGO — food, holidays for poor children, international solidarity.",
      "Крупнейшая французская антибедная НПО — еда, каникулы для бедных детей, международная солидарность.",
      "Secours Populaire Français (founded 1945, separate from Secours Catholique) is one of France's largest anti-poverty NGOs. ~80K volunteers across ~1,250 local branches provide emergency food aid, clothing, summer-holiday programmes for low-income children (Journée des oubliés des vacances), legal advice, plus international development and disaster response.",
      "Secours Populaire Français (основан в 1945 году, отдельно от Secours Catholique) — одна из крупнейших антибедных НПО Франции. ~80 тыс. волонтёров в ~1250 местных отделениях обеспечивают экстренную продовольственную помощь, одежду, летние программы для детей из малообеспеченных семей (Journée des oubliés des vacances), юридические консультации, плюс международное развитие и реагирование на бедствия.",
      "https://don.secourspopulaire.fr/", 195000000, 90, 1945, date(2023, 12, 31),
      ["poverty-reduction", "child-welfare", "hunger"],
      "https://www.secourspopulaire.fr/transparence-comptes", "annual_report", _verify_fr()),

    E("petits-freres-pauvres", "FR", "FR-RNA-W751208870", "people",
      "Les Petits Frères des Pauvres", "Les Petits Frères des Pauvres",
      "French elderly-loneliness charity — befriending older people in isolation.",
      "Французская организация против одиночества пожилых — компаньонство для одиноких пожилых.",
      "Les Petits Frères des Pauvres (founded 1946 by Armand Marquiset in Paris) is France's leading elderly-loneliness charity. ~13K volunteers across France visit and befriend older people in isolation. Annual Christmas réveillon dinners (since the founding year) — bringing isolated seniors together. Federal advocacy on the loneliness epidemic among French elderly.",
      "Les Petits Frères des Pauvres (основан в 1946 году Арманом Маркизе в Париже) — ведущая французская организация против одиночества пожилых. ~13 тыс. волонтёров по всей Франции посещают и дружат с одинокими пожилыми. Ежегодные Christmas réveillon ужины (с года основания) — собирают одиноких пенсионеров вместе. Федеральная адвокация эпидемии одиночества среди французских пожилых.",
      "https://www.petitsfreresdespauvres.fr/faire-un-don/", 75000000, 84, 1946, date(2023, 12, 31),
      ["elderly-care", "senior-care", "faith-based"],
      "https://www.petitsfreresdespauvres.fr/qui-sommes-nous/transparence-financiere/", "annual_report", _verify_fr()),

    # ============== Switzerland (1) ==============
    E("pro-senectute-switzerland", "CH", "CH-660-0028973-1", "people",
      "Pro Senectute Schweiz", "Pro Senectute Schweiz",
      "Largest Swiss organisation for older people — counselling, in-home help, federal-policy advocacy.",
      "Крупнейшая швейцарская организация для пожилых — консультирование, помощь на дому, федеральная адвокация.",
      "Pro Senectute Schweiz (founded 1917 in Olten) is the largest Swiss organisation specifically for older people. Operates 24 cantonal/regional offices plus the national umbrella; provides life-counselling for retirees, in-home help, sport-activities programmes for seniors, federal-policy advocacy on AHV (Swiss state pension) and inheritance law. ZEWO certified.",
      "Pro Senectute Schweiz (основан в 1917 году в Ольтене) — крупнейшая швейцарская организация, специально для пожилых. Управляет 24 кантональными/региональными офисами плюс национальный зонтик; предоставляет жизненное консультирование для пенсионеров, помощь на дому, спортивно-развлекательные программы для пожилых, федеральную адвокацию AHV (швейцарской государственной пенсии) и наследственного права. Сертифицирован ZEWO.",
      "https://www.prosenectute.ch/de/spenden", 165000000, 84, 1917, date(2023, 12, 31),
      ["elderly-care", "senior-care"],
      "https://www.prosenectute.ch/de/ueber-uns/finanzen", "annual_report", _verify_ch()),

    # ============== Italy (2) ==============
    E("istituto-humanitas-italy", "IT", "IT-10125720157", "people",
      "Fondazione Humanitas per la Ricerca", "Fondazione Humanitas per la Ricerca",
      "Funds the Istituto Clinico Humanitas medical research — translational immunology, oncology.",
      "Финансирует Istituto Clinico Humanitas — трансляционная иммунология, онкология.",
      "Fondazione Humanitas per la Ricerca (C.F. 10125720157) raises funds for the Istituto Clinico Humanitas teaching hospital (Rozzano, Milan area). Major research programmes in translational immunology (gut microbiome, immunotherapy for cancer), oncology, and cardiovascular medicine. Hospital is part of Humanitas University.",
      "Fondazione Humanitas per la Ricerca (C.F. 10125720157) собирает средства для университетской клиники Istituto Clinico Humanitas (Розано, район Милана). Крупные исследовательские программы в трансляционной иммунологии (кишечная микробиота, иммунотерапия рака), онкологии, сердечно-сосудистой медицине. Больница — часть Humanitas University.",
      "https://www.fondazionehumanitas.it/dona-ora/", 28000000, 84, 2003, date(2023, 12, 31),
      ["cancer-research", "global-health"],
      "https://www.fondazionehumanitas.it/chi-siamo/bilancio/", "annual_report", _verify_it()),

    E("fondazione-mediolanum", "IT", "IT-04357620153", "people",
      "Fondazione Mediolanum", "Fondazione Mediolanum",
      "Italian corporate-foundation supporting projects for children in Italy and worldwide.",
      "Итальянский корпоративный фонд, поддерживающий проекты для детей в Италии и в мире.",
      "Fondazione Mediolanum (C.F. 04357620153, founded 2005 by Banca Mediolanum) funds children-focused projects in Italy (educational poverty, after-school programmes, child-protection) and through international partners (Bambini in Emergenza in Romania, Operation Smile, Mission Bambini). Co-funded by employees + customers of Banca Mediolanum.",
      "Fondazione Mediolanum (C.F. 04357620153, основан в 2005 году Banca Mediolanum) финансирует проекты, ориентированные на детей, в Италии (образовательная бедность, послешкольные программы, защита детей) и через международных партнёров (Bambini in Emergenza в Румынии, Operation Smile, Mission Bambini). Софинансируется сотрудниками и клиентами Banca Mediolanum.",
      "https://www.fondazionemediolanum.it/donazioni/", 15000000, 86, 2005, date(2023, 12, 31),
      ["child-welfare", "education"],
      "https://www.fondazionemediolanum.it/chi-siamo/bilancio-sociale/", "annual_report", _verify_it(), "medium"),

    # ============== Spain (2) ==============
    E("ayuda-en-accion", "ES", "ES-G79049909", "people",
      "Ayuda en Acción", "Ayuda en Acción",
      "Spanish international development NGO — child sponsorship + community-led poverty work in ~20 countries.",
      "Испанская организация международного развития — спонсорство детей + работа против бедности на уровне общин в ~20 странах.",
      "Ayuda en Acción (NIF G79049909, founded 1981) is one of Spain's leading international development NGOs. Works in ~20 countries on child sponsorship, education access, women's economic empowerment, gender-based violence prevention, food security. Domestic Spain programmes also: educational support for low-income children, refugee integration.",
      "Ayuda en Acción (NIF G79049909, основан в 1981 году) — одна из ведущих испанских НПО международного развития. Работает в ~20 странах: спонсорство детей, доступ к образованию, экономическое расширение прав женщин, профилактика гендерного насилия, продовольственная безопасность. Также внутренние программы в Испании: образовательная поддержка детей из малообеспеченных семей, интеграция беженцев.",
      "https://ayudaenaccion.org/colabora/", 65000000, 84, 1981, date(2023, 12, 31),
      ["poverty-reduction", "child-welfare", "global-womens-rights"],
      "https://ayudaenaccion.org/quienes-somos/transparencia/", "annual_report", _verify_es()),

    E("intermon-oxfam-spain", "ES", "ES-G58236803", "people",
      "Oxfam Intermón", "Oxfam Intermón — испанский член Oxfam",
      "Spanish member of Oxfam International — emergency response, climate justice, inequality work.",
      "Испанский член Oxfam International — экстренное реагирование, климатическая справедливость, работа по неравенству.",
      "Oxfam Intermón (NIF G58236803, founded 1956 as Intermón by Jesuit-affiliated organisations; joined Oxfam in 1997) is the Spanish member of the Oxfam International confederation. ~700 staff and ~600 volunteers across Spain and partner countries. Climate justice and inequality (Davos billionaires-vs-poor annual report) are signature campaigns.",
      "Oxfam Intermón (NIF G58236803, основан в 1956 году как Intermón иезуитско-аффилированными организациями; присоединился к Oxfam в 1997 году) — испанский член международной конфедерации Oxfam. ~700 сотрудников и ~600 волонтёров в Испании и партнёрских странах. Климатическая справедливость и неравенство (ежегодный отчёт Давоса о миллиардерах vs бедных) — знаковые кампании.",
      "https://www.oxfamintermon.org/es/colaborar", 70000000, 82, 1956, date(2023, 12, 31),
      ["poverty-reduction", "humanitarian-medicine", "climate-policy"],
      "https://www.oxfamintermon.org/es/quienes-somos/cuentas-resultados", "annual_report", _verify_es()),
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
                "url": entry["source_url"], "source_label": "IRS Form 990 (ProPublica)", "file_format": "pdf"}
    if entry["country"] == "GB":
        return {"kind": "annual_report", "filed_date": entry["last_filed_date"],
                "label": {"en": "Annual report & accounts (FY 2023)", "ru": "Годовой отчёт и финансовая отчётность (2023)"},
                "url": entry["source_url"], "source_label": "Charity Commission UK — accounts page", "file_format": "html"}
    return {"kind": "annual_report", "filed_date": entry["last_filed_date"],
            "label": {"en": "Annual report", "ru": "Годовой отчёт"},
            "url": entry["source_url"], "source_label": "Org's own annual report", "file_format": "html"}


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
            print(f"[migration 0052] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
    print(f"[migration 0052] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0051_backfill_v312_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

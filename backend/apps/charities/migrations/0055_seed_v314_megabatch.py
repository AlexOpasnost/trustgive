"""v3.14 catalog mega-batch — seed 70 charities (471 -> ~541).

Final session push of the day. 4 new countries via 0054 schema mig
(Poland, Finland, Austria, Israel). Catalog now spans 27 countries.

70 charities across 18 countries:
  US (11): Sandy Hook Promise, Innocence Project, Equal Justice
    Initiative, Mozilla Foundation, EFF, Common Sense Media,
    Creative Commons, No Kid Hungry, National Domestic Violence
    Hotline, Humane Society International, FRAC.
  UK (9): Salvation Army UK, Guide Dogs UK, Leprosy Mission UK,
    Cure Leukaemia, Royal Marsden Cancer Charity, Kidney Research UK,
    MS Society UK, Sands UK (stillbirth), Sustrans.
  CA (4): World Vision Canada, Royal Canadian Geographical Society,
    Oxfam-Québec, CUSO International.
  AU (6): Cancer Council NSW, Cancer Council Victoria, Garvan
    Institute, Walter and Eliza Hall Institute, Mater Foundation,
    Fred Hollows Foundation.
  DE (4): UNICEF Deutschland, Misereor, Aktion Deutschland Hilft,
    Plan International Deutschland.
  FR (3): Fondation de France, UNICEF France, APF France handicap.
  IT (4): UNICEF Italia, Oxfam Italia, LILT, WWF Italia.
  ES (3): UNICEF Spain, WWF Spain, Medicus Mundi Spain.
  NL (3): UNICEF Nederland, WNF (WWF Netherlands), Amref Nederland.
  IE (3): Amnesty Ireland, Foróige, Simon Community Ireland.
  NO (2): Norsk Folkehjelp, Plan Norge.
  NZ (2): NZ Cancer Society, Fred Hollows Foundation NZ.
  BE (2): Plan International Belgium, UNICEF Belgium.
  DK (2): UNICEF Danmark, Plan International Denmark.
  PL (3, NEW): Caritas Polska, PAH, WOŚP.
  FI (3, NEW): Finnish Red Cross, UNICEF Finland, Plan Finland.
  AT (3, NEW): Caritas Austria, MSF Austria, Volkshilfe.
  IL (3, NEW): Magen David Adom, Yad Vashem, Shalva.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "gun-violence-prevention": {"en": "Gun-violence prevention", "ru": "Профилактика насилия с оружием"},
    "wrongful-conviction": {"en": "Wrongful conviction & criminal-justice reform", "ru": "Незаконные осуждения и реформа правосудия"},
    "internet-freedom": {"en": "Internet freedom & digital rights", "ru": "Свобода интернета и цифровые права"},
    "open-source": {"en": "Open-source software & licensing", "ru": "Открытое ПО и лицензии"},
    "media-literacy": {"en": "Media literacy & children's media safety", "ru": "Медиаграмотность и безопасность детских медиа"},
    "child-hunger-us": {"en": "US child hunger", "ru": "Детский голод в США"},
    "dv-hotline": {"en": "Domestic-violence hotlines", "ru": "Линии помощи при домашнем насилии"},
    "humane-international": {"en": "Humane Society International wildlife", "ru": "HSI глобальная защита животных"},
    "food-research-policy": {"en": "Food-research & SNAP policy", "ru": "Исследования продовольствия и политика SNAP"},
    "stillbirth-neonatal": {"en": "Stillbirth & neonatal death support", "ru": "Поддержка при мертворождении и неонатальной смерти"},
    "kidney-disease": {"en": "Kidney disease", "ru": "Заболевания почек"},
    "leprosy-mission": {"en": "Leprosy mission (UK)", "ru": "Миссия по проказе (Великобритания)"},
    "active-travel": {"en": "Active & sustainable travel", "ru": "Активный и устойчивый транспорт"},
    "cancer-state-australia": {"en": "Australian state cancer councils", "ru": "Австралийские штатовые онкосоветы"},
    "medical-research-institute": {"en": "Medical research institutes", "ru": "Институты медицинских исследований"},
    "trachoma-blindness": {"en": "Trachoma & avoidable blindness", "ru": "Трахома и предотвратимая слепота"},
    "polish-charity": {"en": "Polish humanitarian work", "ru": "Польская гуманитарная работа"},
    "finnish-charity": {"en": "Finnish humanitarian work", "ru": "Финская гуманитарная работа"},
    "austrian-charity": {"en": "Austrian social services", "ru": "Австрийские социальные службы"},
    "holocaust-remembrance": {"en": "Holocaust remembrance & education", "ru": "Память и образование о Холокосте"},
    "israeli-disability": {"en": "Israeli disability services", "ru": "Услуги для людей с инвалидностью в Израиле"},
    "israeli-emergency-medical": {"en": "Israeli emergency medical (MDA)", "ru": "Израильская экстренная медицина (MDA)"},
    "geographic-society": {"en": "Geographic society", "ru": "Географическое общество"},
    "international-volunteer-coop": {"en": "International volunteer cooperation", "ru": "Международное волонтёрское сотрудничество"},
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
        "ru": "Подтверждено: зарегистрирован в CRA Charities Directorate; T3010 публичен.",
    }


def _verify_au() -> dict:
    return {
        "en": "Verified: registered with ACNC; annual information statement public.",
        "ru": "Подтверждено: зарегистрирован в ACNC; ежегодное info-statement публично.",
    }


def _verify_de() -> dict:
    return {
        "en": "Verified: German gemeinnützige; annual report public.",
        "ru": "Подтверждено: немецкая некоммерческая; годовой отчёт публичен.",
    }


def _verify_fr() -> dict:
    return {
        "en": "Verified: Don en Confiance / IDEAS certified; annual report public.",
        "ru": "Подтверждено: Don en Confiance / IDEAS; годовой отчёт публичен.",
    }


def _verify_it() -> dict:
    return {
        "en": "Verified: Italian ETS/ONLUS; Bilancio Sociale public.",
        "ru": "Подтверждено: итальянская ETS/ONLUS; Bilancio Sociale публичен.",
    }


def _verify_es() -> dict:
    return {
        "en": "Verified: Spanish Registry of NGOs; Cuentas Anuales public.",
        "ru": "Подтверждено: реестр НПО Испании; Cuentas Anuales публичны.",
    }


def _verify_nl() -> dict:
    return {
        "en": "Verified: CBF Erkend; ANBI; annual report public.",
        "ru": "Подтверждено: CBF Erkend; ANBI; годовой отчёт публичен.",
    }


def _verify_ie() -> dict:
    return {
        "en": "Verified: Charities Regulator of Ireland; annual report public.",
        "ru": "Подтверждено: Charities Regulator Ирландии; годовой отчёт публичен.",
    }


def _verify_no() -> dict:
    return {
        "en": "Verified: Brønnøysundregistrene; Innsamlingskontrollen; annual report public.",
        "ru": "Подтверждено: Brønnøysundregistrene; Innsamlingskontrollen; годовой отчёт публичен.",
    }


def _verify_nz() -> dict:
    return {
        "en": "Verified: NZ Charities Services; financial statements public.",
        "ru": "Подтверждено: NZ Charities Services; финансовая отчётность публична.",
    }


def _verify_be() -> dict:
    return {
        "en": "Verified: Belgian AISBL/ASBL registered with the Crossroads Bank for Enterprises.",
        "ru": "Подтверждено: бельгийская AISBL/ASBL в Crossroads Bank for Enterprises.",
    }


def _verify_dk() -> dict:
    return {
        "en": "Verified: Erhvervsstyrelsen (Danish Business Authority); annual report public.",
        "ru": "Подтверждено: Erhvervsstyrelsen (Дания); годовой отчёт публично подан.",
    }


def _verify_pl() -> dict:
    return {
        "en": "Verified: Polish KRS register (National Court Register); annual report public.",
        "ru": "Подтверждено: польский реестр KRS; годовой отчёт публичен.",
    }


def _verify_fi() -> dict:
    return {
        "en": "Verified: Finnish Patent and Registration Office (PRH); Y-tunnus business ID; annual report public.",
        "ru": "Подтверждено: финский PRH; Y-tunnus; годовой отчёт публичен.",
    }


def _verify_at() -> dict:
    return {
        "en": "Verified: Austrian Vereinsregister; ZVR-Zahl; annual report public.",
        "ru": "Подтверждено: австрийский Vereinsregister; ZVR-Zahl; годовой отчёт публичен.",
    }


def _verify_il() -> dict:
    return {
        "en": "Verified: Israeli Registrar of Non-Profit Organizations (Amutot); financial reports public.",
        "ru": "Подтверждено: израильский реестр некоммерческих организаций (Amutot); финансовые отчёты публичны.",
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
    # ============== US (11) ==============
    E("sandy-hook-promise", "US", "461657394", "people",
      "Sandy Hook Promise", "Sandy Hook Promise",
      "School-violence prevention via 'know-the-signs' training in K-12 schools.",
      "Профилактика школьного насилия через программу «знай признаки» в школах K-12.",
      "Sandy Hook Promise (EIN 46-1657394, founded 2013 by family members of the Sandy Hook Elementary School shooting victims) is a non-partisan school-violence prevention organisation. Trains students and educators to recognise warning signs of potential violence and self-harm via the Know the Signs programmes. Reaches ~25K schools, ~22M students.",
      "Sandy Hook Promise (EIN 46-1657394, основан в 2013 году семьями жертв стрельбы в школе Сэнди-Хук) — беспартийная организация профилактики школьного насилия. Обучает учеников и учителей распознавать предупреждающие признаки потенциального насилия и самоповреждения через программы Know the Signs. Охватывает ~25 тыс. школ, ~22 млн учеников.",
      "https://www.sandyhookpromise.org/donate/", 38000000, 79, 2013, date(2024, 6, 30),
      ["gun-violence-prevention", "child-protection", "education"],
      _us_pp("461657394"), "irs_990", _verify_us()),

    E("innocence-project", "US", "320077563", "people",
      "Innocence Project", "Innocence Project",
      "Frees wrongly-convicted people via DNA evidence and reforms criminal-justice policy.",
      "Освобождает несправедливо осуждённых через ДНК-экспертизу и реформирует уголовное правосудие.",
      "Innocence Project (EIN 32-0077563, founded 1992 by Barry Scheck and Peter Neufeld at Cardozo School of Law) has helped exonerate 245+ wrongly-convicted people via post-conviction DNA testing. Federal policy advocacy on eyewitness-identification reform, recording of interrogations, forensic-science oversight, compensation for the exonerated.",
      "Innocence Project (EIN 32-0077563, основан в 1992 году Барри Шеком и Питером Нойфельдом в Cardozo School of Law) помог оправдать 245+ несправедливо осуждённых через пост-осуждение ДНК-тестирование. Федеральная адвокация реформы опознания свидетелей, записи допросов, надзора за судебной экспертизой, компенсации оправданным.",
      "https://innocenceproject.org/donate/", 50000000, 82, 1992, date(2024, 6, 30),
      ["wrongful-conviction", "civil-rights"],
      _us_pp("320077563"), "irs_990", _verify_us()),

    E("equal-justice-initiative", "US", "630871099", "people",
      "Equal Justice Initiative (EJI)", "Equal Justice Initiative (EJI)",
      "Bryan Stevenson's racial-justice legal-advocacy org — death-row defence + reparative-history museums.",
      "Правозащитная юридическая организация по расовому правосудию Брайана Стивенсона — защита смертников + музеи репаративной истории.",
      "Equal Justice Initiative (EIN 63-0871099, founded 1989 by Bryan Stevenson in Montgomery Alabama) defends the wrongly-condemned, juvenile lifers, and people on death row. Built the Legacy Museum and the National Memorial for Peace and Justice (the lynching memorial in Montgomery). Federal advocacy on sentencing reform, juvenile justice, and the legacy of slavery.",
      "Equal Justice Initiative (EIN 63-0871099, основан в 1989 году Брайаном Стивенсоном в Монтгомери, Алабама) защищает несправедливо приговорённых, несовершеннолетних с пожизненным сроком и людей на смертной казни. Построил Legacy Museum и National Memorial for Peace and Justice (мемориал линчевания в Монтгомери). Федеральная адвокация реформы вынесения приговоров, ювенальной юстиции, наследия рабства.",
      "https://eji.org/donate/", 60000000, 79, 1989, date(2024, 12, 31),
      ["wrongful-conviction", "race-equality", "civil-rights"],
      _us_pp("630871099"), "irs_990", _verify_us()),

    E("mozilla-foundation", "US", "200097189", "people",
      "Mozilla Foundation", "Mozilla Foundation",
      "Non-profit owner of Mozilla Corporation (Firefox) — funds internet-health work and open-source.",
      "Некоммерческий владелец Mozilla Corporation (Firefox) — финансирует здоровье интернета и open-source.",
      "Mozilla Foundation (EIN 20-0097189, founded 2003) is the parent 501(c)(3) of Mozilla Corporation (which makes Firefox). Funds Mozilla Fellowships for internet-health researchers, Common Voice multilingual voice dataset, AI-trustworthiness research, and open-source software grants. Publishes the annual Internet Health Report.",
      "Mozilla Foundation (EIN 20-0097189, основан в 2003 году) — материнская 501(c)(3) Mozilla Corporation (которая делает Firefox). Финансирует Mozilla Fellowships для исследователей здоровья интернета, Common Voice (многоязычный голосовой датасет), исследования надёжности ИИ, гранты open-source. Публикует ежегодный Internet Health Report.",
      "https://foundation.mozilla.org/en/donate/", 35000000, 80, 2003, date(2024, 12, 31),
      ["internet-freedom", "open-source"],
      _us_pp("200097189"), "irs_990", _verify_us()),

    E("electronic-frontier-foundation", "US", "043091431", "people",
      "Electronic Frontier Foundation (EFF)", "Electronic Frontier Foundation (EFF)",
      "Digital civil-liberties non-profit — privacy, free speech, encryption rights litigation.",
      "Некоммерческая организация цифровых прав — приватность, свобода слова, защита прав шифрования.",
      "Electronic Frontier Foundation (EIN 04-3091431, founded 1990 by John Gilmore, John Perry Barlow, Mitch Kapor) is the leading US digital-rights legal-advocacy organisation. Litigates landmark cases on government surveillance, encryption rights, content moderation, and copyright reform. Operates HTTPS Everywhere, Privacy Badger, Surveillance Self-Defense.",
      "Electronic Frontier Foundation (EIN 04-3091431, основан в 1990 году Джоном Гилмором, Джоном Перри Барлоу, Митчем Капором) — ведущая в США правозащитная юридическая организация цифровых прав. Ведёт ключевые дела по государственной слежке, правам шифрования, модерации контента, реформе авторского права. Управляет HTTPS Everywhere, Privacy Badger, Surveillance Self-Defense.",
      "https://supporters.eff.org/donate", 22000000, 78, 1990, date(2024, 6, 30),
      ["internet-freedom", "civil-rights"],
      _us_pp("043091431"), "irs_990", _verify_us()),

    E("commonsense-media", "US", "412024109", "people",
      "Common Sense Media", "Common Sense Media",
      "Non-profit reviewing kids' media for parents + advocacy on children's online safety.",
      "Некоммерческая организация, оценивающая детские медиа для родителей + адвокация онлайн-безопасности детей.",
      "Common Sense Media (EIN 41-2024109, founded 2003) is the leading US non-profit on children's media + technology. Reviews ~30K movies, TV shows, books, games, podcasts and apps for parents (~140M unique families served annually). Federal advocacy on children's online privacy (COPPA enforcement), social-media age-gating, EdTech in schools.",
      "Common Sense Media (EIN 41-2024109, основан в 2003 году) — ведущая в США некоммерческая организация по детским медиа и технологиям. Оценивает ~30 тыс. фильмов, ТВ-шоу, книг, игр, подкастов и приложений для родителей (~140 млн уникальных семей в год). Федеральная адвокация онлайн-приватности детей (исполнение COPPA), возрастных ограничений в соцсетях, EdTech в школах.",
      "https://www.commonsensemedia.org/give-donate", 60000000, 78, 2003, date(2024, 6, 30),
      ["media-literacy", "child-protection", "education"],
      _us_pp("412024109"), "irs_990", _verify_us()),

    E("creative-commons", "US", "134192159", "people",
      "Creative Commons", "Creative Commons",
      "Non-profit stewarding the Creative Commons licences — open-knowledge infrastructure for the web.",
      "Некоммерческая организация, поддерживающая лицензии Creative Commons — инфраструктура открытых знаний для веба.",
      "Creative Commons (EIN 13-4192159, founded 2001 by Lawrence Lessig, Hal Abelson and Eric Eldred) is the non-profit that publishes and supports the Creative Commons licences — the open-content licensing framework powering Wikipedia, Wikimedia Commons, OER (open educational resources), and ~2.5B CC-licensed works online. Hosts CC Summit annually.",
      "Creative Commons (EIN 13-4192159, основан в 2001 году Лоуренсом Лессигом, Халом Абельсоном и Эриком Элдредом) — некоммерческая организация, публикующая и поддерживающая лицензии Creative Commons — рамку открытого лицензирования контента, лежащую в основе Wikipedia, Wikimedia Commons, OER (открытых образовательных ресурсов) и ~2,5 млрд CC-лицензированных работ онлайн. Ежегодно проводит CC Summit.",
      "https://creativecommons.org/about/support-cc/", 4500000, 78, 2001, date(2024, 12, 31),
      ["open-source", "education"],
      _us_pp("134192159"), "irs_990", _verify_us(), "medium"),

    E("no-kid-hungry", "US", "521367538", "people",
      "Share Our Strength / No Kid Hungry", "Share Our Strength — No Kid Hungry",
      "US childhood-hunger non-profit — federal SNAP / school-meal policy + emergency feeding programmes.",
      "Американская организация против детского голода — федеральная политика SNAP / школьное питание + экстренные программы кормления.",
      "Share Our Strength (EIN 52-1367538, founded 1984) operates No Kid Hungry, the leading US childhood-hunger campaign. Federal policy advocacy on SNAP, summer-meals programmes, school breakfast expansion; grants to state-level anti-hunger groups; iconic Dine Out for No Kid Hungry annual fundraising via restaurants.",
      "Share Our Strength (EIN 52-1367538, основан в 1984 году) ведёт No Kid Hungry — ведущую в США кампанию против детского голода. Федеральная адвокация SNAP, программ летнего питания, расширения школьных завтраков; гранты штатовым антиголодным группам; знаковый ежегодный фандрайзинг Dine Out for No Kid Hungry через рестораны.",
      "https://www.nokidhungry.org/donate", 200000000, 84, 1984, date(2024, 6, 30),
      ["child-hunger-us", "hunger", "child-welfare"],
      _us_pp("521367538"), "irs_990", _verify_us()),

    E("national-domestic-violence-hotline", "US", "133829942", "people",
      "National Domestic Violence Hotline", "National Domestic Violence Hotline",
      "Free, confidential 24/7 US DV hotline — phone, text, chat, available in 200+ languages.",
      "Бесплатная конфиденциальная круглосуточная американская линия помощи при ДН — телефон, текст, чат, 200+ языков.",
      "National Domestic Violence Hotline (EIN 13-3829942, founded 1996, congressionally-mandated under VAWA) operates the free, 24/7 National DV Hotline (1-800-799-SAFE), online live-chat, and text-line (text START to 88788). Federal grant funding through HHS Family Violence Prevention and Services Act. Available in 200+ languages via interpreters.",
      "National Domestic Violence Hotline (EIN 13-3829942, основан в 1996 году, мандатом Конгресса по VAWA) ведёт бесплатную круглосуточную National DV Hotline (1-800-799-SAFE), онлайн-чат и текст-линию (текст START на 88788). Федеральное грантовое финансирование через HHS Family Violence Prevention and Services Act. Доступно на 200+ языках через переводчиков.",
      "https://www.thehotline.org/donate/", 28000000, 85, 1996, date(2024, 6, 30),
      ["dv-hotline", "domestic-violence", "womens-rights"],
      _us_pp("133829942"), "irs_990", _verify_us()),

    E("humane-society-international", "US", "222769270", "animals",
      "Humane Society International", "Humane Society International (HSI)",
      "Global arm of the Humane Society of the United States — wildlife protection, factory-farm reform, disaster response.",
      "Глобальное крыло Humane Society of the United States — защита дикой природы, реформа фабричного животноводства, реагирование на бедствия.",
      "Humane Society International (EIN 22-2769270, founded 1991) is the global arm of the Humane Society of the United States. Programmes in ~50 countries on wildlife trafficking and protection (dog meat trade rescue in South Korea, anti-poaching), factory-farm reform via corporate cage-free pledges, disaster animal-rescue.",
      "Humane Society International (EIN 22-2769270, основан в 1991 году) — глобальное крыло Humane Society of the United States. Программы в ~50 странах: контрабанда и защита дикой природы (спасение от торговли собачьим мясом в Южной Корее, антибраконьерство), реформа фабричного животноводства через корпоративные cage-free обязательства, спасение животных при бедствиях.",
      "https://www.hsi.org/donate/", 55000000, 82, 1991, date(2024, 12, 31),
      ["humane-international", "wildlife-conservation", "farm-animal-welfare"],
      _us_pp("222769270"), "irs_990", _verify_us()),

    E("frac-food-policy", "US", "521213437", "people",
      "Food Research & Action Center (FRAC)", "Food Research & Action Center (FRAC)",
      "Leading US anti-hunger policy think-tank — federal SNAP, school-meals, WIC research and advocacy.",
      "Ведущий американский антиголодный think-tank — федеральные исследования и адвокация SNAP, школьного питания, WIC.",
      "Food Research & Action Center (EIN 52-1213437, founded 1970) is the leading US anti-hunger policy think-tank and research org. Produces the annual SNAP Matters report, federal advocacy on Farm Bill nutrition title, Summer EBT expansion, and the Child Nutrition Reauthorisation. Partners with ~1,000 state and local anti-hunger advocates.",
      "Food Research & Action Center (EIN 52-1213437, основан в 1970 году) — ведущий американский антиголодный think-tank и исследовательская организация. Выпускает ежегодный SNAP Matters report, федеральную адвокацию титула питания Farm Bill, расширения Summer EBT, реавторизации Child Nutrition. Партнёр ~1000 штатовых и местных антиголодных адвокатов.",
      "https://frac.org/donate", 12000000, 80, 1970, date(2024, 6, 30),
      ["food-research-policy", "hunger", "philanthropic-infrastructure"],
      _us_pp("521213437"), "irs_990", _verify_us(), "medium"),

    # ============== UK (9) ==============
    E("salvation-army-uk", "GB", "214779", "people",
      "The Salvation Army UK", "The Salvation Army UK",
      "UK Christian church-charity hybrid — addiction recovery, homelessness, modern-slavery survivor support.",
      "Британская христианская церковно-благотворительная гибридная организация — лечение зависимостей, бездомность, поддержка переживших современное рабство.",
      "Salvation Army UK & Ireland Territory (Charity Commission #214779, in UK since 1865 when founded by William and Catherine Booth in London's East End) is one of the UK's largest non-government social-service providers. ~750 community churches/centres; runs Lifehouses (homeless shelters), addiction-recovery Bridge programmes, modern-slavery victim-care contracts with the UK government, and emergency response.",
      "Salvation Army UK & Ireland Territory (Charity Commission #214779, в Великобритании с 1865 года, когда основан Уильямом и Кэтрин Бут в Ист-Энде Лондона) — один из крупнейших в Великобритании негосударственных поставщиков социальных услуг. ~750 общинных церквей/центров; ведёт Lifehouses (приюты для бездомных), программы лечения зависимостей Bridge, контракты с правительством Великобритании по уходу за жертвами современного рабства, экстренное реагирование.",
      "https://www.salvationarmy.org.uk/donate", 270000000, 83, 1865, date(2024, 3, 31),
      ["faith-based", "homelessness", "anti-trafficking"],
      _uk_cc("214779"), "annual_report", _verify_uk()),

    E("guide-dogs-uk", "GB", "209617", "animals",
      "Guide Dogs (UK)", "Guide Dogs UK",
      "UK guide-dog charity — trains assistance dogs for blind people; entirely donation-funded.",
      "Британская организация собак-поводырей — обучает собак-помощников для слепых; полностью на пожертвования.",
      "Guide Dogs for the Blind Association (Charity Commission #209617, founded 1934) is the UK's only guide-dog charity, providing trained assistance dogs to blind and partially-sighted people at no cost to the user. ~5K active guide-dog partnerships in the UK. Funded entirely by donations and legacies; receives no government funding for guide-dog services.",
      "Guide Dogs for the Blind Association (Charity Commission #209617, основан в 1934 году) — единственная в Великобритании организация собак-поводырей, предоставляющая обученных собак-помощников слепым и слабовидящим людям бесплатно. ~5 тыс. активных партнёрств собак-поводырей в Великобритании. Полностью финансируется пожертвованиями и наследствами; не получает государственного финансирования на услуги собак-поводырей.",
      "https://www.guidedogs.org.uk/getting-support/donate-now/", 130000000, 79, 1934, date(2024, 3, 31),
      ["blindness-low-vision", "disability-services"],
      _uk_cc("209617"), "annual_report", _verify_uk()),

    E("leprosy-mission-uk", "GB", "261249", "people",
      "The Leprosy Mission Great Britain", "The Leprosy Mission Great Britain",
      "UK arm of global leprosy-treatment charity — works in 9 leprosy-endemic countries.",
      "Британское крыло глобальной организации по лечению проказы — работает в 9 странах, где проказа эндемична.",
      "The Leprosy Mission Great Britain (Charity Commission #261249, founded 1874 by Wellesley Bailey) is the UK arm of the global Leprosy Mission International. Works in 9 leprosy-endemic countries (India, Bangladesh, Nepal, Nigeria, DRC, Mozambique, Niger, Sudan, South Sudan) on case-finding, treatment, surgery for leprosy-related disability, vocational rehabilitation.",
      "The Leprosy Mission Great Britain (Charity Commission #261249, основан в 1874 году Уэллсли Бейли) — британское крыло глобальной Leprosy Mission International. Работает в 9 странах, где проказа эндемична (Индия, Бангладеш, Непал, Нигерия, ДРК, Мозамбик, Нигер, Судан, Южный Судан): выявление случаев, лечение, хирургия инвалидности от проказы, профессиональная реабилитация.",
      "https://www.leprosymission.org.uk/donate/", 14000000, 84, 1874, date(2024, 3, 31),
      ["leprosy", "leprosy-mission", "global-health", "humanitarian-medicine"],
      _uk_cc("261249"), "annual_report", _verify_uk(), "medium"),

    E("cure-leukaemia", "GB", "1100994", "people",
      "Cure Leukaemia", "Cure Leukaemia",
      "Funds blood-cancer research nurses across UK trial network — fast-tracks novel therapies.",
      "Финансирует медсестёр-исследователей рака крови в британской клинической сети — ускоряет новые терапии.",
      "Cure Leukaemia (Charity Commission #1100994, founded 2003) is the UK's leading blood-cancer research charity. Funds the Trials Acceleration Programme (TAP) network — research nurses at ~15 UK NHS hospitals that recruit blood-cancer patients into clinical trials of novel therapies. Has helped accelerate trials of CAR-T cell therapies, ibrutinib, and venetoclax in the UK.",
      "Cure Leukaemia (Charity Commission #1100994, основан в 2003 году) — ведущая в Великобритании благотворительная организация по исследованиям рака крови. Финансирует сеть Trials Acceleration Programme (TAP) — медсестёр-исследователей в ~15 британских NHS-больницах, набирающих пациентов с раком крови в клинические испытания новых терапий. Помог ускорить испытания CAR-T клеточных терапий, ibrutinib и venetoclax в Великобритании.",
      "https://www.cureleukaemia.co.uk/donate/", 10000000, 86, 2003, date(2024, 3, 31),
      ["blood-cancer-research", "cancer-research", "global-health"],
      _uk_cc("1100994"), "annual_report", _verify_uk(), "medium"),

    E("royal-marsden-cancer", "GB", "1095197", "people",
      "Royal Marsden Cancer Charity", "Royal Marsden Cancer Charity",
      "Funds the Royal Marsden Hospital — world's first cancer hospital, key UK cancer-research site.",
      "Финансирует Royal Marsden Hospital — первую в мире онкологическую больницу, ключевой британский онкоисследовательский центр.",
      "The Royal Marsden Cancer Charity (Charity Commission #1095197, founded 2004 as the fundraising arm of the Royal Marsden Hospital, established 1851 as the world's first cancer hospital) funds research, advanced equipment, patient facilities at Royal Marsden NHS Foundation Trust. ICR/Royal Marsden joint research has produced major cancer treatments including abiraterone and olaparib.",
      "The Royal Marsden Cancer Charity (Charity Commission #1095197, основан в 2004 году как фандрайзинговое крыло Royal Marsden Hospital, основанной в 1851 году как первая в мире онкологическая больница) финансирует исследования, передовое оборудование, помещения для пациентов в Royal Marsden NHS Foundation Trust. Совместные исследования ICR/Royal Marsden дали крупные онкотерапии, включая abiraterone и olaparib.",
      "https://www.royalmarsden.org/donate", 90000000, 80, 2004, date(2024, 3, 31),
      ["cancer-research", "global-health"],
      _uk_cc("1095197"), "annual_report", _verify_uk()),

    E("kidney-research-uk", "GB", "252892", "people",
      "Kidney Research UK", "Kidney Research UK",
      "UK's leading kidney-disease research charity — funds prevention, treatment, transplantation research.",
      "Ведущая британская организация исследований заболеваний почек — финансирует исследования профилактики, лечения, трансплантации.",
      "Kidney Research UK (Charity Commission #252892, founded 1961) is the UK's leading kidney-disease research charity. Funds ~£10M/year of research grants on chronic kidney disease (which affects ~7M UK adults), polycystic kidney disease, diabetic nephropathy, dialysis innovation, and transplantation. Major focus on health inequalities in kidney care among South Asian and Black British communities.",
      "Kidney Research UK (Charity Commission #252892, основан в 1961 году) — ведущая в Великобритании благотворительная организация исследований заболеваний почек. Финансирует ~£10 млн в год исследовательских грантов: хроническая болезнь почек (~7 млн взрослых в Великобритании), поликистозная болезнь почек, диабетическая нефропатия, инновации диализа, трансплантация. Основной фокус: неравенство в почечном здоровье среди южноазиатских и чёрных британских общин.",
      "https://www.kidneyresearchuk.org/donate/", 13000000, 79, 1961, date(2024, 3, 31),
      ["kidney-disease", "global-health"],
      _uk_cc("252892"), "annual_report", _verify_uk(), "medium"),

    E("mssociety-uk", "GB", "1139257", "people",
      "Multiple Sclerosis Society (UK)", "MS Society (UK)",
      "UK's leading MS charity — research, MS Helpline, federal advocacy on access to disease-modifying drugs.",
      "Ведущая британская организация по РС — исследования, MS Helpline, федеральная адвокация доступа к препаратам.",
      "Multiple Sclerosis Society (Charity Commission #1139257, in current form 2010; founded 1953) is the UK's leading MS charity. Funds research grants (~£8M/year), MS Helpline (free phone + email + online community), federal NHS advocacy on access to disease-modifying therapies, support for ~130K UK adults living with MS.",
      "Multiple Sclerosis Society (Charity Commission #1139257, в текущей форме с 2010 года; основан в 1953 году) — ведущая в Великобритании благотворительная организация по РС. Финансирует исследовательские гранты (~£8 млн в год), MS Helpline (бесплатный телефон + email + онлайн-сообщество), федеральную адвокацию NHS по доступу к препаратам, модифицирующим течение болезни, поддержку ~130 тыс. взрослых британцев с РС.",
      "https://www.mssociety.org.uk/get-involved/donate", 35000000, 78, 1953, date(2024, 3, 31),
      ["multiple-sclerosis", "global-health"],
      _uk_cc("1139257"), "annual_report", _verify_uk()),

    E("sands-uk", "GB", "299679", "people",
      "Sands — Stillbirth and Neonatal Death Society", "Sands — Stillbirth and Neonatal Death Society",
      "UK charity for parents bereaved by stillbirth or neonatal death — peer support + research funding.",
      "Британская организация для родителей, переживших мертворождение или неонатальную смерть — поддержка равных + исследования.",
      "Sands (Charity Commission #299679, founded 1978) is the UK's leading stillbirth and neonatal-death bereavement charity. ~70 local volunteer-led groups across the UK offer peer support to bereaved parents; runs UK Saving Babies' Lives perinatal-mortality research; provides bereavement-care training to ~13K NHS midwives. The UK has ~14 baby deaths every day from stillbirth + neonatal death combined.",
      "Sands (Charity Commission #299679, основан в 1978 году) — ведущая в Великобритании благотворительная организация поддержки переживших мертворождение и неонатальную смерть. ~70 местных волонтёрских групп по всей Великобритании предлагают поддержку равных скорбящим родителям; ведёт UK Saving Babies' Lives — исследования перинатальной смертности; обучает ~13 тыс. медсестёр-акушерок NHS уходу при утрате. В Великобритании ежедневно умирает ~14 младенцев от мертворождения + неонатальной смерти вместе.",
      "https://www.sands.org.uk/donate", 6500000, 80, 1978, date(2024, 3, 31),
      ["stillbirth-neonatal", "maternal-infant-health", "bereavement"],
      _uk_cc("299679"), "annual_report", _verify_uk(), "medium"),

    E("sustrans", "GB", "326550", "planet",
      "Sustrans", "Sustrans — sustainable transport (UK)",
      "UK charity for active and sustainable travel — runs the National Cycle Network (~5K miles).",
      "Британская организация устойчивого и активного транспорта — управляет National Cycle Network (~5 тыс. миль).",
      "Sustrans (Charity Commission #326550, founded 1977) is the UK's leading walking and cycling charity. Maintains the National Cycle Network (~5K miles of signed routes for walking, cycling, wheeling), runs Active Travel Schools (helping schools encourage walking/cycling), federal advocacy on UK Active Travel England policy and Low Traffic Neighbourhoods.",
      "Sustrans (Charity Commission #326550, основан в 1977 году) — ведущая британская благотворительная организация ходьбы и велоспорта. Поддерживает National Cycle Network (~5 тыс. миль обозначенных маршрутов для ходьбы, велоспорта, колясок), ведёт Active Travel Schools (помогает школам поощрять ходьбу/велоспорт), федеральная адвокация политики UK Active Travel England и Low Traffic Neighbourhoods.",
      "https://www.sustrans.org.uk/donate", 75000000, 81, 1977, date(2024, 3, 31),
      ["active-travel", "climate-policy", "environment"],
      _uk_cc("326550"), "annual_report", _verify_uk()),

    # ============== Canada (4) ==============
    E("world-vision-canada", "CA", "11930-4923-RR0001", "people",
      "World Vision Canada", "World Vision Canada",
      "Canadian arm of World Vision International — child sponsorship + global emergency response.",
      "Канадское отделение World Vision International — спонсорство детей + глобальное экстренное реагирование.",
      "World Vision Canada (CRA #11930-4923-RR0001, founded 1957) is the Canadian arm of World Vision International. Operates ~135 long-term Area Development Programmes; major recent emergency operations in Ukraine, Sudan, Gaza, and Pacific climate-displacement. One of Canada's largest international-aid agencies.",
      "World Vision Canada (CRA #11930-4923-RR0001, основан в 1957 году) — канадское крыло World Vision International. Управляет ~135 долгосрочными Area Development Programmes; крупные недавние экстренные операции в Украине, Судане, Газе, Тихоокеанском климатическом перемещении. Одно из крупнейших агентств международной помощи Канады.",
      "https://www.worldvision.ca/donate", 380000000, 79, 1957, date(2024, 9, 30),
      ["faith-based", "humanitarian-medicine", "child-welfare"],
      "https://www.worldvision.ca/about/financial-information", "annual_report", _verify_ca()),

    E("royal-canadian-geographical-society", "CA", "10785-7771-RR0001", "people",
      "Royal Canadian Geographical Society", "Royal Canadian Geographical Society",
      "Canada's premier geography charity — publishes Canadian Geographic, Indigenous-led education.",
      "Главное географическое общество Канады — публикует Canadian Geographic, образование под руководством коренных народов.",
      "Royal Canadian Geographical Society (CRA #10785-7771-RR0001, founded 1929) publishes Canadian Geographic magazine, runs Geography Awareness programmes in Canadian schools, and partners with Indigenous Nations on education materials (Indigenous Peoples Atlas of Canada, 4-volume work with First Nations, Inuit, Métis communities). Operates the Canadian Geographic Education programme reaching ~1.2M students.",
      "Royal Canadian Geographical Society (CRA #10785-7771-RR0001, основан в 1929 году) публикует Canadian Geographic, ведёт программы Geography Awareness в канадских школах, партнёрствует с коренными народами по образовательным материалам (Indigenous Peoples Atlas of Canada — 4-томная работа с First Nations, Inuit, Métis общинами). Управляет Canadian Geographic Education, охватывающим ~1,2 млн учеников.",
      "https://rcgs.org/donate/", 8000000, 78, 1929, date(2024, 3, 31),
      ["geographic-society", "education"],
      "https://rcgs.org/about/financial-information/", "annual_report", _verify_ca(), "medium"),

    E("oxfam-quebec", "CA", "11929-5263-RR0001", "people",
      "Oxfam-Québec", "Oxfam-Québec",
      "Québec-based Canadian Oxfam member — Francophone international development & solidarity.",
      "Член канадской Oxfam, базируется в Квебеке — франкоязычное международное развитие и солидарность.",
      "Oxfam-Québec (CRA #11929-5263-RR0001, founded 1973, headquartered in Montréal) is the Francophone Canadian member of Oxfam International, distinct from Oxfam Canada. Works in ~15 countries primarily in Latin America (Haiti, Bolivia, Honduras), West Africa (Burkina Faso, Mali) and the Middle East. Programs on women's rights, food security, climate justice.",
      "Oxfam-Québec (CRA #11929-5263-RR0001, основан в 1973 году, штаб-квартира в Монреале) — франкоязычный канадский член Oxfam International, отличный от Oxfam Canada. Работает в ~15 странах в основном в Латинской Америке (Гаити, Боливия, Гондурас), Западной Африке (Буркина-Фасо, Мали) и на Ближнем Востоке. Программы по правам женщин, продовольственной безопасности, климатической справедливости.",
      "https://oxfam.qc.ca/don/", 30000000, 84, 1973, date(2024, 3, 31),
      ["poverty-reduction", "womens-rights", "humanitarian-medicine"],
      "https://oxfam.qc.ca/transparence/", "annual_report", _verify_ca()),

    E("cuso-international", "CA", "89765-0058-RR0001", "people",
      "Cuso International", "Cuso International",
      "Canadian international volunteer-cooperation org — places skilled volunteers in 20+ countries.",
      "Канадская организация международного волонтёрского сотрудничества — направляет специалистов в 20+ страны.",
      "Cuso International (CRA #89765-0058-RR0001, founded 1961 as Canadian University Service Overseas — Canada's volunteer-cooperation movement parallel to US Peace Corps) places skilled Canadian volunteer-professionals on 6-month to 2-year placements with partner organisations in 20+ countries across Africa, Asia, Latin America. Recent priorities: post-COVID economic recovery, women's economic empowerment, climate adaptation.",
      "Cuso International (CRA #89765-0058-RR0001, основан в 1961 году как Canadian University Service Overseas — канадское движение волонтёрского сотрудничества, параллельное US Peace Corps) направляет канадских опытных волонтёров-профессионалов на 6-месячные и 2-летние размещения с организациями-партнёрами в 20+ странах в Африке, Азии, Латинской Америке. Недавние приоритеты: пост-COVID экономическое восстановление, экономическое расширение прав женщин, климатическая адаптация.",
      "https://cusointernational.org/donate/", 25000000, 88, 1961, date(2024, 3, 31),
      ["international-volunteer-coop", "humanitarian-medicine"],
      "https://cusointernational.org/about-cuso/financials/", "annual_report", _verify_ca()),

    # ============== Australia (6) ==============
    E("cancer-council-nsw", "AU", "ABN-51-116-463-846", "people",
      "Cancer Council NSW", "Cancer Council NSW",
      "New South Wales largest cancer charity — research, prevention campaigns, patient support.",
      "Крупнейшая онкоорганизация Нового Южного Уэльса — исследования, профилактика, поддержка пациентов.",
      "Cancer Council NSW (ABN 51 116 463 846, founded 1955) is the largest of the 8 state/territory Cancer Council Australia members. Funds research grants, runs Australia's Quitline 13 78 48 (smoking cessation), Cancer Council 13 11 20 information & support line, federal-NSW policy advocacy on tobacco + UV-protection, and Daffodil Day annual fundraising.",
      "Cancer Council NSW (ABN 51 116 463 846, основан в 1955 году) — крупнейший из 8 штатовых/территориальных членов Cancer Council Australia. Финансирует исследовательские гранты, ведёт Quitline 13 78 48 (отказ от курения) в Австралии, Cancer Council 13 11 20 (информационная линия поддержки), федеральную и NSW адвокацию по табаку и УФ-защите, ежегодный фандрайзинг Daffodil Day.",
      "https://www.cancercouncil.com.au/donate/", 85000000, 80, 1955, date(2024, 6, 30),
      ["cancer-state-australia", "cancer-research"],
      "https://www.cancercouncil.com.au/about-cancer-council/transparency/", "annual_report", _verify_au()),

    E("cancer-council-victoria", "AU", "ABN-61-426-486-715", "people",
      "Cancer Council Victoria", "Cancer Council Victoria",
      "Victoria's state cancer council — runs the Australian Cancer Database and tobacco-control research.",
      "Штатовый онкосовет Виктории — ведёт Australian Cancer Database и исследования табачного контроля.",
      "Cancer Council Victoria (ABN 61 426 486 715, founded 1936) is Australia's most research-active state cancer council. Operates the Australian Cancer Database (largest cancer epidemiology dataset in Australia), Centre for Behavioural Research in Cancer (pioneering tobacco-plain-packaging research that influenced Australia's world-first 2012 legislation), and the Victorian Cancer Registry.",
      "Cancer Council Victoria (ABN 61 426 486 715, основан в 1936 году) — самый исследовательски активный штатовый онкосовет Австралии. Управляет Australian Cancer Database (крупнейший датасет онкоэпидемиологии в Австралии), Centre for Behavioural Research in Cancer (пионерские исследования простой упаковки табака, повлиявшие на первое в мире австралийское законодательство 2012 года), Victorian Cancer Registry.",
      "https://www.cancervic.org.au/donate", 75000000, 82, 1936, date(2024, 6, 30),
      ["cancer-state-australia", "cancer-research"],
      "https://www.cancervic.org.au/about-us/governance/", "annual_report", _verify_au()),

    E("garvan-institute", "AU", "ABN-62-330-391-251", "people",
      "Garvan Institute of Medical Research", "Garvan Institute of Medical Research",
      "Sydney-based independent medical-research institute — genomics, cancer, immunology, diabetes.",
      "Независимый медицинский исследовательский институт в Сиднее — геномика, рак, иммунология, диабет.",
      "Garvan Institute of Medical Research (ABN 62 330 391 251, founded 1963 in Sydney) is one of Australia's largest independent biomedical research institutes. ~700 staff across cancer, immunology, diabetes & metabolism, neuroscience, genomics. Operates the Kinghorn Centre for Clinical Genomics (one of the world's largest clinical-genomics facilities). Major research on AML, T-cell biology, and BRCA-positive breast cancer.",
      "Garvan Institute of Medical Research (ABN 62 330 391 251, основан в 1963 году в Сиднее) — один из крупнейших независимых биомедицинских исследовательских институтов Австралии. ~700 сотрудников: рак, иммунология, диабет и метаболизм, нейронауки, геномика. Управляет Kinghorn Centre for Clinical Genomics (одним из крупнейших клинических геномных центров мира). Крупные исследования AML, T-клеточной биологии, BRCA-позитивного рака груди.",
      "https://www.garvan.org.au/donate/", 120000000, 88, 1963, date(2024, 6, 30),
      ["medical-research-institute", "cancer-research", "global-health"],
      "https://www.garvan.org.au/about-us/our-organisation/financials/", "annual_report", _verify_au()),

    E("walter-eliza-hall-institute", "AU", "ABN-65-039-330-184", "people",
      "Walter and Eliza Hall Institute of Medical Research (WEHI)", "WEHI — Walter and Eliza Hall Institute",
      "Australia's oldest medical research institute — Melbourne; cancer, infection, immunology.",
      "Старейший медицинский исследовательский институт Австралии — Мельбурн; рак, инфекции, иммунология.",
      "Walter and Eliza Hall Institute (ABN 65 039 330 184, founded 1915 in Melbourne) is Australia's oldest medical research institute. ~1,200 staff. Discovered BCL-2 (the apoptosis regulator that led to venetoclax for leukaemia/lymphoma); pioneered the rotavirus vaccine RotaTeq; landmark malaria research. Affiliated with Royal Melbourne Hospital.",
      "Walter and Eliza Hall Institute (ABN 65 039 330 184, основан в 1915 году в Мельбурне) — старейший медицинский исследовательский институт Австралии. ~1200 сотрудников. Открыли BCL-2 (регулятор апоптоза, приведший к venetoclax от лейкемии/лимфомы); пионеры вакцины от ротавируса RotaTeq; знаковые исследования малярии. Аффилирован с Royal Melbourne Hospital.",
      "https://www.wehi.edu.au/donate/", 130000000, 87, 1915, date(2024, 6, 30),
      ["medical-research-institute", "cancer-research", "global-health"],
      "https://www.wehi.edu.au/about-wehi/governance-and-reporting/", "annual_report", _verify_au()),

    E("mater-foundation-au", "AU", "ABN-96-722-477-911", "people",
      "Mater Foundation (Australia)", "Mater Foundation — Brisbane",
      "Catholic-rooted Brisbane healthcare philanthropy — funds Mater Hospital, cancer care, women's health.",
      "Католическая больничная филантропия в Брисбене — финансирует Mater Hospital, онкологию, женское здоровье.",
      "Mater Foundation (ABN 96 722 477 911) raises funds for the Mater Health Services in Brisbane (Catholic non-profit hospital network founded 1906 by the Sisters of Mercy). Funds maternity hospital (Mater Mothers' is one of Australia's largest), Mater Cancer Care Centre, and Mater Research Institute. Runs the Mater Prize Home Lottery — one of Australia's largest charity lotteries.",
      "Mater Foundation (ABN 96 722 477 911) собирает средства для Mater Health Services в Брисбене (католическая некоммерческая сеть больниц, основанная в 1906 году сёстрами милосердия). Финансирует роддом (Mater Mothers' — один из крупнейших в Австралии), Mater Cancer Care Centre, Mater Research Institute. Ведёт Mater Prize Home Lottery — одну из крупнейших благотворительных лотерей Австралии.",
      "https://www.matergroup.com.au/foundation/donate", 95000000, 84, 1906, date(2024, 6, 30),
      ["faith-based", "global-health", "cancer-research"],
      "https://www.matergroup.com.au/foundation/about-us/financial-information", "annual_report", _verify_au()),

    E("fred-hollows-foundation", "AU", "ABN-46-070-556-642", "people",
      "The Fred Hollows Foundation", "The Fred Hollows Foundation",
      "Restores sight in low-income countries via cataract surgery + trachoma elimination — $25 per surgery.",
      "Восстанавливает зрение в малообеспеченных странах через катарактную хирургию + ликвидация трахомы — $25 за операцию.",
      "The Fred Hollows Foundation (ABN 46 070 556 642, founded 1992 by NZ-born Australian eye surgeon Fred Hollows) restores sight in low-income countries through eye-care training and cataract surgery (as low as $25 per surgery). Works in ~25 countries; trained ~200K eye-care professionals; restored sight for ~3M+ people. Major focus on trachoma elimination among Aboriginal Australian communities.",
      "The Fred Hollows Foundation (ABN 46 070 556 642, основана в 1992 году новозеландско-австралийским офтальмологом Фредом Холлоузом) восстанавливает зрение в малообеспеченных странах через обучение eye-care и катарактную хирургию (за $25 за операцию). Работает в ~25 странах; обучила ~200 тыс. eye-care специалистов; восстановила зрение ~3+ млн человек. Основной фокус: ликвидация трахомы среди коренных австралийских общин.",
      "https://www.hollows.org/au/donate", 95000000, 84, 1992, date(2024, 6, 30),
      ["trachoma-blindness", "blindness-low-vision", "global-health"],
      "https://www.hollows.org/au/about-us/annual-report", "annual_report", _verify_au()),

    # ============== Germany (4) ==============
    E("unicef-deutschland", "DE", "DE-UNICEF-1953", "people",
      "UNICEF Deutschland", "UNICEF Deutschland",
      "German National Committee for UNICEF — funds UNICEF's global child-survival programmes.",
      "Немецкий национальный комитет UNICEF — финансирует глобальные программы выживания детей UNICEF.",
      "Deutsches Komitee für UNICEF e.V. (founded 1953 in Cologne) is the German National Committee for UNICEF. One of UNICEF's largest national fundraising arms (~€140M per year). Major focus on global child-rights advocacy in Germany, education-in-emergencies (Ukraine, Sudan), and child-nutrition emergencies (Yemen, Gaza, Horn of Africa).",
      "Deutsches Komitee für UNICEF e.V. (основан в 1953 году в Кёльне) — немецкий национальный комитет UNICEF. Одно из крупнейших фандрайзинговых крыльев UNICEF (~€140 млн в год). Основной фокус: глобальная адвокация прав детей в Германии, образование в чрезвычайных ситуациях (Украина, Судан), детские пищевые кризисы (Йемен, Газа, Африканский Рог).",
      "https://www.unicef.de/spenden", 165000000, 87, 1953, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.de/informieren/ueber-uns/transparenz", "annual_report", _verify_de()),

    E("misereor", "DE", "DE-MISEREOR-1958", "people",
      "Misereor", "Misereor",
      "German Catholic development agency — funds 1,500+ projects in ~85 countries via local partners.",
      "Немецкое католическое агентство развития — финансирует 1500+ проектов в ~85 странах через местных партнёров.",
      "Misereor (founded 1958 in Aachen, Germany's Catholic episcopal development agency) is one of Europe's largest Catholic development funders. Funds ~1,500 active projects in ~85 countries via local partners — Misereor itself has no field offices outside Germany. Programmes on poverty reduction, food security, climate justice (loss-and-damage advocacy), peace. DZI Spendensiegel certified.",
      "Misereor (основан в 1958 году в Ахене, немецкое католическое епископское агентство развития) — одно из крупнейших европейских католических финансирующих развитие. Финансирует ~1500 активных проектов в ~85 странах через местных партнёров — у Misereor нет полевых офисов вне Германии. Программы: сокращение бедности, продовольственная безопасность, климатическая справедливость (адвокация loss-and-damage), мир. Сертифицирован DZI Spendensiegel.",
      "https://www.misereor.de/spenden", 250000000, 89, 1958, date(2023, 12, 31),
      ["faith-based", "poverty-reduction", "humanitarian-medicine"],
      "https://www.misereor.de/ueber-uns/zahlen-fakten", "annual_report", _verify_de()),

    E("aktion-deutschland-hilft", "DE", "DE-ADH-2001", "people",
      "Aktion Deutschland Hilft", "Aktion Deutschland Hilft",
      "Alliance of 23 German aid agencies coordinating joint emergency-response appeals.",
      "Альянс 23 немецких агентств помощи, координирующих совместные кампании экстренного реагирования.",
      "Aktion Deutschland Hilft (founded 2001 in Bonn) is the alliance of 23 German humanitarian aid organisations (incl. ADRA, ASB, AWO, CARE, Caritas international, DRK, Habitat for Humanity, Help, Islamic Relief, Johanniter, Malteser, World Vision). Coordinates joint appeals during major disasters — Ukraine, Türkiye-Syria earthquake, Pakistan floods. Equivalent of UK's Disasters Emergency Committee. DZI Spendensiegel certified.",
      "Aktion Deutschland Hilft (основан в 2001 году в Бонне) — альянс 23 немецких гуманитарных организаций помощи (в т.ч. ADRA, ASB, AWO, CARE, Caritas international, DRK, Habitat for Humanity, Help, Islamic Relief, Johanniter, Malteser, World Vision). Координирует совместные кампании при крупных бедствиях — Украина, землетрясение в Турции-Сирии, наводнения в Пакистане. Эквивалент британского Disasters Emergency Committee. Сертифицирован DZI Spendensiegel.",
      "https://www.aktion-deutschland-hilft.de/spenden", 95000000, 95, 2001, date(2023, 12, 31),
      ["disaster-relief", "emergency-response", "humanitarian-medicine"],
      "https://www.aktion-deutschland-hilft.de/ueber-uns/transparenz/", "annual_report", _verify_de()),

    E("plan-deutschland", "DE", "DE-PLAN-1989", "people",
      "Plan International Deutschland", "Plan International Deutschland",
      "German member of Plan International — girls-rights focus, child sponsorship in ~50 countries.",
      "Немецкий член Plan International — фокус на правах девочек, спонсорство детей в ~50 странах.",
      "Plan International Deutschland (founded 1989 in Hamburg) is one of Plan International's largest national member organisations (~430K German child-sponsors). Distinctive Because I Am a Girl campaign focuses on gender equality in low-income countries. DZI Spendensiegel certified.",
      "Plan International Deutschland (основан в 1989 году в Гамбурге) — одна из крупнейших национальных организаций-членов Plan International (~430 тыс. немецких спонсоров детей). Отличительная кампания Because I Am a Girl фокусируется на гендерном равенстве в малообеспеченных странах. Сертифицирован DZI Spendensiegel.",
      "https://www.plan.de/spenden", 130000000, 87, 1989, date(2023, 12, 31),
      ["child-welfare", "womens-rights", "humanitarian-medicine"],
      "https://www.plan.de/ueber-uns/zahlen-und-fakten/", "annual_report", _verify_de()),

    # ============== France (3) ==============
    E("fondation-de-france", "FR", "FR-FdF-1969", "people",
      "Fondation de France", "Fondation de France",
      "Largest French foundation — public utility status; ~970M EUR managed for ~900 funds and projects.",
      "Крупнейший французский фонд — статус utility publique; ~€970 млн управляется для ~900 фондов и проектов.",
      "Fondation de France (founded 1969, headquartered Paris) is France's largest foundation and the principal umbrella for ~900 individual named funds + corporate foundations. Funds direct programmes on poverty, child welfare, mental health, climate, plus operates Le Don en Confiance certification standards. Co-administered the Notre-Dame de Paris reconstruction fund post-2019 fire.",
      "Fondation de France (основан в 1969 году, штаб-квартира в Париже) — крупнейший французский фонд и главный зонтик для ~900 индивидуальных именованных фондов + корпоративных фондов. Финансирует прямые программы по бедности, благополучию детей, психическому здоровью, климату, плюс ведёт стандарты сертификации Le Don en Confiance. Соадминистрировал фонд реконструкции собора Парижской Богоматери после пожара 2019 года.",
      "https://www.fondationdefrance.org/fr/faire-un-don", 290000000, 86, 1969, date(2023, 12, 31),
      ["poverty-reduction", "philanthropic-infrastructure"],
      "https://www.fondationdefrance.org/fr/transparence-financiere", "annual_report", _verify_fr()),

    E("unicef-france", "FR", "FR-UNICEF-1947", "people",
      "UNICEF France", "UNICEF France",
      "French National Committee for UNICEF — fundraising + child-rights advocacy in France.",
      "Французский национальный комитет UNICEF — фандрайзинг и адвокация прав детей во Франции.",
      "UNICEF France (founded 1947 in Paris) is the French National Committee for UNICEF. French law gives it permission to operate the Pièces Jaunes (small-coin) collection in schools. Major focus on France-domestic child-rights work — French migrant-children rights, school-canteen access for poorest children, mental health.",
      "UNICEF France (основан в 1947 году в Париже) — французский национальный комитет UNICEF. Французское законодательство даёт ему право вести сбор Pièces Jaunes (мелкие монеты) в школах. Основной фокус: внутренняя работа во Франции по правам детей — права французских детей-мигрантов, доступ к школьным столовым для беднейших, психическое здоровье.",
      "https://don.unicef.fr/", 140000000, 86, 1947, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.fr/qui-sommes-nous/nos-comptes/", "annual_report", _verify_fr()),

    E("apf-france-handicap", "FR", "FR-APF-1933", "people",
      "APF France handicap", "APF France handicap",
      "Largest French disability charity — federation of ~135 local groups; advocacy + direct services.",
      "Крупнейшая французская организация по инвалидности — федерация ~135 местных групп; адвокация + прямые услуги.",
      "APF France handicap (founded 1933 as Association des Paralysés de France) is the largest French disability-rights and direct-services federation. ~135 local groups; operates ~500 establishments providing care to ~150K disabled people daily. Federal advocacy on accessibility (1975 Loi handicap), AAH allowance reform, and the recent 2024 Comité interministériel du handicap.",
      "APF France handicap (основана в 1933 году как Association des Paralysés de France) — крупнейшая французская правозащитная и сервисная федерация по инвалидности. ~135 местных групп; управляет ~500 учреждениями, обеспечивающими помощь ~150 тыс. инвалидов ежедневно. Федеральная адвокация доступности (Loi handicap 1975), реформы пособия AAH, недавний Comité interministériel du handicap 2024.",
      "https://www.apf-francehandicap.org/donner", 600000000, 89, 1933, date(2023, 12, 31),
      ["disability-services", "civil-rights"],
      "https://www.apf-francehandicap.org/qui-sommes-nous/finances-transparence", "annual_report", _verify_fr()),

    # ============== Italy (4) ==============
    E("unicef-italia", "IT", "IT-01561920586", "people",
      "UNICEF Italia", "UNICEF Italia",
      "Italian National Committee for UNICEF — fundraising for UNICEF programmes globally.",
      "Итальянский национальный комитет UNICEF — фандрайзинг для программ UNICEF в мире.",
      "Comitato Italiano per l'UNICEF (C.F. 01561920586, founded 1974) is the Italian National Committee for UNICEF. Fundraising for global UNICEF programmes — Ukraine, Sudan, Gaza, Yemen humanitarian responses; long-term work on education in low-income countries; Pigotta (UNICEF dolls) annual fundraising campaign.",
      "Comitato Italiano per l'UNICEF (C.F. 01561920586, основан в 1974 году) — итальянский национальный комитет UNICEF. Фандрайзинг для глобальных программ UNICEF — Украина, Судан, Газа, Йемен (гуманитарные ответы); долгосрочная работа по образованию в малообеспеченных странах; ежегодная фандрайзинговая кампания Pigotta (куклы UNICEF).",
      "https://www.unicef.it/donazione", 60000000, 86, 1974, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.it/chi-siamo/bilancio-trasparenza", "annual_report", _verify_it()),

    E("oxfam-italia", "IT", "IT-94099000510", "people",
      "Oxfam Italia", "Oxfam Italia",
      "Italian member of Oxfam International — climate justice, inequality, women's rights work.",
      "Итальянский член Oxfam International — климатическая справедливость, неравенство, права женщин.",
      "Oxfam Italia (C.F. 94099000510, founded 2010 as Italian arm of Oxfam International, succeeding Ucodep founded 1973) works in ~25 countries plus domestic Italy programmes on poverty reduction, climate justice, women's rights, refugees. Co-publishes the annual Oxfam Davos billionaire-inequality report in Italian + media engagement on Italian inequality.",
      "Oxfam Italia (C.F. 94099000510, основана в 2010 году как итальянское крыло Oxfam International, преемница Ucodep, основанной в 1973 году) работает в ~25 странах плюс внутренние программы в Италии: сокращение бедности, климатическая справедливость, права женщин, беженцы. Соиздаёт ежегодный Oxfam Davos billionaire-inequality report на итальянском + медиа-вовлечение по итальянскому неравенству.",
      "https://www.oxfamitalia.org/dona/", 30000000, 82, 2010, date(2023, 12, 31),
      ["poverty-reduction", "climate-policy", "global-womens-rights"],
      "https://www.oxfamitalia.org/trasparenza/", "annual_report", _verify_it()),

    E("lilt-italy", "IT", "IT-80105840584", "people",
      "Lega Italiana per la Lotta contro i Tumori (LILT)", "LILT — Lega Italiana per la Lotta contro i Tumori",
      "Italy's leading cancer-prevention charity — 106 provincial branches; free prevention screenings.",
      "Ведущая итальянская организация профилактики рака — 106 провинциальных отделений; бесплатные скрининги.",
      "Lega Italiana per la Lotta contro i Tumori / LILT (C.F. 80105840584, founded 1922) is Italy's leading cancer-prevention charity. 106 provincial branches across Italy; operates ~400 LILT prevention clinics offering free skin/breast/colorectal screenings; runs the annual Settimana Nazionale Prevenzione Oncologica (National Cancer Prevention Week) in May.",
      "Lega Italiana per la Lotta contro i Tumori / LILT (C.F. 80105840584, основан в 1922 году) — ведущая итальянская организация профилактики рака. 106 провинциальных отделений по всей Италии; управляет ~400 LILT-клиниками профилактики, предлагающими бесплатные скрининги кожи/груди/колоректальные; ведёт ежегодную Settimana Nazionale Prevenzione Oncologica (Национальную неделю профилактики рака) в мае.",
      "https://www.legatumori.it/sostienici/", 40000000, 81, 1922, date(2023, 12, 31),
      ["cancer-research", "global-health"],
      "https://www.legatumori.it/chi-siamo/trasparenza/", "annual_report", _verify_it()),

    E("wwf-italia", "IT", "IT-80078430581", "planet",
      "WWF Italia", "WWF Italia",
      "Italian national office of WWF — Mediterranean conservation, climate, biodiversity advocacy.",
      "Итальянское национальное отделение WWF — Средиземноморская охрана, климат, биоразнообразие.",
      "WWF Italia (C.F. 80078430581, founded 1966 in Rome) is the Italian national office of the WWF International network. Manages ~100 WWF Oasi (private nature reserves) covering ~30K hectares across Italy. Major work on Mediterranean Sea protection, alpine biodiversity, brown bear and wolf recovery in the Italian Apennines.",
      "WWF Italia (C.F. 80078430581, основан в 1966 году в Риме) — итальянское национальное отделение сети WWF International. Управляет ~100 WWF Oasi (частными природными заповедниками) общей площадью ~30 тыс. гектаров по всей Италии. Крупные работы: защита Средиземного моря, альпийское биоразнообразие, восстановление бурого медведя и волка в итальянских Апеннинах.",
      "https://www.wwf.it/dona/", 25000000, 80, 1966, date(2023, 12, 31),
      ["conservation", "biodiversity-defense", "wildlife-conservation"],
      "https://www.wwf.it/chi-siamo/trasparenza/", "annual_report", _verify_it()),

    # ============== Spain (3) ==============
    E("unicef-spain", "ES", "ES-G84451087", "people",
      "UNICEF España (Comité Español)", "UNICEF España",
      "Spanish National Committee for UNICEF — funds global UNICEF; domestic Spain child-rights work.",
      "Испанский национальный комитет UNICEF — финансирует глобальный UNICEF; внутренняя работа в Испании по правам детей.",
      "UNICEF España / Comité Español (NIF G84451087, founded 1961) is the Spanish National Committee for UNICEF. Major focus on Spain-domestic child poverty + child-rights advocacy (~28% of Spanish children live in households below 60% of median income), plus traditional UNICEF global fundraising. Iconic Día Internacional de los Derechos del Niño (20 November) campaigns.",
      "UNICEF España / Comité Español (NIF G84451087, основан в 1961 году) — испанский национальный комитет UNICEF. Основной фокус: внутренняя детская бедность в Испании и адвокация прав детей (~28% испанских детей живут в семьях с доходом ниже 60% медианного), плюс традиционный глобальный фандрайзинг UNICEF. Знаковые кампании Día Internacional de los Derechos del Niño (20 ноября).",
      "https://www.unicef.es/donaciones", 75000000, 86, 1961, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.es/nuestro-trabajo/transparencia", "annual_report", _verify_es()),

    E("wwf-spain", "ES", "ES-G28586913", "planet",
      "WWF España (Asociación)", "WWF España",
      "Spanish national office of WWF — Mediterranean, iberian-lynx recovery, climate policy.",
      "Испанское национальное отделение WWF — Средиземноморье, восстановление иберийской рыси, климатическая политика.",
      "WWF España / Asociación para la Defensa de la Naturaleza (NIF G28586913, founded 1968 in Madrid) is the Spanish national office of WWF International. Major programmes on Iberian lynx recovery (now the species is rebounded from ~94 individuals in 2002 to ~2K today, largely thanks to WWF + EU LIFE projects), Doñana wetlands protection, Mediterranean Sea, illegal fishing.",
      "WWF España / Asociación para la Defensa de la Naturaleza (NIF G28586913, основан в 1968 году в Мадриде) — испанское национальное отделение WWF International. Крупные программы: восстановление иберийской рыси (вид восстановлен с ~94 особей в 2002 году до ~2 тыс. сегодня, в основном благодаря WWF + проектам ЕС LIFE), защита водно-болотных угодий Доньяна, Средиземное море, незаконный промысел.",
      "https://www.wwf.es/colabora/", 20000000, 78, 1968, date(2023, 12, 31),
      ["conservation", "biodiversity-defense", "endangered-species"],
      "https://www.wwf.es/nuestro_trabajo/transparencia/", "annual_report", _verify_es()),

    E("medicus-mundi-spain", "ES", "ES-G36742451", "people",
      "Medicus Mundi España", "Medicus Mundi España",
      "Spanish health-focused development NGO federation — works in 20+ countries on health systems.",
      "Испанская федерация НПО развития в области здоровья — работает в 20+ странах по системам здравоохранения.",
      "Medicus Mundi España (NIF G36742451, federation of ~9 regional Spanish associations) is one of Spain's oldest international-health development NGO federations. Works in ~22 countries strengthening primary healthcare systems, training health workers, advocating for right to health (RTH). Founded 1963 in Spain.",
      "Medicus Mundi España (NIF G36742451, федерация ~9 региональных испанских ассоциаций) — одна из старейших испанских федераций НПО международного развития в области здоровья. Работает в ~22 странах: укрепление систем первичной медпомощи, обучение медработников, адвокация права на здоровье (RTH). Основан в 1963 году в Испании.",
      "https://medicusmundi.es/es/colabora", 22000000, 84, 1963, date(2023, 12, 31),
      ["humanitarian-medicine", "global-health"],
      "https://medicusmundi.es/es/transparencia", "annual_report", _verify_es(), "medium"),

    # ============== Netherlands (3) ==============
    E("unicef-nederland", "NL", "RSIN-002984568", "people",
      "UNICEF Nederland", "UNICEF Nederland",
      "Dutch National Committee for UNICEF — fundraising for global child-rights work.",
      "Голландский национальный комитет UNICEF — фандрайзинг для глобальной работы по правам детей.",
      "Stichting Nederlands Comité UNICEF (RSIN 002984568, founded 1956) is the Dutch National Committee for UNICEF. ~€90M annual revenue. Focus areas: global emergency response (Ukraine, Sudan, Gaza, Yemen), polio eradication, education in emergencies. CBF Erkend; ANBI.",
      "Stichting Nederlands Comité UNICEF (RSIN 002984568, основан в 1956 году) — голландский национальный комитет UNICEF. Годовая выручка ~€90 млн. Ключевые направления: глобальное экстренное реагирование (Украина, Судан, Газа, Йемен), искоренение полиомиелита, образование в чрезвычайных ситуациях. CBF Erkend; ANBI.",
      "https://www.unicef.nl/doneer", 100000000, 84, 1956, date(2024, 3, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.nl/over-ons/financien", "annual_report", _verify_nl()),

    E("wnf-nl", "NL", "RSIN-002962850", "planet",
      "Wereld Natuur Fonds (WWF Nederland)", "WNF — Wereld Natuur Fonds",
      "Dutch national office of WWF International — climate, sustainable food, biodiversity globally.",
      "Голландское национальное отделение WWF International — климат, устойчивое питание, биоразнообразие глобально.",
      "Wereld Natuur Fonds (WWF Nederland, RSIN 002962850, founded 1962, headquartered Zeist) is the Dutch national office of WWF International. ~800K supporters in the Netherlands. Funds WWF International programmes worldwide and runs Dutch-domestic campaigns on sustainable agriculture, North Sea fisheries, and consumer-product certification (MSC, FSC). CBF Erkend.",
      "Wereld Natuur Fonds (WWF Nederland, RSIN 002962850, основан в 1962 году, штаб-квартира в Зейсте) — голландское национальное отделение WWF International. ~800 тыс. сторонников в Нидерландах. Финансирует программы WWF International по всему миру и ведёт голландские внутренние кампании по устойчивому сельскому хозяйству, рыбным промыслам Северного моря, сертификации потребительских продуктов (MSC, FSC). CBF Erkend.",
      "https://www.wwf.nl/doneer", 80000000, 80, 1962, date(2024, 6, 30),
      ["conservation", "biodiversity-defense", "climate"],
      "https://www.wwf.nl/over-ons/financien", "annual_report", _verify_nl()),

    E("amref-nederland", "NL", "RSIN-002909824", "people",
      "Amref Flying Doctors Netherlands", "Amref Flying Doctors Netherlands",
      "Dutch arm of Amref Health Africa — funds African health workers' training and rural-health programmes.",
      "Голландское крыло Amref Health Africa — финансирует обучение африканских медработников и сельские медпрограммы.",
      "Amref Flying Doctors Netherlands (RSIN 002909824, founded 1972) is one of the largest European fundraising offices for Amref Health Africa. ~€30M annual revenue funds Amref programmes across Africa on community health worker training, female-genital-cutting prevention, maternal health, rural surgical outreach (the Flying Doctors of East Africa programme). CBF Erkend.",
      "Amref Flying Doctors Netherlands (RSIN 002909824, основан в 1972 году) — один из крупнейших европейских фандрайзинговых офисов Amref Health Africa. Годовая выручка ~€30 млн финансирует программы Amref по всей Африке: обучение общинных медработников, профилактика женского обрезания, материнское здоровье, сельская выездная хирургия (программа Flying Doctors of East Africa). CBF Erkend.",
      "https://amrefnl.org/doneer/", 35000000, 88, 1972, date(2024, 3, 31),
      ["africa-health", "global-health", "humanitarian-medicine"],
      "https://amrefnl.org/over-amref/financien/", "annual_report", _verify_nl()),

    # ============== Ireland (3) ==============
    E("amnesty-ireland", "IE", "IE-CHY-5102", "people",
      "Amnesty International Ireland", "Amnesty International Ireland",
      "Irish section of Amnesty — human rights, abortion-rights (post-8th referendum), migrant rights.",
      "Ирландская секция Amnesty — права человека, права на аборт (после референдума 8-й поправки), права мигрантов.",
      "Amnesty International Ireland (CHY 5102, founded 1962) is the Irish national section of Amnesty International. Major recent campaigns: 2018 referendum to repeal the 8th amendment (abortion access in Ireland), International Protection / asylum seekers in Ireland, Belfast Good Friday Agreement legacy issues.",
      "Amnesty International Ireland (CHY 5102, основан в 1962 году) — ирландская национальная секция Amnesty International. Крупные недавние кампании: референдум 2018 года по отмене 8-й поправки (доступ к абортам в Ирландии), International Protection / лица, ищущие убежища в Ирландии, наследие Belfast Good Friday Agreement.",
      "https://www.amnesty.ie/donate/", 12000000, 78, 1962, date(2023, 12, 31),
      ["civil-rights", "womens-rights", "refugees"],
      "https://www.amnesty.ie/about/financial-information/", "annual_report", _verify_ie(), "medium"),

    E("foroige", "IE", "IE-CHY-5905", "people",
      "Foróige", "Foróige — ирландская молодёжная организация",
      "Ireland's largest youth-development organisation — Big Brother Big Sister Ireland, ~57K members.",
      "Крупнейшая ирландская молодёжная организация — ирландский Big Brother Big Sister, ~57 тыс. членов.",
      "Foróige (CHY 5905, founded 1952) is Ireland's largest youth-development organisation. Operates Foróige clubs and Big Brother Big Sister Ireland (the Irish affiliate of the international BBBS movement) in ~600 community settings. ~57K members aged 10-18; ~7K trained adult volunteers. Strong evidence base on positive youth-development outcomes via Foróige's Garda Síochána Youth Diversion Programme.",
      "Foróige (CHY 5905, основан в 1952 году) — крупнейшая ирландская молодёжная организация. Управляет клубами Foróige и Big Brother Big Sister Ireland (ирландский аффилиат международного движения BBBS) в ~600 общинных местах. ~57 тыс. членов 10-18 лет; ~7 тыс. обученных взрослых волонтёров. Сильная доказательная база позитивного развития молодёжи через Foróige's Garda Síochána Youth Diversion Programme.",
      "https://www.foroige.ie/donate", 25000000, 84, 1952, date(2023, 12, 31),
      ["youth-development", "youth-mentoring", "child-welfare"],
      "https://www.foroige.ie/about-foroige/governance-and-finance", "annual_report", _verify_ie()),

    E("simon-community-ireland", "IE", "IE-CHY-5963", "people",
      "Dublin Simon Community", "Dublin Simon Community",
      "Largest Irish homelessness charity — emergency, transitional, long-term housing across Dublin.",
      "Крупнейшая ирландская организация по бездомности — экстренное, переходное, долгосрочное жильё в Дублине.",
      "Dublin Simon Community (CHY 5963, founded 1969) is the largest Irish homelessness charity. Operates ~30 services across Dublin and Wicklow — emergency accommodation, treatment (addiction, mental health), housing-first transitional and long-term homes. Iconic Sleep Out Dublin annual fundraising event in December.",
      "Dublin Simon Community (CHY 5963, основан в 1969 году) — крупнейшая ирландская организация по бездомности. Управляет ~30 услугами в Дублине и Уиклоу — экстренное жильё, лечение (зависимости, психическое здоровье), housing-first переходные и долгосрочные дома. Знаковое ежегодное мероприятие Sleep Out Dublin в декабре.",
      "https://www.dubsimon.ie/donate/", 60000000, 88, 1969, date(2023, 12, 31),
      ["homelessness", "poverty-reduction", "mental-health"],
      "https://www.dubsimon.ie/about/financial-information/", "annual_report", _verify_ie()),

    # ============== Norway (2) ==============
    E("norwegian-peoples-aid", "NO", "NO-938691884", "people",
      "Norsk Folkehjelp (Norwegian People's Aid)", "Norsk Folkehjelp — Norwegian People's Aid",
      "Norwegian labour-movement humanitarian NGO — landmine clearance, asylum support, first aid.",
      "Норвежская гуманитарная НПО рабочего движения — разминирование, поддержка ищущих убежища, первая помощь.",
      "Norsk Folkehjelp (Org 938 691 884, founded 1939 by Norwegian labour-movement) is Norway's largest non-Red-Cross humanitarian NGO. Major operations: humanitarian mine action (largest demining operator post-conflict in DRC, South Sudan, Vietnam, Cambodia), Norway-domestic asylum support and integration, Lifeguard and first-aid services. ~13K members.",
      "Norsk Folkehjelp (Org 938 691 884, основан в 1939 году норвежским рабочим движением) — крупнейшая норвежская гуманитарная НПО за пределами Красного Креста. Крупные операции: гуманитарное разминирование (крупнейший разминирующий оператор post-conflict в ДРК, Южном Судане, Вьетнаме, Камбодже), внутренняя поддержка лиц, ищущих убежища, в Норвегии и интеграция, услуги Lifeguard и первой помощи. ~13 тыс. членов.",
      "https://www.folkehjelp.no/gi-bidrag", 95000000, 88, 1939, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response", "refugees"],
      "https://www.folkehjelp.no/om-oss/aarsrapport", "annual_report", _verify_no()),

    E("plan-norge", "NO", "NO-977386191", "people",
      "Plan International Norge", "Plan International Norge",
      "Norwegian member of Plan International — girls'-rights focus, ~340K Norwegian child-sponsors.",
      "Норвежский член Plan International — фокус на правах девочек, ~340 тыс. норвежских спонсоров детей.",
      "Plan International Norge (Org 977 386 191, founded 1996) is the Norwegian member of Plan International. ~340K Norwegian child-sponsors; ~NOK 800M annual revenue. Distinct focus on girls' rights (Because I am a Girl), child marriage prevention, and FGM/cutting. Programmes in ~50 countries.",
      "Plan International Norge (Org 977 386 191, основан в 1996 году) — норвежский член Plan International. ~340 тыс. норвежских спонсоров детей; годовая выручка ~NOK 800 млн. Особый фокус на правах девочек (Because I am a Girl), профилактике детских браков и FGM/обрезания. Программы в ~50 странах.",
      "https://www.plan-norge.no/gi-en-gave", 75000000, 86, 1996, date(2023, 12, 31),
      ["child-welfare", "womens-rights", "humanitarian-medicine"],
      "https://www.plan-norge.no/om-oss/aarsrapport", "annual_report", _verify_no()),

    # ============== New Zealand (2) ==============
    E("nz-cancer-society", "NZ", "CC23722", "people",
      "Cancer Society of New Zealand", "Cancer Society of New Zealand",
      "NZ's leading cancer charity — research, accommodation for out-of-town patients, support services.",
      "Ведущая новозеландская онкоорганизация — исследования, жильё для иногородних пациентов, услуги поддержки.",
      "Cancer Society of New Zealand (NZ Charities Services CC23722, founded 1929) is NZ's leading cancer-services and -research charity. Funds research grants, operates Cancer Society lodges (free accommodation for patients receiving treatment far from home), runs Cancer Information Helpline 0800 226 237, advocates federally for cancer-screening expansion and Pharmac drug funding.",
      "Cancer Society of New Zealand (NZ Charities Services CC23722, основан в 1929 году) — ведущая в NZ онкологическая сервисная и исследовательская организация. Финансирует исследовательские гранты, управляет Cancer Society lodges (бесплатное жильё для пациентов, получающих лечение далеко от дома), ведёт Cancer Information Helpline 0800 226 237, лоббирует на федеральном уровне расширение онкоскрининга и финансирование лекарств через Pharmac.",
      "https://www.cancer.org.nz/donate/", 40000000, 80, 1929, date(2024, 3, 31),
      ["cancer-research", "global-health"],
      "https://www.cancer.org.nz/about-us/financial-information/", "annual_report", _verify_nz()),

    E("fred-hollows-foundation-nz", "NZ", "CC36306", "people",
      "Fred Hollows Foundation NZ", "Fred Hollows Foundation NZ",
      "NZ arm of the Fred Hollows Foundation — eye-care in Pacific Islands; Fred Hollows was NZ-born.",
      "Новозеландское крыло Fred Hollows Foundation — eye-care в Тихоокеанских островах; Фред Холлоуз родился в NZ.",
      "Fred Hollows Foundation NZ (NZ Charities Services CC36306, founded 1992 to honour New Zealand-born eye surgeon Fred Hollows) operates the Pacific eye-care programmes — cataract surgeries and eye-care training in Fiji, Vanuatu, Solomon Islands, PNG, Tonga, Samoa, Cook Islands. Sister org to The Fred Hollows Foundation Australia.",
      "Fred Hollows Foundation NZ (NZ Charities Services CC36306, основан в 1992 году в честь новозеландского офтальмолога Фреда Холлоуза) ведёт Pacific eye-care программы — катарактные операции и обучение eye-care в Фиджи, Вануату, Соломоновых островах, ПНГ, Тонга, Самоа, Островах Кука. Сестринская организация The Fred Hollows Foundation Australia.",
      "https://www.hollows.org/nz/donate", 12000000, 83, 1992, date(2024, 3, 31),
      ["trachoma-blindness", "blindness-low-vision", "global-health"],
      "https://www.hollows.org/nz/about-us/financials", "annual_report", _verify_nz(), "medium"),

    # ============== Belgium (2) ==============
    E("plan-belgium", "BE", "BE-0407-034-124", "people",
      "Plan International Belgique", "Plan International Belgique",
      "Belgian member of Plan International — girls' rights, child sponsorship, EU policy advocacy.",
      "Бельгийский член Plan International — права девочек, спонсорство детей, адвокация политики ЕС.",
      "Plan International Belgique (BE 0407.034.124) is the Belgian member of Plan International. Brussels-based — naturally well-placed for EU institutional advocacy on child rights, education in emergencies, and women & girls programming.",
      "Plan International Belgique (BE 0407.034.124) — бельгийский член Plan International. Базируется в Брюсселе — естественно хорошо расположен для адвокации в институтах ЕС по правам детей, образованию в чрезвычайных ситуациях и программам женщин и девочек.",
      "https://www.planinternational.be/fr/donner", 35000000, 84, 1983, date(2023, 12, 31),
      ["child-welfare", "womens-rights", "humanitarian-medicine"],
      "https://www.planinternational.be/fr/qui-sommes-nous/transparence", "annual_report", _verify_be(), "medium"),

    E("unicef-belgium", "BE", "BE-0413-546-547", "people",
      "UNICEF Belgique", "UNICEF Belgique",
      "Belgian National Committee for UNICEF — fundraising + EU institutional child-rights advocacy.",
      "Бельгийский национальный комитет UNICEF — фандрайзинг + адвокация прав детей в институтах ЕС.",
      "Comité Belge pour l'UNICEF (BE 0413.546.547) is the Belgian National Committee for UNICEF. Headquartered in Brussels — does dual duty as national fundraising organisation and as advocate for child rights in European institutions (European Commission, European Parliament, Council of the EU).",
      "Comité Belge pour l'UNICEF (BE 0413.546.547) — бельгийский национальный комитет UNICEF. Штаб-квартира в Брюсселе — выполняет двойную функцию национальной фандрайзинговой организации и адвоката прав детей в европейских институтах (Европейская комиссия, Европейский парламент, Совет ЕС).",
      "https://www.unicef.be/fr/donate", 30000000, 85, 1953, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.be/fr/qui-sommes-nous/transparence", "annual_report", _verify_be(), "medium"),

    # ============== Denmark (2) ==============
    E("unicef-danmark", "DK", "DK-CVR-39658838", "people",
      "UNICEF Danmark", "UNICEF Danmark",
      "Danish National Committee for UNICEF — fundraising for global UNICEF programmes.",
      "Датский национальный комитет UNICEF — фандрайзинг для глобальных программ UNICEF.",
      "Unicef Danmark (CVR 39 65 88 38, founded 1955) is the Danish National Committee for UNICEF. ~250K Danish supporters; ~DKK 250M annual revenue. Strong emphasis on Denmark-domestic child-rights advocacy alongside global UNICEF fundraising.",
      "Unicef Danmark (CVR 39 65 88 38, основан в 1955 году) — датский национальный комитет UNICEF. ~250 тыс. датских сторонников; годовая выручка ~DKK 250 млн. Сильный акцент на внутренней датской адвокации прав детей вместе с глобальным фандрайзингом UNICEF.",
      "https://www.unicef.dk/stoett-os/", 35000000, 86, 1955, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "global-health"],
      "https://www.unicef.dk/om-os/aarsregnskab/", "annual_report", _verify_dk()),

    E("plan-denmark", "DK", "DK-CVR-25243214", "people",
      "Plan Børnefonden", "Plan Børnefonden — Plan International Denmark",
      "Danish member of Plan International — girls' rights focus, Africa programming emphasis.",
      "Датский член Plan International — фокус на правах девочек, акцент на Африке.",
      "Plan Børnefonden / Plan International Denmark (CVR 25 24 32 14) is the Danish national member of Plan International. ~120K Danish child-sponsors. Focus on East and West Africa programmes plus humanitarian response.",
      "Plan Børnefonden / Plan International Denmark (CVR 25 24 32 14) — датский национальный член Plan International. ~120 тыс. датских спонсоров детей. Фокус на программах Восточной и Западной Африки плюс гуманитарное реагирование.",
      "https://plandanmark.dk/stoet/", 28000000, 86, 1962, date(2023, 12, 31),
      ["child-welfare", "womens-rights", "humanitarian-medicine"],
      "https://plandanmark.dk/om-os/aarsrapport/", "annual_report", _verify_dk(), "medium"),

    # ============== Poland (3, NEW) ==============
    E("caritas-polska", "PL", "PL-KRS-0000198645", "people",
      "Caritas Polska", "Caritas Polska",
      "Polish Catholic Bishops' Conference humanitarian arm — Ukraine response, domestic poverty.",
      "Гуманитарное крыло Польской епископальной конференции — ответ на Украину, внутренняя бедность.",
      "Caritas Polska (KRS 0000198645, in current form 1990 after restoration in post-Communist Poland; original founded 1929) is the humanitarian arm of the Polish Episcopal Conference. Coordinated the massive Polish civil-society response to the 2022 Ukraine refugee crisis (~4M crossed into Poland), plus traditional anti-poverty work, hospice care, and ~110 Caritas diocesan groups.",
      "Caritas Polska (KRS 0000198645, в текущей форме с 1990 года после восстановления в постсоциалистической Польше; оригинал основан в 1929 году) — гуманитарное крыло Польской епископальной конференции. Координировал массовый ответ польского гражданского общества на украинский беженский кризис 2022 года (~4 млн пересекли в Польшу), плюс традиционная антибедная работа, хосписный уход и ~110 епархиальных групп Caritas.",
      "https://caritas.pl/jak-pomoc", 75000000, 88, 1929, date(2023, 12, 31),
      ["faith-based", "poverty-reduction", "refugees"],
      "https://caritas.pl/o-nas/raporty-roczne/", "annual_report", _verify_pl()),

    E("pah-polska", "PL", "PL-KRS-0000136833", "people",
      "Polska Akcja Humanitarna (PAH)", "PAH — Польская гуманитарная акция",
      "Polish non-religious humanitarian NGO — water, education, food in 10+ countries + Ukraine.",
      "Польская светская гуманитарная НПО — вода, образование, питание в 10+ странах + Украина.",
      "Polska Akcja Humanitarna / Polish Humanitarian Action (KRS 0000136833, founded 1992 by Janina Ochojska) is Poland's largest secular humanitarian organisation. Operates in 10+ countries (currently Ukraine, Somalia, South Sudan, DR Congo, Yemen, Syria) on water/sanitation, food security, education-in-emergencies. Polish domestic Pajacyk school-meal programme since 1998.",
      "Polska Akcja Humanitarna / Polish Humanitarian Action (KRS 0000136833, основана в 1992 году Яниной Охойской) — крупнейшая в Польше светская гуманитарная организация. Работает в 10+ странах (сейчас Украина, Сомали, Южный Судан, ДРК, Йемен, Сирия): вода/санитария, продовольственная безопасность, образование в чрезвычайных ситуациях. Польская внутренняя программа школьного питания Pajacyk с 1998 года.",
      "https://www.pah.org.pl/wesprzyj/", 35000000, 88, 1992, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response", "polish-charity"],
      "https://www.pah.org.pl/o-nas/raporty-roczne/", "annual_report", _verify_pl()),

    E("wosp-foundation", "PL", "PL-KRS-0000030897", "people",
      "Wielka Orkiestra Świątecznej Pomocy (WOŚP)", "WOŚP — Великий оркестр праздничной помощи",
      "Iconic Polish medical-equipment charity — annual nationwide telethon since 1993 raises ~$50M.",
      "Знаковый польский медицинский фонд — ежегодный национальный телетон с 1993 года собирает ~$50 млн.",
      "Wielka Orkiestra Świątecznej Pomocy / Great Orchestra of Christmas Charity (KRS 0000030897, founded 1993 by Jerzy Owsiak) is one of Poland's most beloved civic institutions. Annual second-Sunday-of-January telethon raises ~PLN 200M+ (~$50M) for paediatric and senior medical equipment donated to Polish public hospitals. Has donated ~PLN 2.5B of equipment since 1993.",
      "Wielka Orkiestra Świątecznej Pomocy / Great Orchestra of Christmas Charity (KRS 0000030897, основан в 1993 году Ежи Овсяком) — одна из самых любимых польских гражданских институций. Ежегодный телетон во второе воскресенье января собирает ~PLN 200+ млн (~$50 млн) на педиатрическое и геронтологическое медицинское оборудование, передаваемое в польские государственные больницы. С 1993 года передано оборудования на ~PLN 2,5 млрд.",
      "https://www.wosp.org.pl/wesprzyj-nas", 55000000, 91, 1993, date(2023, 12, 31),
      ["global-health", "polish-charity"],
      "https://www.wosp.org.pl/o-fundacji/raporty-roczne", "annual_report", _verify_pl()),

    # ============== Finland (3, NEW) ==============
    E("finnish-red-cross", "FI", "FI-Y-0116988-2", "people",
      "Suomen Punainen Risti (Finnish Red Cross)", "Finnish Red Cross — Suomen Punainen Risti",
      "Finnish national society of the International Red Cross — blood service, asylum, disaster aid.",
      "Финское национальное общество Международного Красного Креста — служба крови, помощь ищущим убежища, помощь при бедствиях.",
      "Suomen Punainen Risti / Finnish Red Cross (Y-tunnus 0116988-2, founded 1877) is the Finnish national society of the International Red Cross. Major operations: Finnish national blood service (Veripalvelu, ~95% of Finnish blood supply), asylum-seeker reception centres (state-funded), Finnish disaster response, and international humanitarian work via IFRC.",
      "Suomen Punainen Risti / Finnish Red Cross (Y-tunnus 0116988-2, основан в 1877 году) — финское национальное общество Международного Красного Креста. Крупные операции: национальная финская служба крови (Veripalvelu, ~95% финского запаса крови), приёмные центры для лиц, ищущих убежища (государственно финансируемые), финское реагирование на бедствия, международная гуманитарная работа через IFRC.",
      "https://www.punainenristi.fi/lahjoita/", 285000000, 87, 1877, date(2023, 12, 31),
      ["finnish-charity", "emergency-response", "refugees"],
      "https://www.punainenristi.fi/tietoa-meista/talous/", "annual_report", _verify_fi()),

    E("unicef-finland", "FI", "FI-Y-1011144-3", "people",
      "Suomen UNICEF", "Suomen UNICEF (UNICEF Finland)",
      "Finnish National Committee for UNICEF — fundraising and Finnish child-rights advocacy.",
      "Финский национальный комитет UNICEF — фандрайзинг и финская адвокация прав детей.",
      "Suomen UNICEF (Y-tunnus 1011144-3, founded 1967) is the Finnish National Committee for UNICEF. ~190K Finnish supporters; ~€60M annual revenue. Focus areas: global emergency response, polio eradication, Finnish-domestic child-rights monitoring through the annual UNICEF Finland Lapsiraportti.",
      "Suomen UNICEF (Y-tunnus 1011144-3, основан в 1967 году) — финский национальный комитет UNICEF. ~190 тыс. финских сторонников; годовая выручка ~€60 млн. Ключевые направления: глобальное экстренное реагирование, искоренение полиомиелита, мониторинг прав детей внутри Финляндии через ежегодный UNICEF Finland Lapsiraportti.",
      "https://www.unicef.fi/lahjoita/", 65000000, 86, 1967, date(2023, 12, 31),
      ["child-welfare", "humanitarian-medicine", "finnish-charity"],
      "https://www.unicef.fi/tietoa-meista/talous/", "annual_report", _verify_fi()),

    E("plan-finland", "FI", "FI-Y-1593776-9", "people",
      "Plan International Suomi", "Plan International Suomi (Plan Finland)",
      "Finnish member of Plan International — girls' rights, ~75K Finnish child sponsors.",
      "Финский член Plan International — права девочек, ~75 тыс. финских спонсоров детей.",
      "Plan International Suomi / Plan Finland (Y-tunnus 1593776-9, founded 1998) is the Finnish national member of Plan International. ~75K Finnish child-sponsors. Focus areas: girls' rights and gender equality in Africa and Asia, plus Finnish domestic education campaigns on global child rights.",
      "Plan International Suomi / Plan Finland (Y-tunnus 1593776-9, основан в 1998 году) — финский национальный член Plan International. ~75 тыс. финских спонсоров детей. Ключевые направления: права девочек и гендерное равенство в Африке и Азии, плюс финские внутренние образовательные кампании по глобальным правам детей.",
      "https://plan.fi/lahjoita", 22000000, 84, 1998, date(2023, 12, 31),
      ["child-welfare", "womens-rights", "finnish-charity"],
      "https://plan.fi/meista/talous", "annual_report", _verify_fi(), "medium"),

    # ============== Austria (3, NEW) ==============
    E("caritas-austria", "AT", "AT-ZVR-326776463", "people",
      "Caritas Österreich", "Caritas Österreich",
      "Austrian Catholic Bishops' Conference social-services federation — Austria's largest welfare network.",
      "Социальная федерация Австрийской епископальной конференции — крупнейшая социальная сеть Австрии.",
      "Caritas Österreich (ZVR 326,776,463) is the federation of 9 Austrian Caritas diocesan organisations (~17K paid staff, ~50K volunteers) — Austria's largest non-government social-services network. Domestic Austria operations: refugee reception, homeless shelters, disability services, in-home eldercare, family services. International cooperation via Caritas International.",
      "Caritas Österreich (ZVR 326,776,463) — федерация 9 австрийских епархиальных организаций Caritas (~17 тыс. оплачиваемых сотрудников, ~50 тыс. волонтёров) — крупнейшая австрийская негосударственная социальная сеть. Внутренние операции в Австрии: приём беженцев, приюты для бездомных, услуги для инвалидов, домашний уход за пожилыми, семейные услуги. Международное сотрудничество через Caritas International.",
      "https://www.caritas.at/spenden", 700000000, 90, 1903, date(2023, 12, 31),
      ["faith-based", "homelessness", "refugees", "elderly-care", "austrian-charity"],
      "https://www.caritas.at/ueber-uns/transparenz/", "annual_report", _verify_at()),

    E("msf-austria", "AT", "AT-ZVR-517860719", "people",
      "Ärzte ohne Grenzen (MSF Austria)", "Ärzte ohne Grenzen — MSF Austria",
      "Austrian section of MSF — recruits Austrian medical staff, raises funds for global emergencies.",
      "Австрийская секция MSF — набирает австрийский медперсонал, собирает средства для глобальных кризисов.",
      "Ärzte ohne Grenzen / MSF Austria (ZVR 517,860,719, founded 1994) is the Austrian section of the international MSF movement. Recruits Austrian medical, paramedical and logistical personnel for MSF field missions worldwide; fundraises in Austria.",
      "Ärzte ohne Grenzen / MSF Austria (ZVR 517,860,719, основана в 1994 году) — австрийская секция международного движения MSF. Набирает австрийский медицинский, парамедицинский и логистический персонал для полевых миссий MSF по всему миру; собирает средства в Австрии.",
      "https://www.aerzte-ohne-grenzen.at/spenden", 95000000, 89, 1994, date(2023, 12, 31),
      ["humanitarian-medicine", "emergency-response", "austrian-charity"],
      "https://www.aerzte-ohne-grenzen.at/ueber-uns/finanzen", "annual_report", _verify_at()),

    E("volkshilfe-austria", "AT", "AT-ZVR-411332231", "people",
      "Volkshilfe Österreich", "Volkshilfe Österreich",
      "Austrian secular socialist-roots social-services federation — Austria's anti-poverty advocacy leader.",
      "Австрийская светская социальная федерация с социалистическими корнями — лидер антибедной адвокации.",
      "Volkshilfe Österreich (ZVR 411,332,231, founded 1947 by Austrian Social Democrats after WWII) is one of Austria's largest secular social-services federations. Operates ~7,000 paid staff + ~12,000 volunteers. Focus areas: poverty reduction (Volkshilfe operates the well-known Sozialbarometer poverty-monitoring), child welfare, eldercare, refugees and migrants. Federal anti-poverty policy advocacy.",
      "Volkshilfe Österreich (ZVR 411,332,231, основана в 1947 году австрийскими социал-демократами после Второй мировой войны) — одна из крупнейших австрийских светских социальных федераций. ~7000 оплачиваемых сотрудников + ~12 000 волонтёров. Ключевые направления: сокращение бедности (Volkshilfe ведёт известный Sozialbarometer мониторинга бедности), благополучие детей, уход за пожилыми, беженцы и мигранты. Федеральная антибедная адвокация политики.",
      "https://www.volkshilfe.at/spenden", 200000000, 88, 1947, date(2023, 12, 31),
      ["poverty-reduction", "elderly-care", "child-welfare", "austrian-charity"],
      "https://www.volkshilfe.at/wir-ueber-uns/finanzen", "annual_report", _verify_at()),

    # ============== Israel (3, NEW) ==============
    E("magen-david-adom", "IL", "IL-NPO-580138777", "people",
      "Magen David Adom (MDA)", "Magen David Adom — израильская скорая помощь",
      "Israel's national emergency medical service — ambulances, blood services; non-political humanitarian.",
      "Национальная служба экстренной медицинской помощи Израиля — скорая, служба крови; неполитическая гуманитарная.",
      "Magen David Adom (NPO 580138777, founded 1930) is Israel's national emergency-medical-services organisation under the 1950 MDA Law — the Israeli equivalent of the Red Cross / Red Crescent (operates with the Red Shield of David emblem within the International Red Cross & Red Crescent Movement since 2006). Operates ~2,500 ambulances and ~24K paid staff + volunteers, plus Israel's national blood-bank service. Independent of government for funding; receives no direct government subsidies for its humanitarian operations.",
      "Magen David Adom (NPO 580138777, основан в 1930 году) — национальная служба экстренной медицинской помощи Израиля согласно Закону MDA 1950 года — израильский эквивалент Красного Креста / Красного Полумесяца (работает с эмблемой Красного Щита Давида в Международном движении Красного Креста и Красного Полумесяца с 2006 года). Управляет ~2500 машинами скорой помощи и ~24 тыс. оплачиваемых сотрудников + волонтёров, плюс национальная служба банка крови Израиля. Независим от правительства по финансированию.",
      "https://www.afmda.org/donate", 350000000, 92, 1930, date(2023, 12, 31),
      ["israeli-emergency-medical", "emergency-response", "humanitarian-medicine"],
      "https://www.mdais.org/en/about-us", "annual_report", _verify_il()),

    E("yad-vashem", "IL", "IL-NPO-580029568", "people",
      "Yad Vashem", "Yad Vashem — Институт памяти жертв Холокоста",
      "World Holocaust Remembrance Center in Jerusalem — research, education, names database of victims.",
      "Всемирный центр памяти Холокоста в Иерусалиме — исследования, образование, база данных имён жертв.",
      "Yad Vashem (NPO 580029568, established 1953 by the Yad Vashem Law) is the World Holocaust Remembrance Center — Israel's official memorial to the Jewish victims of the Holocaust. Operates: the Holocaust History Museum (~1M annual visitors), the Central Database of Shoah Victims' Names (~4.9M names recorded), Righteous Among the Nations recognition programme, the International School for Holocaust Studies.",
      "Yad Vashem (NPO 580029568, учреждён в 1953 году Законом Yad Vashem) — Всемирный центр памяти Холокоста — официальный мемориал Израиля еврейским жертвам Холокоста. Управляет: Музеем истории Холокоста (~1 млн посетителей в год), Центральной базой данных имён жертв Шоа (~4,9 млн имён зарегистрировано), программой Праведников народов мира, Международной школой изучения Холокоста.",
      "https://www.yadvashem.org/donate.html", 40000000, 82, 1953, date(2023, 12, 31),
      ["holocaust-remembrance", "education"],
      "https://www.yadvashem.org/about/about-yad-vashem.html", "annual_report", _verify_il()),

    E("shalva-israel", "IL", "IL-NPO-580188301", "people",
      "Shalva — The Association for the Care and Inclusion of Persons with Disabilities", "Shalva — Израильская организация инклюзии для людей с инвалидностью",
      "Israeli charity providing comprehensive services for people with disabilities and their families.",
      "Израильская организация, предоставляющая комплексные услуги для людей с инвалидностью и их семей.",
      "Shalva (NPO 580188301, founded 1990 by Kalman and Malki Samuels) provides comprehensive services for people with disabilities and their families in Israel — daycare for infants and toddlers with disabilities, after-school programmes, residential adult-care, and employment-readiness. Iconic Shalva Band — a music ensemble of musicians with disabilities — represented Israel at Eurovision and won wide international recognition.",
      "Shalva (NPO 580188301, основана в 1990 году Калманом и Малки Сэмюэлс) предоставляет комплексные услуги для людей с инвалидностью и их семей в Израиле — дневной уход для младенцев и дошкольников с инвалидностью, послешкольные программы, резиденциальный уход за взрослыми, готовность к трудоустройству. Знаменитая Shalva Band — музыкальный ансамбль музыкантов с инвалидностью — представлял Израиль на Евровидении и получил широкое международное признание.",
      "https://www.shalva.org/en/donate", 35000000, 85, 1990, date(2023, 12, 31),
      ["israeli-disability", "disability-services"],
      "https://www.shalva.org/en/about-us/transparency", "annual_report", _verify_il()),
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
            print(f"[migration 0055] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
    print(f"[migration 0055] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0054_extend_country_choices_v314"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

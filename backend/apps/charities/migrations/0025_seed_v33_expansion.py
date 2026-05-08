"""v3.3 catalog scale-up — seed ~40 more curated charities (58 -> ~98).

People (+20), Animals (+8), Planet (+12). EINs zero-padded to 9 digits per
KB-017. US 501(c)(3) source URLs use the ProPublica `/organizations/{ein}`
overview page (KB-014; the /download-filing path is behind Cloudflare's
challenge wall and breaks for some users — see migration 0024). UK orgs
point at the Charity Commission charity-details accounts page.

Hero photos & logos: empty in this migration. Backfilled by:
  - 0026_backfill_v33_logos.py     (logo_url via uplead/Google s2)
  - 0027_backfill_v33_hero_photos.py (Wikimedia Commons + Unsplash CC0)

Verification: each EIN/Charity# was checked against ProPublica or
the Charity Commission register at curation time per KB-012. Iodine Global
Network was substituted (no clean US 501(c)(3) presence — their global
work runs as ICCIDD via fiscal sponsorship).

Substitutions made vs. the original brief (verification failures):
  - "Iodine Global Network" — substituted with "Possible Health" (Nyaya
    Health USA, EIN 56-2618866). Both are small global-health 501c3s; the
    bucket-level "people / global-health" coverage is preserved.

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
    "childhood-cancer": {
        "en": "Childhood cancer",
        "ru": "Детская онкология",
    },
    "disability-services": {
        "en": "Disability services",
        "ru": "Помощь людям с инвалидностью",
    },
    "classroom-funding": {
        "en": "Classroom funding",
        "ru": "Финансирование школьных классов",
    },
    "free-education": {
        "en": "Free education",
        "ru": "Бесплатное образование",
    },
    "open-knowledge": {
        "en": "Open knowledge",
        "ru": "Открытые знания",
    },
    "civil-rights": {
        "en": "Civil rights",
        "ru": "Гражданские права",
    },
    "working-animals": {
        "en": "Working animals",
        "ru": "Рабочие животные",
    },
    "donkey-welfare": {
        "en": "Donkey welfare",
        "ru": "Защита ослов",
    },
    "ocean-protection": {
        "en": "Ocean protection",
        "ru": "Защита океана",
    },
    "demand-reduction": {
        "en": "Demand reduction (wildlife trade)",
        "ru": "Снижение спроса (торговля дикими животными)",
    },
    "biodiversity-defense": {
        "en": "Biodiversity defense",
        "ru": "Защита биоразнообразия",
    },
    "climate-policy": {
        "en": "Climate policy",
        "ru": "Климатическая политика",
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


def _uk_verify_note() -> dict:
    return {
        "en": (
            "Verified: registered charity with the UK Charity Commission, "
            "annual accounts on file."
        ),
        "ru": (
            "Подтверждено: благотворительная организация в реестре "
            "Charity Commission UK, годовая отчётность на сайте регулятора."
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


def _uk_charity_url(reg_id: str) -> str:
    return (
        f"https://register-of-charities.charitycommission.gov.uk/"
        f"charity-search/-/charity-details/{reg_id}/accounts-and-annual-returns"
    )


SEED: list[dict] = [
    # ===================== PEOPLE — 20 new =====================
    # ----- Smile Train -----
    {
        "slug": "smile-train",
        "country": "US",
        "registration_id": "133661416",
        "bucket": "people",
        "name": {"en": "Smile Train", "ru": "Smile Train"},
        "tagline": {
            "en": "Trains local surgeons to provide cleft care for children",
            "ru": "Обучает местных хирургов оказывать помощь детям с расщелиной",
        },
        "description": {
            "en": (
                "Smile Train is a US 501(c)(3) that funds free cleft-lip "
                "and palate surgery in 90+ countries. Differs from "
                "mission-style models by training and equipping LOCAL "
                "surgeons year-round, so care continues without external "
                "teams. Has supported 1.5M+ surgeries since 1999."
            ),
            "ru": (
                "Smile Train — американская 501(c)(3), финансирует "
                "бесплатные операции на расщелине губы и нёба в 90+ "
                "странах. В отличие от выездных миссий, обучает и "
                "оснащает МЕСТНЫХ хирургов круглый год — помощь "
                "оказывается постоянно. С 1999 года поддержано более "
                "1,5 млн операций."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.smiletrain.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1999,
        "cause_slugs": ["global-health", "cleft-surgery"],
        **_empty_photo(),
    },
    # ----- The Carter Center -----
    {
        "slug": "carter-center",
        "country": "US",
        "registration_id": "581454716",
        "bucket": "people",
        "name": {"en": "The Carter Center", "ru": "The Carter Center"},
        "tagline": {
            "en": "Disease eradication and democracy support in 80+ countries",
            "ru": "Искоренение болезней и поддержка демократии в 80+ странах",
        },
        "description": {
            "en": (
                "Founded in 1982 by President Jimmy and Rosalynn Carter, "
                "the Carter Center is a US 501(c)(3) tackling neglected "
                "tropical diseases (Guinea worm — from 3.5M cases to "
                "<25/yr; river blindness; trachoma; lymphatic filariasis) "
                "and supporting democratic elections globally. Partner of "
                "Emory University in Atlanta."
            ),
            "ru": (
                "Основан в 1982 году президентом Джимми и Розалинн Картер. "
                "Carter Center — американская 501(c)(3), борется с "
                "забытыми тропическими болезнями (ришта — с 3,5 млн "
                "случаев до <25 в год; речная слепота; трахома; "
                "лимфатический филяриатоз) и поддерживает демократические "
                "выборы по миру. Партнёр университета Эмори в Атланте."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.cartercenter.org/donate/index.html",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 14),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1982,
        "cause_slugs": ["global-health", "civil-rights"],
        **_empty_photo(),
    },
    # ----- Sightsavers (UK) -----
    {
        "slug": "sightsavers-uk",
        "country": "GB",
        "registration_id": "207544",
        "bucket": "people",
        "name": {"en": "Sightsavers", "ru": "Sightsavers"},
        "tagline": {
            "en": "Prevents avoidable blindness in low-income countries",
            "ru": "Предотвращает предотвратимую слепоту в странах с низкими доходами",
        },
        "description": {
            "en": (
                "Sightsavers is a UK-registered charity (Charity 207544) "
                "working in 30+ countries to prevent avoidable blindness "
                "(cataract surgery, trachoma elimination, river-blindness "
                "treatment) and to protect the rights of people with "
                "disabilities. A GiveWell-recommended charity for its "
                "deworming and trachoma programmes."
            ),
            "ru": (
                "Sightsavers — британская благотворительная организация "
                "(Charity 207544), работает в 30+ странах: предотвращает "
                "предотвратимую слепоту (операции при катаракте, борьба с "
                "трахомой, лечение речной слепоты) и защищает права людей "
                "с инвалидностью. Рекомендована GiveWell за программы "
                "дегельминтизации и борьбы с трахомой."
            ),
        },
        "methodology_note": _uk_verify_note(),
        "logo_url": "",
        "donation_url": "https://www.sightsavers.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("440000000.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 1950,
        "cause_slugs": ["global-health", "disability-services"],
        **_empty_photo(),
    },
    # ----- One Acre Fund -----
    {
        "slug": "one-acre-fund",
        "country": "US",
        "registration_id": "203668110",
        "bucket": "people",
        "name": {"en": "One Acre Fund", "ru": "One Acre Fund"},
        "tagline": {
            "en": "Bundles seed, training and finance for African smallholders",
            "ru": "Семена, обучение и финансы для мелких фермеров Африки",
        },
        "description": {
            "en": (
                "One Acre Fund is a US 501(c)(3) serving 1.5M+ smallholder "
                "farm families across East and Southern Africa. The model "
                "bundles quality seed and fertiliser on credit, agronomic "
                "training, market linkages and crop insurance — repaid at "
                "harvest. Independent evaluations show ~40% income gain "
                "for participating farmers."
            ),
            "ru": (
                "One Acre Fund — американская 501(c)(3), обслуживает "
                "более 1,5 млн фермерских семей в Восточной и Южной "
                "Африке. Модель: качественные семена и удобрения в "
                "кредит, агрономическое обучение, выход на рынок и "
                "страхование урожая — возврат после сбора. Независимые "
                "оценки: рост доходов фермеров примерно на 40%."
            ),
        },
        "methodology_note": _verify_note(
            "Independently evaluated impact data published.",
            "Доказанная эффективность по независимым оценкам.",
        ),
        "logo_url": "",
        "donation_url": "https://oneacrefund.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("220000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2006,
        "cause_slugs": ["poverty-reduction", "food-security"],
        **_empty_photo(),
    },
    # ----- Last Mile Health -----
    {
        "slug": "last-mile-health",
        "country": "US",
        "registration_id": "208058182",
        "bucket": "people",
        "name": {"en": "Last Mile Health", "ru": "Last Mile Health"},
        "tagline": {
            "en": "Trains community health workers in rural Liberia and beyond",
            "ru": "Обучает общинных медработников в сельской Либерии и других странах",
        },
        "description": {
            "en": (
                "Last Mile Health is a US 501(c)(3) that designs and "
                "supports professional community-health-worker programmes "
                "in remote communities, partnering with the governments "
                "of Liberia, Sierra Leone, Malawi and Ethiopia. Born out "
                "of the Liberian civil war in 2007 — co-founded by a "
                "MacArthur Fellow physician."
            ),
            "ru": (
                "Last Mile Health — американская 501(c)(3), проектирует "
                "и поддерживает профессиональные программы общинных "
                "медработников в удалённых сообществах в партнёрстве с "
                "правительствами Либерии, Сьерра-Леоне, Малави и Эфиопии. "
                "Создана в 2007 году после гражданской войны в Либерии."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://lastmilehealth.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("48000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 2007,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
    },
    # ----- VillageReach -----
    {
        "slug": "villagereach",
        "country": "US",
        "registration_id": "911580672",
        "bucket": "people",
        "name": {"en": "VillageReach", "ru": "VillageReach"},
        "tagline": {
            "en": "Strengthens vaccine cold-chain and last-mile health logistics",
            "ru": "Укрепляет холодовую цепь вакцин и логистику последней мили",
        },
        "description": {
            "en": (
                "VillageReach is a Seattle-based US 501(c)(3) working in "
                "Mozambique, Malawi, DRC and other African countries on "
                "the unsexy but vital problem of getting vaccines, drugs "
                "and supplies through the cold chain to rural clinics on "
                "time and at the right temperature. Builds health-system "
                "logistics rather than running parallel programs."
            ),
            "ru": (
                "VillageReach — американская 501(c)(3) из Сиэтла, "
                "работает в Мозамбике, Малави, ДРК и других странах "
                "Африки над важной задачей: доставлять вакцины, "
                "препараты и расходники через холодовую цепь в сельские "
                "клиники вовремя и при нужной температуре. Укрепляет "
                "государственные системы здравоохранения."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.villagereach.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 2000,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
    },
    # ----- Population Services International (PSI) -----
    {
        "slug": "psi",
        "country": "US",
        "registration_id": "560942853",
        "bucket": "people",
        "name": {
            "en": "Population Services International",
            "ru": "Population Services International",
        },
        "tagline": {
            "en": "Marketing-based public health in 40+ countries",
            "ru": "Социальный маркетинг в здравоохранении в 40+ странах",
        },
        "description": {
            "en": (
                "PSI is a US 501(c)(3) that uses social marketing to make "
                "health products and services (contraception, malaria "
                "nets, water-purification tablets, HIV testing, maternal "
                "health) affordable and desirable for low-income consumers "
                "in 40+ countries. One of the larger global-health NGOs "
                "by revenue."
            ),
            "ru": (
                "PSI — американская 501(c)(3), использует социальный "
                "маркетинг, чтобы товары и услуги здравоохранения "
                "(контрацепция, противомалярийные сетки, таблетки для "
                "обеззараживания воды, тесты на ВИЧ, материнское здоровье) "
                "были доступны малоимущим в 40+ странах. Одна из крупных "
                "глобальных медицинских НКО по выручке."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.psi.org/give/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("440000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1970,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
    },
    # ----- Project HOPE -----
    {
        "slug": "project-hope",
        "country": "US",
        "registration_id": "530242962",
        "bucket": "people",
        "name": {"en": "Project HOPE", "ru": "Project HOPE"},
        "tagline": {
            "en": "Health-worker training and emergency medical aid worldwide",
            "ru": "Обучение медработников и экстренная медицинская помощь",
        },
        "description": {
            "en": (
                "Project HOPE is a US 501(c)(3) global health and "
                "humanitarian organisation that trains health workers, "
                "responds to medical emergencies (including the COVID-19 "
                "response and Ukraine, Türkiye-Syria earthquake, Gaza "
                "responses), and supports public-health programmes in "
                "30+ countries. Founded around the SS HOPE hospital ship "
                "in 1958."
            ),
            "ru": (
                "Project HOPE — американская 501(c)(3), глобальная "
                "медицинская и гуманитарная организация: обучает "
                "медработников, реагирует на медицинские чрезвычайные "
                "ситуации (COVID-19, землетрясение в Турции и Сирии, "
                "Газа), ведёт программы общественного здравоохранения "
                "в 30+ странах. Создана в 1958 году вокруг госпитального "
                "судна SS HOPE."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.projecthope.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 13),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1958,
        "cause_slugs": ["global-health", "emergency-response"],
        **_empty_photo(),
    },
    # ----- Possible Health (substitute for Iodine Global Network) -----
    {
        "slug": "possible-health",
        "country": "US",
        "registration_id": "562618866",
        "bucket": "people",
        "name": {
            "en": "Possible Health (Nyaya Health USA)",
            "ru": "Possible Health (Nyaya Health USA)",
        },
        "tagline": {
            "en": "Public health-care delivery in rural Nepal",
            "ru": "Государственное здравоохранение в сельском Непале",
        },
        "description": {
            "en": (
                "Possible Health (legal name Nyaya Health USA) is a US "
                "501(c)(3) that runs durable public-private health-system "
                "partnerships in rural Nepal, providing free primary care "
                "in district hospitals and community health-worker "
                "networks. Has published its full operational and "
                "financial data openly. Substituted for Iodine Global "
                "Network in the v3.3 expansion (no clean US 501c3)."
            ),
            "ru": (
                "Possible Health (юр. лицо Nyaya Health USA) — "
                "американская 501(c)(3), ведёт устойчивые "
                "государственно-частные партнёрства в здравоохранении "
                "сельского Непала: бесплатная первичная помощь в "
                "районных больницах и сети общинных медработников. Все "
                "операционные и финансовые данные публикуются открыто. "
                "Заменена в v3.3 на Iodine Global Network (нет чистого "
                "501c3)."
            ),
        },
        "methodology_note": _verify_note(
            "Open financials and operational data published.",
            "Финансы и операционные данные публикуются открыто.",
        ),
        "logo_url": "",
        "donation_url": "https://possiblehealth.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2008,
        "cause_slugs": ["global-health"],
        **_empty_photo(),
    },
    # ----- St. Jude Children's Research Hospital (ALSAC) -----
    {
        "slug": "st-jude",
        "country": "US",
        "registration_id": "620646012",
        "bucket": "people",
        "name": {
            "en": "St. Jude Children's Research Hospital (ALSAC)",
            "ru": "St. Jude — детская исследовательская больница (ALSAC)",
        },
        "tagline": {
            "en": "Free childhood-cancer care and research in Memphis",
            "ru": "Бесплатное лечение и исследования детской онкологии",
        },
        "description": {
            "en": (
                "St. Jude is a Memphis-based pediatric research hospital "
                "that treats children with catastrophic illnesses — "
                "cancer, sickle-cell, and other life-threatening "
                "conditions — at no cost to families. Funded by ALSAC, "
                "the US 501(c)(3) fundraising arm. Pioneered childhood "
                "leukaemia treatment; survival rates rose from 4% to 94% "
                "since 1962."
            ),
            "ru": (
                "St. Jude — детская исследовательская больница в "
                "Мемфисе, лечит детей с тяжёлыми заболеваниями: онкология, "
                "серповидноклеточная анемия и другие угрожающие жизни — "
                "бесплатно для семей. Финансируется через ALSAC, "
                "американскую 501(c)(3). Лидер в лечении детского "
                "лейкоза: выживаемость выросла с 4% до 94% с 1962 года."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.stjude.org/donate/donate-to-st-jude.html",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("2400000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1957,
        "cause_slugs": ["childhood-cancer", "global-health"],
        **_empty_photo(),
    },
    # ----- Make-A-Wish America -----
    {
        "slug": "make-a-wish",
        "country": "US",
        "registration_id": "860481941",
        "bucket": "people",
        "name": {"en": "Make-A-Wish America", "ru": "Make-A-Wish America"},
        "tagline": {
            "en": "Grants wishes for children with critical illnesses",
            "ru": "Исполняет желания детей с тяжёлыми заболеваниями",
        },
        "description": {
            "en": (
                "Make-A-Wish America is a US 501(c)(3) that grants wishes "
                "for children diagnosed with critical illnesses. Operates "
                "via 60 chapters across the United States, plus a global "
                "affiliate network in 50+ countries. Grants ~30,000 "
                "wishes per year. Independent research suggests wish "
                "fulfilment is associated with measurable improvements "
                "in pediatric well-being."
            ),
            "ru": (
                "Make-A-Wish America — американская 501(c)(3), исполняет "
                "желания детей с тяжёлыми заболеваниями. Работает через "
                "60 отделений по США и глобальную партнёрскую сеть в 50+ "
                "странах. Около 30 тыс. желаний в год. Независимые "
                "исследования связывают исполнение желаний с измеримым "
                "улучшением самочувствия пациентов."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://wish.org/ways-to-give",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("440000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1980,
        "cause_slugs": ["childhood-cancer", "child-sponsorship"],
        **_empty_photo(),
    },
    # ----- Pratham USA -----
    {
        "slug": "pratham-usa",
        "country": "US",
        "registration_id": "650510769",
        "bucket": "people",
        "name": {"en": "Pratham USA", "ru": "Pratham USA"},
        "tagline": {
            "en": "Foundational literacy and numeracy for Indian children",
            "ru": "Базовая грамотность и счёт для детей в Индии",
        },
        "description": {
            "en": (
                "Pratham USA is a US 501(c)(3) supporting Pratham, one "
                "of India's largest education NGOs. Pratham developed "
                "the 'Teaching at the Right Level' (TaRL) approach — "
                "grouping children by learning level, not age — which "
                "the World Bank has scaled across multiple countries "
                "as one of the most evidence-backed education "
                "interventions globally."
            ),
            "ru": (
                "Pratham USA — американская 501(c)(3), поддерживает "
                "Pratham, одну из крупнейших образовательных НКО Индии. "
                "Pratham разработала подход 'Teaching at the Right Level' "
                "(обучение по уровню знаний, а не по возрасту) — Всемирный "
                "банк масштабировал его в нескольких странах как одну из "
                "самых доказательных образовательных интервенций в мире."
            ),
        },
        "methodology_note": _verify_note(
            "RCT-backed methodology (TaRL) scaled by World Bank.",
            "Методика TaRL подтверждена RCT и масштабирована Всемирным банком.",
        ),
        "logo_url": "",
        "donation_url": "https://prathamusa.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 2000,
        "cause_slugs": ["education", "free-education"],
        **_empty_photo(),
    },
    # ----- Educate Girls Globally -----
    {
        "slug": "educate-girls",
        "country": "US",
        "registration_id": "200352796",
        "bucket": "people",
        "name": {"en": "Educate Girls Globally", "ru": "Educate Girls Globally"},
        "tagline": {
            "en": "Enrolls out-of-school girls in rural India",
            "ru": "Возвращает девочек из сельской Индии в школу",
        },
        "description": {
            "en": (
                "Educate Girls Globally is a US 501(c)(3) supporting the "
                "India-based Educate Girls programme, which mobilises "
                "village volunteers to identify out-of-school girls and "
                "enroll them, plus runs in-school remedial learning. The "
                "programme was the first education intervention to use a "
                "Development Impact Bond, with an independent evaluation "
                "showing strong learning gains."
            ),
            "ru": (
                "Educate Girls Globally — американская 501(c)(3), "
                "поддерживает индийскую программу Educate Girls: "
                "сельские волонтёры выявляют девочек, не посещающих "
                "школу, возвращают их в школу и ведут дополнительные "
                "занятия. Первая образовательная программа, "
                "профинансированная через Development Impact Bond с "
                "доказанным независимой оценкой ростом результатов."
            ),
        },
        "methodology_note": _verify_note(
            "Development Impact Bond outcomes independently verified.",
            "Результаты Development Impact Bond независимо подтверждены.",
        ),
        "logo_url": "",
        "donation_url": "https://www.educategirls.ngo/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("8500000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2007,
        "cause_slugs": ["education", "free-education"],
        **_empty_photo(),
    },
    # ----- DonorsChoose -----
    {
        "slug": "donorschoose",
        "country": "US",
        "registration_id": "134129457",
        "bucket": "people",
        "name": {"en": "DonorsChoose", "ru": "DonorsChoose"},
        "tagline": {
            "en": "Funds classroom projects for US public-school teachers",
            "ru": "Финансирует проекты учителей государственных школ США",
        },
        "description": {
            "en": (
                "DonorsChoose is a US 501(c)(3) crowdfunding platform "
                "where US public-school teachers post specific classroom "
                "needs (books, supplies, field trips, instruments) and "
                "donors fund them directly. Has funded ~3M projects "
                "for teachers in every public school district in the "
                "country since 2000."
            ),
            "ru": (
                "DonorsChoose — американская 501(c)(3), краудфандинговая "
                "платформа: учителя государственных школ США публикуют "
                "конкретные нужды класса (книги, расходники, экскурсии, "
                "инструменты), жертвователи напрямую их финансируют. С "
                "2000 года профинансировано около 3 млн проектов в школах "
                "каждого школьного округа США."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.donorschoose.org/donors/give.html",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("190000000.00"),
        "program_expense_pct": Decimal("88.00"),
        "founded_year": 2000,
        "cause_slugs": ["education", "classroom-funding"],
        **_empty_photo(),
    },
    # ----- Khan Academy -----
    {
        "slug": "khan-academy",
        "country": "US",
        "registration_id": "262617390",
        "bucket": "people",
        "name": {"en": "Khan Academy", "ru": "Khan Academy"},
        "tagline": {
            "en": "Free world-class education for anyone, anywhere",
            "ru": "Бесплатное образование мирового уровня для всех",
        },
        "description": {
            "en": (
                "Khan Academy is a US 501(c)(3) providing free online "
                "educational content — interactive practice, instructional "
                "videos, and personalised learning across mathematics, "
                "science, computing, history, art and economics. Reaches "
                "100M+ learners annually in 50+ languages. Funded by "
                "philanthropy; no ads, no subscriptions, no paywalls."
            ),
            "ru": (
                "Khan Academy — американская 501(c)(3), даёт бесплатные "
                "онлайн-образовательные материалы: интерактивные задачи, "
                "обучающие видео, индивидуализированное обучение по "
                "математике, естествознанию, информатике, истории, "
                "искусству и экономике. Охватывает 100+ млн учащихся в "
                "год на 50+ языках. Финансируется за счёт филантропии, "
                "без рекламы и подписок."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.khanacademy.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("80000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2008,
        "cause_slugs": ["education", "free-education"],
        **_empty_photo(),
    },
    # ----- Wikimedia Foundation -----
    {
        "slug": "wikimedia-foundation",
        "country": "US",
        "registration_id": "200049703",
        "bucket": "people",
        "name": {"en": "Wikimedia Foundation", "ru": "Wikimedia Foundation"},
        "tagline": {
            "en": "Hosts Wikipedia and the free-knowledge sister projects",
            "ru": "Содержит Википедию и проекты свободных знаний",
        },
        "description": {
            "en": (
                "The Wikimedia Foundation is a US 501(c)(3) that hosts "
                "and supports Wikipedia, Wikimedia Commons, Wiktionary, "
                "Wikidata and the other Wikimedia projects — a free, "
                "open knowledge resource available in 300+ languages. "
                "Funded almost entirely by small donations from the public; "
                "carries no advertising."
            ),
            "ru": (
                "Wikimedia Foundation — американская 501(c)(3), "
                "содержит и поддерживает Википедию, Wikimedia Commons, "
                "Wiktionary, Wikidata и другие проекты Wikimedia — "
                "свободный открытый ресурс знаний на 300+ языках. "
                "Финансируется почти полностью мелкими пожертвованиями, "
                "без рекламы."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://donate.wikimedia.org/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2003,
        "cause_slugs": ["open-knowledge", "free-education"],
        **_empty_photo(),
    },
    # ----- Code.org -----
    {
        "slug": "code-org",
        "country": "US",
        "registration_id": "464205692",
        "bucket": "people",
        "name": {"en": "Code.org", "ru": "Code.org"},
        "tagline": {
            "en": "Expands access to computer science in K-12 schools",
            "ru": "Расширяет доступ к информатике в школах K-12",
        },
        "description": {
            "en": (
                "Code.org is a US 501(c)(3) advocating that every K-12 "
                "student should have the opportunity to learn computer "
                "science. Provides free curriculum used by ~30% of US "
                "K-12 students, runs the Hour of Code campaign, and works "
                "on policy to add CS to state curricula. Translated "
                "materials available in 70+ languages."
            ),
            "ru": (
                "Code.org — американская 501(c)(3), отстаивает идею: "
                "каждый школьник K-12 должен иметь возможность учить "
                "информатику. Даёт бесплатную учебную программу (около "
                "30% школьников США), ведёт кампанию Hour of Code, "
                "работает над включением информатики в школьные "
                "программы штатов. Материалы переведены на 70+ языков."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://code.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("78000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 2013,
        "cause_slugs": ["education", "free-education"],
        **_empty_photo(),
    },
    # ----- Teach For America -----
    {
        "slug": "teach-for-america",
        "country": "US",
        "registration_id": "133541913",
        "bucket": "people",
        "name": {"en": "Teach For America", "ru": "Teach For America"},
        "tagline": {
            "en": "Recruits and trains teachers for under-resourced US schools",
            "ru": "Готовит учителей для недофинансированных школ США",
        },
        "description": {
            "en": (
                "Teach For America is a US 501(c)(3) that recruits "
                "recent college graduates and professionals to teach in "
                "high-need US public schools for at least two years, "
                "with the goal of building a long-term leadership network "
                "addressing educational inequity. ~3,000 corps members "
                "active across ~50 regions; ~70,000 alumni since 1990."
            ),
            "ru": (
                "Teach For America — американская 501(c)(3), готовит "
                "выпускников вузов и профессионалов к работе учителями "
                "в школах с высокой потребностью на 2+ года, чтобы "
                "выстроить долгосрочную сеть лидеров против "
                "образовательного неравенства. Около 3 тыс. участников "
                "в 50 регионах, 70+ тыс. выпускников с 1990 года."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.teachforamerica.org/support-our-work",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("280000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1990,
        "cause_slugs": ["education"],
        **_empty_photo(),
    },
    # ----- Human Rights Watch -----
    {
        "slug": "human-rights-watch",
        "country": "US",
        "registration_id": "132875808",
        "bucket": "people",
        "name": {"en": "Human Rights Watch", "ru": "Human Rights Watch"},
        "tagline": {
            "en": "Investigates and exposes human-rights abuses worldwide",
            "ru": "Расследует и предаёт огласке нарушения прав человека",
        },
        "description": {
            "en": (
                "Human Rights Watch is a US 501(c)(3) that investigates "
                "human-rights abuses in 100+ countries — publishing "
                "rigorous, on-the-ground reporting and pressing "
                "governments and international bodies to enforce "
                "accountability. Refuses government funding to preserve "
                "independence; ~500 staff including local researchers "
                "in many countries."
            ),
            "ru": (
                "Human Rights Watch — американская 501(c)(3), "
                "расследует нарушения прав человека в 100+ странах: "
                "выпускает строгие отчёты, основанные на полевой работе, "
                "и добивается ответственности от правительств и "
                "международных органов. Принципиально не принимает "
                "государственное финансирование. Около 500 сотрудников "
                "включая местных исследователей во многих странах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://donate.hrw.org/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 1, 31),
        "total_revenue_usd": Decimal("110000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1978,
        "cause_slugs": ["civil-rights"],
        **_empty_photo(),
    },
    # ----- ACLU Foundation -----
    {
        "slug": "aclu-foundation",
        "country": "US",
        "registration_id": "136213516",
        "bucket": "people",
        "name": {
            "en": "ACLU Foundation",
            "ru": "Фонд ACLU",
        },
        "tagline": {
            "en": "Litigation and education on US civil liberties",
            "ru": "Судебная защита и просвещение по гражданским правам в США",
        },
        "description": {
            "en": (
                "The ACLU Foundation is a US 501(c)(3) — the litigation "
                "and public-education arm of the American Civil Liberties "
                "Union. Brings constitutional civil-rights cases on free "
                "speech, voting rights, racial justice, immigrants' "
                "rights, LGBTQ+ rights, reproductive rights and "
                "criminal-justice reform across all 50 states and federal "
                "courts. Founded in 1920."
            ),
            "ru": (
                "Фонд ACLU — американская 501(c)(3), судебно-просвети-"
                "тельская часть American Civil Liberties Union. Ведёт "
                "конституционные дела о гражданских правах: свобода "
                "слова, избирательные права, расовая справедливость, "
                "права мигрантов, права ЛГБТК+, репродуктивные права и "
                "реформа уголовной юстиции — во всех 50 штатах и "
                "федеральных судах. Основан в 1920 году."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://action.aclu.org/give/donate-aclu",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("400000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1920,
        "cause_slugs": ["civil-rights"],
        **_empty_photo(),
    },
    # ===================== ANIMALS — 8 new =====================
    # ----- The Donkey Sanctuary (UK) -----
    {
        "slug": "donkey-sanctuary",
        "country": "GB",
        "registration_id": "264818",
        "bucket": "animals",
        "name": {"en": "The Donkey Sanctuary", "ru": "The Donkey Sanctuary"},
        "tagline": {
            "en": "Donkey welfare and rescue — UK and globally",
            "ru": "Защита и спасение ослов — Великобритания и весь мир",
        },
        "description": {
            "en": (
                "The Donkey Sanctuary is a UK-registered charity (Charity "
                "264818) headquartered in Devon. The world's largest "
                "donkey-welfare charity. Operates UK farms and rescue "
                "centres, runs international working-donkey welfare "
                "programmes in 30+ countries, and has campaigned against "
                "the donkey-skin trade for traditional medicine."
            ),
            "ru": (
                "The Donkey Sanctuary — британская благотворительная "
                "организация (Charity 264818) со штабом в Девоне. "
                "Крупнейшая в мире организация защиты ослов: фермы и "
                "центры реабилитации в Великобритании, программы помощи "
                "рабочим ослам в 30+ странах, кампании против торговли "
                "ослиными шкурами для традиционной медицины."
            ),
        },
        "methodology_note": _uk_verify_note(),
        "logo_url": "",
        "donation_url": "https://www.thedonkeysanctuary.org.uk/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 12, 31),
        "total_revenue_usd": Decimal("60000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1969,
        "cause_slugs": [
            "animal-welfare",
            "donkey-welfare",
            "working-animals",
        ],
        **_empty_photo(),
    },
    # ----- Sheldrick Wildlife Trust USA -----
    {
        "slug": "sheldrick-wildlife-trust",
        "country": "US",
        "registration_id": "300224549",
        "bucket": "animals",
        "name": {
            "en": "Sheldrick Wildlife Trust USA",
            "ru": "Sheldrick Wildlife Trust USA",
        },
        "tagline": {
            "en": "Rescues orphaned elephants and rhinos in Kenya",
            "ru": "Спасает осиротевших слонов и носорогов в Кении",
        },
        "description": {
            "en": (
                "Sheldrick Wildlife Trust USA is a US 501(c)(3) that "
                "supports the David Sheldrick Wildlife Trust in Kenya — "
                "famous for its orphan-elephant rescue and rehabilitation "
                "programme in Nairobi National Park. Also funds "
                "anti-poaching aerial and mobile vet units, habitat "
                "preservation and community outreach across Kenya."
            ),
            "ru": (
                "Sheldrick Wildlife Trust USA — американская 501(c)(3), "
                "поддерживает David Sheldrick Wildlife Trust в Кении: "
                "известную программу спасения и реабилитации "
                "осиротевших слонят в Найробийском национальном парке. "
                "Финансирует противобраконьерские воздушные и мобильные "
                "ветеринарные группы, охрану мест обитания и работу "
                "с сообществами в Кении."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.sheldrickwildlifetrust.org/usa/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("18000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2004,
        "cause_slugs": [
            "wildlife-conservation",
            "biodiversity-defense",
            "animal-welfare",
        ],
        **_empty_photo(),
    },
    # ----- Wildlife Alliance -----
    {
        "slug": "wildlife-alliance",
        "country": "US",
        "registration_id": "411533188",
        "bucket": "animals",
        "name": {"en": "Wildlife Alliance", "ru": "Wildlife Alliance"},
        "tagline": {
            "en": "Direct frontline rainforest and wildlife protection",
            "ru": "Прямая защита тропических лесов и диких животных",
        },
        "description": {
            "en": (
                "Wildlife Alliance is a US 501(c)(3) running direct, "
                "on-the-ground rainforest and wildlife protection in "
                "Cambodia and at-risk forest landscapes. Operates the "
                "Wildlife Rapid Rescue Team (anti-trafficking police "
                "support), Cardamom Mountains forest patrols, and the "
                "Phnom Tamao Wildlife Rescue Centre. Heavy focus on "
                "tigers, gibbons and pangolins."
            ),
            "ru": (
                "Wildlife Alliance — американская 501(c)(3), ведёт "
                "прямую полевую защиту тропических лесов и диких "
                "животных в Камбодже и других уязвимых лесных регионах. "
                "Работает Wildlife Rapid Rescue Team (поддержка полиции "
                "против контрабанды), патрули в горах Кардамон и центр "
                "спасения животных Phnom Tamao. Фокус — тигры, гиббоны, "
                "панголины."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.wildlifealliance.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("13000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1995,
        "cause_slugs": [
            "wildlife-conservation",
            "biodiversity-defense",
            "forest-protection",
        ],
        **_empty_photo(),
    },
    # ----- WildAid -----
    {
        "slug": "wildaid",
        "country": "US",
        "registration_id": "200373501",
        "bucket": "animals",
        "name": {"en": "WildAid", "ru": "WildAid"},
        "tagline": {
            "en": "Reduces consumer demand for illegal wildlife products",
            "ru": "Снижает спрос на нелегальные товары из диких животных",
        },
        "description": {
            "en": (
                "WildAid is a US 501(c)(3) with a distinctive theory of "
                "change: 'When the buying stops, the killing can too.' "
                "Runs large-scale public-awareness campaigns in China, "
                "Vietnam and other consumer-market countries to reduce "
                "demand for ivory, rhino horn, shark fin and pangolin "
                "scales. Documented impact: ~70% drop in shark-fin "
                "consumption in mainland China."
            ),
            "ru": (
                "WildAid — американская 501(c)(3) с особой теорией "
                "изменений: «Когда покупки прекращаются, убийства тоже». "
                "Ведёт масштабные публичные кампании в Китае, Вьетнаме "
                "и других странах-потребителях для снижения спроса на "
                "слоновую кость, рог носорога, акульи плавники и чешую "
                "панголина. Подтверждённое снижение потребления акульих "
                "плавников в континентальном Китае примерно на 70%."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://wildaid.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("18000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2000,
        "cause_slugs": [
            "wildlife-conservation",
            "demand-reduction",
            "biodiversity-defense",
        ],
        **_empty_photo(),
    },
    # ----- Sea Shepherd Conservation Society -----
    {
        "slug": "sea-shepherd",
        "country": "US",
        "registration_id": "953923077",
        "bucket": "animals",
        "name": {
            "en": "Sea Shepherd Conservation Society",
            "ru": "Sea Shepherd Conservation Society",
        },
        "tagline": {
            "en": "Direct-action marine wildlife defence at sea",
            "ru": "Прямые действия по защите морских животных в открытом море",
        },
        "description": {
            "en": (
                "Sea Shepherd Conservation Society is a US 501(c)(3) "
                "running direct-action marine-wildlife-protection "
                "campaigns at sea: anti-poaching patrols (often in "
                "partnership with national coast guards in the Gulf of "
                "Mexico, West Africa, Pacific), abandoned-net retrieval, "
                "and documenting illegal whaling and totoaba/vaquita "
                "operations."
            ),
            "ru": (
                "Sea Shepherd Conservation Society — американская "
                "501(c)(3), ведёт кампании прямых действий по защите "
                "морских животных в открытом море: антибраконьерские "
                "патрули (часто совместно с береговыми службами стран "
                "в Мексиканском заливе, Западной Африке, Тихом океане), "
                "сбор брошенных сетей, документирование нелегального "
                "китобойного промысла и операций тотоаба/вакита."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.seashepherd.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("12000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1977,
        "cause_slugs": [
            "marine-life",
            "ocean-protection",
            "wildlife-conservation",
        ],
        **_empty_photo(),
    },
    # ----- Performing Animal Welfare Society (PAWS) -----
    {
        "slug": "paws-sanctuary",
        "country": "US",
        "registration_id": "942681680",
        "bucket": "animals",
        "name": {
            "en": "Performing Animal Welfare Society (PAWS)",
            "ru": "Performing Animal Welfare Society (PAWS)",
        },
        "tagline": {
            "en": "Sanctuary for retired captive elephants, big cats and bears",
            "ru": "Приют для слонов, крупных кошек и медведей из неволи",
        },
        "description": {
            "en": (
                "Performing Animal Welfare Society (PAWS) is a US "
                "501(c)(3) running ARK 2000 — a 2,300-acre sanctuary in "
                "California that retires elephants, big cats, bears and "
                "other large animals from circuses, zoos, and the "
                "entertainment industry. Provides species-appropriate "
                "habitats and lifetime veterinary care; advocates "
                "against captive-elephant performance."
            ),
            "ru": (
                "Performing Animal Welfare Society (PAWS) — американская "
                "501(c)(3), управляет ARK 2000 — приютом площадью "
                "около 930 га в Калифорнии: пожизненный уход за слонами, "
                "крупными кошками, медведями и другими крупными "
                "животными, освобождёнными из цирков, зоопарков и "
                "индустрии развлечений. Среды обитания, "
                "соответствующие видам, и пожизненная ветпомощь."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.pawsweb.org/donate.html",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1984,
        "cause_slugs": ["animal-welfare"],
        **_empty_photo(),
    },
    # ----- The Brooke (UK) -----
    {
        "slug": "the-brooke",
        "country": "GB",
        "registration_id": "1085760",
        "bucket": "animals",
        "name": {
            "en": "Brooke Action for Working Horses and Donkeys",
            "ru": "Brooke — помощь рабочим лошадям и ослам",
        },
        "tagline": {
            "en": "Welfare for working equines in low-income countries",
            "ru": "Защита рабочих лошадей и ослов в странах с низкими доходами",
        },
        "description": {
            "en": (
                "Brooke Action for Working Horses and Donkeys is a UK-"
                "registered charity (Charity 1085760) operating in 11+ "
                "low-income countries to improve the welfare of working "
                "horses, donkeys and mules — animals whose labour "
                "supports an estimated 600M people in informal economies. "
                "Trains farriers, vets and owners, and runs mobile "
                "veterinary clinics."
            ),
            "ru": (
                "Brooke — британская благотворительная организация "
                "(Charity 1085760), работает в 11+ странах с низкими "
                "доходами, чтобы улучшить условия рабочих лошадей, ослов "
                "и мулов, чей труд поддерживает около 600 млн человек в "
                "неформальной экономике. Обучает кузнецов, ветеринаров и "
                "владельцев, ведёт мобильные ветеринарные клиники."
            ),
        },
        "methodology_note": _uk_verify_note(),
        "logo_url": "",
        "donation_url": "https://www.thebrooke.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1934,
        "cause_slugs": [
            "animal-welfare",
            "working-animals",
        ],
        **_empty_photo(),
    },
    # ----- Compassion in World Farming (UK) -----
    {
        "slug": "ciwf",
        "country": "GB",
        "registration_id": "1095050",
        "bucket": "animals",
        "name": {
            "en": "Compassion in World Farming",
            "ru": "Compassion in World Farming",
        },
        "tagline": {
            "en": "Ends factory farming through investigation and policy",
            "ru": "Прекращает промышленное животноводство через расследования и политику",
        },
        "description": {
            "en": (
                "Compassion in World Farming (CIWF) is a UK-registered "
                "charity (Charity 1095050) that campaigns to end factory "
                "farming. Conducts undercover investigations of intensive "
                "livestock systems, lobbies for higher animal-welfare "
                "standards in EU/UK/US legislation, and pressures food "
                "companies to source from higher-welfare supply chains. "
                "Founded by a UK dairy farmer in 1967."
            ),
            "ru": (
                "Compassion in World Farming (CIWF) — британская "
                "благотворительная организация (Charity 1095050), "
                "ведёт кампанию против промышленного животноводства. "
                "Проводит расследования в системах интенсивного "
                "животноводства, лоббирует более высокие стандарты "
                "защиты животных в законах ЕС/Великобритании/США и "
                "давит на пищевые компании, чтобы они закупали продукцию "
                "у поставщиков с более высокими стандартами. Основана "
                "британским молочным фермером в 1967 году."
            ),
        },
        "methodology_note": _uk_verify_note(),
        "logo_url": "",
        "donation_url": "https://www.ciwf.org.uk/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 12, 31),
        "total_revenue_usd": Decimal("16000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1967,
        "cause_slugs": ["animal-welfare"],
        **_empty_photo(),
    },
    # ===================== PLANET — 12 new =====================
    # ----- Project Drawdown -----
    {
        "slug": "project-drawdown",
        "country": "US",
        "registration_id": "464982110",
        "bucket": "planet",
        "name": {"en": "Project Drawdown", "ru": "Project Drawdown"},
        "tagline": {
            "en": "Models and accelerates the most viable climate solutions",
            "ru": "Моделирует и ускоряет самые жизнеспособные климатические решения",
        },
        "description": {
            "en": (
                "Project Drawdown is a US 501(c)(3) climate-research "
                "organisation that maintains a public, peer-reviewed "
                "database ranking ~100 climate solutions by their "
                "potential to draw down atmospheric greenhouse-gas levels "
                "(food systems, electricity, land sinks, transport, "
                "buildings, materials). Used by funders, governments and "
                "companies for climate-strategy planning."
            ),
            "ru": (
                "Project Drawdown — американская 501(c)(3), "
                "климатическая исследовательская организация, ведёт "
                "публичную рецензируемую базу примерно 100 решений по "
                "снижению парниковых газов (продовольственные системы, "
                "электричество, поглотители углерода, транспорт, "
                "здания, материалы). Используется фондами, "
                "правительствами и компаниями для планирования "
                "климатической стратегии."
            ),
        },
        "methodology_note": _verify_note(
            "Peer-reviewed climate-solution database.",
            "Рецензируемая база решений по климату.",
        ),
        "logo_url": "",
        "donation_url": "https://drawdown.org/donate",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("9500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 2014,
        "cause_slugs": ["climate", "climate-policy"],
        **_empty_photo(),
    },
    # ----- ClimateWorks Foundation -----
    {
        "slug": "climateworks-foundation",
        "country": "US",
        "registration_id": "260588550",
        "bucket": "planet",
        "name": {
            "en": "ClimateWorks Foundation",
            "ru": "ClimateWorks Foundation",
        },
        "tagline": {
            "en": "Re-grants climate philanthropy to high-leverage strategies",
            "ru": "Перераспределяет климатическую филантропию в эффективные стратегии",
        },
        "description": {
            "en": (
                "ClimateWorks Foundation is a US 501(c)(3) re-granting "
                "intermediary that pools and channels climate philanthropy "
                "to high-leverage strategies in the energy transition, "
                "transport decarbonisation, food and land use, "
                "industrial materials and short-lived climate pollutants. "
                "Acts as a research and coordination hub for climate "
                "funders globally."
            ),
            "ru": (
                "ClimateWorks Foundation — американская 501(c)(3), "
                "посредник по перераспределению грантов: объединяет и "
                "направляет климатическую филантропию в эффективные "
                "стратегии — энергопереход, декарбонизация транспорта, "
                "продовольствие и землепользование, промышленные "
                "материалы и короткоживущие климатические загрязнители. "
                "Координирующий и исследовательский центр для "
                "климатических доноров по миру."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.climateworks.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("420000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2008,
        "cause_slugs": ["climate", "climate-policy", "environment"],
        **_empty_photo(),
    },
    # ----- Friends of the Earth -----
    {
        "slug": "friends-of-the-earth",
        "country": "US",
        "registration_id": "237420660",
        "bucket": "planet",
        "name": {
            "en": "Friends of the Earth (US)",
            "ru": "Friends of the Earth (US)",
        },
        "tagline": {
            "en": "Environmental advocacy on climate and corporate accountability",
            "ru": "Экологическая работа: климат и корпоративная ответственность",
        },
        "description": {
            "en": (
                "Friends of the Earth (US) is a US 501(c)(3) "
                "environmental advocacy organisation campaigning on "
                "climate, ocean, food and tech policy. US member of the "
                "Friends of the Earth International federation, which "
                "operates in 70+ countries. Known for shareholder "
                "advocacy and litigation against environmentally harmful "
                "federal policies and large corporations."
            ),
            "ru": (
                "Friends of the Earth (US) — американская 501(c)(3), "
                "экологическая организация: кампании по климату, океану, "
                "продовольствию и технологиям. Член федерации Friends of "
                "the Earth International (70+ стран). Известна работой с "
                "акционерами и судами против вредных для окружающей "
                "среды федеральных политик и крупных корпораций."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://act.foe.org/donate/foe-donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("18000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1969,
        "cause_slugs": ["environment", "climate-policy"],
        **_empty_photo(),
    },
    # ----- Center for Biological Diversity -----
    {
        "slug": "center-for-biological-diversity",
        "country": "US",
        "registration_id": "270266467",
        "bucket": "planet",
        "name": {
            "en": "Center for Biological Diversity",
            "ru": "Center for Biological Diversity",
        },
        "tagline": {
            "en": "Litigation-driven defense of endangered species",
            "ru": "Судебная защита видов под угрозой исчезновения",
        },
        "description": {
            "en": (
                "The Center for Biological Diversity is a US 501(c)(3) "
                "that uses petitions and lawsuits — primarily under the "
                "Endangered Species Act and other US environmental law — "
                "to compel federal protection of imperiled species and "
                "their habitats. Has secured Endangered Species Act "
                "protection for hundreds of species since 1989."
            ),
            "ru": (
                "Center for Biological Diversity — американская "
                "501(c)(3), использует петиции и иски — в основном по "
                "Endangered Species Act и другим экологическим законам "
                "США — для принудительной федеральной защиты видов под "
                "угрозой и их мест обитания. С 1989 года добилась "
                "защиты по ESA для сотен видов."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://support.biologicaldiversity.org/a/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1989,
        "cause_slugs": [
            "biodiversity-defense",
            "wildlife-conservation",
            "environment",
        ],
        **_empty_photo(),
    },
    # ----- Surfrider Foundation -----
    {
        "slug": "surfrider-foundation",
        "country": "US",
        "registration_id": "953941826",
        "bucket": "planet",
        "name": {"en": "Surfrider Foundation", "ru": "Surfrider Foundation"},
        "tagline": {
            "en": "Grassroots ocean and coastal protection across US beaches",
            "ru": "Низовая защита океана и побережий США",
        },
        "description": {
            "en": (
                "Surfrider Foundation is a US 501(c)(3) grassroots "
                "environmental network protecting the world's oceans, "
                "waves and beaches via ~80 volunteer-led chapters across "
                "the United States. Programmes target plastic pollution, "
                "ocean protection, beach access, water quality and "
                "coastal climate adaptation — combining citizen science "
                "with policy advocacy."
            ),
            "ru": (
                "Surfrider Foundation — американская 501(c)(3), низовая "
                "экологическая сеть, защищает океан, волны и пляжи мира "
                "через около 80 волонтёрских отделений по США. "
                "Программы: пластиковое загрязнение, защита океана, "
                "доступ к пляжам, качество воды, адаптация прибрежных "
                "зон к климату — сочетание гражданской науки и работы "
                "над политикой."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.surfrider.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("14000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1984,
        "cause_slugs": [
            "ocean-protection",
            "marine-life",
            "environment",
        ],
        **_empty_photo(),
    },
    # ----- Rainforest Action Network -----
    {
        "slug": "rainforest-action-network",
        "country": "US",
        "registration_id": "943045180",
        "bucket": "planet",
        "name": {
            "en": "Rainforest Action Network",
            "ru": "Rainforest Action Network",
        },
        "tagline": {
            "en": "Pressures banks and corporations on rainforest destruction",
            "ru": "Давит на банки и корпорации против уничтожения тропических лесов",
        },
        "description": {
            "en": (
                "Rainforest Action Network (RAN) is a US 501(c)(3) that "
                "pressures banks, corporations and policymakers to stop "
                "financing tropical-forest destruction (palm oil, pulp, "
                "fossil fuels). Annual 'Banking on Climate Chaos' "
                "report tracks bank financing of fossil fuels and "
                "deforestation; campaigns target supply-chain deforestation "
                "in consumer goods."
            ),
            "ru": (
                "Rainforest Action Network (RAN) — американская "
                "501(c)(3), давит на банки, корпорации и политиков, "
                "чтобы остановить финансирование вырубки тропических "
                "лесов (пальмовое масло, целлюлоза, ископаемое топливо). "
                "Ежегодный отчёт 'Banking on Climate Chaos' отслеживает "
                "банковское финансирование ископаемого топлива и "
                "обезлесения. Кампании по обезлесению в цепочках "
                "поставок потребтоваров."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.ran.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("11000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1985,
        "cause_slugs": [
            "forest-protection",
            "climate-policy",
            "environment",
        ],
        **_empty_photo(),
    },
    # ----- The Wilderness Society -----
    {
        "slug": "wilderness-society",
        "country": "US",
        "registration_id": "530167933",
        "bucket": "planet",
        "name": {"en": "The Wilderness Society", "ru": "The Wilderness Society"},
        "tagline": {
            "en": "Protects US public lands and wilderness areas",
            "ru": "Защищает общественные земли и заповедники США",
        },
        "description": {
            "en": (
                "The Wilderness Society is a US 501(c)(3) that protects "
                "wild public lands across the United States. Helped "
                "draft the 1964 Wilderness Act, has supported the "
                "designation of 110+ million acres of wilderness, and "
                "advocates for the protection of US national monuments, "
                "forests and BLM lands from drilling, logging and "
                "extractive development."
            ),
            "ru": (
                "The Wilderness Society — американская 501(c)(3), "
                "защищает дикие общественные земли США. Участвовала в "
                "разработке Wilderness Act 1964 года, способствовала "
                "присвоению статуса заповедной территории более чем 110 "
                "млн акров и отстаивает защиту национальных памятников, "
                "лесов и земель BLM от бурения, вырубки и добычи "
                "ресурсов."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://act.wilderness.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("38000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1935,
        "cause_slugs": [
            "land-conservation",
            "biodiversity-defense",
            "environment",
        ],
        **_empty_photo(),
    },
    # ----- League of Conservation Voters Education Fund -----
    {
        "slug": "lcv-education-fund",
        "country": "US",
        "registration_id": "521823083",
        "bucket": "planet",
        "name": {
            "en": "League of Conservation Voters Education Fund",
            "ru": "League of Conservation Voters Education Fund",
        },
        "tagline": {
            "en": "Civic education on environmental policy and voting records",
            "ru": "Гражданское просвещение по экологической политике",
        },
        "description": {
            "en": (
                "The LCV Education Fund is a US 501(c)(3) that educates "
                "the public on environmental policy and tracks Congress's "
                "votes on environmental legislation through the National "
                "Environmental Scorecard. Sister 501(c)(4) (LCV) handles "
                "lobbying; the Education Fund focuses on non-partisan "
                "voter and policymaker education."
            ),
            "ru": (
                "LCV Education Fund — американская 501(c)(3), просвещает "
                "общественность по экологической политике и отслеживает "
                "голосования Конгресса США по экологическим законам "
                "через National Environmental Scorecard. Сестринская "
                "501(c)(4) (LCV) ведёт лоббирование; Education Fund "
                "сосредоточен на беспартийном просвещении избирателей "
                "и политиков."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.lcv.org/donate-to-lcv-education-fund/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("28000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1985,
        "cause_slugs": ["climate-policy", "environment", "civil-rights"],
        **_empty_photo(),
    },
    # ----- Forest Stewardship Council US -----
    {
        "slug": "fsc-us",
        "country": "US",
        "registration_id": "522098212",
        "bucket": "planet",
        "name": {
            "en": "Forest Stewardship Council US",
            "ru": "Forest Stewardship Council US",
        },
        "tagline": {
            "en": "Sets and certifies responsible-forestry standards",
            "ru": "Устанавливает и сертифицирует стандарты ответственного лесопользования",
        },
        "description": {
            "en": (
                "Forest Stewardship Council US is a US 501(c)(3) — the "
                "national body of the FSC global forest-certification "
                "system. Develops the US-specific FSC standard and "
                "supports certified forest managers, manufacturers and "
                "retailers. FSC certifies ~150M hectares globally; the "
                "FSC label is the most widely respected mark for "
                "responsibly sourced wood and paper."
            ),
            "ru": (
                "Forest Stewardship Council US — американская 501(c)(3), "
                "национальный орган глобальной системы сертификации FSC. "
                "Разрабатывает американский стандарт FSC и поддерживает "
                "сертифицированных лесоуправляющих, производителей и "
                "розничные сети. FSC сертифицирует около 150 млн "
                "гектаров по миру; знак FSC — самый авторитетный для "
                "ответственно заготовленных древесины и бумаги."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://us.fsc.org/en-us/get-involved/donate",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4800000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1995,
        "cause_slugs": [
            "forest-protection",
            "environment",
            "biodiversity-defense",
        ],
        **_empty_photo(),
    },
    # ----- Pesticide Action Network North America -----
    {
        "slug": "pan-na",
        "country": "US",
        "registration_id": "942961165",
        "bucket": "planet",
        "name": {
            "en": "Pesticide Action Network North America",
            "ru": "Pesticide Action Network North America",
        },
        "tagline": {
            "en": "Advances safer alternatives to hazardous pesticides",
            "ru": "Развивает безопасные альтернативы опасным пестицидам",
        },
        "description": {
            "en": (
                "Pesticide Action Network North America (PANNA) is a US "
                "501(c)(3), the regional centre of the international PAN "
                "network. Works with farmers, scientists and rural "
                "communities to phase out the most hazardous pesticides "
                "and to advance ecological farming alternatives. "
                "Documents pesticide drift impacts on farmworker and "
                "rural-community health."
            ),
            "ru": (
                "Pesticide Action Network North America (PANNA) — "
                "американская 501(c)(3), региональный центр международной "
                "сети PAN. Работает с фермерами, учёными и сельскими "
                "сообществами, чтобы вывести из обращения самые опасные "
                "пестициды и продвигать экологические альтернативы. "
                "Документирует влияние сноса пестицидов на здоровье "
                "сельхозработников и сельских жителей."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.panna.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("3200000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1982,
        "cause_slugs": ["environment", "biodiversity-defense"],
        **_empty_photo(),
    },
    # ----- 5 Gyres Institute -----
    {
        "slug": "five-gyres",
        "country": "US",
        "registration_id": "271809845",
        "bucket": "planet",
        "name": {"en": "5 Gyres Institute", "ru": "5 Gyres Institute"},
        "tagline": {
            "en": "Science-based fight against ocean plastic pollution",
            "ru": "Научная борьба с пластиковым загрязнением океана",
        },
        "description": {
            "en": (
                "5 Gyres Institute is a US 501(c)(3) focused on "
                "plastic-pollution research and advocacy. Conducted the "
                "first global ocean-plastic surveys (estimating ~270K "
                "tonnes floating in oceans), runs citizen-science "
                "expeditions, and lobbied for the US Microbead-Free "
                "Waters Act of 2015 banning plastic microbeads in "
                "personal-care products."
            ),
            "ru": (
                "5 Gyres Institute — американская 501(c)(3), занимается "
                "исследованиями и работой против пластикового "
                "загрязнения океана. Провели первые глобальные оценки "
                "морского пластика (около 270 тыс. тонн на поверхности "
                "океанов), ведут гражданские научные экспедиции, "
                "лоббировали закон США 2015 года о запрете "
                "микропластика в косметике."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.5gyres.org/donate",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("1200000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2009,
        "cause_slugs": [
            "ocean-protection",
            "environment",
            "marine-life",
        ],
        **_empty_photo(),
    },
    # ----- Earthworks -----
    {
        "slug": "earthworks",
        "country": "US",
        "registration_id": "521557765",
        "bucket": "planet",
        "name": {"en": "Earthworks", "ru": "Earthworks"},
        "tagline": {
            "en": "Protects communities from mining and oil & gas impacts",
            "ru": "Защищает сообщества от воздействия добычи и нефтегаза",
        },
        "description": {
            "en": (
                "Earthworks is a US 501(c)(3) that supports communities "
                "and Indigenous nations facing impacts from hard-rock "
                "mining and oil & gas extraction. Combines field "
                "documentation (including infrared imaging of methane "
                "leaks), litigation support, and federal-mining-law "
                "reform advocacy. Works on US public lands and the "
                "global mineral-supply chain."
            ),
            "ru": (
                "Earthworks — американская 501(c)(3), поддерживает "
                "сообщества и коренные народы, пострадавшие от "
                "горнодобычи и нефтегаза. Сочетает полевую "
                "документацию (включая инфракрасную съёмку утечек "
                "метана), юридическую поддержку и работу над реформой "
                "федерального горного законодательства США. Работает на "
                "общественных землях США и в глобальной цепочке "
                "минералов."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://earthworks.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("6500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1988,
        "cause_slugs": [
            "environment",
            "biodiversity-defense",
            "climate-policy",
        ],
        **_empty_photo(),
    },
]


def _financial_row(entry: dict) -> dict:
    """Build the single Financial row for an entry, matching 0021's shape."""
    if entry["country"] == "US":
        source_url = _us_propublica_url(entry["registration_id"])
        source_label = "IRS Form 990, FY 2023 (ProPublica)"
    else:
        source_url = _uk_charity_url(entry["registration_id"])
        source_label = "Annual report & accounts (Charity Commission UK)"
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
    if entry["country"] == "US":
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
    return {
        "kind": "annual_report",
        "filed_date": entry["last_filed_date"],
        "label": {
            "en": "Annual report & accounts (FY 2023)",
            "ru": "Годовой отчёт и финансовая отчётность (2023)",
        },
        "url": _uk_charity_url(entry["registration_id"]),
        "source_label": "Charity Commission UK — accounts page",
        "file_format": "html",
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
                f"[migration 0025] BLOCKED {entry['slug']} "
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
        f"[migration 0025] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total_charities}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0024_propublica_download_to_overview"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

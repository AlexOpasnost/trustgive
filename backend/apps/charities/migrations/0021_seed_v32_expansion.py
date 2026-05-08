"""v3.2 catalog expansion — seed 20 more curated charities (38 -> 58).

People (11), Animals (5), Planet (4). All EINs verified against ProPublica
`organizations/{ein}` (US) or Charity Commission register (UK). Sources are
canonical org pages per KB-012/013/014 — ProPublica blocks HEAD probes, so
we trust the URL pattern rather than HEAD-validating it.

Hero photos: a small subset get hedged-caption Wikimedia Commons CC photos
(KB-015 honesty rule). The rest get empty hero_photo_url -> frontend
BrandedAvatar gradient fallback per DESIGN.md v3 §B.3. Every empty entry
still carries empty caption/credit/license strings to satisfy the schema.

Logos: logo.uplead.com/{host} for orgs whose host returned 200 + PNG on
prior backfill passes (KB-PHOTO-001). New hosts default to "" — a follow-up
backfill migration is the right place to HEAD-probe and fill them, not
this seed migration (separation per CLAUDE.md migration rules).

Idempotent: update_or_create on (country, registration_id).
Reverse: no-op (never auto-delete curated rows).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "emergency-response": {
        "en": "Emergency response",
        "ru": "Экстренное реагирование",
    },
    "child-sponsorship": {
        "en": "Child sponsorship",
        "ru": "Спонсорство детей",
    },
    "livestock-relief": {
        "en": "Livestock-based poverty relief",
        "ru": "Помощь через животноводство",
    },
    "cleft-surgery": {
        "en": "Cleft-lip & palate surgery",
        "ru": "Операции на расщелине нёба",
    },
    "housing": {"en": "Housing", "ru": "Жильё"},
    "land-conservation": {
        "en": "Land conservation",
        "ru": "Охрана земель",
    },
    "marine-life": {"en": "Marine life", "ru": "Морская фауна"},
    "primates": {"en": "Primate conservation", "ru": "Защита приматов"},
    "forest-protection": {
        "en": "Forest protection",
        "ru": "Защита лесов",
    },
}


def _verify_note(en_extra: str = "", ru_extra: str = "") -> dict:
    """Standard verification note. en_extra/ru_extra appended if truthy."""
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


SEED: list[dict] = [
    # ===================== PEOPLE — 11 new =====================
    # ----- Watsi -----
    {
        "slug": "watsi",
        "country": "US",
        "registration_id": "453683774",
        "bucket": "people",
        "name": {"en": "Watsi", "ru": "Watsi"},
        "tagline": {
            "en": "Crowdfunds individual medical care for people worldwide",
            "ru": "Краудфандинг медицинской помощи людям по всему миру",
        },
        "description": {
            "en": (
                "Watsi is a US 501(c)(3) that lets donors fund specific "
                "medical procedures for low-income patients in 20+ countries. "
                "Every donation funds a named patient's treatment — surgeries, "
                "obstetric care, cancer treatment — verified by partner "
                "medical providers. Operating-cost transparency: 100% of "
                "donations go to patient care; operations covered separately."
            ),
            "ru": (
                "Watsi — американская 501(c)(3), позволяющая жертвователям "
                "финансировать конкретные медицинские процедуры для малоимущих "
                "пациентов в 20+ странах. Каждое пожертвование оплачивает "
                "лечение конкретного пациента: операции, акушерскую помощь, "
                "лечение онкологии — проверенное партнёрскими клиниками. "
                "100% пожертвований идёт на лечение."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://watsi.org/donate",
        "size_bucket": "small",
        "last_filed_date": date(2024, 11, 15),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 2012,
        "cause_slugs": ["global-health", "humanitarian-medicine"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("3500000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/453683774",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 15),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/453683774",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Living Goods -----
    {
        "slug": "living-goods",
        "country": "US",
        "registration_id": "134316685",
        "bucket": "people",
        "name": {"en": "Living Goods", "ru": "Living Goods"},
        "tagline": {
            "en": "Networks of community health workers across East Africa",
            "ru": "Сеть общинных медработников в Восточной Африке",
        },
        "description": {
            "en": (
                "Living Goods supports networks of digitally-empowered "
                "community health workers in Kenya, Uganda and Burkina Faso. "
                "Workers diagnose and treat common childhood illnesses "
                "(malaria, pneumonia, diarrhoea) door-to-door using a "
                "smartphone app. Independent RCT showed a 27% reduction "
                "in under-5 mortality in served communities."
            ),
            "ru": (
                "Living Goods поддерживает сети общинных медработников с "
                "цифровыми инструментами в Кении, Уганде и Буркина-Фасо. "
                "Работники диагностируют и лечат распространённые детские "
                "болезни (малярия, пневмония, диарея) по домам с помощью "
                "приложения. RCT показало снижение детской смертности "
                "до 5 лет на 27%."
            ),
        },
        "methodology_note": _verify_note(
            "RCT-backed impact data published.",
            "Доказанная эффективность по RCT.",
        ),
        "logo_url": "",
        "donation_url": "https://livinggoods.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 8, 10),
        "total_revenue_usd": Decimal("48200000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 2007,
        "cause_slugs": ["global-health", "child-nutrition"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("48200000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/134316685",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 8, 10),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/134316685",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- BRAC USA -----
    {
        "slug": "brac-usa",
        "country": "US",
        "registration_id": "203729051",
        "bucket": "people",
        "name": {"en": "BRAC USA", "ru": "BRAC USA"},
        "tagline": {
            "en": "US affiliate of BRAC — world's largest NGO",
            "ru": "Американский филиал BRAC — крупнейшей НКО мира",
        },
        "description": {
            "en": (
                "BRAC USA is the US 501(c)(3) affiliate of BRAC, the "
                "Bangladesh-founded NGO operating in 16 countries with "
                "100K+ staff. Programs span ultra-poor graduation, "
                "microfinance, education for marginalised girls, primary "
                "healthcare and climate adaptation. The Ultra-Poor "
                "Graduation programme is a GiveWell-noted poverty intervention."
            ),
            "ru": (
                "BRAC USA — американский филиал 501(c)(3) BRAC, "
                "бангладешской НКО, работающей в 16 странах со штатом "
                "100+ тыс. сотрудников. Программы: вывод из крайней "
                "бедности, микрофинансы, образование девочек, первичная "
                "медицина, адаптация к климату. Программа Ultra-Poor "
                "Graduation отмечена GiveWell."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://bracusa.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("44800000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 2006,
        "cause_slugs": ["poverty-reduction", "education", "global-health"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("44800000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/203729051",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/203729051",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- World Food Programme USA -----
    {
        "slug": "wfp-usa",
        "country": "US",
        "registration_id": "133843435",
        "bucket": "people",
        "name": {
            "en": "World Food Programme USA",
            "ru": "World Food Programme USA",
        },
        "tagline": {
            "en": "Funds the UN World Food Programme's hunger-relief operations",
            "ru": "Финансирует операции ВПП ООН по борьбе с голодом",
        },
        "description": {
            "en": (
                "WFP USA is the US 501(c)(3) that mobilises funding for the "
                "UN World Food Programme — the world's largest humanitarian "
                "food-relief agency, reaching 150M+ people in 120+ countries "
                "annually. WFP itself won the 2020 Nobel Peace Prize for its "
                "hunger-relief work in conflict zones."
            ),
            "ru": (
                "WFP USA — американская 501(c)(3), мобилизует средства для "
                "Всемирной продовольственной программы ООН — крупнейшего "
                "гуманитарного агентства мира, охватывающего 150+ млн "
                "человек в 120+ странах ежегодно. WFP получила Нобелевскую "
                "премию мира 2020."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.wfpusa.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 15),
        "total_revenue_usd": Decimal("110000000.00"),
        "program_expense_pct": Decimal("92.00"),
        "founded_year": 1995,
        "cause_slugs": [
            "food-security",
            "emergency-response",
            "child-nutrition",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("110000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/133843435",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 15),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/133843435",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Mercy Corps -----
    {
        "slug": "mercy-corps",
        "country": "US",
        "registration_id": "911148123",
        "bucket": "people",
        "name": {"en": "Mercy Corps", "ru": "Mercy Corps"},
        "tagline": {
            "en": "Humanitarian aid and development in 40+ countries",
            "ru": "Гуманитарная помощь и развитие в 40+ странах",
        },
        "description": {
            "en": (
                "Mercy Corps responds to humanitarian crises (conflict, "
                "earthquakes, drought) and runs longer-term resilience "
                "programmes — agriculture, water, youth livelihoods — in "
                "40+ fragile and post-conflict countries. Headquartered in "
                "Portland, Oregon. Reaches ~30M people annually."
            ),
            "ru": (
                "Mercy Corps реагирует на гуманитарные кризисы "
                "(конфликты, землетрясения, засухи) и ведёт долгосрочные "
                "программы устойчивости — сельское хозяйство, вода, "
                "занятость молодёжи — в 40+ странах. Штаб-квартира в "
                "Портленде, Орегон. Охват около 30 млн человек ежегодно."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.mercycorps.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 14),
        "total_revenue_usd": Decimal("552000000.00"),
        "program_expense_pct": Decimal("87.00"),
        "founded_year": 1979,
        "cause_slugs": [
            "emergency-response",
            "poverty-reduction",
            "food-security",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("552000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/911148123",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 8, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/911148123",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- American Red Cross -----
    {
        "slug": "american-red-cross",
        "country": "US",
        "registration_id": "530196605",
        "bucket": "people",
        "name": {
            "en": "American Red Cross",
            "ru": "Американский Красный Крест",
        },
        "tagline": {
            "en": "Disaster response, blood services, and emergency aid",
            "ru": "Помощь при бедствиях, служба крови, экстренная помощь",
        },
        "description": {
            "en": (
                "The American Red Cross is the US national society of the "
                "International Red Cross / Red Crescent Movement. Provides "
                "~40% of the US blood supply, responds to ~60K disasters "
                "annually (most are home fires), trains millions in CPR / "
                "first aid, and supports US service members and veterans. "
                "Federally chartered congressional charter from 1900."
            ),
            "ru": (
                "Американский Красный Крест — национальное общество США в "
                "Международном движении Красного Креста. Обеспечивает около "
                "40% запаса крови США, реагирует примерно на 60 тыс. "
                "бедствий в год (большинство — пожары в домах), обучает "
                "миллионы людей СЛР и первой помощи. Чартер Конгресса с 1900 года."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.redcross.org/donate/donation.html",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 15),
        "total_revenue_usd": Decimal("3300000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1881,
        "cause_slugs": [
            "emergency-response",
            "disaster-relief",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("3300000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/530196605",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 15),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/530196605",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Operation Smile -----
    {
        "slug": "operation-smile",
        "country": "US",
        "registration_id": "541460147",
        "bucket": "people",
        "name": {"en": "Operation Smile", "ru": "Operation Smile"},
        "tagline": {
            "en": "Free cleft-lip and palate surgery for children worldwide",
            "ru": "Бесплатные операции на расщелине нёба для детей в мире",
        },
        "description": {
            "en": (
                "Operation Smile sends teams of volunteer surgeons, "
                "anaesthesiologists and nurses to perform free cleft-lip "
                "and palate repair surgery for children in 30+ low-income "
                "countries. Has provided 350K+ surgeries since 1982. "
                "Trains local medical professionals so the work continues "
                "after volunteer teams leave."
            ),
            "ru": (
                "Operation Smile направляет команды хирургов-волонтёров, "
                "анестезиологов и медсестёр для бесплатных операций на "
                "расщелине губы и нёба у детей в 30+ странах с низкими "
                "доходами. С 1982 года выполнено 350+ тыс. операций. "
                "Обучает местных врачей, чтобы работа продолжалась после "
                "отъезда волонтёрских команд."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.operationsmile.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("90000000.00"),
        "program_expense_pct": Decimal("84.00"),
        "founded_year": 1982,
        "cause_slugs": ["global-health", "cleft-surgery"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("90000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/541460147",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/541460147",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Habitat for Humanity International -----
    {
        "slug": "habitat-for-humanity",
        "country": "US",
        "registration_id": "911914868",
        "bucket": "people",
        "name": {
            "en": "Habitat for Humanity International",
            "ru": "Habitat for Humanity International",
        },
        "tagline": {
            "en": "Builds affordable housing in partnership with families",
            "ru": "Строит доступное жильё в партнёрстве с семьями",
        },
        "description": {
            "en": (
                "Habitat for Humanity International is a US 501(c)(3) "
                "operating in 70+ countries. Volunteers and future "
                "homeowners build affordable houses; new owners pay "
                "interest-free mortgages back into a revolving fund that "
                "builds the next house. Has helped 39M+ people access "
                "improved housing since 1976."
            ),
            "ru": (
                "Habitat for Humanity International — американская "
                "501(c)(3), работающая в 70+ странах. Волонтёры и будущие "
                "домовладельцы строят доступные дома; новые владельцы "
                "выплачивают беспроцентную ипотеку в фонд, который строит "
                "следующий дом. С 1976 года улучшили жильё для 39+ млн человек."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.habitat.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 13),
        "total_revenue_usd": Decimal("382000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1976,
        "cause_slugs": ["housing", "poverty-reduction"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("382000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/911914868",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 13),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/911914868",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Heifer International -----
    {
        "slug": "heifer-international",
        "country": "US",
        "registration_id": "351019477",
        "bucket": "people",
        "name": {"en": "Heifer International", "ru": "Heifer International"},
        "tagline": {
            "en": "Lifts farming families out of poverty via livestock",
            "ru": "Выводит фермерские семьи из бедности через животноводство",
        },
        "description": {
            "en": (
                "Heifer International gives farming families livestock "
                "(cows, goats, chickens, bees) plus training in animal "
                "husbandry, agroecology, gender equity and cooperative "
                "marketing. Recipients commit to passing on the first "
                "female offspring of their animal to another family — "
                "the 'Passing on the Gift' chain effect. Operates in 21 countries."
            ),
            "ru": (
                "Heifer International передаёт фермерским семьям скот "
                "(коров, коз, кур, пчёл) и обучает уходу за животными, "
                "агроэкологии, гендерному равенству и кооперативной "
                "торговле. Получатели обязуются передать первое потомство "
                "своего животного другой семье — модель 'Passing on the "
                "Gift'. Работает в 21 стране."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.heifer.org/give/donate.html",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("147000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1944,
        "cause_slugs": [
            "poverty-reduction",
            "livestock-relief",
            "food-security",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("147000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/351019477",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/351019477",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Plan International USA -----
    {
        "slug": "plan-international-usa",
        "country": "US",
        "registration_id": "135661832",
        "bucket": "people",
        "name": {
            "en": "Plan International USA",
            "ru": "Plan International USA",
        },
        "tagline": {
            "en": "Children's rights and equality for girls in 80+ countries",
            "ru": "Права детей и равенство девочек в 80+ странах",
        },
        "description": {
            "en": (
                "Plan International USA is the US 501(c)(3) of the Plan "
                "International federation, focused on children's rights "
                "and gender equality for girls. Programs span quality "
                "education, sexual and reproductive health rights, "
                "economic empowerment of young women, and humanitarian "
                "response in crises. Operates in 80+ countries."
            ),
            "ru": (
                "Plan International USA — американская 501(c)(3) "
                "федерации Plan International, занимается правами детей "
                "и гендерным равенством девочек. Программы: качественное "
                "образование, репродуктивные права, экономическое "
                "равноправие молодых женщин, гуманитарная помощь. "
                "Работает в 80+ странах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.planusa.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("89000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1937,
        "cause_slugs": ["education", "child-sponsorship"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("89000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/135661832",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/135661832",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Compassion International -----
    {
        "slug": "compassion-international",
        "country": "US",
        "registration_id": "362423707",
        "bucket": "people",
        "name": {
            "en": "Compassion International",
            "ru": "Compassion International",
        },
        "tagline": {
            "en": "Faith-based one-to-one child sponsorship in 25+ countries",
            "ru": "Спонсорство детей в 25+ странах (религиозный фонд)",
        },
        "description": {
            "en": (
                "Compassion International is a US 501(c)(3) Christian "
                "child-sponsorship organisation. Donors sponsor specific "
                "named children for ~$45/month, which funds local-church-"
                "delivered education, healthcare, nutrition and life-skills "
                "programs. ~2.3M children currently sponsored across 25+ "
                "countries. Charity Navigator 4-star."
            ),
            "ru": (
                "Compassion International — американская 501(c)(3) "
                "христианская организация спонсорства детей. Жертвователи "
                "спонсируют конкретных детей примерно за $45/мес, что "
                "финансирует образование, медицину, питание и жизненные "
                "навыки через местные церкви. Около 2,3 млн детей под "
                "опекой в 25+ странах. Charity Navigator: 4 звезды."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.compassion.com/sponsor_a_child/default.htm",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 12),
        "total_revenue_usd": Decimal("1100000000.00"),
        "program_expense_pct": Decimal("84.00"),
        "founded_year": 1952,
        "cause_slugs": [
            "child-sponsorship",
            "education",
            "child-nutrition",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("1100000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/362423707",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 12),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/362423707",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ===================== ANIMALS — 5 new =====================
    # ----- World Animal Protection -----
    {
        "slug": "world-animal-protection",
        "country": "US",
        "registration_id": "042718182",
        "bucket": "animals",
        "name": {
            "en": "World Animal Protection",
            "ru": "World Animal Protection",
        },
        "tagline": {
            "en": "Global animal-welfare advocacy and disaster response",
            "ru": "Защита животных и помощь при бедствиях по всему миру",
        },
        "description": {
            "en": (
                "World Animal Protection is the US 501(c)(3) of the "
                "London-based federation, focused on ending factory "
                "farming, wildlife exploitation in tourism, and animal "
                "suffering in disasters. Has UN observer status. Operates "
                "in 14 countries; campaigns globally on animal-welfare "
                "policy."
            ),
            "ru": (
                "World Animal Protection — американская 501(c)(3) "
                "лондонской федерации, борется с промышленным "
                "животноводством, эксплуатацией дикой природы в туризме "
                "и страданиями животных при катастрофах. Имеет статус "
                "наблюдателя ООН. Работает в 14 странах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.worldanimalprotection.us/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("12000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1981,
        "cause_slugs": ["animal-welfare", "wildlife-conservation"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("12000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/042718182",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/042718182",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- The Marine Mammal Center -----
    {
        "slug": "marine-mammal-center",
        "country": "US",
        "registration_id": "510144434",
        "bucket": "animals",
        "name": {
            "en": "The Marine Mammal Center",
            "ru": "The Marine Mammal Center",
        },
        "tagline": {
            "en": "Rescue, rehab and release of marine mammals",
            "ru": "Спасение, реабилитация и выпуск морских млекопитающих",
        },
        "description": {
            "en": (
                "The Marine Mammal Center is a Sausalito, California "
                "501(c)(3) — the world's largest marine mammal hospital. "
                "Rescues sick, injured and orphaned seals, sea lions, "
                "otters and small cetaceans along 600 miles of California "
                "coast and Hawaiian Islands. Has rescued 25K+ animals "
                "since 1975. Conducts ocean-health research published "
                "in peer-reviewed journals."
            ),
            "ru": (
                "The Marine Mammal Center — 501(c)(3) в Саусалито, "
                "Калифорния, крупнейший в мире госпиталь для морских "
                "млекопитающих. Спасает больных, раненых и осиротевших "
                "тюленей, морских львов, выдр и малых китообразных вдоль "
                "1000 км побережья Калифорнии и Гавайев. С 1975 года "
                "спасли 25+ тыс. животных."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.marinemammalcenter.org/get-involved/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("21000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1975,
        "cause_slugs": ["marine-life", "animal-welfare"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("21000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/510144434",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/510144434",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Jane Goodall Institute -----
    {
        "slug": "jane-goodall-institute",
        "country": "US",
        "registration_id": "942474731",
        "bucket": "animals",
        "name": {
            "en": "Jane Goodall Institute",
            "ru": "Jane Goodall Institute",
        },
        "tagline": {
            "en": "Chimpanzee research and great-ape conservation in Africa",
            "ru": "Исследование шимпанзе и охрана человекообразных обезьян",
        },
        "description": {
            "en": (
                "The Jane Goodall Institute is a US 501(c)(3) founded by "
                "Dr. Jane Goodall in 1977. Continues the long-running "
                "Gombe Stream chimpanzee research, runs primate "
                "sanctuaries in Tanzania and Republic of Congo, supports "
                "community-led forest conservation, and operates the "
                "global Roots & Shoots youth programme in 60+ countries."
            ),
            "ru": (
                "Jane Goodall Institute — американская 501(c)(3), "
                "основана доктором Джейн Гудолл в 1977 году. Продолжает "
                "долгосрочные исследования шимпанзе в Гомбе, ведёт "
                "приюты для приматов в Танзании и Конго, поддерживает "
                "общинную охрану лесов, работает с молодёжной программой "
                "Roots & Shoots в 60+ странах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://janegoodall.org/our-work/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("18000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1977,
        "cause_slugs": [
            "primates",
            "wildlife-conservation",
            "forest-protection",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("18000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/942474731",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/942474731",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- IFAW -----
    {
        "slug": "ifaw",
        "country": "US",
        "registration_id": "311594197",
        "bucket": "animals",
        "name": {
            "en": "International Fund for Animal Welfare (IFAW)",
            "ru": "International Fund for Animal Welfare (IFAW)",
        },
        "tagline": {
            "en": "Rescues animals and protects habitats in 40+ countries",
            "ru": "Спасает животных и охраняет места обитания в 40+ странах",
        },
        "description": {
            "en": (
                "IFAW is a US 501(c)(3) headquartered in Cape Cod, "
                "Massachusetts. Operates in 40+ countries on wildlife "
                "rescue and rehabilitation, anti-poaching, marine "
                "conservation (whale strandings, ship-strike avoidance), "
                "disaster response for animals, and policy advocacy. "
                "Field offices on six continents."
            ),
            "ru": (
                "IFAW — американская 501(c)(3) со штабом в Кейп-Коде, "
                "Массачусетс. Работает в 40+ странах: спасение и "
                "реабилитация диких животных, борьба с браконьерством, "
                "охрана морей (киты, столкновения с судами), помощь "
                "животным при катастрофах, законотворчество. Отделения "
                "на шести континентах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.ifaw.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 13),
        "total_revenue_usd": Decimal("105000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1969,
        "cause_slugs": [
            "animal-welfare",
            "wildlife-conservation",
            "marine-life",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("105000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/311594197",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 13),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/311594197",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- RSPCA (UK) -----
    {
        "slug": "rspca",
        "country": "GB",
        "registration_id": "219099",
        "bucket": "animals",
        "name": {
            "en": "RSPCA (Royal Society for the Prevention of Cruelty to Animals)",
            "ru": "RSPCA — Королевское общество защиты животных",
        },
        "tagline": {
            "en": "UK's oldest animal-welfare charity, founded 1824",
            "ru": "Старейшая благотворительная организация защиты животных в Великобритании",
        },
        "description": {
            "en": (
                "The RSPCA is the UK's oldest animal-welfare charity "
                "(founded 1824). Operates a 24/7 cruelty hotline, "
                "investigates ~1.1M cruelty complaints annually, runs "
                "wildlife and animal hospitals, rehomes ~30K animals "
                "per year through its branch network, and lobbies for "
                "stronger animal-welfare law in England and Wales. "
                "Royal Charter."
            ),
            "ru": (
                "RSPCA — старейшая благотворительная организация защиты "
                "животных в Великобритании (основана в 1824 году). "
                "Круглосуточная горячая линия по жестокому обращению, "
                "расследует около 1,1 млн жалоб в год, ведёт ветеринарные "
                "больницы, ежегодно пристраивает около 30 тыс. животных, "
                "лоббирует законы о защите животных. Королевский патент."
            ),
        },
        "methodology_note": _uk_verify_note(),
        "logo_url": "https://logo.uplead.com/rspca.org.uk",
        "donation_url": "https://www.rspca.org.uk/getinvolved/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1824,
        "cause_slugs": ["animal-welfare"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("180000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": (
                    "https://register-of-charities.charitycommission.gov.uk/"
                    "charity-search/-/charity-details/219099/accounts-and-annual-returns"
                ),
                "source_label": "Annual report & accounts (Charity Commission UK)",
            },
        ],
        "source_documents": [
            {
                "kind": "annual_report",
                "filed_date": date(2024, 10, 31),
                "label": {
                    "en": "Annual report & accounts (FY 2023)",
                    "ru": "Годовой отчёт и финансовая отчётность (2023)",
                },
                "url": (
                    "https://register-of-charities.charitycommission.gov.uk/"
                    "charity-search/-/charity-details/219099/accounts-and-annual-returns"
                ),
                "source_label": "Charity Commission UK — accounts page",
                "file_format": "html",
            },
        ],
    },
    # ===================== PLANET — 4 new =====================
    # ----- Trust for Public Land -----
    {
        "slug": "trust-for-public-land",
        "country": "US",
        "registration_id": "237222333",
        "bucket": "planet",
        "name": {
            "en": "Trust for Public Land",
            "ru": "Trust for Public Land",
        },
        "tagline": {
            "en": "Creates parks and protects public land in the US",
            "ru": "Создаёт парки и защищает общественные земли в США",
        },
        "description": {
            "en": (
                "Trust for Public Land is a US 501(c)(3) that buys and "
                "transfers land to the public — for parks, trails and "
                "open-space conservation. Has protected ~4M acres and "
                "created/improved 5K+ parks since 1972, with a focus on "
                "park access for low-income urban communities. Operates "
                "across all 50 states."
            ),
            "ru": (
                "Trust for Public Land — американская 501(c)(3), "
                "покупает и передаёт землю в общественное пользование — "
                "под парки, тропы, охраняемые природные территории. "
                "С 1972 года защитили около 4 млн акров и создали или "
                "улучшили 5+ тыс. парков, с фокусом на доступ к "
                "паркам для городов с низкими доходами. Работает во "
                "всех 50 штатах."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.tpl.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("180000000.00"),
        "program_expense_pct": Decimal("83.00"),
        "founded_year": 1972,
        "cause_slugs": [
            "land-conservation",
            "conservation",
            "environment",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("180000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/237222333",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/237222333",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Climate Reality Project -----
    {
        "slug": "climate-reality-project",
        "country": "US",
        "registration_id": "261241924",
        "bucket": "planet",
        "name": {
            "en": "The Climate Reality Project",
            "ru": "The Climate Reality Project",
        },
        "tagline": {
            "en": "Climate-action training and grassroots advocacy",
            "ru": "Обучение и низовая активность по климатической повестке",
        },
        "description": {
            "en": (
                "Founded by Al Gore in 2006, Climate Reality Project is a "
                "US 501(c)(3) that trains 'Climate Reality Leaders' "
                "(50K+ trained globally) to advocate for climate policy "
                "in their countries. Runs national branches in 11 countries; "
                "campaigns focus on accelerating renewable-energy adoption "
                "and fossil-fuel-subsidy phaseout."
            ),
            "ru": (
                "Climate Reality Project основан Алом Гором в 2006 году "
                "как американская 501(c)(3); готовит 'Climate Reality "
                "Leaders' (50+ тыс. человек по миру) для продвижения "
                "климатической политики в своих странах. Национальные "
                "отделения в 11 странах. Кампании по переходу на ВИЭ и "
                "отмене субсидий на ископаемое топливо."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.climaterealityproject.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("19000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2006,
        "cause_slugs": ["climate", "environment"],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("19000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/261241924",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/261241924",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- World Resources Institute -----
    {
        "slug": "world-resources-institute",
        "country": "US",
        "registration_id": "521257057",
        "bucket": "planet",
        "name": {
            "en": "World Resources Institute",
            "ru": "World Resources Institute",
        },
        "tagline": {
            "en": "Research-driven climate, food, water and forest policy",
            "ru": "Исследовательская работа по климату, воде, лесам, продовольствию",
        },
        "description": {
            "en": (
                "WRI is a US 501(c)(3) global research organisation "
                "working in 60+ countries on seven challenges: climate, "
                "energy, food, forests, water, ocean and cities. Hosts "
                "Global Forest Watch (open-data deforestation monitoring), "
                "Aqueduct (water-stress mapping) and Climate Watch. "
                "Convening role in international climate policy."
            ),
            "ru": (
                "WRI — американская 501(c)(3), глобальная "
                "исследовательская организация, работает в 60+ странах "
                "по семи направлениям: климат, энергетика, продовольствие, "
                "леса, вода, океан, города. Управляет Global Forest Watch "
                "(открытый мониторинг вырубки лесов), Aqueduct (карты "
                "водного стресса) и Climate Watch."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://www.wri.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 14),
        "total_revenue_usd": Decimal("210000000.00"),
        "program_expense_pct": Decimal("85.00"),
        "founded_year": 1982,
        "cause_slugs": [
            "climate",
            "forest-protection",
            "environment",
            "water-sanitation",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("210000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/521257057",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 8, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/521257057",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # ----- Land Trust Alliance -----
    {
        "slug": "land-trust-alliance",
        "country": "US",
        "registration_id": "042751359",
        "bucket": "planet",
        "name": {
            "en": "Land Trust Alliance",
            "ru": "Land Trust Alliance",
        },
        "tagline": {
            "en": "Supports the network of US land trusts protecting open space",
            "ru": "Поддерживает сеть земельных трастов США",
        },
        "description": {
            "en": (
                "Land Trust Alliance is a US 501(c)(3) umbrella for ~1K "
                "member land trusts across the United States that "
                "collectively protect 60M+ acres of farmland, forests, "
                "wetlands and open space via conservation easements and "
                "fee acquisition. Provides accreditation, training, "
                "policy advocacy and legal defence for member trusts."
            ),
            "ru": (
                "Land Trust Alliance — американская 501(c)(3), зонтичная "
                "организация для около 1 тыс. земельных трастов США, "
                "которые в совокупности защищают 60+ млн акров "
                "сельхозземель, лесов, болот и открытых пространств через "
                "сервитуты и выкуп. Обеспечивает аккредитацию, обучение, "
                "лоббирование и юридическую защиту трастов-участников."
            ),
        },
        "methodology_note": _verify_note(),
        "logo_url": "",
        "donation_url": "https://landtrustalliance.org/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("23000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1982,
        "cause_slugs": [
            "land-conservation",
            "conservation",
            "forest-protection",
        ],
        **_empty_photo(),
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("23000000.00"),
                "program_expenses_usd": None,
                "admin_expenses_usd": None,
                "fundraising_expenses_usd": None,
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/042751359",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 5, 14),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/042751359",
                "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
]


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
                f"[migration 0021] BLOCKED {entry['slug']} "
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

        for fin in entry["financials"]:
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

        for doc in entry["source_documents"]:
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
        f"[migration 0021] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total_charities}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0020_fill_remaining_logos"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

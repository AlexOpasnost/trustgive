"""v3.0 photo-first redesign — seed Animals + Planet bucket charities.

DESIGN.md v3.0 §G calls for 4–5 well-known orgs per bucket so each bucket
has at least 4–5 cards on its catalog page. This migration seeds:

  Animals (4):
    - World Wildlife Fund (WWF) — using US affiliate WWF-US (EIN 52-1693387).
      DESIGN.md §G.2 explicitly forbids seeding WWF Russia branch (foreign-
      agent designation) — we use the US 501(c)(3) only.
    - ASPCA — American Society for the Prevention of Cruelty to Animals
      (US, EIN 13-1623829)
    - Best Friends Animal Society (US, EIN 23-7147797) — no-kill movement
      leader in Kanab, Utah.
    - Born Free Foundation (UK, Charity Commission 1070906) — wildlife
      protection with rigorous filings.

  Planet (4):
    - Cool Earth (UK, Charity Commission 1117978) — indigenous-led
      rainforest protection.
    - The Nature Conservancy (US, EIN 53-0242652) — one of the largest
      US environmental orgs.
    - Ocean Conservancy (US, EIN 23-2527671) — oceans-specialised.
    - 350.org (US, EIN 26-3988708) — climate movement org.

Russia-law compliance: every entry runs through `is_blocked()` defensively.
DESIGN.md §G.3 explicitly EXCLUDES Greenpeace International (NL, foreign-
agent in RU per blocklist.py) and WWF Russia branch — we ship only WWF-US.

Idempotent — uses `update_or_create` keyed on (country, registration_id),
so re-running this migration replaces curated data without touching anything
else. Reverse migration is a no-op (never auto-delete real curated rows).

Photo URLs were each HEAD-probed and confirmed 200 + Content-Type: image/*
before this migration was written. Best Friends Animal Society has
hero_photo_url="" because no Commons photo specific to their work was
found (search attempts: "Best Friends Sanctuary Utah", "Animal Sanctuary
Kanab" — only landscape shots, no animal-care photos); frontend falls back
to BrandedAvatar per §D fallback chain.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


# Causes referenced by these seeds — created lazily via get_or_create.
NEW_CAUSES: dict[str, dict[str, str]] = {
    "animal-welfare": {"en": "Animal welfare", "ru": "Защита животных"},
    "wildlife-conservation": {
        "en": "Wildlife conservation",
        "ru": "Охрана дикой природы",
    },
    "endangered-species": {
        "en": "Endangered species",
        "ru": "Исчезающие виды",
    },
    "climate": {"en": "Climate", "ru": "Климат"},
    "rainforest": {"en": "Rainforest protection", "ru": "Защита тропических лесов"},
    "conservation": {"en": "Conservation", "ru": "Охрана природы"},
    "oceans": {"en": "Oceans", "ru": "Океаны"},
    "environment": {"en": "Environment", "ru": "Окружающая среда"},
}


SEED: list[dict] = [
    # =========================================================================
    # ANIMALS BUCKET
    # =========================================================================
    # -------------------------------------------------------------------
    # World Wildlife Fund — US affiliate (DESIGN.md §G.2)
    # We seed WWF-US, NOT WWF International (HQ in Switzerland — no clean
    # public registration ID), and explicitly NOT WWF Russia (foreign-agent).
    # -------------------------------------------------------------------
    {
        "slug": "wwf-us",
        "country": "US",
        "registration_id": "521693387",
        "bucket": "animals",
        "name": {
            "en": "World Wildlife Fund (WWF-US)",
            "ru": "Всемирный фонд дикой природы (WWF-US)",
        },
        "tagline": {
            "en": "Conserves nature and reduces threats to biodiversity",
            "ru": "Охрана природы и снижение угроз биоразнообразию",
        },
        "description": {
            "en": (
                "WWF-US is the United States affiliate of the global "
                "WWF network, the world's largest independent conservation "
                "organisation. Active in 100+ countries on wildlife "
                "conservation, climate, oceans, food, freshwater, and "
                "forests. WWF-US files Form 990 with the IRS annually. "
                "Note: per Russian law we do not include the WWF Russia "
                "branch, which holds a foreign-agent designation."
            ),
            "ru": (
                "WWF-US — американское отделение глобальной сети WWF, "
                "крупнейшей независимой природоохранной организации в мире. "
                "Работает в более чем 100 странах в темах охраны "
                "дикой природы, климата, океанов, еды, пресной воды и лесов. "
                "WWF-US ежегодно подаёт форму 990 в IRS. Примечание: "
                "согласно российскому праву мы не включаем российское "
                "отделение WWF, имеющее статус иностранного агента."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) registered with IRS (ProPublica), "
                "Form 990 filed FY 2023."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год."
            ),
        },
        "logo_url": "https://upload.wikimedia.org/wikipedia/en/2/24/WWF_logo.svg",
        "donation_url": "https://support.worldwildlife.org/site/Donation2",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 13),
        "total_revenue_usd": Decimal("394700000.00"),
        "program_expense_pct": Decimal("84.20"),
        "founded_year": 1961,
        "cause_slugs": [
            "wildlife-conservation",
            "endangered-species",
            "conservation",
            "environment",
        ],
        # Photo: a radio-collared elephant in Northern Mara Conservancy, Kenya
        # — represents WWF's wildlife conservation field work. CC-BY-SA 4.0.
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Front_view_of_elephant_in_Northern_Mara_Conservancy%2C_Kenya.jpg",
        "hero_photo_caption": {
            "en": "A radio-collared elephant walking the savanna of the Northern Mara Conservancy in Kenya — the kind of monitored wildlife conservation work WWF supports across 100+ countries.",
            "ru": "Слон с радио-ошейником гуляет по саванне заповедника Северный Мара в Кении — тип мониторинговой охраны дикой природы, которую WWF поддерживает в более чем 100 странах.",
        },
        "hero_photo_credit": "Daniel Case / Wikimedia Commons / CC BY-SA 4.0",
        "hero_photo_license": "cc-by-sa",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("394700000.00"),
                "program_expenses_usd": Decimal("332300000.00"),
                "admin_expenses_usd": Decimal("23200000.00"),
                "fundraising_expenses_usd": Decimal("38800000.00"),
                "top_executive_comp_usd": Decimal("1300000.00"),
                "top_executive_name": "Carter Roberts",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/521693387",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 13),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/521693387",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # ASPCA — American Society for the Prevention of Cruelty to Animals
    # -------------------------------------------------------------------
    {
        "slug": "aspca",
        "country": "US",
        "registration_id": "131623829",
        "bucket": "animals",
        "name": {
            "en": "ASPCA",
            "ru": "ASPCA (Американское общество против жестокости к животным)",
        },
        "tagline": {
            "en": "Prevents cruelty to animals across the United States",
            "ru": "Предотвращение жестокости к животным в США",
        },
        "description": {
            "en": (
                "Founded in 1866, the ASPCA is the largest US humane "
                "society, running animal welfare programs nationwide: "
                "shelter operations, anti-cruelty law enforcement support, "
                "veterinary services, and the Rescue Ride program that "
                "transports adoptable animals from over-capacity southern "
                "shelters to high-demand northern shelters."
            ),
            "ru": (
                "ASPCA, основанное в 1866 году, — крупнейшее гуманное "
                "общество США. Ведёт программы защиты животных по всей "
                "стране: приюты, поддержка правоприменения против "
                "жестокого обращения, ветеринарные услуги, программа "
                "Rescue Ride по перевозке животных из переполненных "
                "южных приютов в северные с высоким спросом."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023, founded 1866."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год, основано в 1866 году."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.aspca.org/ways-to-give",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 14),
        "total_revenue_usd": Decimal("404500000.00"),
        "program_expense_pct": Decimal("76.30"),
        "founded_year": 1866,
        "cause_slugs": ["animal-welfare"],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/ASPCA_Rescue_Ride%3B_Dale_City%2C_VA.jpg",
        "hero_photo_caption": {
            "en": "An ASPCA Rescue Ride transport van — used to move adoptable animals from over-capacity southern shelters to high-demand northern ones.",
            "ru": "Микроавтобус ASPCA Rescue Ride — перевозит животных из переполненных южных приютов в северные приюты с высоким спросом на усыновление.",
        },
        "hero_photo_credit": "DanTD / Wikimedia Commons / CC BY-SA 4.0",
        "hero_photo_license": "cc-by-sa",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("404500000.00"),
                "program_expenses_usd": Decimal("308600000.00"),
                "admin_expenses_usd": Decimal("31400000.00"),
                "fundraising_expenses_usd": Decimal("64500000.00"),
                "top_executive_comp_usd": Decimal("852000.00"),
                "top_executive_name": "Matt Bershadker",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/131623829",
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
                "url": "https://projects.propublica.org/nonprofits/organizations/131623829",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # Best Friends Animal Society
    # -------------------------------------------------------------------
    {
        "slug": "best-friends-animal-society",
        "country": "US",
        "registration_id": "237147797",
        "bucket": "animals",
        "name": {
            "en": "Best Friends Animal Society",
            "ru": "Best Friends Animal Society",
        },
        "tagline": {
            "en": "Leading the no-kill movement for shelter animals in the US",
            "ru": "Лидер движения за приюты без эвтаназии в США",
        },
        "description": {
            "en": (
                "Best Friends operates the largest no-kill animal "
                "sanctuary in the United States in Kanab, Utah, and "
                "leads a national network campaign to make all US "
                "shelters no-kill. Strong financial transparency: "
                "Form 990 filed annually with the IRS."
            ),
            "ru": (
                "Best Friends содержит крупнейший в США приют без "
                "эвтаназии в Канабе, штат Юта, и ведёт национальную "
                "сетевую кампанию, чтобы все американские приюты "
                "перешли на политику без эвтаназии. Высокий уровень "
                "финансовой прозрачности: форма 990 подаётся ежегодно."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://bestfriends.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 15),
        "total_revenue_usd": Decimal("177800000.00"),
        "program_expense_pct": Decimal("75.50"),
        "founded_year": 1984,
        "cause_slugs": ["animal-welfare"],
        # Best Friends — no specific Commons photo of the sanctuary's care
        # work (only landscape shots of Kanab found). Falling back to
        # BrandedAvatar per DESIGN.md §D.
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("177800000.00"),
                "program_expenses_usd": Decimal("134200000.00"),
                "admin_expenses_usd": Decimal("18900000.00"),
                "fundraising_expenses_usd": Decimal("24700000.00"),
                "top_executive_comp_usd": Decimal("464000.00"),
                "top_executive_name": "Julie Castle",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/237147797",
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
                "url": "https://projects.propublica.org/nonprofits/organizations/237147797",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # Born Free Foundation (UK Charity 1070906)
    # -------------------------------------------------------------------
    {
        "slug": "born-free-foundation",
        "country": "GB",
        "registration_id": "1070906",
        "bucket": "animals",
        "name": {
            "en": "Born Free Foundation",
            "ru": "Born Free Foundation",
        },
        "tagline": {
            "en": "Protects wild animals in their natural habitats",
            "ru": "Защита диких животных в их естественной среде",
        },
        "description": {
            "en": (
                "Born Free Foundation is a UK wildlife charity working "
                "globally to keep wild animals in the wild. Programs "
                "include sanctuary operations for rescued big cats, "
                "anti-poaching support in Kenya and Ethiopia, and "
                "advocacy against captive-wildlife exploitation. "
                "Annual returns filed with the UK Charity Commission."
            ),
            "ru": (
                "Born Free Foundation — британская организация защиты "
                "дикой природы, работающая по всему миру с миссией "
                "сохранять диких животных в дикой природе. Программы: "
                "приюты для спасённых крупных кошек, поддержка борьбы "
                "с браконьерством в Кении и Эфиопии, адвокация против "
                "содержания диких животных в неволе. Годовые отчёты "
                "подаются в UK Charity Commission."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #1070906 (Charity "
                "Commission), annual report filed within last 12 months."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #1070906 "
                "(Charity Commission), годовой отчёт за последние 12 месяцев."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.bornfree.org.uk/donate",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("8400000.00"),
        "program_expense_pct": Decimal("78.20"),
        "founded_year": 1984,
        "cause_slugs": [
            "wildlife-conservation",
            "endangered-species",
            "animal-welfare",
        ],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/5/50/Born_free_foundation_kenya_landrover.jpg",
        "hero_photo_caption": {
            "en": "A Born Free Foundation Land Rover in Kenya at the 2016 Global March for Elephants — Born Free supports anti-poaching and wildlife protection across East Africa.",
            "ru": "Land Rover Born Free Foundation в Кении на Глобальном марше за слонов 2016 года — Born Free поддерживает борьбу с браконьерством и охрану дикой природы в Восточной Африке.",
        },
        "hero_photo_credit": "Kengee8 / Wikimedia Commons / CC BY-SA 4.0",
        "hero_photo_license": "cc-by-sa",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("8400000.00"),
                "program_expenses_usd": Decimal("6570000.00"),
                "admin_expenses_usd": Decimal("680000.00"),
                "fundraising_expenses_usd": Decimal("1150000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1070906",
                "source_label": "Charity Commission filing FY 2023",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 9, 30),
                "label": {
                    "en": "Charity Commission filing (FY 2023)",
                    "ru": "Charity Commission, отчёт за 2023",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1070906",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # =========================================================================
    # PLANET BUCKET
    # =========================================================================
    # -------------------------------------------------------------------
    # Cool Earth (UK Charity 1117978) — indigenous-led rainforest protection
    # -------------------------------------------------------------------
    {
        "slug": "cool-earth",
        "country": "GB",
        "registration_id": "1117978",
        "bucket": "planet",
        "name": {"en": "Cool Earth", "ru": "Cool Earth"},
        "tagline": {
            "en": "Indigenous-led protection of rainforest, by paying communities directly",
            "ru": "Охрана тропических лесов руками коренных общин — прямым финансированием",
        },
        "description": {
            "en": (
                "Cool Earth partners with indigenous and local rainforest "
                "communities in Peru, Papua New Guinea, and the Democratic "
                "Republic of Congo, channelling funding directly to those "
                "communities so they can keep their forests standing. The "
                "Asháninka project in Peru is the longest-running. Annual "
                "returns filed with the UK Charity Commission."
            ),
            "ru": (
                "Cool Earth сотрудничает с коренными общинами тропических "
                "лесов Перу, Папуа-Новой Гвинеи и Демократической "
                "Республики Конго, направляя финансирование прямо в эти "
                "общины, чтобы они могли сохранять свои леса. Проект "
                "Ашанинка в Перу — старейший. Годовые отчёты подаются в "
                "UK Charity Commission."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: registered UK charity #1117978 (Charity "
                "Commission), annual report filed within last 12 months."
            ),
            "ru": (
                "Подтверждено: благотворительная организация UK #1117978 "
                "(Charity Commission), годовой отчёт за последние 12 месяцев."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.coolearth.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("3400000.00"),
        "program_expense_pct": Decimal("82.40"),
        "founded_year": 2007,
        "cause_slugs": [
            "rainforest",
            "climate",
            "conservation",
            "environment",
        ],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/c/c4/Girls_in_a_village_of_Cool_Earth%27s_Ashaninka_Project.jpg",
        "hero_photo_caption": {
            "en": "Girls in the rainforest village of Cutivireni, Peru — a partner community in Cool Earth's Asháninka Project.",
            "ru": "Девочки в деревне Кутивирени в тропическом лесу, Перу — партнёрское сообщество проекта Ашанинка фонда Cool Earth.",
        },
        "hero_photo_credit": "Cool Earth / Wikimedia Commons / CC BY-SA 3.0",
        "hero_photo_license": "cc-by-sa",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("3400000.00"),
                "program_expenses_usd": Decimal("2800000.00"),
                "admin_expenses_usd": Decimal("280000.00"),
                "fundraising_expenses_usd": Decimal("320000.00"),
                "top_executive_comp_usd": None,
                "top_executive_name": "",
                "source_url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1117978",
                "source_label": "Charity Commission filing FY 2023",
            },
        ],
        "source_documents": [
            {
                "kind": "charity_commission_filing",
                "filed_date": date(2024, 9, 30),
                "label": {
                    "en": "Charity Commission filing (FY 2023)",
                    "ru": "Charity Commission, отчёт за 2023",
                },
                "url": "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1117978",
                "source_label": "UK Charity Commission Register",
                "file_format": "html",
            },
        ],
    },
    # -------------------------------------------------------------------
    # The Nature Conservancy (US, EIN 53-0242652)
    # -------------------------------------------------------------------
    {
        "slug": "the-nature-conservancy",
        "country": "US",
        "registration_id": "530242652",
        "bucket": "planet",
        "name": {
            "en": "The Nature Conservancy",
            "ru": "The Nature Conservancy",
        },
        "tagline": {
            "en": "Protects ecologically important lands and waters globally",
            "ru": "Охрана важных экосистем суши и водоёмов по всему миру",
        },
        "description": {
            "en": (
                "The Nature Conservancy is one of the largest "
                "environmental non-profits in the United States, with a "
                "science-driven model for land and water protection. "
                "Operates in 79 countries and territories, holds millions "
                "of acres in protected status across the US. Files Form "
                "990 with the IRS annually."
            ),
            "ru": (
                "The Nature Conservancy — одна из крупнейших "
                "природоохранных НКО США с научно-обоснованной моделью "
                "охраны суши и воды. Работает в 79 странах и территориях, "
                "под её охраной — миллионы акров земли в США. Ежегодно "
                "подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://www.nature.org/en-us/get-involved/how-to-help/donate-to-nature/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 15),
        "total_revenue_usd": Decimal("1370000000.00"),
        "program_expense_pct": Decimal("76.80"),
        "founded_year": 1951,
        "cause_slugs": ["conservation", "climate", "environment", "oceans"],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/1/11/Christie_Boser_%28The_Nature_Conservancy%29_%2826825620610%29.jpg",
        "hero_photo_caption": {
            "en": "Christie Boser, a field biologist with The Nature Conservancy, at work — TNC's science-driven model is rooted in field research like this.",
            "ru": "Кристи Босер, полевой биолог The Nature Conservancy, на работе — научная модель TNC основана именно на таких полевых исследованиях.",
        },
        "hero_photo_credit": "Pacific Southwest Region USFWS / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("1370000000.00"),
                "program_expenses_usd": Decimal("816400000.00"),
                "admin_expenses_usd": Decimal("96900000.00"),
                "fundraising_expenses_usd": Decimal("149200000.00"),
                "top_executive_comp_usd": Decimal("978000.00"),
                "top_executive_name": "Jennifer Morris",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/530242652",
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
                "url": "https://projects.propublica.org/nonprofits/organizations/530242652",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # Ocean Conservancy (US, EIN 23-2527671)
    # -------------------------------------------------------------------
    {
        "slug": "ocean-conservancy",
        "country": "US",
        "registration_id": "232527671",
        "bucket": "planet",
        "name": {
            "en": "Ocean Conservancy",
            "ru": "Ocean Conservancy",
        },
        "tagline": {
            "en": "Protects oceans through science-based policy and the International Coastal Cleanup",
            "ru": "Охрана океанов: научная политика и международная уборка побережья",
        },
        "description": {
            "en": (
                "Ocean Conservancy is a US ocean-conservation non-profit "
                "specialised on plastic pollution, sustainable fisheries, "
                "and Arctic protection. Best known for the International "
                "Coastal Cleanup, the world's largest volunteer effort to "
                "remove trash from beaches and waterways. Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "Ocean Conservancy — американская НКО по охране океанов, "
                "специализирующаяся на пластиковом загрязнении, устойчивом "
                "рыболовстве и защите Арктики. Известна благодаря "
                "International Coastal Cleanup — крупнейшей в мире "
                "добровольческой акции по уборке мусора с пляжей и водоёмов. "
                "Ежегодно подаёт форму 990 в IRS."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://oceanconservancy.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 8, 8),
        "total_revenue_usd": Decimal("38900000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1972,
        "cause_slugs": ["oceans", "conservation", "environment", "climate"],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d6/Volunteers_participate_in_beach_debris_cleanup_-_52751597181.jpg",
        "hero_photo_caption": {
            "en": "Volunteers remove debris from a beach — Ocean Conservancy's International Coastal Cleanup is the world's largest one-day volunteer effort against marine plastic pollution.",
            "ru": "Волонтёры убирают мусор с пляжа — International Coastal Cleanup от Ocean Conservancy — крупнейшая в мире однодневная добровольческая акция против пластикового загрязнения океанов.",
        },
        "hero_photo_credit": "CapeHatterasNPS / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("38900000.00"),
                "program_expenses_usd": Decimal("27800000.00"),
                "admin_expenses_usd": Decimal("3500000.00"),
                "fundraising_expenses_usd": Decimal("4400000.00"),
                "top_executive_comp_usd": Decimal("431000.00"),
                "top_executive_name": "Janis Searles Jones",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/232527671",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 8, 8),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/232527671",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
                "file_format": "pdf",
            },
        ],
    },
    # -------------------------------------------------------------------
    # 350.org (US, EIN 26-3988708)
    # -------------------------------------------------------------------
    {
        "slug": "three-fifty-org",
        "country": "US",
        "registration_id": "263988708",
        "bucket": "planet",
        "name": {"en": "350.org", "ru": "350.org"},
        "tagline": {
            "en": "Builds a global grassroots climate movement",
            "ru": "Развивает глобальное низовое климатическое движение",
        },
        "description": {
            "en": (
                "350.org is an international climate-movement organisation, "
                "named for the 350 ppm of atmospheric CO2 considered safe. "
                "Co-founded by Bill McKibben, it organises grassroots "
                "campaigns for fossil-fuel divestment, climate marches, "
                "and policy pressure across 180+ countries. Files Form 990 "
                "with the IRS annually."
            ),
            "ru": (
                "350.org — международная организация климатического "
                "движения, названная в честь 350 ppm CO2 в атмосфере, "
                "считающихся безопасным уровнем. Сооснователь — Билл "
                "Маккиббен. Организует низовые кампании за отказ от "
                "ископаемого топлива, климатические марши и давление на "
                "политику в 180+ странах. Ежегодно подаёт форму 990."
            ),
        },
        "methodology_note": {
            "en": (
                "Verified: 501(c)(3) with IRS (ProPublica), Form 990 "
                "filed FY 2023."
            ),
            "ru": (
                "Подтверждено: 501(c)(3) в IRS (ProPublica), "
                "форма 990 за 2023 финансовый год."
            ),
        },
        "logo_url": "",
        "donation_url": "https://act.350.org/donate/our_movement_needs_you/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 11, 8),
        "total_revenue_usd": Decimal("19800000.00"),
        "program_expense_pct": Decimal("80.50"),
        "founded_year": 2008,
        "cause_slugs": ["climate", "environment"],
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/350.org_Forward_on_Climate-Washington_DC.jpg",
        "hero_photo_caption": {
            "en": "350.org founder Bill McKibben at the Forward on Climate Rally in Washington DC, 2013 — 350.org organises mass grassroots mobilisation for climate action across 180+ countries.",
            "ru": "Основатель 350.org Билл Маккиббен на климатическом митинге Forward on Climate в Вашингтоне, 2013 — 350.org организует массовую низовую мобилизацию за климатические действия в 180+ странах.",
        },
        "hero_photo_credit": "chesapeakeclimate / Wikimedia Commons / CC BY-SA 2.0",
        "hero_photo_license": "cc-by-sa",
        "financials": [
            {
                "year": 2023,
                "total_revenue_usd": Decimal("19800000.00"),
                "program_expenses_usd": Decimal("15940000.00"),
                "admin_expenses_usd": Decimal("1980000.00"),
                "fundraising_expenses_usd": Decimal("1880000.00"),
                "top_executive_comp_usd": Decimal("212000.00"),
                "top_executive_name": "May Boeve",
                "source_url": "https://projects.propublica.org/nonprofits/organizations/263988708",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
            },
        ],
        "source_documents": [
            {
                "kind": "irs_990",
                "filed_date": date(2024, 11, 8),
                "label": {
                    "en": "IRS Form 990 (FY 2023)",
                    "ru": "Налоговая форма IRS 990 (2023)",
                },
                "url": "https://projects.propublica.org/nonprofits/organizations/263988708",
                "source_label": "IRS Form 990, FY 2023 (ProPublica)",
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

    # 1. Ensure cause taxonomy entries exist for every new slug.
    for slug, label in NEW_CAUSES.items():
        Cause.objects.update_or_create(slug=slug, defaults={"name": label})

    upserted = 0
    skipped_blocked = 0

    for entry in SEED:
        # Defensive blocklist check — DESIGN.md §G.3 explicitly excluded
        # Greenpeace and WWF Russia branch; we don't seed them here, but if
        # this list ever grows, the check catches accidental additions.
        block = is_blocked(
            country=entry["country"],
            registration_id=entry["registration_id"],
            cause_tags=entry["cause_slugs"],
            name=entry["name"]["en"] + " " + entry["name"]["ru"],
            description=entry["description"]["en"],
        )
        if block is not None:
            print(
                f"[migration 0012] BLOCKED {entry['slug']} "
                f"({entry['country']}/{entry['registration_id']}): {block}"
            )
            skipped_blocked += 1
            continue

        is_stale = (date.today() - entry["last_filed_date"]).days > 730

        charity, _created = Charity.objects.update_or_create(
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
                # v3.0 photo + bucket payload:
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

    # Refresh denormalised charity_count on Cause rows we touched.
    for slug in NEW_CAUSES.keys():
        count = Charity.objects.filter(cause_tags__contains=[slug]).count()
        Cause.objects.filter(slug=slug).update(charity_count=count)

    print(
        f"[migration 0012] Animals + Planet bucket charities upserted: "
        f"{upserted}, blocked: {skipped_blocked}"
    )


def backwards(apps, schema_editor):
    """No-op. We never auto-delete real curated rows on rollback."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0011_seed_hero_photos_existing"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

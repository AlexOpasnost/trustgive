"""v3.6 catalog expansion — seed 20 more curated charities (198 -> ~218).

Focus: filling underserved gaps surfaced by an audit of the live catalog.

  - UK Charity Commission orgs (+6): Mind, Macmillan Cancer Support,
    Marie Curie, Cancer Research UK, Samaritans, Anthony Nolan. UK is
    under-represented vs. our US count and the regulator (UK Charity
    Commission) is one of the strongest in the world.
  - Disability services (+5): Special Olympics, United Cerebral Palsy,
    RNIB (UK), Sense (UK), DREDF. Existing catalog covered NFB / The Arc
    / Easterseals / Best Buddies but missed major sport-inclusion,
    cerebral-palsy, blind-UK, deafblind and disability-rights-litigation.
  - Mental health (+5): AFSP, Active Minds, BBRF, ADAA, TWLOHA. Catalog
    already had NAMI / MHA / JED / Trevor Project / Vibrant (988) /
    Crisis Text Line; these five fill suicide-prevention research,
    youth-led campus mental health, neuroscience research funding,
    anxiety/depression patient-facing, and contemporary peer-support.
  - International (US 501c3 affiliates of global orgs) (+4): Oxfam
    America, International Medical Corps, HelpAge USA, Catholic Medical
    Mission Board. We already had Oxfam GB, MSF USA, UNICEF USA, IRC,
    CARE USA, Save the Children, Mercy Corps, Action Against Hunger USA
    and World Vision US — these four fill US-Oxfam (vs. Oxfam-GB),
    crisis-medical-response, global-elderly and faith-based-medical
    that none of the existing affiliates touched directly.

EINs verified against ProPublica Nonprofit Explorer at curation time
per KB-012; UK charity numbers verified against the Charity Commission
register. EINs are zero-padded to 9 digits per KB-017. US source URL is
the ProPublica `/organizations/{ein}` overview page (KB-014, NOT
`/download-filing` which is Cloudflare-bot-blocked). UK source URL is
`/charity-search/-/charity-details/{number}/accounts-and-annual-returns`
(per KB-014 — listing page, not direct PDF, since CC PDFs change yearly).

Hero photos & logos: empty here. Filled by:
  - 0036_backfill_v36_logos.py            (logo_url via uplead)
  - existing scrape_og_images management command will pick up
    hero_photo_url on next OG-scrape pass (no separate migration).

Substitutions vs. the original brief:
  - "Helen Keller International" already seeded earlier — no entry added.
  - "Compassion International" already seeded in 0021 — skipped.
  - "Conrad N. Hilton Foundation" — private foundation (990-PF),
    grant-maker, doesn't fit the public-donation catalog model — replaced
    with HelpAge USA (US, EIN 13-3445198) and Catholic Medical Mission
    Board (US, EIN 13-5602340) so the International bucket stays at 4.
  - Considered "Autism Speaks" — well-known controversies in autistic
    self-advocacy community (cure-framing, prior support of ABA without
    nuance); excluded out of an abundance of caution. Catalog covers IDD
    via The Arc / Easterseals / Best Buddies / DREDF instead.
  - Considered "Mencap" (UK CC #222377) — would overlap thematically
    with The Arc; chose UCP (US) and Sense (UK) for cause-tag breadth
    instead.
  - Considered "Royal British Legion" — military/veterans is already
    covered by Hope For The Warriors / Fisher House; chose
    cancer/end-of-life UK orgs to fill the bigger gap.
  - Considered "Scope" (UK CC #208231) — would overlap with The Arc;
    chose Sense for cross-disability deafblind specialisation.

No Russia-targeted charities in this batch (per task constraints).

Idempotent: `update_or_create((country, registration_id))`. Defensive
`is_blocked()` per entry (Russia-law compliance, KB pattern). Reverse
is a no-op (never auto-delete real curated rows).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "hospice-palliative": {
        "en": "Hospice & palliative care",
        "ru": "Паллиативная помощь и хосписы",
    },
    "blood-cancer": {
        "en": "Blood cancer & marrow",
        "ru": "Рак крови и трансплантация костного мозга",
    },
    "blindness": {
        "en": "Blindness & vision",
        "ru": "Слепота и нарушения зрения",
    },
    "deafblind": {
        "en": "Deafblind support",
        "ru": "Помощь людям с одновременными нарушениями зрения и слуха",
    },
    "cerebral-palsy": {
        "en": "Cerebral palsy",
        "ru": "Детский церебральный паралич",
    },
    "intellectual-disability-sport": {
        "en": "Sport for intellectual disabilities",
        "ru": "Спорт для людей с нарушениями развития",
    },
    "anxiety-depression": {
        "en": "Anxiety & depression",
        "ru": "Тревожные расстройства и депрессия",
    },
    "neuroscience-research": {
        "en": "Neuroscience research",
        "ru": "Исследования в нейронауках",
    },
}


def _verify_note_us(en_extra: str = "", ru_extra: str = "") -> dict:
    return {
        "en": (
            "Verified: 501(c)(3) registered with IRS (ProPublica), Form 990 "
            "on file with ProPublica."
            + (f" {en_extra}" if en_extra else "")
        ),
        "ru": (
            "Подтверждено: 501(c)(3) в IRS (ProPublica), форма 990 на ProPublica."
            + (f" {ru_extra}" if ru_extra else "")
        ),
    }


def _verify_note_uk(en_extra: str = "", ru_extra: str = "") -> dict:
    return {
        "en": (
            "Verified: registered charity with the UK Charity Commission, "
            "annual accounts on file."
            + (f" {en_extra}" if en_extra else "")
        ),
        "ru": (
            "Подтверждено: благотворительная организация в реестре Charity "
            "Commission UK, годовая отчётность на сайте регулятора."
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
    """Per KB-014: ProPublica /organizations/{ein} overview, NOT /download-filing."""
    return f"https://projects.propublica.org/nonprofits/organizations/{ein}"


def _uk_cc(number: str) -> str:
    """Per KB-014: Charity Commission accounts listing page, not direct PDF."""
    return (
        "https://register-of-charities.charitycommission.gov.uk/"
        f"charity-search/-/charity-details/{number}/accounts-and-annual-returns"
    )


SEED: list[dict] = [
    # ===================== UK CHARITY COMMISSION (6) =====================
    # ----- Mind (UK) -----
    {
        "slug": "mind-uk",
        "country": "GB",
        "registration_id": "219830",
        "bucket": "people",
        "name": {
            "en": "Mind",
            "ru": "Mind — британская организация по психическому здоровью",
        },
        "tagline": {
            "en": "UK's leading mental-health charity, supporting anyone with a mental health problem",
            "ru": "Ведущая благотворительная организация Великобритании в сфере психического здоровья",
        },
        "description": {
            "en": (
                "Mind is the UK's leading mental-health charity (Charity "
                "Commission #219830, founded 1946). Operates a national "
                "Infoline and Legal Line, runs ~125 local Mind associations "
                "across England and Wales delivering crisis services, peer "
                "support and advocacy, campaigns for better mental-health "
                "policy and challenges discrimination. Together with Rethink "
                "Mental Illness, Mind co-leads the Time to Change campaign "
                "to end mental-health stigma."
            ),
            "ru": (
                "Mind — ведущая благотворительная организация Великобритании "
                "в сфере психического здоровья (Charity Commission #219830, "
                "основана в 1946 году). Ведёт национальную информационную и "
                "юридическую линию, около 125 местных отделений в Англии и "
                "Уэльсе оказывают кризисную помощь, поддержку равных и "
                "адвокацию, кампании за улучшение политики в области "
                "психического здоровья и борьба с дискриминацией. Совместно "
                "с Rethink Mental Illness руководит кампанией Time to Change "
                "по борьбе со стигматизацией."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.mind.org.uk/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("75000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1946,
        "cause_slugs": ["mental-health"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("219830"),
    },
    # ----- Macmillan Cancer Support (UK) -----
    {
        "slug": "macmillan-cancer-support",
        "country": "GB",
        "registration_id": "261017",
        "bucket": "people",
        "name": {
            "en": "Macmillan Cancer Support",
            "ru": "Macmillan Cancer Support",
        },
        "tagline": {
            "en": "Practical, emotional and financial support for people living with cancer in the UK",
            "ru": "Практическая, эмоциональная и финансовая поддержка людей с онкологией в Великобритании",
        },
        "description": {
            "en": (
                "Macmillan Cancer Support is a UK charity (Charity Commission "
                "#261017, founded 1911). Funds Macmillan nurses (specialist "
                "cancer-care nurses embedded in the NHS), runs a free Support "
                "Line, provides grants for travel and household costs to "
                "people undergoing treatment, and produces patient-facing "
                "information across all cancer types. Reaches ~2.3M people "
                "with cancer in the UK each year."
            ),
            "ru": (
                "Macmillan Cancer Support — британская благотворительная "
                "организация (Charity Commission #261017, основана в 1911 "
                "году). Финансирует медсестёр Macmillan — специализированных "
                "онкологических медсестёр в системе NHS, ведёт бесплатную "
                "линию поддержки, предоставляет гранты на дорогу и бытовые "
                "расходы пациентам на лечении, выпускает материалы для "
                "пациентов по всем видам рака. Охватывает около 2,3 млн "
                "человек с онкологией в Великобритании ежегодно."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.macmillan.org.uk/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("315000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1911,
        "cause_slugs": ["cancer-research", "hospice-palliative"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("261017"),
    },
    # ----- Marie Curie (UK) -----
    {
        "slug": "marie-curie-uk",
        "country": "GB",
        "registration_id": "207994",
        "bucket": "people",
        "name": {
            "en": "Marie Curie",
            "ru": "Marie Curie — британский фонд паллиативной помощи",
        },
        "tagline": {
            "en": "End-of-life care, hospice services and bereavement support across the UK",
            "ru": "Уход в конце жизни, хосписы и поддержка близких в горе по всей Великобритании",
        },
        "description": {
            "en": (
                "Marie Curie is the UK's leading charity for people living "
                "with terminal illness (Charity Commission #207994, founded "
                "1948). Operates 9 Marie Curie hospices, sends specially "
                "trained nurses into people's homes to provide overnight "
                "care, runs a free national Support Line, funds palliative-"
                "care research, and offers free bereavement support. Cares "
                "for ~40K people every year across all four UK nations."
            ),
            "ru": (
                "Marie Curie — ведущая британская благотворительная "
                "организация по уходу за людьми с неизлечимыми "
                "заболеваниями (Charity Commission #207994, основана в 1948 "
                "году). Управляет 9 хосписами Marie Curie, направляет "
                "специально обученных медсестёр в дома пациентов для "
                "ночного ухода, ведёт бесплатную национальную линию "
                "поддержки, финансирует исследования в области "
                "паллиативной помощи, оказывает бесплатную поддержку в "
                "случае утраты. Помогает около 40 тыс. человек ежегодно во "
                "всех четырёх странах Соединённого Королевства."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.mariecurie.org.uk/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("210000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1948,
        "cause_slugs": ["hospice-palliative", "cancer-research"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("207994"),
    },
    # ----- Cancer Research UK -----
    {
        "slug": "cancer-research-uk",
        "country": "GB",
        "registration_id": "1089464",
        "bucket": "people",
        "name": {
            "en": "Cancer Research UK",
            "ru": "Cancer Research UK",
        },
        "tagline": {
            "en": "World's largest independent cancer research charity",
            "ru": "Крупнейшая в мире независимая благотворительная организация по исследованию рака",
        },
        "description": {
            "en": (
                "Cancer Research UK is the world's largest independent "
                "funder of cancer research (Charity Commission #1089464; "
                "formed in 2002 by the merger of Cancer Research Campaign "
                "and Imperial Cancer Research Fund). Funds the work of ~4K "
                "scientists, doctors and nurses across the UK; supports the "
                "Francis Crick Institute and the CRUK Cambridge Institute; "
                "runs nationwide cancer-awareness campaigns; advocates for "
                "evidence-based cancer policy."
            ),
            "ru": (
                "Cancer Research UK — крупнейший в мире независимый "
                "финансист исследований рака (Charity Commission #1089464; "
                "образована в 2002 году слиянием Cancer Research Campaign и "
                "Imperial Cancer Research Fund). Финансирует работу около "
                "4 тыс. учёных, врачей и медсестёр по Великобритании, "
                "поддерживает Francis Crick Institute и CRUK Cambridge "
                "Institute, ведёт национальные кампании по информированию о "
                "раке, лоббирует доказательную онкологическую политику."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.cancerresearchuk.org/get-involved/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("875000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 2002,
        "cause_slugs": ["cancer-research"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("1089464"),
    },
    # ----- Samaritans (UK) -----
    {
        "slug": "samaritans-uk",
        "country": "GB",
        "registration_id": "219432",
        "bucket": "people",
        "name": {
            "en": "Samaritans",
            "ru": "Samaritans — британская служба эмоциональной поддержки",
        },
        "tagline": {
            "en": "24/7 listening service for anyone in emotional distress, UK & Ireland",
            "ru": "Круглосуточная служба эмоциональной поддержки в Великобритании и Ирландии",
        },
        "description": {
            "en": (
                "Samaritans is a UK charity (Charity Commission #219432, "
                "founded 1953) operating a free 24/7 phone listening service "
                "for anyone experiencing emotional distress, struggling to "
                "cope, or at risk of suicide. Volunteers in 200+ branches "
                "across the UK and Ireland answer a call every 10 seconds; "
                "the charity also runs prison support, school programmes, "
                "rail-network suicide-prevention partnerships and "
                "research-driven media-reporting guidelines."
            ),
            "ru": (
                "Samaritans — британская благотворительная организация "
                "(Charity Commission #219432, основана в 1953 году), ведёт "
                "бесплатную круглосуточную телефонную службу поддержки для "
                "всех, кто переживает эмоциональный кризис, не справляется "
                "или находится в группе риска суицида. Волонтёры более чем "
                "200 отделений в Великобритании и Ирландии принимают звонок "
                "каждые 10 секунд; организация также работает в тюрьмах и "
                "школах, ведёт партнёрства с железнодорожной сетью по "
                "профилактике суицидов и публикует научно-обоснованные "
                "рекомендации СМИ."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.samaritans.org/donate-now/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 10, 31),
        "total_revenue_usd": Decimal("32000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1953,
        "cause_slugs": ["mental-health", "suicide-prevention"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("219432"),
    },
    # ----- Anthony Nolan (UK) -----
    {
        "slug": "anthony-nolan",
        "country": "GB",
        "registration_id": "803716",
        "bucket": "people",
        "name": {
            "en": "Anthony Nolan",
            "ru": "Anthony Nolan",
        },
        "tagline": {
            "en": "Matches stem-cell donors with people in need of bone-marrow transplants",
            "ru": "Подбирает доноров стволовых клеток для людей, нуждающихся в трансплантации костного мозга",
        },
        "description": {
            "en": (
                "Anthony Nolan is a UK charity (Charity Commission #803716, "
                "founded 1974 — the world's first bone-marrow donor "
                "register). Recruits stem-cell donors aged 16-30 onto its "
                "register, provides matched donors to UK transplant centres "
                "for people with blood cancers and blood disorders, runs a "
                "Cell & Gene Therapy Service, and conducts research at the "
                "Anthony Nolan Research Institute in London."
            ),
            "ru": (
                "Anthony Nolan — британская благотворительная организация "
                "(Charity Commission #803716, основана в 1974 году — "
                "первый в мире реестр доноров костного мозга). Привлекает "
                "доноров стволовых клеток 16-30 лет в свой реестр, "
                "предоставляет подобранных доноров британским "
                "трансплантационным центрам для пациентов с раком крови и "
                "заболеваниями крови, ведёт Cell & Gene Therapy Service и "
                "проводит исследования в Anthony Nolan Research Institute "
                "в Лондоне."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.anthonynolan.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("65000000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1974,
        "cause_slugs": ["blood-cancer", "cancer-research"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("803716"),
    },
    # ===================== DISABILITY (5) =====================
    # ----- Special Olympics -----
    {
        "slug": "special-olympics",
        "country": "US",
        "registration_id": "520889518",
        "bucket": "people",
        "name": {
            "en": "Special Olympics",
            "ru": "Special Olympics",
        },
        "tagline": {
            "en": "Year-round sports training and competition for people with intellectual disabilities",
            "ru": "Круглогодичные спортивные тренировки и соревнования для людей с нарушениями развития",
        },
        "description": {
            "en": (
                "Special Olympics is a US 501(c)(3) (founded 1968 by Eunice "
                "Kennedy Shriver) providing year-round sports training and "
                "competition for children and adults with intellectual "
                "disabilities. Operates in 190+ countries with 5M+ athletes "
                "and 1M+ coaches and volunteers; runs the World Games, "
                "Unified Sports (athletes with and without IDD on the same "
                "team) and a Healthy Athletes screening programme."
            ),
            "ru": (
                "Special Olympics — американская 501(c)(3) (основана в "
                "1968 году Юнис Кеннеди Шрайвер), круглогодичные спортивные "
                "тренировки и соревнования для детей и взрослых с "
                "нарушениями развития. Работает в 190+ странах: 5+ млн "
                "атлетов и 1+ млн тренеров и волонтёров. Проводит Всемирные "
                "игры, программу Unified Sports (спортсмены с нарушениями "
                "развития и без них в одной команде) и программу "
                "медицинских скринингов Healthy Athletes."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://www.specialolympics.org/ways-to-give/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("160000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1968,
        "cause_slugs": [
            "disability-services",
            "intellectual-disability-sport",
        ],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("520889518"),
    },
    # ----- United Cerebral Palsy -----
    {
        "slug": "united-cerebral-palsy",
        "country": "US",
        "registration_id": "131947690",
        "bucket": "people",
        "name": {
            "en": "United Cerebral Palsy",
            "ru": "United Cerebral Palsy",
        },
        "tagline": {
            "en": "Independence and inclusion for people with cerebral palsy and other disabilities",
            "ru": "Самостоятельность и инклюзия для людей с ДЦП и другими нарушениями",
        },
        "description": {
            "en": (
                "United Cerebral Palsy (UCP) is a US 501(c)(3) (founded "
                "1949) supporting people with cerebral palsy and a wider "
                "range of disabilities. Federation of ~50 affiliates across "
                "the US delivering early intervention, independent-living "
                "support, employment services and housing; national office "
                "leads federal policy advocacy on Medicaid, the ADA and "
                "long-term services and supports."
            ),
            "ru": (
                "United Cerebral Palsy (UCP) — американская 501(c)(3) "
                "(основана в 1949 году) для людей с детским церебральным "
                "параличом и более широким кругом нарушений. Федерация "
                "около 50 региональных отделений в США: раннее "
                "вмешательство, поддержка самостоятельной жизни, "
                "трудоустройство и жильё; центральный офис ведёт "
                "национальную адвокацию по Medicaid, ADA и долгосрочной "
                "поддержке."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://ucp.org/donate/",
        "size_bucket": "medium",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("8000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1949,
        "cause_slugs": ["disability-services", "cerebral-palsy"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("131947690"),
    },
    # ----- RNIB (UK) -----
    {
        "slug": "rnib",
        "country": "GB",
        "registration_id": "226227",
        "bucket": "people",
        "name": {
            "en": "Royal National Institute of Blind People (RNIB)",
            "ru": "Royal National Institute of Blind People (RNIB)",
        },
        "tagline": {
            "en": "UK's leading charity for blind and partially sighted people",
            "ru": "Ведущая благотворительная организация Великобритании для незрячих и слабовидящих людей",
        },
        "description": {
            "en": (
                "RNIB is the UK's leading charity for blind and partially "
                "sighted people (Charity Commission #226227, founded 1868). "
                "Operates a national Helpline, runs RNIB Talking Books "
                "(largest free audiobook library in the UK for blind "
                "readers), produces Braille and large-print materials, "
                "supports children with vision impairment in mainstream "
                "schools, and campaigns for accessible transport, services "
                "and digital products."
            ),
            "ru": (
                "RNIB — ведущая благотворительная организация Великобритании "
                "для незрячих и слабовидящих людей (Charity Commission "
                "#226227, основана в 1868 году). Ведёт национальную "
                "горячую линию, RNIB Talking Books (крупнейшая в "
                "Великобритании бесплатная аудиокнижная библиотека для "
                "незрячих читателей), выпускает материалы шрифтом Брайля и "
                "крупным шрифтом, поддерживает детей с нарушением зрения в "
                "обычных школах, лоббирует доступный транспорт, услуги и "
                "цифровые продукты."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.rnib.org.uk/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 9, 30),
        "total_revenue_usd": Decimal("105000000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1868,
        "cause_slugs": ["disability-services", "blindness"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("226227"),
    },
    # ----- Sense (UK) -----
    {
        "slug": "sense-uk",
        "country": "GB",
        "registration_id": "289868",
        "bucket": "people",
        "name": {
            "en": "Sense",
            "ru": "Sense — британская организация поддержки слепоглухих людей",
        },
        "tagline": {
            "en": "UK charity for people with complex disabilities, including deafblindness",
            "ru": "Британская благотворительная организация для людей с комплексными нарушениями, в том числе слепоглухих",
        },
        "description": {
            "en": (
                "Sense is a UK charity (Charity Commission #289868, founded "
                "1955) supporting people with complex disabilities, "
                "particularly those who are deafblind or have sensory "
                "impairments combined with other needs. Provides specialist "
                "communication support, residential care services, "
                "intervenor services for children, holidays and short "
                "breaks, and disability-rights campaigning across England, "
                "Wales and Northern Ireland."
            ),
            "ru": (
                "Sense — британская благотворительная организация (Charity "
                "Commission #289868, основана в 1955 году) для людей с "
                "комплексными нарушениями, прежде всего слепоглухих и "
                "людей с сенсорными нарушениями в сочетании с другими "
                "потребностями. Специализированная поддержка коммуникации, "
                "стационарные социальные службы, услуги intervenor для "
                "детей, отдых и короткие перерывы, защита прав инвалидов в "
                "Англии, Уэльсе и Северной Ирландии."
            ),
        },
        "methodology_note": _verify_note_uk(),
        "logo_url": "",
        "donation_url": "https://www.sense.org.uk/get-involved/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 6, 30),
        "total_revenue_usd": Decimal("85000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1955,
        "cause_slugs": ["disability-services", "deafblind"],
        **_empty_photo(),
        "source_kind": "annual_report",
        "source_url": _uk_cc("289868"),
    },
    # ----- Disability Rights Education and Defense Fund (DREDF) -----
    {
        "slug": "dredf",
        "country": "US",
        "registration_id": "942780521",
        "bucket": "people",
        "name": {
            "en": "Disability Rights Education and Defense Fund",
            "ru": "Disability Rights Education and Defense Fund",
        },
        "tagline": {
            "en": "Civil-rights law firm advancing the rights of people with disabilities",
            "ru": "Правозащитная юридическая организация по защите прав людей с инвалидностью",
        },
        "description": {
            "en": (
                "DREDF is a US 501(c)(3) (founded 1979 in Berkeley, CA) "
                "national disability-rights law and policy organisation "
                "led by people with disabilities and parents of children "
                "with disabilities. Litigates landmark federal cases under "
                "the ADA, Section 504 and IDEA; trains lawyers and "
                "self-advocates; advises on disability-rights policy at "
                "federal and state level; runs a Special Education Clinic."
            ),
            "ru": (
                "DREDF — американская 501(c)(3) (основана в 1979 году в "
                "Беркли, Калифорния), национальная правозащитная и "
                "политическая организация в области прав людей с "
                "инвалидностью, под руководством людей с инвалидностью и "
                "родителей детей с инвалидностью. Ведёт знаковые "
                "федеральные дела по ADA, Section 504 и IDEA, обучает "
                "юристов и самозащитников, консультирует по политике в "
                "области прав инвалидов на федеральном уровне и уровне "
                "штатов, ведёт клинику по специальному образованию."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://dredf.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("4500000.00"),
        "program_expense_pct": Decimal("80.00"),
        "founded_year": 1979,
        "cause_slugs": ["disability-services", "civil-rights"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("942780521"),
    },
    # ===================== MENTAL HEALTH (5) =====================
    # ----- American Foundation for Suicide Prevention (AFSP) -----
    {
        "slug": "afsp",
        "country": "US",
        "registration_id": "133393329",
        "bucket": "people",
        "name": {
            "en": "American Foundation for Suicide Prevention",
            "ru": "American Foundation for Suicide Prevention (AFSP)",
        },
        "tagline": {
            "en": "Saves lives by funding suicide-prevention research and supporting those affected",
            "ru": "Спасает жизни через исследования профилактики суицида и поддержку пострадавших",
        },
        "description": {
            "en": (
                "AFSP is a US 501(c)(3) (founded 1987) — the largest "
                "private funder of suicide-prevention research in the US. "
                "Funds research grants, runs the Out of the Darkness "
                "community walks (300+ events / year), provides loss-survivor "
                "support, trains educators and clinicians in evidence-based "
                "prevention programmes (e.g., Talk Saves Lives), and "
                "advocates for federal mental-health and 988 Lifeline funding."
            ),
            "ru": (
                "AFSP — американская 501(c)(3) (основана в 1987 году), "
                "крупнейший частный финансист исследований профилактики "
                "суицида в США. Финансирует исследовательские гранты, "
                "проводит общественные марши Out of the Darkness (300+ "
                "событий в год), поддерживает близких ушедших, обучает "
                "педагогов и клиницистов доказательным программам "
                "профилактики (например, Talk Saves Lives), ведёт адвокацию "
                "федерального финансирования психического здоровья и линии "
                "988."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://afsp.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("44000000.00"),
        "program_expense_pct": Decimal("82.00"),
        "founded_year": 1987,
        "cause_slugs": ["mental-health", "suicide-prevention"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("133393329"),
    },
    # ----- Active Minds -----
    {
        "slug": "active-minds",
        "country": "US",
        "registration_id": "352229543",
        "bucket": "people",
        "name": {
            "en": "Active Minds",
            "ru": "Active Minds",
        },
        "tagline": {
            "en": "Youth-led mental-health awareness on US high-school and college campuses",
            "ru": "Молодёжная просветительская работа по психическому здоровью в школах и колледжах США",
        },
        "description": {
            "en": (
                "Active Minds is a US 501(c)(3) (founded 2003) running the "
                "largest youth-led mental-health movement in the US, with "
                "600+ student-led chapters on high-school and college "
                "campuses. Equips young people to start campus conversations "
                "on mental health, hosts the travelling Send Silence "
                "Packing exhibit on suicide loss, and runs evidence-based "
                "Active Minds Speakers and V-A-R (Validate, Appreciate, "
                "Refer) trainings."
            ),
            "ru": (
                "Active Minds — американская 501(c)(3) (основана в 2003 "
                "году), крупнейшее в США молодёжное движение в области "
                "психического здоровья, более 600 студенческих отделений в "
                "школах и колледжах. Учит молодых людей вести разговор о "
                "психическом здоровье на кампусах, ведёт передвижную "
                "выставку Send Silence Packing об ушедших из-за суицида, "
                "проводит доказательные тренинги Active Minds Speakers и "
                "V-A-R (Validate, Appreciate, Refer)."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://www.activeminds.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("9500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2003,
        "cause_slugs": ["mental-health", "suicide-prevention"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("352229543"),
    },
    # ----- Brain & Behavior Research Foundation -----
    {
        "slug": "bbrf",
        "country": "US",
        "registration_id": "311020010",
        "bucket": "people",
        "name": {
            "en": "Brain & Behavior Research Foundation",
            "ru": "Brain & Behavior Research Foundation",
        },
        "tagline": {
            "en": "Funds psychiatric research grants — 100% of donations to grants",
            "ru": "Финансирует гранты на психиатрические исследования — 100% пожертвований идёт на гранты",
        },
        "description": {
            "en": (
                "BBRF is a US 501(c)(3) (founded 1987 as NARSAD) funding "
                "scientific research on psychiatric and neurological "
                "conditions including schizophrenia, depression, bipolar "
                "disorder, anxiety, autism and PTSD. Awards Young "
                "Investigator, Independent Investigator and Distinguished "
                "Investigator grants reviewed by a 191-member Scientific "
                "Council that includes Nobel laureates. Operating costs "
                "covered separately so 100% of donations fund research."
            ),
            "ru": (
                "BBRF — американская 501(c)(3) (основана в 1987 году как "
                "NARSAD), финансирует научные исследования психических и "
                "неврологических заболеваний — шизофрении, депрессии, "
                "биполярного расстройства, тревожных расстройств, аутизма "
                "и ПТСР. Выдаёт гранты Young Investigator, Independent "
                "Investigator и Distinguished Investigator под рецензией "
                "Scientific Council из 191 учёного, включая нобелевских "
                "лауреатов. Операционные расходы покрываются отдельно — "
                "100% пожертвований идёт на исследования."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://www.bbrfoundation.org/donate",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("36000000.00"),
        "program_expense_pct": Decimal("90.00"),
        "founded_year": 1987,
        "cause_slugs": ["mental-health", "neuroscience-research"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("311020010"),
    },
    # ----- Anxiety and Depression Association of America (ADAA) -----
    {
        "slug": "adaa",
        "country": "US",
        "registration_id": "521248820",
        "bucket": "people",
        "name": {
            "en": "Anxiety and Depression Association of America",
            "ru": "Anxiety and Depression Association of America (ADAA)",
        },
        "tagline": {
            "en": "Patient-facing education and clinician finder for anxiety & depression",
            "ru": "Просвещение пациентов и поиск врачей для тревожных расстройств и депрессии",
        },
        "description": {
            "en": (
                "ADAA is a US 501(c)(3) (founded 1980) advancing prevention, "
                "treatment and cure of anxiety, depression and co-occurring "
                "disorders. Maintains a free public Find-A-Therapist "
                "directory of licensed clinicians, publishes peer-reviewed "
                "patient education and the journal Depression & Anxiety, "
                "supports clinical research training, and runs an annual "
                "international conference for researchers and clinicians."
            ),
            "ru": (
                "ADAA — американская 501(c)(3) (основана в 1980 году), "
                "развивает профилактику, лечение и поиск лекарств для "
                "тревожных расстройств, депрессии и сопутствующих "
                "состояний. Ведёт бесплатный публичный каталог Find-A-"
                "Therapist лицензированных клиницистов, публикует "
                "рецензированные материалы для пациентов и журнал "
                "Depression & Anxiety, поддерживает обучение клинических "
                "исследователей, проводит ежегодную международную "
                "конференцию для исследователей и клиницистов."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://adaa.org/donate",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("3200000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 1980,
        "cause_slugs": ["mental-health", "anxiety-depression"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("521248820"),
    },
    # ----- To Write Love On Her Arms (TWLOHA) -----
    {
        "slug": "twloha",
        "country": "US",
        "registration_id": "205527077",
        "bucket": "people",
        "name": {
            "en": "To Write Love on Her Arms",
            "ru": "To Write Love on Her Arms (TWLOHA)",
        },
        "tagline": {
            "en": "Hope and help for people struggling with depression, addiction, self-injury and suicide",
            "ru": "Поддержка людей с депрессией, зависимостями, самоповреждением и суицидальными мыслями",
        },
        "description": {
            "en": (
                "TWLOHA is a US 501(c)(3) (founded 2006 in Florida) "
                "providing connection, encouragement and resources for "
                "people facing depression, addiction, self-injury and "
                "suicide. Runs a free Treatment & Recovery Scholarship "
                "Program funding therapy for people who can't otherwise "
                "afford it, maintains FIND HELP — a global directory of "
                "mental-health resources, partners with universities and "
                "music tours to reach young people who don't see themselves "
                "in clinical mental-health messaging."
            ),
            "ru": (
                "TWLOHA — американская 501(c)(3) (основана в 2006 году во "
                "Флориде), создаёт связь, поддержку и ресурсы для людей с "
                "депрессией, зависимостями, самоповреждением и "
                "суицидальными мыслями. Бесплатная программа Treatment & "
                "Recovery Scholarship оплачивает терапию людям, которые "
                "иначе не могут её себе позволить, ведёт FIND HELP — "
                "глобальный каталог ресурсов в области психического "
                "здоровья, работает с университетами и музыкальными турами, "
                "чтобы достучаться до молодых людей, которым не близок "
                "клинический язык."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://twloha.com/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("3500000.00"),
        "program_expense_pct": Decimal("75.00"),
        "founded_year": 2006,
        "cause_slugs": [
            "mental-health",
            "suicide-prevention",
            "anxiety-depression",
        ],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("205527077"),
    },
    # ===================== INTERNATIONAL — US AFFILIATES (4) =====================
    # ----- Oxfam America -----
    {
        "slug": "oxfam-america",
        "country": "US",
        "registration_id": "237069110",
        "bucket": "people",
        "name": {
            "en": "Oxfam America",
            "ru": "Oxfam America",
        },
        "tagline": {
            "en": "US 501(c)(3) of the Oxfam confederation — fights global poverty and inequality",
            "ru": "Американская 501(c)(3) конфедерации Oxfam — борьба с глобальной бедностью и неравенством",
        },
        "description": {
            "en": (
                "Oxfam America is the US 501(c)(3) member of the Oxfam "
                "confederation (a federation of 21 affiliate organisations "
                "operating in 80+ countries). Programs include emergency "
                "response in crises, long-term resilience and livelihoods "
                "work, gender-justice programmes, climate-justice campaigns, "
                "and US-side advocacy on aid, taxation and corporate "
                "accountability. Headquartered in Boston, MA. Distinct from "
                "the UK-registered Oxfam GB."
            ),
            "ru": (
                "Oxfam America — американский член 501(c)(3) конфедерации "
                "Oxfam (федерация из 21 аффилированной организации, работа "
                "в 80+ странах). Программы: экстренное реагирование на "
                "кризисы, долгосрочные программы устойчивости и "
                "благосостояния, гендерное правосудие, климатическое "
                "правосудие, адвокация в США по вопросам помощи, "
                "налогообложения и корпоративной ответственности. "
                "Штаб-квартира в Бостоне. Отдельно от британской Oxfam GB."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://www.oxfamamerica.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("105000000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 1970,
        "cause_slugs": [
            "poverty-reduction",
            "emergency-response",
            "womens-rights",
        ],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("237069110"),
    },
    # ----- International Medical Corps -----
    {
        "slug": "international-medical-corps",
        "country": "US",
        "registration_id": "953949646",
        "bucket": "people",
        "name": {
            "en": "International Medical Corps",
            "ru": "International Medical Corps",
        },
        "tagline": {
            "en": "Emergency medical response and health-system rebuilding in conflict and disaster zones",
            "ru": "Экстренная медицинская помощь и восстановление систем здравоохранения в зонах конфликтов и бедствий",
        },
        "description": {
            "en": (
                "International Medical Corps is a US 501(c)(3) (founded "
                "1984) deploying emergency-medical and public-health teams "
                "to conflict zones and natural disasters in 30+ countries. "
                "Trains local medical staff so capacity stays once IMC "
                "leaves; runs primary healthcare clinics, mental-health and "
                "psychosocial-support programmes, water-and-sanitation "
                "infrastructure, and gender-based-violence response. "
                "Headquartered in Los Angeles, CA."
            ),
            "ru": (
                "International Medical Corps — американская 501(c)(3) "
                "(основана в 1984 году), направляет команды экстренной "
                "медицинской и санитарной помощи в зоны конфликтов и "
                "природных катастроф в 30+ стран. Обучает местный "
                "медицинский персонал, чтобы потенциал оставался после "
                "ухода IMC: первичные клиники, программы психического "
                "здоровья и психосоциальной поддержки, водоснабжение и "
                "санитария, реагирование на гендерное насилие. "
                "Штаб-квартира в Лос-Анджелесе."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://internationalmedicalcorps.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("190000000.00"),
        "program_expense_pct": Decimal("89.00"),
        "founded_year": 1984,
        "cause_slugs": [
            "global-health",
            "emergency-response",
            "humanitarian-medicine",
        ],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("953949646"),
    },
    # ----- HelpAge USA -----
    {
        "slug": "helpage-usa",
        "country": "US",
        "registration_id": "133445198",
        "bucket": "people",
        "name": {
            "en": "HelpAge USA",
            "ru": "HelpAge USA",
        },
        "tagline": {
            "en": "US 501(c)(3) for the global rights and well-being of older people",
            "ru": "Американская 501(c)(3) по защите прав и благополучия пожилых людей в мире",
        },
        "description": {
            "en": (
                "HelpAge USA is a US 501(c)(3) (founded 2010) and the US "
                "affiliate of the HelpAge global network — a federation of "
                "118+ member organisations in 85+ countries working on the "
                "rights and well-being of older people. Funds programmes "
                "across the network covering social protection, age-"
                "inclusive humanitarian response, and health and care for "
                "older people in low- and middle-income countries; "
                "advocates at the UN for a Convention on the Rights of "
                "Older Persons."
            ),
            "ru": (
                "HelpAge USA — американская 501(c)(3) (основана в 2010 "
                "году), американский филиал глобальной сети HelpAge — "
                "федерации из 118+ организаций-членов в 85+ странах, "
                "работающих над правами и благополучием пожилых людей. "
                "Финансирует программы сети по социальной защите, "
                "возрастно-инклюзивной гуманитарной помощи, здоровью и "
                "уходу за пожилыми людьми в странах с низким и средним "
                "уровнем доходов; ведёт адвокацию в ООН за Конвенцию о "
                "правах пожилых людей."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://www.helpageusa.org/donate/",
        "size_bucket": "small",
        "last_filed_date": date(2024, 5, 14),
        "total_revenue_usd": Decimal("1500000.00"),
        "program_expense_pct": Decimal("78.00"),
        "founded_year": 2010,
        "cause_slugs": ["senior-care", "poverty-reduction"],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("133445198"),
    },
    # ----- Catholic Medical Mission Board (CMMB) -----
    {
        "slug": "cmmb",
        "country": "US",
        "registration_id": "135602340",
        "bucket": "people",
        "name": {
            "en": "Catholic Medical Mission Board",
            "ru": "Catholic Medical Mission Board (CMMB)",
        },
        "tagline": {
            "en": "Faith-based 501(c)(3) delivering healthcare and medical aid to vulnerable communities",
            "ru": "Религиозная 501(c)(3) — медицинская помощь уязвимым сообществам в мире",
        },
        "description": {
            "en": (
                "CMMB is a US 501(c)(3) (founded 1912 in New York) and one "
                "of the longest-running US-based global health charities. "
                "Operates long-term country programmes in Haiti, Kenya, "
                "Peru, South Sudan and Zambia focused on women's and "
                "children's health, runs the CHAMPS (Children and Mothers "
                "Partnerships) programme, ships donated medicines and "
                "medical supplies to under-resourced clinics worldwide, and "
                "places medical volunteers in partner facilities."
            ),
            "ru": (
                "CMMB — американская 501(c)(3) (основана в 1912 году в "
                "Нью-Йорке), одна из старейших глобальных медицинских "
                "благотворительных организаций США. Ведёт долгосрочные "
                "страновые программы в Гаити, Кении, Перу, Южном Судане и "
                "Замбии с фокусом на здоровье женщин и детей, программу "
                "CHAMPS (Children and Mothers Partnerships), доставляет "
                "пожертвованные лекарства и расходные материалы в "
                "клиники с ограниченными ресурсами, направляет медицинских "
                "волонтёров в партнёрские учреждения."
            ),
        },
        "methodology_note": _verify_note_us(),
        "logo_url": "",
        "donation_url": "https://cmmb.org/donate/",
        "size_bucket": "large",
        "last_filed_date": date(2024, 11, 14),
        "total_revenue_usd": Decimal("400000000.00"),
        "program_expense_pct": Decimal("96.00"),
        "founded_year": 1912,
        "cause_slugs": [
            "global-health",
            "humanitarian-medicine",
            "faith-based",
        ],
        **_empty_photo(),
        "source_kind": "irs_990",
        "source_url": _us_pp("135602340"),
    },
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
            "IRS Form 990, FY 2023 (ProPublica)"
            if entry["country"] == "US"
            else "Annual report & accounts (Charity Commission UK)"
        ),
    }


def _source_doc(entry: dict) -> dict:
    if entry["country"] == "US":
        return {
            "kind": "irs_990",
            "filed_date": entry["last_filed_date"],
            "label": {
                "en": "IRS Form 990 (FY 2023)",
                "ru": "Налоговая форма IRS 990 (2023)",
            },
            "url": entry["source_url"],
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
        "url": entry["source_url"],
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
                f"[migration 0035] BLOCKED {entry['slug']} "
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

    total = Charity.objects.count()
    print(
        f"[migration 0035] new charities upserted: {upserted}, "
        f"blocked: {skipped_blocked}, total in DB now: {total}"
    )


def backwards(apps, schema_editor):
    """No-op. Never auto-delete real curated rows on rollback."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0034_extend_hero_photo_url_to_500"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

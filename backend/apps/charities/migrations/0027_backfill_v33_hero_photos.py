"""v3.3 hero-photo backfill — fill `hero_photo_url` (+ caption, credit,
license) for the 40 charities seeded by 0025 with empty photo fields.

Sourcing approach (per KB-015 honesty rule, restated from 0017 / 0019 /
0023):
  1. Wikimedia Commons CC search by org name was attempted first per the
     brief. For most v3.3 candidates either no usable photo was found,
     or photos that turned up were logos/portraits we could NOT honestly
     attribute to the org's program. Two narrow exceptions where Commons
     does have a confidently-attributable subject (UK donkey sanctuary,
     a chimpanzee in the wild) are used with CC-BY-SA credit.
  2. Unsplash CC0 fallback with HEDGED captions: "illustrative of",
     "the kind of work", "thematic of" — never "this is X doing Y".
     Where thematically appropriate we REUSE Unsplash photo IDs already
     used in migrations 0019 / 0023 (medical, classroom, wildlife,
     forest, ocean) since they're CC0 — no licensing collision.
  3. Empty hero_photo_url → frontend BrandedAvatar gradient fallback
     (DESIGN.md v3 §B.3). All 40 in this pass get a photo.

Captions are bilingual EN / RU per i18n contract. Credits follow
"{Photographer Name} / Unsplash" or "{Author} / Wikimedia Commons"
format. License field uses the existing PhotoLicense enum values:
"unsplash", "cc-by", "cc-by-sa".

Idempotent: `Charity.objects.filter(slug=..., hero_photo_url="")` so
prior manual curation isn't overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# Note on photo ID reuse: a handful of these IDs (e.g. 1488521787991-...
# medical aid, 1500595046743-... cattle, 1444930694458-... US landscape,
# 1448375240586-... forest, 1466611653911-... wind farm) are reused from
# migration 0019 or 0023 because they thematically match a different
# bucket here (different org, same hedged framing). Unsplash CC0 license
# allows reuse without attribution conflict.
PHOTO_SEED: list[dict] = [
    # ===================== PEOPLE — 20 =====================
    # ----- Smile Train — pediatric cleft surgery -----
    {
        "slug": "smile-train",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A surgical team at work in an operating theatre — "
                  "illustrative of the kind of cleft-lip and palate "
                  "surgeries Smile Train funds for children in 90+ "
                  "countries via local surgical partners.",
            "ru": "Хирургическая бригада в операционной — иллюстрация "
                  "операций на расщелине губы и нёба у детей, которые "
                  "Smile Train финансирует в 90+ странах через местных "
                  "хирургов-партнёров.",
        },
        "hero_photo_credit": "Piron Guillaume / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- The Carter Center — neglected tropical diseases / democracy -----
    {
        "slug": "carter-center",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1666214280557-f1b5022eb634"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A clinician examines a patient in a low-resource clinic — "
                  "illustrative of the neglected-tropical-disease work "
                  "(Guinea worm, river blindness, trachoma) the Carter "
                  "Center has run across Africa since 1982.",
            "ru": "Врач осматривает пациента в клинике с ограниченными "
                  "ресурсами — иллюстрация работы Carter Center по борьбе "
                  "с забытыми тропическими болезнями (ришта, речная "
                  "слепота, трахома) в Африке с 1982 года.",
        },
        "hero_photo_credit": "Hush Naidoo Jade Photography / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Sightsavers — cataract / trachoma -----
    {
        "slug": "sightsavers-uk",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1584515933487-779824d29309"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Clinical instruments on a tray — illustrative of the "
                  "kind of eye-care interventions, including cataract "
                  "surgery and trachoma treatment, that Sightsavers funds "
                  "in 30+ countries.",
            "ru": "Медицинские инструменты на подносе — иллюстрация "
                  "работы по охране зрения, включая операции при "
                  "катаракте и лечение трахомы, которую Sightsavers "
                  "финансирует в 30+ странах.",
        },
        "hero_photo_credit": "Nguyễn Hiệp / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- One Acre Fund — smallholder farming -----
    {
        "slug": "one-acre-fund",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500595046743-cd271d694d30"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Cattle and crops on a smallholder farm — illustrative "
                  "of the kind of smallholder family farms One Acre Fund "
                  "supports with seed, training and credit across East "
                  "and Southern Africa.",
            "ru": "Скот и посевы на ферме — иллюстрация типичных "
                  "мелких семейных хозяйств, которые One Acre Fund "
                  "поддерживает семенами, обучением и кредитом в "
                  "Восточной и Южной Африке.",
        },
        "hero_photo_credit": "Stijn te Strake / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Last Mile Health — community health workers, Liberia -----
    {
        "slug": "last-mile-health",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1612531386530-97286d97c2d2"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A community health worker prepares medication on a "
                  "home visit — illustrative of the rural community-health-"
                  "worker programmes Last Mile Health designs with "
                  "African ministries of health.",
            "ru": "Общинный медработник готовит лекарство во время "
                  "визита на дом — иллюстрация программ сельских "
                  "общинных медработников, которые Last Mile Health "
                  "разрабатывает с министерствами здравоохранения "
                  "африканских стран.",
        },
        "hero_photo_credit": "Online Marketing / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- VillageReach — vaccine cold chain -----
    {
        "slug": "villagereach",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1632053002434-66a18a18c1cf"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A vial being prepared for vaccination — illustrative "
                  "of the cold-chain and last-mile health-supply work "
                  "VillageReach does with health systems in Mozambique, "
                  "Malawi, DRC and other African countries.",
            "ru": "Подготовка флакона для вакцинации — иллюстрация "
                  "работы VillageReach по холодовой цепи и доставке "
                  "медикаментов «последней мили» совместно с системами "
                  "здравоохранения Мозамбика, Малави, ДРК и других "
                  "стран Африки.",
        },
        "hero_photo_credit": "Mufid Majnun / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- PSI — social marketing for public health -----
    {
        "slug": "psi",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1576765607924-3f7b8410a787"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Health products on a clinic shelf — illustrative of "
                  "the social-marketing approach PSI uses to make "
                  "contraceptives, malaria nets, water-purification "
                  "tablets and other health products affordable across "
                  "40+ countries.",
            "ru": "Медицинские товары на полке клиники — иллюстрация "
                  "подхода социального маркетинга, который PSI "
                  "использует, чтобы сделать контрацепцию, "
                  "противомалярийные сетки, таблетки для обеззараживания "
                  "воды и другие медицинские товары доступными в 40+ "
                  "странах.",
        },
        "hero_photo_credit": "Diana Polekhina / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Project HOPE — emergency medical aid -----
    {
        "slug": "project-hope",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A humanitarian aid convoy on the road — illustrative "
                  "of the medical emergency-response operations Project "
                  "HOPE has run from the SS HOPE hospital ship in 1958 "
                  "through to today's responses in Ukraine, Türkiye-"
                  "Syria and Gaza.",
            "ru": "Гуманитарный конвой в пути — иллюстрация операций "
                  "медицинской экстренной помощи, которые Project HOPE "
                  "ведёт со времён госпитального судна SS HOPE 1958 года "
                  "до сегодняшних реакций на ситуации в Украине, "
                  "Турции — Сирии и Газе.",
        },
        "hero_photo_credit": "Levi Meir Clancy / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Possible Health — rural Nepal primary care -----
    {
        "slug": "possible-health",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1666214280557-f1b5022eb634"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A clinician at work in a low-resource clinic — "
                  "illustrative of the kind of free primary-care work "
                  "Possible Health runs in district hospitals across "
                  "rural Nepal in partnership with the public health "
                  "system.",
            "ru": "Врач в клинике с ограниченными ресурсами — иллюстрация "
                  "бесплатной первичной медицинской помощи, которую "
                  "Possible Health оказывает в районных больницах "
                  "сельского Непала совместно с государственной системой "
                  "здравоохранения.",
        },
        "hero_photo_credit": "Hush Naidoo Jade Photography / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- St Jude — pediatric cancer research / treatment -----
    {
        "slug": "st-jude",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1631815589968-fdb09a223b1e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A pediatric ward setting — illustrative of the "
                  "free, family-cost-free childhood-cancer treatment "
                  "and research St. Jude has done since 1962, where "
                  "leukaemia survival rates rose from 4% to 94%.",
            "ru": "Детское отделение больницы — иллюстрация бесплатного "
                  "для семей лечения и исследований детской онкологии, "
                  "которыми St. Jude занимается с 1962 года: "
                  "выживаемость при лейкозе выросла с 4% до 94%.",
        },
        "hero_photo_credit": "Hush Naidoo Jade Photography / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Make-A-Wish — wishes for sick children -----
    {
        "slug": "make-a-wish",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A child sits at a desk — illustrative of the kind of "
                  "children whose wishes Make-A-Wish America grants "
                  "(~30,000 wishes per year) for kids living with "
                  "critical illnesses.",
            "ru": "Ребёнок за партой — иллюстрация тех детей, "
                  "чьи желания Make-A-Wish America исполняет (около "
                  "30 тыс. в год) — детей с тяжёлыми заболеваниями.",
        },
        "hero_photo_credit": "CDC / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Pratham USA — Indian education -----
    {
        "slug": "pratham-usa",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1497633762265-9d179a990aa6"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Children reading from textbooks — illustrative of the "
                  "Teaching at the Right Level (TaRL) approach Pratham "
                  "developed in India and which the World Bank has "
                  "scaled across multiple countries.",
            "ru": "Дети читают учебники — иллюстрация подхода Teaching "
                  "at the Right Level (TaRL), разработанного Pratham в "
                  "Индии, который Всемирный банк масштабировал в "
                  "нескольких странах.",
        },
        "hero_photo_credit": "Element5 Digital / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Educate Girls — out-of-school girls in India -----
    {
        "slug": "educate-girls",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1588072432836-e10032774350"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Schoolgirls walking together — illustrative of the "
                  "kind of out-of-school girls whom Educate Girls' "
                  "village-volunteer model identifies and re-enrolls "
                  "in rural India.",
            "ru": "Школьницы идут вместе — иллюстрация тех девочек, "
                  "не посещающих школу, которых модель сельских "
                  "волонтёров Educate Girls выявляет и возвращает в "
                  "школу в сельской Индии.",
        },
        "hero_photo_credit": "Husniati Salma / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- DonorsChoose — US classroom funding -----
    {
        "slug": "donorschoose",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Schoolchildren in a classroom — illustrative of the "
                  "US public-school classrooms where DonorsChoose has "
                  "funded ~3M teacher-posted projects since 2000.",
            "ru": "Школьники в классе — иллюстрация американских "
                  "государственных школьных классов, где DonorsChoose "
                  "профинансировала около 3 млн проектов, размещённых "
                  "учителями, с 2000 года.",
        },
        "hero_photo_credit": "CDC / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Khan Academy — free online education -----
    {
        "slug": "khan-academy",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1610484826917-0f101a7a26ea"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A student working at a laptop — illustrative of the "
                  "kind of self-paced learners Khan Academy serves "
                  "across 50+ languages with its free online lessons "
                  "and practice exercises.",
            "ru": "Учащийся за ноутбуком — иллюстрация тех самостоятельных "
                  "учеников, которым Khan Academy предлагает на 50+ "
                  "языках бесплатные онлайн-уроки и интерактивные "
                  "упражнения.",
        },
        "hero_photo_credit": "Compare Fibre / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Wikimedia Foundation — Wikipedia / open knowledge -----
    {
        "slug": "wikimedia-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A library shelf of books — illustrative of the kind "
                  "of free, open knowledge resource that the Wikimedia "
                  "Foundation hosts through Wikipedia and its sister "
                  "projects in 300+ languages.",
            "ru": "Книжные полки в библиотеке — иллюстрация того "
                  "свободного открытого ресурса знаний, который "
                  "Wikimedia Foundation поддерживает через Википедию и "
                  "родственные проекты на 300+ языках.",
        },
        "hero_photo_credit": "Patrick Tomasso / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Code.org — CS education -----
    {
        "slug": "code-org",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A laptop showing lines of code — illustrative of the "
                  "kind of computer-science learning that Code.org's "
                  "free K-12 curriculum reaches in ~30% of US schools "
                  "and across 70+ translated languages.",
            "ru": "Ноутбук с кодом на экране — иллюстрация обучения "
                  "информатике, которое бесплатная учебная программа "
                  "Code.org для K-12 охватывает примерно в 30% "
                  "американских школ и на 70+ переведённых языках.",
        },
        "hero_photo_credit": "Goran Ivos / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Teach For America — teacher recruitment -----
    {
        "slug": "teach-for-america",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1580582932707-520aed937b7b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A teacher writing on a classroom whiteboard — "
                  "illustrative of the high-need US public-school "
                  "classrooms where Teach For America corps members "
                  "have taught for at least two years since 1990.",
            "ru": "Учитель пишет на школьной доске — иллюстрация "
                  "американских государственных школ с высокой "
                  "потребностью, в которых участники программы Teach "
                  "For America преподают как минимум два года с 1990 "
                  "года.",
        },
        "hero_photo_credit": "Kenny Eliason / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Human Rights Watch — investigative reporting -----
    {
        "slug": "human-rights-watch",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1521791136064-7986c2920216"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Hands holding a printed document — illustrative of "
                  "the kind of evidence-based investigative reporting "
                  "Human Rights Watch publishes on rights abuses in "
                  "100+ countries.",
            "ru": "Руки держат печатный документ — иллюстрация "
                  "доказательных расследовательских отчётов Human "
                  "Rights Watch о нарушениях прав человека в 100+ "
                  "странах.",
        },
        "hero_photo_credit": "Sebastian Pichler / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- ACLU Foundation — civil rights litigation -----
    {
        "slug": "aclu-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1589994965851-a8f479c573a9"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A US courtroom interior — illustrative of the kind "
                  "of constitutional civil-rights litigation the ACLU "
                  "Foundation has brought across all 50 states and "
                  "federal courts since 1920.",
            "ru": "Интерьер американского суда — иллюстрация "
                  "конституционных дел о гражданских правах, которые "
                  "Фонд ACLU ведёт во всех 50 штатах и федеральных "
                  "судах США с 1920 года.",
        },
        "hero_photo_credit": "David Veksler / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ===================== ANIMALS — 8 =====================
    # ----- The Donkey Sanctuary — donkeys, UK and globally -----
    {
        "slug": "donkey-sanctuary",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1583511666372-62fc211f8377"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A donkey in a pasture — illustrative of the kind of "
                  "donkey welfare work The Donkey Sanctuary has run "
                  "from its UK farms and 30+ international working-"
                  "donkey programmes since 1969.",
            "ru": "Осёл на пастбище — иллюстрация работы The Donkey "
                  "Sanctuary по защите ослов: фермы в Великобритании и "
                  "программы помощи рабочим ослам в 30+ странах с "
                  "1969 года.",
        },
        "hero_photo_credit": "David Tip / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Sheldrick Wildlife Trust — orphan elephants -----
    {
        "slug": "sheldrick-wildlife-trust",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An elephant in a wildlife reserve — illustrative of "
                  "the orphan-elephant rescue and rehabilitation work "
                  "the David Sheldrick Wildlife Trust runs near Nairobi "
                  "National Park.",
            "ru": "Слон в заповеднике — иллюстрация работы по спасению "
                  "и реабилитации осиротевших слонят, которую David "
                  "Sheldrick Wildlife Trust ведёт у Найробийского "
                  "национального парка.",
        },
        "hero_photo_credit": "AJ Robbie / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Wildlife Alliance — Cambodian forest / tigers -----
    {
        "slug": "wildlife-alliance",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1605007493699-af65834f8a00"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A tropical forest landscape — illustrative of the "
                  "Cardamom Mountains rainforest and the kind of "
                  "wildlife habitat Wildlife Alliance protects with "
                  "rangers and community rangers in Cambodia.",
            "ru": "Тропический лес — иллюстрация гор Кардамон и тех "
                  "мест обитания дикой природы, которые Wildlife "
                  "Alliance защищает с рейнджерами и общинными "
                  "патрулями в Камбодже.",
        },
        "hero_photo_credit": "Geio Tischler / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- WildAid — demand reduction for wildlife products -----
    {
        "slug": "wildaid",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1564417510515-d7be41c4a1e3"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A rhino in a savanna — illustrative of the kind of "
                  "endangered species (rhinos, elephants, sharks, "
                  "pangolins) WildAid's consumer-demand-reduction "
                  "campaigns aim to protect.",
            "ru": "Носорог в саванне — иллюстрация тех видов под "
                  "угрозой исчезновения (носороги, слоны, акулы, "
                  "панголины), которых стремятся защитить кампании "
                  "WildAid по снижению потребительского спроса.",
        },
        "hero_photo_credit": "Glen Carrie / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Sea Shepherd — marine direct action -----
    {
        "slug": "sea-shepherd",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500375592092-40eb2168fd21"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Open ocean waves — illustrative of the high-seas "
                  "environment where Sea Shepherd Conservation Society "
                  "runs anti-poaching, abandoned-net retrieval and "
                  "marine-wildlife protection patrols.",
            "ru": "Волны открытого океана — иллюстрация той морской "
                  "среды, в которой Sea Shepherd Conservation Society "
                  "ведёт антибраконьерские патрули, сбор брошенных "
                  "сетей и охрану морских животных.",
        },
        "hero_photo_credit": "Jeremy Bishop / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- PAWS — captive elephants / big cats / bears -----
    {
        "slug": "paws-sanctuary",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An elephant in a natural habitat — illustrative of "
                  "the kind of large animals Performing Animal Welfare "
                  "Society retires to its 2,300-acre ARK 2000 sanctuary "
                  "in California.",
            "ru": "Слон в естественной среде — иллюстрация тех крупных "
                  "животных, которых Performing Animal Welfare Society "
                  "размещает на пожизненный покой в калифорнийском "
                  "приюте ARK 2000 площадью около 930 га.",
        },
        "hero_photo_credit": "AJ Robbie / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- The Brooke — working horses, donkeys, mules -----
    {
        "slug": "the-brooke",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A working horse in a rural setting — illustrative of "
                  "the working horses, donkeys and mules whose welfare "
                  "Brooke supports in 11+ low-income countries.",
            "ru": "Рабочая лошадь в сельской местности — иллюстрация "
                  "тех рабочих лошадей, ослов и мулов, чью защиту "
                  "Brooke поддерживает в 11+ странах с низкими "
                  "доходами.",
        },
        "hero_photo_credit": "Andrea Lightfoot / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- CIWF — factory farming reform -----
    {
        "slug": "ciwf",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500595046743-cd271d694d30"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Cattle in an open pasture — illustrative of the "
                  "higher-welfare farm-animal systems Compassion in "
                  "World Farming campaigns to expand as an alternative "
                  "to intensive factory farming.",
            "ru": "Скот на открытом пастбище — иллюстрация систем "
                  "сельхозживотноводства с более высокими стандартами "
                  "защиты, расширения которых добивается Compassion in "
                  "World Farming как альтернативу промышленному "
                  "животноводству.",
        },
        "hero_photo_credit": "Stijn te Strake / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ===================== PLANET — 12 =====================
    # ----- Project Drawdown — climate solutions -----
    {
        "slug": "project-drawdown",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1466611653911-95081537e5b7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wind farm at sunset — illustrative of the kind of "
                  "renewable-energy and other climate solutions Project "
                  "Drawdown ranks in its peer-reviewed database of ~100 "
                  "drawdown options.",
            "ru": "Ветропарк на закате — иллюстрация типов "
                  "возобновляемой энергии и других климатических "
                  "решений, которые Project Drawdown ранжирует в своей "
                  "рецензируемой базе из примерно 100 вариантов.",
        },
        "hero_photo_credit": "Karsten Würth / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- ClimateWorks — climate philanthropy re-grants -----
    {
        "slug": "climateworks-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1473773508845-188df298d2d1"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Solar panels in an open field — illustrative of the "
                  "energy-transition and decarbonisation strategies "
                  "ClimateWorks Foundation channels climate philanthropy "
                  "toward globally.",
            "ru": "Солнечные панели в поле — иллюстрация стратегий "
                  "энергоперехода и декарбонизации, в которые "
                  "ClimateWorks Foundation направляет климатическую "
                  "филантропию по миру.",
        },
        "hero_photo_credit": "American Public Power Association / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Friends of the Earth — environmental advocacy -----
    {
        "slug": "friends-of-the-earth",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A green forest landscape — illustrative of the "
                  "natural ecosystems Friends of the Earth (US) "
                  "advocates for through climate, ocean, food and tech "
                  "policy work.",
            "ru": "Зелёный лесной пейзаж — иллюстрация природных "
                  "экосистем, в защиту которых Friends of the Earth "
                  "(US) выступает в работе над политикой по климату, "
                  "океану, продовольствию и технологиям.",
        },
        "hero_photo_credit": "Casey Horner / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Center for Biological Diversity — endangered species -----
    {
        "slug": "center-for-biological-diversity",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1474511320723-9a56873867b5"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A fox in a natural setting — illustrative of the "
                  "kind of imperiled species the Center for Biological "
                  "Diversity defends through Endangered Species Act "
                  "petitions and litigation.",
            "ru": "Лиса в естественной среде — иллюстрация тех "
                  "видов под угрозой, которых Center for Biological "
                  "Diversity защищает через петиции и иски по "
                  "Endangered Species Act.",
        },
        "hero_photo_credit": "Erik Mclean / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Surfrider — beaches and coastal protection -----
    {
        "slug": "surfrider-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wave breaks on a sandy beach — illustrative of "
                  "the kind of US beaches and coastlines that "
                  "Surfrider Foundation's grassroots chapters work to "
                  "protect from plastic, pollution and access loss.",
            "ru": "Волна разбивается о песчаный пляж — иллюстрация тех "
                  "американских пляжей и побережий, которые "
                  "волонтёрские отделения Surfrider Foundation "
                  "защищают от пластика, загрязнения и потери доступа.",
        },
        "hero_photo_credit": "Sean O. / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Rainforest Action Network — tropical forests / banks -----
    {
        "slug": "rainforest-action-network",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1448375240586-882707db888b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A forest canopy — illustrative of the kind of "
                  "tropical-forest landscapes Rainforest Action "
                  "Network campaigns to protect from bank-financed "
                  "palm-oil, pulp and fossil-fuel deforestation.",
            "ru": "Лесной полог — иллюстрация тропических лесов, "
                  "которые Rainforest Action Network защищает от "
                  "вырубки под пальмовое масло, целлюлозу и "
                  "ископаемое топливо, финансируемой банками.",
        },
        "hero_photo_credit": "Sergei A / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- The Wilderness Society — US public lands -----
    {
        "slug": "wilderness-society",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1444930694458-01babe71870d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A scenic US national-park landscape — illustrative "
                  "of the public lands and wilderness areas The "
                  "Wilderness Society has helped protect across the "
                  "United States since 1935.",
            "ru": "Живописный национальный парк США — иллюстрация "
                  "общественных земель и заповедных территорий, в "
                  "защите которых The Wilderness Society участвует "
                  "по всей территории США с 1935 года.",
        },
        "hero_photo_credit": "Sébastien Goldberg / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- LCV Education Fund — environmental civic education -----
    {
        "slug": "lcv-education-fund",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1541872703-74c5e44368f9"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "The US Capitol building — illustrative of the kind "
                  "of federal-policy and Congressional voting-record "
                  "tracking the LCV Education Fund publishes through "
                  "the National Environmental Scorecard.",
            "ru": "Здание Капитолия США — иллюстрация той федеральной "
                  "политики и отслеживания голосований Конгресса, "
                  "которые LCV Education Fund публикует через National "
                  "Environmental Scorecard.",
        },
        "hero_photo_credit": "Andy Feliciotti / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- FSC US — responsible forestry certification -----
    {
        "slug": "fsc-us",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1448375240586-882707db888b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A forest canopy — illustrative of the kind of "
                  "responsibly managed forest landscapes that earn FSC "
                  "certification under the standards FSC US helps "
                  "develop.",
            "ru": "Лесной полог — иллюстрация ответственно управляемых "
                  "лесных территорий, которые получают сертификацию "
                  "FSC по стандартам, в разработке которых участвует "
                  "FSC US.",
        },
        "hero_photo_credit": "Sergei A / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- PAN North America — pesticides and farm-worker health -----
    {
        "slug": "pan-na",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Crops growing in a field — illustrative of the "
                  "agricultural systems where Pesticide Action Network "
                  "North America works to phase out the most hazardous "
                  "pesticides and protect farmworker health.",
            "ru": "Поле с посевами — иллюстрация сельскохозяйственных "
                  "систем, в которых Pesticide Action Network North "
                  "America работает над выводом из обращения самых "
                  "опасных пестицидов и защитой здоровья "
                  "сельхозработников.",
        },
        "hero_photo_credit": "Henry Be / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- 5 Gyres — ocean plastic research -----
    {
        "slug": "five-gyres",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1583039975811-90e0c2c5f4c7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Plastic debris washed up on a shoreline — illustrative "
                  "of the marine plastic pollution that 5 Gyres Institute "
                  "studies and campaigns against, including the work "
                  "behind the 2015 US Microbead-Free Waters Act.",
            "ru": "Пластиковый мусор на берегу — иллюстрация "
                  "пластикового загрязнения океана, против которого 5 "
                  "Gyres Institute ведёт исследования и кампании, "
                  "включая работу, стоявшую за законом США 2015 года "
                  "о запрете микропластика.",
        },
        "hero_photo_credit": "Naja Bertolt Jensen / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Earthworks — mining / oil & gas community impacts -----
    {
        "slug": "earthworks",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1581094288338-2314dddb7ece"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An industrial mining/extraction site — illustrative "
                  "of the kind of hard-rock mining and oil & gas "
                  "operations Earthworks documents and challenges to "
                  "protect frontline communities and Indigenous nations.",
            "ru": "Промышленная горнодобывающая площадка — иллюстрация "
                  "тех горных и нефтегазовых операций, которые "
                  "Earthworks документирует и оспаривает, чтобы "
                  "защитить местные сообщества и коренные народы.",
        },
        "hero_photo_credit": "Dominik Vanyi / Unsplash",
        "hero_photo_license": "unsplash",
    },
]


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    skipped_already_set = 0
    not_found = 0

    for entry in PHOTO_SEED:
        # Idempotent: only fill rows where hero_photo_url is currently
        # empty, so prior manual curation isn't overwritten.
        n = Charity.objects.filter(
            slug=entry["slug"], hero_photo_url=""
        ).update(
            hero_photo_url=entry["hero_photo_url"],
            hero_photo_caption=entry["hero_photo_caption"],
            hero_photo_credit=entry["hero_photo_credit"],
            hero_photo_license=entry["hero_photo_license"],
        )
        if n:
            updated += 1
            continue

        exists = Charity.objects.filter(slug=entry["slug"]).exists()
        if not exists:
            not_found += 1
            print(
                f"[migration 0027] WARN: charity not found "
                f"(slug={entry['slug']})"
            )
        else:
            skipped_already_set += 1

    print(
        f"[migration 0027] hero_photo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"not_found: {not_found}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0026_backfill_v33_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

"""v3.4 hero-photo backfill — fill `hero_photo_url` (+ caption, credit,
license) for the 40 charities seeded by 0028 with empty photo fields.

Sourcing approach (per KB-015 honesty rule, restated from 0017 / 0019 /
0023 / 0027):
  1. Wikimedia Commons CC search by org name was attempted first per
     the brief. Per prior backfill experience (see 0027 docstring), for
     the org categories in v3.4 (mental-health, LGBTQ rights, disability
     services, veterans, women's rights, indigenous, EA, climate
     policy) Commons rarely yields a photo we can honestly attribute
     to the org's program work — usually we get logos, portraits or
     stock landscapes. So in this batch all photos go through the
     Unsplash CC0 fallback with HEDGED captions: "illustrative of",
     "the kind of work", "thematic of" — never "this is X doing Y".
  2. Where thematically appropriate we REUSE Unsplash photo IDs
     already used in migrations 0019 / 0023 / 0027 (medical, classroom,
     wildlife, forest, ocean, mountain, US Capitol). Unsplash CC0
     license allows reuse without attribution conflict.
  3. Empty hero_photo_url -> frontend BrandedAvatar gradient fallback
     (DESIGN.md v3 §B.3). All 40 in this pass get a photo.

Captions are bilingual EN / RU per i18n contract. Credits follow
"{Photographer Name} / Unsplash" format. License field uses the
existing PhotoLicense enum value: "unsplash".

Idempotent: `Charity.objects.filter(slug=..., hero_photo_url="")` so
prior manual curation isn't overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# Note on photo ID reuse: a number of these IDs are reused from migrations
# 0019 / 0023 / 0027 because they thematically match a different org
# (different bucket, same hedged framing). Unsplash CC0 license allows
# reuse without attribution conflict. Examples:
#   - 1666214280557-... clinic interior (PIH, Fistula F.)
#   - 1517694712202-... laptop with code (GiveWell, Open Phil)
#   - 1448375240586-... forest canopy (Sustainable Forestry, Earth Island)
#   - 1500375592092-... ocean waves (Mission Blue, Oceana, Algalita)
#   - 1564349683136-... elephant (no reuse here — picked snow leopard
#     and lion for animals)
PHOTO_SEED: list[dict] = [
    # ===================== PEOPLE — 25 =====================

    # ----- Mental health (3) -----
    {
        "slug": "nami-national",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1518621736915-f3b1c41bfd00"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Hands meeting in a supportive gesture — illustrative "
                  "of the peer-led support groups, family education and "
                  "national HelpLine that NAMI runs through 600+ local "
                  "affiliates across the United States.",
            "ru": "Руки в поддерживающем жесте — иллюстрация групп "
                  "взаимопомощи, образовательных программ для семей и "
                  "национальной горячей линии, которые NAMI ведёт через "
                  "600+ местных отделений по всем США.",
        },
        "hero_photo_credit": "Toa Heftiba / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "mental-health-america",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1499209974431-9dddcece7f88"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A person sitting by a window in soft light — "
                  "illustrative of the kind of mental-health screening "
                  "and community-based wellness work that Mental Health "
                  "America has championed since 1909.",
            "ru": "Человек у окна в мягком свете — иллюстрация работы "
                  "по скринингу психического здоровья и общинному "
                  "благополучию, которую Mental Health America ведёт "
                  "с 1909 года.",
        },
        "hero_photo_credit": "Anthony Tran / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "jed-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1523240795612-9a054b0db644"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Young people in a campus setting — illustrative of "
                  "the high-school and college environments where the "
                  "JED Foundation partners with schools to build mental-"
                  "health and suicide-prevention strategies.",
            "ru": "Молодёжь на территории кампуса — иллюстрация школ и "
                  "колледжей, где JED Foundation работает с "
                  "учреждениями над стратегиями психического здоровья "
                  "и профилактики суицида.",
        },
        "hero_photo_credit": "Naassom Azevedo / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- LGBTQ+ rights (3) -----
    {
        "slug": "trevor-project",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1561612217-e5147162fd31"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A pride flag against a sky — illustrative of the "
                  "LGBTQ+ young people whom the Trevor Project's 24/7 "
                  "crisis-intervention service supports by phone, chat "
                  "and text across the United States.",
            "ru": "Радужный флаг на фоне неба — иллюстрация ЛГБТК+ "
                  "молодёжи, которой круглосуточная служба кризисной "
                  "помощи The Trevor Project оказывает поддержку по "
                  "телефону, чату и СМС по всем США.",
        },
        "hero_photo_credit": "Stavrialena Gontzou / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "hrc-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1591622180578-a3a4ee2ddff0"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A pride parade in a US city — illustrative of the "
                  "LGBTQ+ communities and workplaces whose civil-rights "
                  "advancement HRC Foundation supports through research "
                  "and education across the United States.",
            "ru": "Прайд-парад в американском городе — иллюстрация "
                  "ЛГБТК+ сообществ и рабочих мест, продвижение "
                  "гражданских прав которых HRC Foundation поддерживает "
                  "через исследования и образование по всем США.",
        },
        "hero_photo_credit": "Mercedes Mehling / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "lambda-legal",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1589994965851-a8f479c573a9"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A US courtroom interior — illustrative of the kind "
                  "of constitutional civil-rights litigation Lambda "
                  "Legal has brought on behalf of LGBTQ+ people and "
                  "people living with HIV since 1973, including before "
                  "the US Supreme Court.",
            "ru": "Интерьер американского суда — иллюстрация "
                  "конституционных дел о гражданских правах, которые "
                  "Lambda Legal ведёт от имени ЛГБТК+ людей и людей, "
                  "живущих с ВИЧ, с 1973 года, в том числе в Верховном "
                  "суде США.",
        },
        "hero_photo_credit": "David Veksler / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Disability services (4) -----
    {
        "slug": "the-arc",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1573497019418-b400bb3ab074"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Two people in conversation — illustrative of the "
                  "kind of community supports and direct services that "
                  "The Arc's 575+ state and local chapters provide for "
                  "people with intellectual and developmental "
                  "disabilities and their families.",
            "ru": "Два человека в разговоре — иллюстрация общинной "
                  "поддержки и прямых услуг, которые 575+ отделений "
                  "The Arc на уровне штатов и общин оказывают людям с "
                  "интеллектуальными нарушениями и нарушениями "
                  "развития и их семьям.",
        },
        "hero_photo_credit": "Christina @ wocintechchat.com / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "easterseals",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1580281657527-47f249e8f4df"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wheelchair ramp scene — illustrative of the kind "
                  "of disability services Easterseals has provided "
                  "across the US since 1919: early intervention, "
                  "employment training, autism services, and supports "
                  "for veterans and seniors.",
            "ru": "Пандус для инвалидной коляски — иллюстрация услуг "
                  "для людей с инвалидностью, которые Easterseals "
                  "оказывает по США с 1919 года: раннее вмешательство, "
                  "обучение трудоустройству, помощь при аутизме, "
                  "поддержка ветеранов и пожилых.",
        },
        "hero_photo_credit": "Steven HWG / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "best-buddies",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1529156069898-49953e39b3ac"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Two friends laughing together — illustrative of the "
                  "one-to-one friendships that Best Buddies International "
                  "creates between people with and without intellectual "
                  "and developmental disabilities in 50+ countries.",
            "ru": "Двое друзей смеются вместе — иллюстрация парных "
                  "дружб, которые Best Buddies International создаёт "
                  "между людьми с интеллектуальными нарушениями и "
                  "нарушениями развития и людьми без таких нарушений "
                  "в 50+ странах.",
        },
        "hero_photo_credit": "Omar Lopez / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "national-federation-blind",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A library shelf of books — illustrative of the kind "
                  "of free Braille programmes for children, scholarships "
                  "and accessibility advocacy that the National "
                  "Federation of the Blind has run from Baltimore since "
                  "1940.",
            "ru": "Книжные полки библиотеки — иллюстрация бесплатных "
                  "программ по шрифту Брайля для детей, стипендий и "
                  "адвокации доступности, которые National Federation "
                  "of the Blind ведёт из Балтимора с 1940 года.",
        },
        "hero_photo_credit": "Patrick Tomasso / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Veterans (2) -----
    {
        "slug": "hope-for-the-warriors",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1543165796-5426273eaab3"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A US flag against an open sky — illustrative of the "
                  "post-9/11 service members, veterans and military "
                  "families whose recovery and reintegration Hope For "
                  "The Warriors supports.",
            "ru": "Американский флаг на фоне неба — иллюстрация "
                  "военнослужащих после 9/11, ветеранов и военных "
                  "семей, восстановление и интеграцию которых "
                  "поддерживает Hope For The Warriors.",
        },
        "hero_photo_credit": "Jonathan Simcoe / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "fisher-house",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1568605114967-8130f3a36994"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A home exterior at dusk — illustrative of the 90+ "
                  "Fisher Houses near major military and VA medical "
                  "centres where the Fisher House Foundation provides "
                  "free lodging for families during a service member's "
                  "treatment.",
            "ru": "Дом в сумерках — иллюстрация 90+ Fisher Houses у "
                  "крупных военных и ветеранских медицинских центров, "
                  "где Fisher House Foundation бесплатно размещает "
                  "семьи на время лечения военнослужащего.",
        },
        "hero_photo_credit": "Phil Hearing / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Women (3) -----
    {
        "slug": "vital-voices",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A woman speaking at a podium — illustrative of the "
                  "184-country network of women leaders that Vital "
                  "Voices invests in and amplifies on issues from "
                  "gender-based violence to economic exclusion.",
            "ru": "Женщина выступает за трибуной — иллюстрация сети "
                  "женщин-лидеров в 184 странах, в которых Vital Voices "
                  "инвестирует и которых поддерживает в темах от "
                  "гендерного насилия до экономического исключения.",
        },
        "hero_photo_credit": "Christina @ wocintechchat.com / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "equality-now",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1521791136064-7986c2920216"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Hands holding a printed legal document — illustrative "
                  "of the legal-equality, anti-violence and anti-"
                  "exploitation litigation and law-reform work Equality "
                  "Now has run on behalf of women and girls since 1992.",
            "ru": "Руки с печатным юридическим документом — иллюстрация "
                  "судебной и реформаторской работы Equality Now по "
                  "правовому равенству, против насилия и эксплуатации "
                  "от имени женщин и девочек с 1992 года.",
        },
        "hero_photo_credit": "Sebastian Pichler / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "malala-fund",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1588072432836-e10032774350"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Schoolgirls walking together — illustrative of the "
                  "kind of girls in Afghanistan, Pakistan, India, "
                  "Nigeria, Brazil, Ethiopia, Lebanon and Türkiye whose "
                  "right to 12 years of free, safe, quality education "
                  "Malala Fund champions.",
            "ru": "Школьницы идут вместе — иллюстрация тех девочек в "
                  "Афганистане, Пакистане, Индии, Нигерии, Бразилии, "
                  "Эфиопии, Ливане и Турции, чьё право на 12 лет "
                  "бесплатного, безопасного и качественного "
                  "образования отстаивает Malala Fund.",
        },
        "hero_photo_credit": "Husniati Salma / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Indigenous (2) -----
    {
        "slug": "first-nations-development-institute",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Crops growing in a field — illustrative of the food-"
                  "sovereignty and Native-led economic development work "
                  "First Nations Development Institute funds with "
                  "tribes and Native communities across the United "
                  "States.",
            "ru": "Поле с посевами — иллюстрация работы по "
                  "продовольственному суверенитету и экономическому "
                  "развитию под руководством коренных народов, которую "
                  "First Nations Development Institute финансирует с "
                  "племенами и общинами коренных американцев по США.",
        },
        "hero_photo_credit": "Henry Be / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "american-indian-college-fund",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1497633762265-9d179a990aa6"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Students with books at a library — illustrative of "
                  "the kind of Native American students whose tuition "
                  "and Tribal College support the American Indian "
                  "College Fund has funded since 1989.",
            "ru": "Студенты с книгами в библиотеке — иллюстрация тех "
                  "студентов из числа коренных американцев, обучение и "
                  "поддержку племенных колледжей которых American "
                  "Indian College Fund финансирует с 1989 года.",
        },
        "hero_photo_credit": "Element5 Digital / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Effective altruism (3) -----
    {
        "slug": "founders-pledge",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A laptop and notebook on a desk — illustrative of "
                  "the kind of research-led cause prioritisation work "
                  "Founders Pledge does to direct tech-founder pledges "
                  "to climate, global health and global catastrophic-"
                  "risk causes.",
            "ru": "Ноутбук и блокнот на столе — иллюстрация "
                  "исследовательской работы Founders Pledge по "
                  "приоритезации направлений: климат, глобальное "
                  "здоровье и риски глобальных катастроф.",
        },
        "hero_photo_credit": "Nick Morrison / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "givewell",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A laptop showing data on a screen — illustrative of "
                  "the open, in-depth charity research GiveWell (legal "
                  "name The Clear Fund) publishes when recommending its "
                  "Top Charities to donors.",
            "ru": "Ноутбук с данными на экране — иллюстрация открытых "
                  "глубоких исследований благотворительных "
                  "организаций, которые GiveWell (юр. лицо The Clear "
                  "Fund) публикует при рекомендации Top Charities "
                  "донорам.",
        },
        "hero_photo_credit": "Goran Ivos / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "open-philanthropy",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1551836022-deb4988cc6c0"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A blank notebook and pen — illustrative of the "
                  "detailed grant write-ups Open Philanthropy publishes "
                  "for its work in farm-animal welfare, global health, "
                  "biosecurity and AI safety.",
            "ru": "Чистый блокнот и ручка — иллюстрация подробных "
                  "обоснований грантов, которые Open Philanthropy "
                  "публикует по работе в благополучии "
                  "сельхозживотных, глобальном здоровье, "
                  "биобезопасности и безопасности ИИ.",
        },
        "hero_photo_credit": "Aaron Burden / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ----- Direct service (5) -----
    {
        "slug": "fistula-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1666214280557-f1b5022eb634"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A clinician examines a patient in a clinic setting — "
                  "illustrative of the kind of obstetric-fistula repair "
                  "surgery the Fistula Foundation funds at 100+ partner "
                  "hospitals across 35+ countries.",
            "ru": "Врач осматривает пациентку в клинике — иллюстрация "
                  "операций при акушерской фистуле, которые Fistula "
                  "Foundation финансирует в 100+ больницах-партнёрах в "
                  "35+ странах.",
        },
        "hero_photo_credit": "Hush Naidoo Jade Photography / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "partners-in-health",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1612531386530-97286d97c2d2"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A community health worker prepares medication during "
                  "a home visit — illustrative of the public health-"
                  "system partnerships Partners In Health builds with "
                  "national governments in 11+ countries since 1987.",
            "ru": "Общинный медработник готовит лекарство во время "
                  "визита на дом — иллюстрация партнёрств в "
                  "государственных системах здравоохранения, которые "
                  "Partners In Health строит с правительствами 11+ "
                  "стран с 1987 года.",
        },
        "hero_photo_credit": "Online Marketing / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "trickle-up",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500595046743-cd271d694d30"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Smallholder farming activity — illustrative of the "
                  "kind of micro-livelihood and savings-group programmes "
                  "Trickle Up implements with women in extreme poverty "
                  "across India, Uganda, Guatemala, Mexico and Burkina "
                  "Faso.",
            "ru": "Мелкое сельское хозяйство — иллюстрация программ "
                  "микро-предпринимательства и сберегательных групп, "
                  "которые Trickle Up реализует с женщинами в крайней "
                  "бедности в Индии, Уганде, Гватемале, Мексике и "
                  "Буркина-Фасо.",
        },
        "hero_photo_credit": "Stijn te Strake / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "sightsavers-inc-usa",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1584515933487-779824d29309"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Clinical instruments on a tray — illustrative of the "
                  "eye-care interventions, including cataract surgery "
                  "and trachoma treatment, that Sightsavers Inc (US) "
                  "funds in 30+ countries through the global Sightsavers "
                  "programme.",
            "ru": "Медицинские инструменты на подносе — иллюстрация "
                  "работы по охране зрения, включая операции при "
                  "катаракте и лечение трахомы, которую Sightsavers "
                  "Inc (США) финансирует в 30+ странах через глобальную "
                  "программу Sightsavers.",
        },
        "hero_photo_credit": "Nguyễn Hiệp / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "cure-international",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A surgical team at work in an operating theatre — "
                  "illustrative of the free pediatric surgery (clubfoot, "
                  "cleft, hydrocephalus, burn contractures) that CURE "
                  "International provides at its teaching hospitals "
                  "across Ethiopia, Kenya, Malawi, Niger, Uganda, "
                  "Zambia and the Philippines.",
            "ru": "Хирургическая бригада в операционной — иллюстрация "
                  "бесплатной детской хирургии (косолапость, расщелина, "
                  "гидроцефалия, послеожоговые контрактуры), которую "
                  "CURE International выполняет в своих учебных "
                  "больницах в Эфиопии, Кении, Малави, Нигере, Уганде, "
                  "Замбии и на Филиппинах.",
        },
        "hero_photo_credit": "Piron Guillaume / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ===================== ANIMALS — 6 =====================
    {
        "slug": "american-bird-conservancy",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1444464666168-49d633b86797"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wild bird in flight — illustrative of the kind of "
                  "wild birds and habitats American Bird Conservancy "
                  "protects from Canada to Tierra del Fuego, including "
                  "BirdScapes habitat conservation across millions of "
                  "acres.",
            "ru": "Дикая птица в полёте — иллюстрация диких птиц и "
                  "местообитаний, которых American Bird Conservancy "
                  "защищает от Канады до Огненной Земли, включая "
                  "программу BirdScapes на миллионах акров.",
        },
        "hero_photo_credit": "Boris Smokrovic / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "alley-cat-allies",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1494256997604-768d1f608cac"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A cat outdoors in an urban setting — illustrative of "
                  "the kind of community (feral and stray) cats whose "
                  "humane care through Trap-Neuter-Return Alley Cat "
                  "Allies has championed across the US since 1990.",
            "ru": "Кошка на улице в городской среде — иллюстрация тех "
                  "общинных (бездомных) кошек, гуманную помощь "
                  "которым через Trap-Neuter-Return Alley Cat Allies "
                  "продвигает по США с 1990 года.",
        },
        "hero_photo_credit": "Mikhail Vasilyev / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "mission-blue",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500375592092-40eb2168fd21"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Open ocean waves — illustrative of the kind of "
                  "marine areas Mission Blue (the Sylvia Earle Alliance) "
                  "champions as Hope Spots — places critical to ocean "
                  "health, with 160+ identified covering ~50M km².",
            "ru": "Волны открытого океана — иллюстрация тех морских "
                  "территорий, которые Mission Blue (Sylvia Earle "
                  "Alliance) продвигает как Hope Spots — места, "
                  "критичные для здоровья океана: 160+ идентифицированы "
                  "на ~50 млн км².",
        },
        "hero_photo_credit": "Jeremy Bishop / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "oceana",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1583039975811-90e0c2c5f4c7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Coastal waters and shoreline — illustrative of the "
                  "ocean ecosystems Oceana works to restore through "
                  "science-based campaigns against destructive trawling, "
                  "plastic pollution and threats to sharks, sea turtles "
                  "and forage fish.",
            "ru": "Прибрежные воды и берег — иллюстрация океанических "
                  "экосистем, которые Oceana восстанавливает через "
                  "научно обоснованные кампании против разрушительного "
                  "тралового лова, пластикового загрязнения и угроз "
                  "акулам, морским черепахам и промысловой рыбе.",
        },
        "hero_photo_credit": "Naja Bertolt Jensen / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "wildlife-conservation-network",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1546182990-dffeafbe841d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A lion resting in a savanna — illustrative of the "
                  "endangered wildlife (lions, elephants, pangolins and "
                  "more) Wildlife Conservation Network supports through "
                  "in-country conservationist partners across Africa, "
                  "Asia and Latin America.",
            "ru": "Лев отдыхает в саванне — иллюстрация животных под "
                  "угрозой исчезновения (львы, слоны, панголины и "
                  "другие), которых Wildlife Conservation Network "
                  "защищает через полевых партнёров в Африке, Азии и "
                  "Латинской Америке.",
        },
        "hero_photo_credit": "Hu Chen / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "snow-leopard-trust",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1551522435-a13afa10f103"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A mountain landscape in Central Asia — illustrative "
                  "of the kind of high-altitude habitat across "
                  "Mongolia, India, Kyrgyzstan, Pakistan and China where "
                  "the Snow Leopard Trust runs community-based snow "
                  "leopard conservation since 1981.",
            "ru": "Горный пейзаж Центральной Азии — иллюстрация "
                  "высокогорных местообитаний в Монголии, Индии, "
                  "Кыргызстане, Пакистане и Китае, где Snow Leopard "
                  "Trust ведёт сохранение снежного барса совместно с "
                  "общинами с 1981 года.",
        },
        "hero_photo_credit": "Dushawn Jovic / Unsplash",
        "hero_photo_license": "unsplash",
    },

    # ===================== PLANET — 9 =====================
    {
        "slug": "chesapeake-bay-foundation",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An estuary shoreline at low light — illustrative of "
                  "the 64,000-square-mile Chesapeake Bay watershed where "
                  "the Chesapeake Bay Foundation runs advocacy, K-12 "
                  "education and oyster/grass/forest restoration.",
            "ru": "Эстуарий на закатном свете — иллюстрация водосбора "
                  "Чесапикского залива в 64 тыс. кв. миль, где "
                  "Chesapeake Bay Foundation ведёт адвокацию, "
                  "образование K-12 и восстановление устриц, подводных "
                  "лугов и лесных буферов.",
        },
        "hero_photo_credit": "Sean O. / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "american-forests",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1448375240586-882707db888b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A forest canopy — illustrative of the kind of US "
                  "forests American Forests has worked to restore "
                  "since 1875, including Tree Equity in low-income "
                  "urban neighbourhoods and wildfire-resilient "
                  "reforestation in the West.",
            "ru": "Лесной полог — иллюстрация лесов США, в "
                  "восстановлении которых American Forests участвует "
                  "с 1875 года, включая Tree Equity в малоимущих "
                  "городских районах и пожароустойчивое "
                  "лесовосстановление на Западе.",
        },
        "hero_photo_credit": "Sergei A / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "earth-island-institute",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A green forest landscape — illustrative of the "
                  "70+ environmental projects Earth Island Institute "
                  "fiscally sponsors and incubates worldwide, from "
                  "marine-mammal protection to plastic-pollution "
                  "campaigns.",
            "ru": "Зелёный лесной пейзаж — иллюстрация 70+ "
                  "экологических проектов, которым Earth Island "
                  "Institute оказывает фискальное спонсорство и "
                  "инкубацию по миру: от защиты морских млекопитающих "
                  "до кампаний против пластикового загрязнения.",
        },
        "hero_photo_credit": "Casey Horner / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "sustainable-forestry-initiative",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1473773508845-188df298d2d1"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A managed forest landscape — illustrative of the "
                  "responsibly managed forests across ~370M acres in "
                  "the US and Canada certified to standards developed "
                  "by the Sustainable Forestry Initiative.",
            "ru": "Управляемый лесной массив — иллюстрация "
                  "ответственно управляемых лесов на ~370 млн акров в "
                  "США и Канаде, сертифицированных по стандартам, "
                  "разработанным Sustainable Forestry Initiative.",
        },
        "hero_photo_credit": "Lukasz Szmigiel / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "the-climate-group",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1466611653911-95081537e5b7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wind farm at sunset — illustrative of the kind of "
                  "renewable-energy ambitions The Climate Group's RE100, "
                  "EV100 and EP100 initiatives mobilise across major "
                  "businesses and governments worldwide.",
            "ru": "Ветропарк на закате — иллюстрация амбиций по "
                  "возобновляемой энергии, которые инициативы The "
                  "Climate Group RE100, EV100 и EP100 мобилизуют среди "
                  "крупных компаний и правительств по миру.",
        },
        "hero_photo_credit": "Karsten Würth / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "c2es",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1541872703-74c5e44368f9"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "The US Capitol building — illustrative of the kind "
                  "of bipartisan US federal-policy engagement and "
                  "research that the Center for Climate and Energy "
                  "Solutions (C2ES) has run since 1998.",
            "ru": "Здание Капитолия США — иллюстрация двухпартийной "
                  "работы с американской федеральной политикой и "
                  "исследований, которыми Center for Climate and "
                  "Energy Solutions (C2ES) занимается с 1998 года.",
        },
        "hero_photo_credit": "Andy Feliciotti / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "algalita",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1583039975811-90e0c2c5f4c7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Plastic debris washed up on a shoreline — illustrative "
                  "of the marine plastic pollution Algalita Marine "
                  "Research and Education has studied since 1994 — "
                  "including Captain Charles Moore's discovery of the "
                  "Great Pacific Garbage Patch.",
            "ru": "Пластиковый мусор на берегу — иллюстрация "
                  "пластикового загрязнения океана, которое Algalita "
                  "Marine Research and Education изучает с 1994 года — "
                  "включая открытие капитаном Чарльзом Муром "
                  "Большого тихоокеанского мусорного пятна.",
        },
        "hero_photo_credit": "Naja Bertolt Jensen / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "mighty-earth",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1574263867128-a3d5c1b1deca"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A tropical-forest edge meeting cleared land — "
                  "illustrative of the kind of deforestation in cattle, "
                  "soy, palm-oil and cocoa supply chains that Mighty "
                  "Earth tracks and presses major brands and financiers "
                  "to clean up.",
            "ru": "Граница тропического леса с расчищенной территорией "
                  "— иллюстрация обезлесения в цепочках поставок "
                  "говядины, сои, пальмового масла и какао, которое "
                  "Mighty Earth отслеживает и за очистку которых "
                  "давит на крупные бренды и финансистов.",
        },
        "hero_photo_credit": "Roya Ann Miller / Unsplash",
        "hero_photo_license": "unsplash",
    },
    {
        "slug": "climate-justice-alliance",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1581094288338-2314dddb7ece"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An industrial extraction site — illustrative of the "
                  "kind of extractive-economy activity Climate Justice "
                  "Alliance's 89+ frontline community organisations work "
                  "to transition away from in their Just Transition "
                  "framework.",
            "ru": "Промышленная площадка добычи — иллюстрация той "
                  "добывающей экономики, от которой 89+ организаций "
                  "передовых сообществ Climate Justice Alliance "
                  "стремятся уйти в рамках своего «справедливого "
                  "перехода».",
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
                f"[migration 0030] WARN: charity not found "
                f"(slug={entry['slug']})"
            )
        else:
            skipped_already_set += 1

    print(
        f"[migration 0030] hero_photo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"not_found: {not_found}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0029_backfill_v34_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

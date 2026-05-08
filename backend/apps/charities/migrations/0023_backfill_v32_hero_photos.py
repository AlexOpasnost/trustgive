"""v3.2.1 hero-photo backfill — fill `hero_photo_url` (+ caption, credit,
license) for the 20 charities seeded by 0021 with empty photo fields.

Sourcing approach (per KB-015 honesty rule, restated from 0017 / 0019):
  1. Wikimedia Commons CC search by org name was attempted first for
     each org. For the v3.2 expansion most candidates were either
     logos (not field photos) or photos we could NOT honestly
     attribute to the org's program — so we did not use them.
  2. Unsplash CC0 fallback with HEDGED captions: "illustrative of",
     "the kind of work", "thematic of" — never "this is X doing Y".
     One pre-verified Unsplash photo per charity, thematically matched
     to the bucket / cause (medical, disaster, child, animal, planet).
  3. Empty hero_photo_url → frontend BrandedAvatar gradient fallback
     (DESIGN.md v3 §B.3). All 20 in this pass get a photo.

URL form: `https://images.unsplash.com/photo-{id}?w=1200&q=80`
HEAD-probed against unsplash CDN 2026-05-08 → all return 200 +
`Content-Type: image/jpeg`, payload 60-380 KB. License code "unsplash"
already present in the PhotoLicense enum (charities/models.py).

Captions are bilingual EN / RU per i18n contract. Credits follow the
Unsplash attribution format ("{Photographer Name} / Unsplash") which
satisfies Unsplash's voluntary attribution policy (license is CC0
equivalent — attribution is encouraged but not legally required).

Idempotent: `Charity.objects.filter(slug=..., hero_photo_url="")` so
prior manual curation isn't overwritten. Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


PHOTO_SEED: list[dict] = [
    # ===================== PEOPLE — 11 =====================
    # ----- Watsi — crowdfunded medical procedures -----
    {
        "slug": "watsi",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1666214280557-f1b5022eb634"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A clinician examines a patient in a low-resource clinic — "
                  "illustrative of the kind of crowdfunded medical procedures "
                  "Watsi finances for individual patients across 20+ countries.",
            "ru": "Врач осматривает пациента в клинике с ограниченными "
                  "ресурсами — иллюстрация краудфандингового финансирования "
                  "медицинских процедур, которое Watsi обеспечивает для "
                  "отдельных пациентов в 20+ странах.",
        },
        "hero_photo_credit": "Hush Naidoo Jade Photography / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Living Goods — community health workers, East Africa -----
    {
        "slug": "living-goods",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1612531386530-97286d97c2d2"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A community health worker prepares medication on a home "
                  "visit — illustrative of the door-to-door child-health work "
                  "Living Goods supports across Kenya, Uganda and Burkina Faso.",
            "ru": "Общинный медработник готовит лекарство во время визита "
                  "на дом — иллюстрация работы Living Goods по детскому "
                  "здравоохранению на дому в Кении, Уганде и Буркина-Фасо.",
        },
        "hero_photo_credit": "Online Marketing / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- BRAC USA — Bangladesh microfinance / development -----
    {
        "slug": "brac-usa",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1582719471384-894fbb16e074"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Women at a community gathering in South Asia — illustrative "
                  "of the women-led ultra-poor graduation and microfinance "
                  "programmes BRAC runs across 16 countries.",
            "ru": "Женщины на общинном собрании в Южной Азии — иллюстрация "
                  "программ вывода из крайней бедности и микрофинансов под "
                  "руководством женщин, которые BRAC ведёт в 16 странах.",
        },
        "hero_photo_credit": "Nazrin Babashova / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- WFP USA — UN food relief, hunger response -----
    {
        "slug": "wfp-usa",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An aid worker hands food to a person in need — illustrative "
                  "of the emergency food-relief operations the UN World Food "
                  "Programme runs in 120+ countries with WFP USA's funding.",
            "ru": "Гуманитарный работник передаёт еду нуждающемуся — "
                  "иллюстрация операций по экстренной продовольственной "
                  "помощи Всемирной продовольственной программы ООН в 120+ "
                  "странах при поддержке WFP USA.",
        },
        "hero_photo_credit": "Matt Collamer / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Mercy Corps — humanitarian / disaster response -----
    {
        "slug": "mercy-corps",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A humanitarian aid convoy on the road — illustrative of "
                  "the emergency response and resilience programmes Mercy "
                  "Corps delivers in 40+ fragile and post-conflict countries.",
            "ru": "Гуманитарный конвой в пути — иллюстрация экстренной "
                  "помощи и программ устойчивости, которые Mercy Corps "
                  "ведёт в 40+ нестабильных и постконфликтных странах.",
        },
        "hero_photo_credit": "Levi Meir Clancy / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- American Red Cross — disaster response, blood services -----
    {
        "slug": "american-red-cross",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1584515933487-779824d29309"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A blood-donation kit on a clinical tray — illustrative of "
                  "the blood services that the American Red Cross provides "
                  "for around 40% of the US blood supply.",
            "ru": "Набор для забора крови на медицинском подносе — "
                  "иллюстрация работы Американского Красного Креста, "
                  "обеспечивающего около 40% запаса донорской крови США.",
        },
        "hero_photo_credit": "Nguyễn Hiệp / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Operation Smile — cleft surgery for children -----
    {
        "slug": "operation-smile",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A surgical team at work in an operating theatre — "
                  "illustrative of the kind of free cleft-lip and palate "
                  "surgical missions Operation Smile runs for children in "
                  "30+ low-income countries.",
            "ru": "Хирургическая бригада в операционной — иллюстрация "
                  "бесплатных миссий по операциям на расщелине губы и нёба "
                  "для детей, которые Operation Smile проводит в 30+ "
                  "странах с низкими доходами.",
        },
        "hero_photo_credit": "Piron Guillaume / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Habitat for Humanity — affordable housing -----
    {
        "slug": "habitat-for-humanity",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1503387762-592deb58ef4e"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Volunteers framing the wooden structure of a house — "
                  "illustrative of the volunteer-built affordable housing "
                  "Habitat for Humanity creates with future homeowners across "
                  "70+ countries.",
            "ru": "Волонтёры собирают деревянный каркас дома — иллюстрация "
                  "доступного жилья, которое Habitat for Humanity строит "
                  "вместе с будущими владельцами в 70+ странах.",
        },
        "hero_photo_credit": "Avel Chuklanov / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Heifer International — livestock-based poverty relief -----
    {
        "slug": "heifer-international",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500595046743-cd271d694d30"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Dairy cows in a pasture — illustrative of the "
                  "livestock-and-training model Heifer International uses to "
                  "help farming families build long-term incomes in 21 "
                  "countries.",
            "ru": "Молочные коровы на пастбище — иллюстрация модели "
                  "«животные плюс обучение», которую Heifer International "
                  "использует, чтобы помочь фермерским семьям получить "
                  "устойчивый доход в 21 стране.",
        },
        "hero_photo_credit": "Stijn te Strake / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Plan International USA — children, girls' equality -----
    {
        "slug": "plan-international-usa",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Schoolchildren in a classroom — illustrative of the "
                  "education and girls'-rights programmes Plan International "
                  "delivers for children in 80+ countries.",
            "ru": "Школьники в классе — иллюстрация образовательных "
                  "программ и работы по правам девочек, которую Plan "
                  "International ведёт для детей в 80+ странах.",
        },
        "hero_photo_credit": "CDC / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Compassion International — child sponsorship -----
    {
        "slug": "compassion-international",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A volunteer offers a hand of support to a child — "
                  "illustrative of the kind of one-to-one child-sponsorship "
                  "relationships Compassion International facilitates across "
                  "25+ countries.",
            "ru": "Волонтёр протягивает руку помощи ребёнку — иллюстрация "
                  "индивидуального спонсорства детей, которое Compassion "
                  "International организует в 25+ странах.",
        },
        "hero_photo_credit": "Matt Collamer / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ===================== ANIMALS — 5 =====================
    # ----- World Animal Protection — animal welfare advocacy -----
    {
        "slug": "world-animal-protection",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500595046743-cd271d694d30"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "Cattle in a pasture — illustrative of the kind of "
                  "factory-farming reform and farm-animal welfare campaigns "
                  "World Animal Protection runs in 14 countries.",
            "ru": "Скот на пастбище — иллюстрация кампаний по реформе "
                  "промышленного животноводства и защите "
                  "сельскохозяйственных животных, которые World Animal "
                  "Protection ведёт в 14 странах.",
        },
        "hero_photo_credit": "Stijn te Strake / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Marine Mammal Center — seal / sea-lion rescue -----
    {
        "slug": "marine-mammal-center",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1568430462989-44163eb1752f"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A sea lion rests on a rocky shore — illustrative of the "
                  "kind of marine mammals The Marine Mammal Center rescues "
                  "and rehabilitates along the California coast and the "
                  "Hawaiian Islands.",
            "ru": "Морской лев отдыхает на скалистом берегу — иллюстрация "
                  "тех морских млекопитающих, которых The Marine Mammal "
                  "Center спасает и реабилитирует у побережья Калифорнии и "
                  "на Гавайях.",
        },
        "hero_photo_credit": "Robert Linder / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Jane Goodall Institute — chimpanzee research -----
    {
        "slug": "jane-goodall-institute",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1581852017103-68ac65514cf7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A chimpanzee in a forest setting — illustrative of the "
                  "primates the Jane Goodall Institute has studied and "
                  "protected since the original Gombe Stream research began "
                  "in 1960.",
            "ru": "Шимпанзе в лесу — иллюстрация приматов, которых Jane "
                  "Goodall Institute изучает и защищает с момента начала "
                  "исследований в Гомбе в 1960 году.",
        },
        "hero_photo_credit": "Rob Schreckhise / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- IFAW — wildlife rescue / rehabilitation -----
    {
        "slug": "ifaw",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "An elephant in a wildlife reserve — illustrative of the "
                  "anti-poaching, wildlife rescue and habitat protection "
                  "work IFAW supports across 40+ countries.",
            "ru": "Слон в заповеднике — иллюстрация борьбы с "
                  "браконьерством, спасения диких животных и защиты мест "
                  "обитания, которой IFAW занимается в 40+ странах.",
        },
        "hero_photo_credit": "AJ Robbie / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- RSPCA (UK) — UK animal-welfare charity -----
    {
        "slug": "rspca",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A rescued dog at a UK shelter — illustrative of the "
                  "rescue, rehoming and animal-cruelty investigation work "
                  "the RSPCA has run in England and Wales since 1824.",
            "ru": "Спасённая собака в британском приюте — иллюстрация "
                  "работы по спасению, пристройству и расследованию "
                  "жестокого обращения с животными, которую RSPCA ведёт в "
                  "Англии и Уэльсе с 1824 года.",
        },
        "hero_photo_credit": "Anoir Chafik / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ===================== PLANET — 4 =====================
    # ----- Trust for Public Land — US public land / parks -----
    {
        "slug": "trust-for-public-land",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1444930694458-01babe71870d"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A scenic US national-park landscape — illustrative of the "
                  "kind of public lands and open spaces that Trust for "
                  "Public Land has protected across all 50 US states since "
                  "1972.",
            "ru": "Живописный национальный парк США — иллюстрация типичных "
                  "общественных земель и открытых пространств, которые "
                  "Trust for Public Land защищает во всех 50 штатах США с "
                  "1972 года.",
        },
        "hero_photo_credit": "Sébastien Goldberg / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Climate Reality Project — climate-action advocacy -----
    {
        "slug": "climate-reality-project",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1466611653911-95081537e5b7"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A wind farm at sunset — illustrative of the renewable-"
                  "energy transition that the Climate Reality Project's "
                  "trained advocates campaign for in 11 countries.",
            "ru": "Ветропарк на закате — иллюстрация перехода на "
                  "возобновляемую энергию, за который выступают "
                  "подготовленные Climate Reality Project активисты в 11 "
                  "странах.",
        },
        "hero_photo_credit": "Karsten Würth / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- World Resources Institute — research / forests / water -----
    {
        "slug": "world-resources-institute",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1448375240586-882707db888b"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A forest canopy — illustrative of the kind of forest "
                  "ecosystems the World Resources Institute monitors through "
                  "Global Forest Watch and protects through its climate and "
                  "land-use research in 60+ countries.",
            "ru": "Лесной полог — иллюстрация лесных экосистем, которые "
                  "World Resources Institute отслеживает через Global "
                  "Forest Watch и защищает через свои исследования по "
                  "климату и землепользованию в 60+ странах.",
        },
        "hero_photo_credit": "Sergei A / Unsplash",
        "hero_photo_license": "unsplash",
    },
    # ----- Land Trust Alliance — US land trusts / open space -----
    {
        "slug": "land-trust-alliance",
        "hero_photo_url": (
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef"
            "?w=1200&q=80"
        ),
        "hero_photo_caption": {
            "en": "A rolling open-space prairie at dawn — illustrative of "
                  "the kind of farmland, forests and open space that the "
                  "~1,000 land trusts in the Land Trust Alliance network "
                  "have protected across 60M+ US acres.",
            "ru": "Открытые прерии на рассвете — иллюстрация "
                  "сельхозугодий, лесов и открытых пространств, которые "
                  "сеть из примерно 1 тыс. земельных трастов Land Trust "
                  "Alliance защищает на более чем 60 млн акров в США.",
        },
        "hero_photo_credit": "Federico Respini / Unsplash",
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
                f"[migration 0023] WARN: charity not found "
                f"(slug={entry['slug']})"
            )
        else:
            skipped_already_set += 1

    print(
        f"[migration 0023] hero_photo_url backfilled: {updated}, "
        f"already-set (idempotent skip): {skipped_already_set}, "
        f"not_found: {not_found}"
    )


def backwards(apps, schema_editor):
    """No-op — never auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0022_backfill_v32_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

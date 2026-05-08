"""v3.1.2 data-quality fill pass — backfill `hero_photo_url` (+ caption,
credit, license) for the 21 charities where migration 0011 / 0015 left the
field empty.

User feedback after v3.1 ship: ~21 of 38 cards render the gradient
placeholder because Commons had no obviously matching photo at the time of
v3.1. This migration adds GENERIC ILLUSTRATIVE photos — visually relevant
to each org's mission, with HONEST captions that DO NOT misattribute the
photo to the charity itself. (Example: a public-domain FEMA dog-shelter
photo is a fair illustration of Humane Society's work without claiming
HSUS took the picture.)

Photo sourcing rules (DESIGN.md v3.0 §D, restated):
  1. Wikimedia Commons (CC-BY / CC-BY-SA / CC0 / Public Domain) preferred
  2. Charity press kit / media library — out of scope for this migration
     (would require manual licensing review per org)
  3. Empty hero_photo_url → frontend falls back to BrandedAvatar gradient

Captions are honest: "Generic illustrative photo of {topic}" or
"{Specific event}, illustrating the kind of work {org} does." We never
claim the photo IS of the org's program unless it actually is.

Probe protocol — see migration 0016 docstring. All 16 URLs in this file
were HEAD-probed 2026-05-08 → HTTP 200 + Content-Type image/jpeg.

Skipped (no suitable Commons photo found):
  - msf-usa: Commons has many MSF logos but no field photo we could
    confidently attribute as MSF work. Skipped.
  - earthjustice: no relevant litigation/courtroom photo on Commons. Skipped.
  - sierra-club-foundation: no relevant wilderness-conservation photo
    we could attribute to Sierra Club program. Skipped.
  - nrdc: only generic climate-protest photos; not the right framing for
    NRDC's environmental-law mission. Skipped.
  - nuzhna-pomosh: Russian charity; no representative single image
    (the foundation supports many sub-orgs). Skipped — gradient placeholder.

Idempotent: uses Charity.objects.filter().update() keyed on
(country, registration_id). Reverse is a no-op.
"""
from __future__ import annotations

from django.db import migrations


# Each entry: (country, registration_id) → photo payload
PHOTO_SEED: list[dict] = [
    # ---------- People bucket ----------
    {
        "country": "US",
        "registration_id": "060726487",  # Save the Children
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/6/67/"
            "Providing_check-ups_for_newborn_children_at_a_Save_the_Children"
            "_clinic_in_Lebanons_Bekaa_Valley_%2811174159186%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "A health worker provides check-ups for newborn children at a "
                  "Save the Children clinic in Lebanon's Bekaa Valley — the "
                  "frontline child-health work Save the Children Federation runs "
                  "in conflict-affected regions.",
            "ru": "Медицинский работник осматривает новорождённых в клинике Save "
                  "the Children в долине Бекаа, Ливан — пример работы фонда по "
                  "защите детей в зонах конфликтов.",
        },
        "hero_photo_credit": "Russell Watkins / DFID / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    {
        "country": "US",
        "registration_id": "131760110",  # UNICEF USA
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/d/df/"
            "Kenya_Polio_Vaccination_Launch_%289308090393%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Polio vaccination campaign launch in Kenya — the kind of "
                  "child-immunisation programme UNICEF runs at national scale "
                  "across 190+ countries.",
            "ru": "Запуск кампании по вакцинации от полиомиелита в Кении — "
                  "пример национальных программ детской иммунизации UNICEF в "
                  "более чем 190 странах.",
        },
        "hero_photo_credit": "Pete Lewis / DFID / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "951831116",  # Direct Relief
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/3/30/"
            "Third_Army_prepares_for_future_humanitarian_aid%2C_disaster_relief"
            "_110825-A-WD324-001.jpg"
        ),
        "hero_photo_caption": {
            "en": "Crews load humanitarian-aid pallets for disaster-relief "
                  "delivery — illustrative of Direct Relief's emergency-medical "
                  "response model in over 80 countries.",
            "ru": "Бригада грузит гуманитарные грузы для отправки в зону "
                  "стихийного бедствия — пример модели экстренного "
                  "медицинского реагирования Direct Relief в более чем 80 "
                  "странах.",
        },
        "hero_photo_credit": "U.S. Army / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "263618722",  # Pencils of Promise
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/e/e2/"
            "Children_being_taught_in_an_outdoor_clasroom_in_northern_Ghana"
            "_%288406164622%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Children in an outdoor classroom in northern Ghana — "
                  "illustrative of the school-building and education programmes "
                  "Pencils of Promise runs in Ghana, Guatemala and Laos.",
            "ru": "Дети в классе под открытым небом на севере Ганы — пример "
                  "образовательных программ и строительства школ, которые "
                  "Pencils of Promise ведёт в Гане, Гватемале и Лаосе.",
        },
        "hero_photo_credit": "DFID / Wikimedia Commons / CC BY-SA 2.0",
        "hero_photo_license": "cc-by-sa",
    },
    {
        "country": "US",
        "registration_id": "135660870",  # International Rescue Committee
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/f/fb/"
            "Walking_down_the_main_street_of_Zaatari_refugee_camp"
            "_%289638143042%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Main street of the Zaatari refugee camp, Jordan — the kind "
                  "of refugee-camp setting where the International Rescue "
                  "Committee delivers health, education and protection "
                  "services.",
            "ru": "Главная улица лагеря беженцев Заатари в Иордании — пример "
                  "лагеря, где International Rescue Committee оказывает "
                  "медицинскую, образовательную и защитную помощь.",
        },
        "hero_photo_credit": "Russell Watkins / DFID / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    {
        "country": "US",
        "registration_id": "131685039",  # CARE USA
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/a/a6/"
            "Tiru_with_her_baby_daughter%2C_receiving_nutrition_support_in"
            "_southern_Ethiopia%2C_thanks_to_CARE_International_%286021951280%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "A mother and her baby daughter receive nutrition support in "
                  "southern Ethiopia through a CARE International programme — "
                  "the food-security and maternal-health work CARE delivers "
                  "across 100+ countries.",
            "ru": "Мать с дочерью получают пищевую поддержку в южной Эфиопии "
                  "по программе CARE International — пример работы CARE по "
                  "продовольственной безопасности и материнскому здоровью в "
                  "более чем 100 странах.",
        },
        "hero_photo_credit": "DFID / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    {
        "country": "US",
        "registration_id": "223936753",  # charity:water
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/2/2f/"
            "Providing_clean_water_%287047883897%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Children gather around a clean-water well — illustrative of "
                  "the well-drilling and water-system projects charity:water "
                  "funds in 29 countries.",
            "ru": "Дети у колодца с чистой водой — пример проектов по бурению "
                  "скважин и созданию водных систем, которые charity:water "
                  "финансирует в 29 странах.",
        },
        "hero_photo_credit": "DFID / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    # ---------- Animals bucket ----------
    {
        "country": "US",
        "registration_id": "530225390",  # Humane Society of the United States
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/6/69/"
            "FEMA_-_38418_-_Rescued_dog_at_a_shelter_in_Texas.jpg"
        ),
        "hero_photo_caption": {
            "en": "A rescued dog at an emergency animal shelter in Texas — "
                  "illustrative of the disaster-response, rescue and shelter "
                  "advocacy work the Humane Society of the United States "
                  "supports nationwide.",
            "ru": "Спасённая собака во временном приюте в Техасе — пример "
                  "работы по реагированию на стихийные бедствия и поддержке "
                  "приютов, которой занимается Humane Society of the United "
                  "States.",
        },
        "hero_photo_credit": "FEMA / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "931140967",  # PetSmart Charities
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/a/a2/"
            "Families_find_new_furry_friends_at_adoption_event"
            "_140726-M-DN141-001.jpg"
        ),
        "hero_photo_caption": {
            "en": "Families meet adoptable pets at a community adoption event "
                  "— illustrative of the in-store adoption events and shelter "
                  "grants PetSmart Charities funds across North America.",
            "ru": "Семьи знакомятся с питомцами на мероприятии по пристройству "
                  "— пример программ по пристройству и грантов приютам, "
                  "которые PetSmart Charities финансирует в Северной Америке.",
        },
        "hero_photo_credit": "U.S. Marine Corps / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "131740011",  # Wildlife Conservation Society
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/8/8d/"
            "Bronx_Zoo_Little_Blue_Penguin_Habitat.jpg"
        ),
        "hero_photo_caption": {
            "en": "Little blue penguin habitat at the Bronx Zoo — the Wildlife "
                  "Conservation Society operates the Bronx Zoo and four other "
                  "New York City wildlife parks alongside its global field "
                  "conservation programmes.",
            "ru": "Вольер малых пингвинов в Бронксском зоопарке — Wildlife "
                  "Conservation Society управляет Бронксским и ещё четырьмя "
                  "зоопарками Нью-Йорка наряду с глобальными программами "
                  "охраны природы.",
        },
        "hero_photo_credit": "Wildlife Conservation Society / Wikimedia Commons / CC0",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "131624102",  # National Audubon Society
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/3/3e/"
            "Audubons_Curtis_Smalling_discusses_bird_conservation"
            "_%288190239591%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "An Audubon ornithologist discusses bird-conservation work "
                  "in the field — the National Audubon Society protects birds "
                  "and habitats across the Americas through science, advocacy "
                  "and education.",
            "ru": "Орнитолог Audubon рассказывает о работе по охране птиц в "
                  "поле — National Audubon Society защищает птиц и их места "
                  "обитания в Америках через науку, адвокатство и "
                  "образование.",
        },
        "hero_photo_credit": "U.S. Forest Service / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "237147797",  # Best Friends Animal Society
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/e/e5/"
            "Kanab%2C_Utah_%28101365726%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Kanab, Utah — home of the Best Friends Animal Sanctuary, "
                  "the largest no-kill animal sanctuary in the United States.",
            "ru": "Канаб, Юта — здесь расположено Best Friends Animal "
                  "Sanctuary, крупнейший в США приют, не практикующий "
                  "усыпление.",
        },
        "hero_photo_credit": "Bureau of Land Management / Wikimedia Commons / CC BY-SA 2.0",
        "hero_photo_license": "cc-by-sa",
    },
    {
        "country": "US",
        "registration_id": "530183181",  # Defenders of Wildlife
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/0/03/"
            "Wildlife_Safari_Park_%2814%29_-_gray_wolfs_%2848620984343%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Gray wolves at a wildlife park — illustrative of Defenders "
                  "of Wildlife's flagship work to protect wolves and other "
                  "endangered species across North America.",
            "ru": "Серые волки в природном парке — пример флагманской работы "
                  "Defenders of Wildlife по защите волков и других видов, "
                  "находящихся под угрозой исчезновения, в Северной Америке.",
        },
        "hero_photo_credit": "Eric Kilby / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    # ---------- Planet bucket ----------
    {
        "country": "US",
        "registration_id": "521497470",  # Conservation International
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/a/a5/"
            "Improve_Forest_Management_and_Protect_Biodiversity"
            "_%285475465287%29.jpg"
        ),
        "hero_photo_caption": {
            "en": "Sustainable forest-management activity in a tropical "
                  "biodiversity hotspot — illustrative of Conservation "
                  "International's work in 30+ countries to protect "
                  "biodiversity and natural carbon storage.",
            "ru": "Устойчивое лесопользование в тропической зоне с высоким "
                  "биоразнообразием — пример работы Conservation "
                  "International в более чем 30 странах по защите "
                  "биоразнообразия и природных накопителей углерода.",
        },
        "hero_photo_credit": "USAID / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    {
        "country": "US",
        "registration_id": "133500609",  # Rainforest Trust
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/d/d0/"
            "Aerial_view_of_the_Amazon_Rainforest.jpg"
        ),
        "hero_photo_caption": {
            "en": "Aerial view of the Amazon rainforest — illustrative of the "
                  "tropical-forest land purchases Rainforest Trust funds with "
                  "local partners across 60+ countries.",
            "ru": "Амазонский тропический лес с воздуха — пример покупок "
                  "земельных участков, которые Rainforest Trust финансирует "
                  "вместе с местными партнёрами в более чем 60 странах.",
        },
        "hero_photo_credit": "Neil Palmer / CIAT / Wikimedia Commons / CC BY-SA 2.0",
        "hero_photo_license": "cc-by-sa",
    },
    {
        "country": "US",
        "registration_id": "116107128",  # Environmental Defense Fund
        "hero_photo_url": (
            "https://upload.wikimedia.org/wikipedia/commons/2/22/"
            "Wind_turbines_-_Flickr_-_the_russians_are_here.jpg"
        ),
        "hero_photo_caption": {
            "en": "Wind turbines — illustrative of the clean-energy transition "
                  "the Environmental Defense Fund advocates for through "
                  "science-based climate policy work.",
            "ru": "Ветрогенераторы — пример перехода к чистой энергии, за "
                  "который выступает Environmental Defense Fund через "
                  "научно-обоснованную климатическую политику.",
        },
        "hero_photo_credit": "Glyn Lowe / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
]


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    not_found = 0

    for entry in PHOTO_SEED:
        n = Charity.objects.filter(
            country=entry["country"],
            registration_id=entry["registration_id"],
        ).update(
            hero_photo_url=entry["hero_photo_url"],
            hero_photo_caption=entry["hero_photo_caption"],
            hero_photo_credit=entry["hero_photo_credit"],
            hero_photo_license=entry["hero_photo_license"],
        )
        if n == 0:
            print(
                f"[migration 0017] WARN: charity not found "
                f"({entry['country']}/{entry['registration_id']})"
            )
            not_found += 1
        else:
            updated += 1

    print(
        f"[migration 0017] hero_photo_url backfilled: {updated}, "
        f"not_found: {not_found}"
    )


def backwards(apps, schema_editor):
    """No-op. Don't auto-clear curated photo metadata."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0016_fill_missing_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

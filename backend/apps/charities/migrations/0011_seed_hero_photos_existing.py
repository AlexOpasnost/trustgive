"""v3.0 photo-first redesign — backfill hero photos + bucket on existing 11 charities.

Companion to schema migration 0010. For each of the 11 charities seeded in
migration 0008 we attach:

  - hero_photo_url   — verified Wikimedia Commons / OGL / public-domain URL
  - hero_photo_caption — bilingual one-line caption (en + ru)
  - hero_photo_credit — photographer + license attribution string
  - hero_photo_license — short license code (cc-by, cc-by-sa, cc0, ogl)
  - bucket           — all 11 are bucket="people" per DESIGN.md §G.1

Photo sourcing rules (DESIGN.md v3.0 §D):
  1. Wikimedia Commons (CC-BY/CC-BY-SA/CC0/OGL/PD) preferred
  2. Charity press kit / media library (license="press-kit")
  3. Unsplash CC0 (license="unsplash") — fallback only

Every URL was validated by HEAD-probing upload.wikimedia.org; all 10
returned HTTP 200 + Content-Type: image/jpeg before this migration was
written. The Need Help Foundation row has hero_photo_url="" because no
suitable Russian charity-work-specific photo was found on Commons after 5
search attempts; frontend falls back to BrandedAvatar per §D fallback chain.

Idempotent — uses Charity.objects.filter(...).update(...) keyed on
(country, registration_id), so re-running this migration just re-stamps the
photo metadata. Won't create duplicate rows; won't touch financials or
source_documents (those belong to migration 0008).

Reverse migration is a no-op — we never null-out manually curated photo
fields on rollback (would lose human-curated work).
"""
from __future__ import annotations

from django.db import migrations


# Each entry: dict keyed by (country, registration_id) of the existing
# row from migration 0008, plus the v3.0 photo + bucket payload.
PHOTO_SEED: list[dict] = [
    # -------------------------------------------------------------------
    # GiveDirectly (US, EIN 27-1661997) — bucket=people
    # Photo: water kiosk in low-income Nairobi neighbourhood (Bulbul) —
    # documents the kind of community where GiveDirectly operates cash
    # transfer programs. CC-BY 2.0 via SuSanA Secretariat.
    # -------------------------------------------------------------------
    {
        "country": "US",
        "registration_id": "271661997",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/7/75/Water_kiosk_at_low-income_area_Bulbul_near_Nairobi%2C_Kenya_%2810543518693%29.jpg",
        "hero_photo_caption": {
            "en": "Residents of the low-income Bulbul neighbourhood near Nairobi, Kenya — the kind of community where GiveDirectly delivers unconditional cash transfers via mobile money.",
            "ru": "Жители малообеспеченного района Булбул недалеко от Найроби, Кения — типичное сообщество, где GiveDirectly переводит безусловные денежные пособия через мобильные деньги.",
        },
        "hero_photo_credit": "SuSanA Secretariat / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    # -------------------------------------------------------------------
    # Helen Keller International (US, EIN 13-2623126) — bucket=people
    # Photo: Health Minister administering a Vitamin A capsule to a child
    # at the Dhaka Shishu Hospital national vitamin A campaign launch —
    # visually exact for HKI's flagship program. Public Domain.
    # -------------------------------------------------------------------
    {
        "country": "US",
        "registration_id": "132623126",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Health_Minister_Zahid_Maleque_administering_Vitamin_A_Plus_capsule_to_child_during_campaign_Dhaka_Shishu_Hospital_2019-06-22_%28PID-0038147%29.jpg",
        "hero_photo_caption": {
            "en": "A health worker administers a Vitamin A capsule to a child at the National Vitamin A Plus Campaign launch, Dhaka Shishu Hospital, 2019.",
            "ru": "Медицинский работник даёт капсулу витамина A ребёнку на запуске национальной кампании Vitamin A Plus, Госпиталь детей Даки, 2019.",
        },
        "hero_photo_credit": "Press Information Department / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    # -------------------------------------------------------------------
    # New Incentives (US, EIN 45-5165903) — bucket=people
    # Photo: Polio vaccination in Nigeria — exactly New Incentives' core
    # program: cash incentives for routine immunisation in Nigeria. CC-BY-SA 4.0.
    # -------------------------------------------------------------------
    {
        "country": "US",
        "registration_id": "455165903",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Polio_Vaccination_in_Nigeria.jpg",
        "hero_photo_caption": {
            "en": "Polio vaccination of an infant in Nigeria — New Incentives runs conditional cash transfers for routine immunisation in Northern Nigeria.",
            "ru": "Вакцинация младенца от полиомиелита в Нигерии — New Incentives ведёт программу денежных стимулов за плановую вакцинацию в Северной Нигерии.",
        },
        "hero_photo_credit": "Asap_Kamal / Wikimedia Commons / CC BY-SA 4.0",
        "hero_photo_license": "cc-by-sa",
    },
    # -------------------------------------------------------------------
    # The END Fund (US, EIN 27-0983322) — bucket=people
    # Photo: Community volunteers distributing anti-parasitic drugs in
    # Cote d'Ivoire — exact match for END Fund's mass-drug-administration
    # model. Public Domain via USAID Africa.
    # -------------------------------------------------------------------
    {
        "country": "US",
        "registration_id": "270983322",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/8/87/On_the_Road_to_Eliminating_Neglected_Tropical_Diseases_in_Cote_d%27Ivoire_%2829464931444%29.jpg",
        "hero_photo_caption": {
            "en": "Community volunteers distribute anti-parasitic medicine to villagers during a mass drug administration campaign for neglected tropical diseases in Côte d'Ivoire.",
            "ru": "Волонтёры из местного сообщества раздают противопаразитарные препараты жителям деревни в ходе массовой кампании по лечению забытых тропических болезней в Кот-д'Ивуаре.",
        },
        "hero_photo_credit": "USAID in Africa / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    # -------------------------------------------------------------------
    # Evidence Action (US, EIN 46-0704563) — bucket=people
    # Photo: Schoolchildren receiving a deworming dose — exact match for
    # the Deworm the World flagship program. Public Domain via USAID Vietnam.
    # -------------------------------------------------------------------
    {
        "country": "US",
        "registration_id": "460704563",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/School_children_receive_a_dose_of_deworming_medicine_in_Dien_Bien_%288141252442%29.jpg",
        "hero_photo_caption": {
            "en": "Schoolchildren receive a dose of deworming medicine — the model behind Evidence Action's Deworm the World program, deployed at national scale across low-income countries.",
            "ru": "Школьники принимают дозу противоглистного препарата — модель программы Deworm the World фонда Evidence Action, развёрнутой в национальном масштабе в странах с низкими доходами.",
        },
        "hero_photo_credit": "USAID Vietnam (Richard Nyberg) / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    # -------------------------------------------------------------------
    # AMF — Against Malaria Foundation (UK, Charity 1105319) — bucket=people
    # Photo: Mother setting up an insecticide-treated bed net for her child
    # in Tanzania — exact match for AMF's bed-net distribution work.
    # Public Domain via President's Malaria Initiative.
    # -------------------------------------------------------------------
    {
        "country": "GB",
        "registration_id": "1105319",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Tanzania_School_ITN_Distribution_43509-60_%2827521858660%29.jpg",
        "hero_photo_caption": {
            "en": "A mother sets up an insecticide-treated bed net for her child in Mitengo Mtwara, Tanzania — the LLIN distribution model AMF funds across sub-Saharan Africa.",
            "ru": "Мать устанавливает противомоскитную сетку с инсектицидом для своего ребёнка в Митенго Мтвара, Танзания — модель распределения LLIN, которую AMF финансирует в Африке к югу от Сахары.",
        },
        "hero_photo_credit": "Vector Works / Mark Bashagi (President's Malaria Initiative) / Wikimedia Commons / Public Domain",
        "hero_photo_license": "cc0",
    },
    # -------------------------------------------------------------------
    # Crisis (UK, Charity 1082947) — bucket=people
    # Photo: Two homeless people sleeping rough on Christmas Day morning
    # in Woolwich, London — visually exact for Crisis's flagship Crisis at
    # Christmas program. CC-BY-SA 2.0 via Alisdare Hickson.
    # -------------------------------------------------------------------
    {
        "country": "GB",
        "registration_id": "1082947",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Sleeping_rough_on_Christmas_Day_morning_-_two_homeless_people_in_Woolwich%2C_London._%2823877445861%29.jpg",
        "hero_photo_caption": {
            "en": "Two homeless people sleeping rough on Christmas Day morning, Woolwich, London — the reality Crisis tackles year-round and through the flagship Crisis at Christmas program.",
            "ru": "Двое бездомных спят на улице утром Рождества, Вулидж, Лондон — реальность, с которой Crisis борется круглый год и через флагманскую программу Crisis at Christmas.",
        },
        "hero_photo_credit": "Alisdare Hickson / Wikimedia Commons / CC BY-SA 2.0",
        "hero_photo_license": "cc-by-sa",
    },
    # -------------------------------------------------------------------
    # RNLI (UK, Charity 209603) — bucket=people
    # Photo: An RNLI lifeboat crew member reaches out to a Royal Navy
    # winchman during a night-time rescue exercise off the Cornish coast.
    # OGL v1.0 (Open Government License) via UK MoD.
    # -------------------------------------------------------------------
    {
        "country": "GB",
        "registration_id": "209603",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/8/84/RNLI_Lifeboat_Crew_Reaching_Out_to_Royal_Navy_Rescue_Winchman_MOD_45153646.jpg",
        "hero_photo_caption": {
            "en": "An RNLI lifeboat crew member reaches out to a Royal Navy rescue winchman during a night-time search-and-rescue exercise off the Cornish coast.",
            "ru": "Член экипажа спасательного судна RNLI принимает спасателя с вертолёта Королевского флота на ночной тренировке поиска и спасения у побережья Корнуолла.",
        },
        "hero_photo_credit": "POA(Phot) Paul A'Barrow / UK MoD via Wikimedia Commons / OGL v1.0",
        "hero_photo_license": "ogl",
    },
    # -------------------------------------------------------------------
    # Oxfam GB (UK, Charity 202918) — bucket=people
    # Photo: Oxfam health workers distributing aid (jerry cans + soap) in
    # Dadaab refugee camp — the kind of humanitarian work Oxfam GB delivers
    # globally. CC-BY 2.0 via Oxfam East Africa.
    # -------------------------------------------------------------------
    {
        "country": "GB",
        "registration_id": "202918",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/3/32/Oxfam_East_Africa_-_Oxfam_workers_distribute_aid_in_Dadaab_camp.jpg",
        "hero_photo_caption": {
            "en": "Oxfam workers prepare to distribute jerry cans and soap to newly arrived refugees at the Dadaab camp, Kenya — the kind of humanitarian operation Oxfam GB runs in 70+ countries.",
            "ru": "Сотрудники Oxfam готовятся к раздаче канистр и мыла прибывающим беженцам в лагере Дадааб, Кения — тип гуманитарной операции, которую Oxfam GB ведёт в более чем 70 странах.",
        },
        "hero_photo_credit": "Oxfam East Africa / Wikimedia Commons / CC BY 2.0",
        "hero_photo_license": "cc-by",
    },
    # -------------------------------------------------------------------
    # Need Help Foundation / Нужна Помощь (RU, ОГРН 1157700009330) — bucket=people
    # No suitable Russian-charity-work-specific Commons photo found after
    # 5+ search attempts; the fund supports many regional NGOs across many
    # cause areas, so no single image is representative. Falling back to
    # BrandedAvatar (DESIGN.md §D fallback chain).
    # -------------------------------------------------------------------
    {
        "country": "RU",
        "registration_id": "1157700009330",
        "bucket": "people",
        "hero_photo_url": "",
        "hero_photo_caption": {"en": "", "ru": ""},
        "hero_photo_credit": "",
        "hero_photo_license": "",
    },
    # -------------------------------------------------------------------
    # Nochlezhka / Ночлежка (RU, ОГРН 1037800033170) — bucket=people
    # Photo: Distribution of hot food at the Nochlezhka "Night Bus" stop —
    # the iconic Nochlezhka outreach program. CC-BY-SA 4.0 via Kalinovskaia
    # (the photo IS from Nochlezhka's own Commons category).
    # -------------------------------------------------------------------
    {
        "country": "RU",
        "registration_id": "1037800033170",
        "bucket": "people",
        "hero_photo_url": "https://upload.wikimedia.org/wikipedia/commons/6/67/%D0%9D%D0%BE%D1%87%D0%BD%D0%BE%D0%B9_%D0%B0%D0%B2%D1%82%D0%BE%D0%B1%D1%83%D1%81.jpg",
        "hero_photo_caption": {
            "en": "Hot meal distribution at a Nochlezhka 'Night Bus' stop in St Petersburg — the iconic mobile outreach program reaching homeless people on cold nights.",
            "ru": "Раздача горячей еды на остановке «Ночного автобуса» Ночлежки в Санкт-Петербурге — флагманская мобильная программа поддержки бездомных людей в холодные ночи.",
        },
        "hero_photo_credit": "Kalinovskaia / Wikimedia Commons / CC BY-SA 4.0",
        "hero_photo_license": "cc-by-sa",
    },
]


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    updated = 0
    not_found = 0

    for entry in PHOTO_SEED:
        # Use update() not save() — bypasses signals (we don't need to
        # re-trigger the Postgres search_vector trigger; it doesn't index
        # photo fields). update_or_create-style: filter by the natural
        # key, .update() on whatever matches.
        n = Charity.objects.filter(
            country=entry["country"],
            registration_id=entry["registration_id"],
        ).update(
            bucket=entry["bucket"],
            hero_photo_url=entry["hero_photo_url"],
            hero_photo_caption=entry["hero_photo_caption"],
            hero_photo_credit=entry["hero_photo_credit"],
            hero_photo_license=entry["hero_photo_license"],
        )
        if n == 0:
            print(
                f"[migration 0011] WARNING: charity not found "
                f"({entry['country']}/{entry['registration_id']}) — "
                f"skipping. Migration 0008 must run first."
            )
            not_found += 1
        else:
            updated += 1

    print(
        f"[migration 0011] hero photos backfilled: {updated} updated, "
        f"{not_found} not found (need 0008 to have run first)."
    )


def backwards(apps, schema_editor):
    """No-op. We never auto-clear curated photo metadata on rollback."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0010_charity_v3_photo_and_bucket"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

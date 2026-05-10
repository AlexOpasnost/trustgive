"""v3.12 catalog expansion — seed 31 Animal + Planet charities (407 -> ~438).

User-requested batch focused on the two underrepresented buckets:
  - Animals: was 45, now 59 (+14)
  - Planet:  was 64, now 81 (+17)

No new countries — uses existing US/GB only.

Animal entries (14): backfilling well-known orgs the catalog was missing
in the animal-welfare, marine-life, farm-animal-protection space.
Planet entries (17): national parks, reforestation, climate strategy,
ocean/coast protection, US conservation policy.

Idempotent. Defensive is_blocked(). Reverse no-op.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import migrations

from apps.charities.blocklist import is_blocked


NEW_CAUSES: dict[str, dict[str, str]] = {
    "marine-mammal-protection": {"en": "Marine mammals (whales, dolphins, seals)", "ru": "Морские млекопитающие (киты, дельфины, тюлени)"},
    "national-parks-us": {"en": "US National Parks", "ru": "Национальные парки США"},
    "redwoods-old-growth": {"en": "Redwoods & old-growth forests", "ru": "Секвойи и старовозрастные леса"},
    "reforestation": {"en": "Reforestation & tree-planting", "ru": "Лесовосстановление и посадка деревьев"},
    "rewilding": {"en": "Rewilding", "ru": "Восстановление дикой природы (rewilding)"},
    "marine-pollution": {"en": "Marine pollution", "ru": "Загрязнение океанов"},
    "freshwater-fish": {"en": "Freshwater fisheries", "ru": "Пресноводные рыбные ресурсы"},
    "pollinators": {"en": "Pollinators (bees, butterflies)", "ru": "Опылители (пчёлы, бабочки)"},
    "animal-rights-legal": {"en": "Animal-rights legal advocacy", "ru": "Юридическая защита прав животных"},
    "energy-efficiency": {"en": "Energy efficiency & RMI-style strategy", "ru": "Энергоэффективность и стратегия RMI"},
    "carbon-offsetting": {"en": "Verified carbon offset projects", "ru": "Верифицированные углеродные офсеты"},
    "rural-protection-uk": {"en": "Rural England protection", "ru": "Защита сельской Англии"},
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
    # ============== ANIMALS (14) ==============
    E("animal-equality", "US", "271601357", "animals",
      "Animal Equality", "Animal Equality",
      "International farm-animal protection NGO — investigations, corporate campaigns, legal advocacy.",
      "Международная НПО по защите сельхозживотных — расследования, корпоративные кампании, юридическая адвокация.",
      "Animal Equality (EIN 27-1601357, founded 2006) operates in 9 countries (US, UK, Spain, Italy, Germany, Mexico, Brazil, India, Liechtenstein). Conducts undercover investigations of factory farms, pushes corporate cage-free and welfare-improvement commitments, and runs Love Veg outreach. Top-rated charity by Animal Charity Evaluators.",
      "Animal Equality (EIN 27-1601357, основан в 2006 году) работает в 9 странах (США, Великобритания, Испания, Италия, Германия, Мексика, Бразилия, Индия, Лихтенштейн). Проводит тайные расследования фабричных ферм, продвигает корпоративные обязательства cage-free и улучшения благополучия, ведёт outreach Love Veg. Топ-рейтинг Animal Charity Evaluators.",
      "https://animalequality.org/donate/", 15000000, 82, 2006, date(2024, 12, 31),
      ["farm-animal-welfare", "animal-welfare"],
      _us_pp("271601357"), "irs_990", _verify_us(), "medium"),

    E("peta-foundation", "US", "521218336", "animals",
      "PETA Foundation", "PETA Foundation",
      "Provides legal and educational support to People for the Ethical Treatment of Animals.",
      "Обеспечивает юридическую и образовательную поддержку People for the Ethical Treatment of Animals.",
      "PETA Foundation (EIN 52-1218336, founded 1980) is the 501(c)(3) charitable arm of PETA, providing legal services and educational programmes to fight animal cruelty in factory farming, fur, cosmetics testing, captive entertainment, and pet industry. Has filed landmark animal-rights legal cases. PETA itself is a 501(c)(4).",
      "PETA Foundation (EIN 52-1218336, основан в 1980 году) — благотворительное крыло PETA в форме 501(c)(3), обеспечивающее юридические услуги и образовательные программы против жестокости к животным в фабричном животноводстве, мехе, тестировании косметики, развлекательном плену, индустрии домашних животных. Подал знаковые правозащитные иски. Сама PETA — 501(c)(4).",
      "https://www.peta.org/donate/", 80000000, 84, 1980, date(2024, 7, 31),
      ["animal-welfare", "farm-animal-welfare", "animal-rights-legal"],
      _us_pp("521218336"), "irs_990", _verify_us()),

    E("sea-shepherd-conservation-society", "US", "953220919", "animals",
      "Sea Shepherd Conservation Society (US)", "Sea Shepherd Conservation Society",
      "Direct-action marine conservation — patrol ships disrupting illegal fishing and whaling.",
      "Прямое действие по охране океанов — корабли патрулируют, нарушая нелегальный промысел и китобойство.",
      "Sea Shepherd Conservation Society (EIN 95-3220919, founded 1977 by Paul Watson) is the US 501(c)(3) of the international Sea Shepherd movement. Operates a fleet of ~10 ships disrupting illegal fishing in marine-protected areas, partnering with national governments (e.g. Liberia, Gabon, Mexico Vaquita protection). Sea Shepherd Global is a separate Netherlands entity.",
      "Sea Shepherd Conservation Society (EIN 95-3220919, основано в 1977 году Полом Уотсоном) — американская 501(c)(3) международного движения Sea Shepherd. Управляет флотом ~10 кораблей, нарушающих нелегальный промысел в морских охраняемых районах, в партнёрстве с национальными правительствами (Либерия, Габон, Мексика — защита Vaquita). Sea Shepherd Global — отдельная нидерландская организация.",
      "https://seashepherd.org/donate/", 13000000, 76, 1977, date(2024, 6, 30),
      ["marine-mammal-protection", "wildlife-conservation", "ocean-protection"],
      _us_pp("953220919"), "irs_990", _verify_us(), "medium"),

    E("whale-dolphin-conservation-us", "US", "043570715", "animals",
      "Whale and Dolphin Conservation (US)", "Whale and Dolphin Conservation (WDC) — US",
      "US arm of UK-headquartered cetacean-conservation charity — anti-captivity, anti-whaling, research.",
      "Американское крыло британской организации по сохранению китообразных — против пленения, против китобойства, исследования.",
      "Whale and Dolphin Conservation US (EIN 04-3570715) is the US 501(c)(3) of WDC, the leading global cetacean-conservation charity (HQ Wiltshire, UK). Campaigns against marine-park captivity (SeaWorld in particular), against commercial whaling, supports field research and ship-strike prevention. North Atlantic right-whale recovery is a current priority.",
      "Whale and Dolphin Conservation US (EIN 04-3570715) — американская 501(c)(3) WDC, ведущей в мире благотворительной организации по сохранению китообразных (штаб-квартира в Уилтшире, Великобритания). Кампании против пленения в морских парках (особенно SeaWorld), против коммерческого китобойства, поддержка полевых исследований и предотвращения столкновений с кораблями. Восстановление популяции североатлантического гладкого кита — текущий приоритет.",
      "https://us.whales.org/donate/", 4500000, 80, 1987, date(2024, 6, 30),
      ["marine-mammal-protection", "wildlife-conservation"],
      _us_pp("043570715"), "irs_990", _verify_us(), "medium"),

    E("born-free-usa", "US", "943177064", "animals",
      "Born Free USA", "Born Free USA",
      "Wildlife protection + primate sanctuary in Texas — sister org to UK's Born Free Foundation.",
      "Защита дикой природы + приматический санктуарий в Техасе — сестринская UK Born Free Foundation.",
      "Born Free USA (EIN 94-3177064, founded 2002, sister organisation to UK's Born Free Foundation) operates the largest primate sanctuary in the United States in Texas (~600 monkeys rescued from labs, pet trade, roadside zoos). Campaigns against exotic-pet ownership and trophy hunting, runs CITES advocacy.",
      "Born Free USA (EIN 94-3177064, основан в 2002 году, сестринская британской Born Free Foundation) управляет крупнейшим в США приматическим санктуарием в Техасе (~600 обезьян, спасённых из лабораторий, торговли домашними животными, придорожных зоопарков). Кампании против владения экзотическими питомцами и трофейной охоты, адвокация CITES.",
      "https://www.bornfreeusa.org/donate/", 4000000, 78, 2002, date(2024, 12, 31),
      ["wildlife-conservation", "animal-welfare", "endangered-species"],
      _us_pp("943177064"), "irs_990", _verify_us(), "medium"),

    E("friends-of-animals", "US", "136018107", "animals",
      "Friends of Animals", "Friends of Animals",
      "US animal-rights org running a low-cost spay/neuter program + wildlife legal advocacy.",
      "Американская правозащитная организация животных с программой дешёвой стерилизации + юридическая защита дикой природы.",
      "Friends of Animals (EIN 13-6018107, founded 1957) runs one of the longest-running low-cost spay/neuter programmes in the US (~50K animals per year). Wildlife Law Programme litigates against trophy hunting, animal cruelty, and lack of Endangered Species Act enforcement.",
      "Friends of Animals (EIN 13-6018107, основан в 1957 году) ведёт одну из старейших в США программ дешёвой стерилизации (~50 тыс. животных в год). Wildlife Law Programme судится против трофейной охоты, жестокости к животным и неисполнения Endangered Species Act.",
      "https://friendsofanimals.org/donate/", 7500000, 82, 1957, date(2024, 12, 31),
      ["animal-welfare", "animal-rights-legal", "wildlife-conservation"],
      _us_pp("136018107"), "irs_990", _verify_us(), "medium"),

    E("wdc-uk", "GB", "1014705", "animals",
      "Whale and Dolphin Conservation (UK)", "Whale and Dolphin Conservation (WDC) — UK",
      "UK-HQ global cetacean-conservation charity — research, anti-captivity, anti-whaling.",
      "Британская штаб-квартира глобальной организации сохранения китообразных — исследования, против пленения, против китобойства.",
      "Whale and Dolphin Conservation UK (Charity Commission #1014705, founded 1987) is the global HQ of WDC (Wiltshire, England). Largest cetacean-only conservation charity in the world. Runs marine-mammal research stations on the Moray Firth (Scotland), Argentina, Hebrides; anti-captivity legislation in EU; rehabilitation centres for stranded cetaceans.",
      "Whale and Dolphin Conservation UK (Charity Commission #1014705, основан в 1987 году) — глобальный штаб WDC (Уилтшир, Англия). Крупнейшая в мире благотворительная организация, специализирующаяся только на китообразных. Управляет станциями исследования морских млекопитающих в Moray Firth (Шотландия), Аргентине, Гебридах; антипленительное законодательство в ЕС; реабилитационные центры для выброшенных на берег китообразных.",
      "https://uk.whales.org/donate/", 18000000, 79, 1987, date(2024, 3, 31),
      ["marine-mammal-protection", "wildlife-conservation"],
      _uk_cc("1014705"), "annual_report", _verify_uk(), "medium"),

    E("ducks-unlimited", "US", "135613815", "animals",
      "Ducks Unlimited", "Ducks Unlimited",
      "North American waterfowl & wetland conservation — has protected ~16M acres since 1937.",
      "Сохранение водоплавающих и водно-болотных угодий Северной Америки — защитили ~16 млн акров с 1937 года.",
      "Ducks Unlimited (EIN 13-5613815, founded 1937) is North America's largest waterfowl and wetland-conservation organisation. Has conserved ~16M acres of wetland habitat across the US, Canada, and Mexico through purchase, easements, and habitat-restoration projects. Funded primarily by ~700K hunter/non-hunter members.",
      "Ducks Unlimited (EIN 13-5613815, основан в 1937 году) — крупнейшая в Северной Америке организация по сохранению водоплавающих и водно-болотных угодий. Сохранили ~16 млн акров водно-болотного среды обитания в США, Канаде и Мексике через покупку, сервитуты и проекты восстановления среды обитания. Финансируется преимущественно ~700 тыс. членами охотниками и неохотниками.",
      "https://www.ducks.org/donate", 290000000, 80, 1937, date(2024, 6, 30),
      ["wildlife-conservation", "biodiversity-defense", "conservation"],
      _us_pp("135613815"), "irs_990", _verify_us()),

    E("animal-welfare-institute", "US", "135655952", "animals",
      "Animal Welfare Institute", "Animal Welfare Institute (AWI)",
      "Long-running US animal welfare science + policy org — humane farming standards, federal advocacy.",
      "Давняя американская организация по благополучию животных, наука + политика — стандарты гуманного животноводства, федеральная адвокация.",
      "Animal Welfare Institute (EIN 13-5655952, founded 1951 by Christine Stevens) is one of the oldest US animal welfare organisations. Develops Animal Welfare Approved certification for higher-welfare farms, runs Compassion Index scoring of Congress on animal-welfare votes, federal advocacy on Horse Protection Act, marine-mammal protection, and farmed-animal slaughter regulation.",
      "Animal Welfare Institute (EIN 13-5655952, основан в 1951 году Кристиной Стивенс) — одна из старейших в США организаций по благополучию животных. Разрабатывает сертификацию Animal Welfare Approved для ферм с улучшенным благополучием, ведёт Compassion Index с оценкой Конгресса по голосованию по благополучию животных, федеральная адвокация Horse Protection Act, защиты морских млекопитающих, регулирования убоя сельхозживотных.",
      "https://awionline.org/content/donate", 9000000, 80, 1951, date(2024, 9, 30),
      ["animal-welfare", "farm-animal-welfare", "marine-mammal-protection"],
      _us_pp("135655952"), "irs_990", _verify_us(), "medium"),

    E("wildlife-trusts", "GB", "207238", "animals",
      "The Wildlife Trusts", "The Wildlife Trusts — UK сеть природоохранных трастов",
      "Federation of 46 UK Wildlife Trusts — manage 2,300 nature reserves; 870K members.",
      "Федерация 46 британских Wildlife Trusts — управляют 2300 природными заповедниками; 870 тыс. членов.",
      "The Wildlife Trusts (Royal Society of Wildlife Trusts, Charity Commission #207238, founded 1912) is the federation of 46 county-based Wildlife Trusts across the UK. Collectively manage ~2,300 nature reserves covering ~98K hectares, 870K members, federal advocacy on the State of Nature, beavers reintroduction, hedgehog protection, and farming-for-nature policy.",
      "The Wildlife Trusts (Royal Society of Wildlife Trusts, Charity Commission #207238, основан в 1912 году) — федерация 46 окружных Wildlife Trusts по всей Великобритании. Коллективно управляют ~2300 природными заповедниками общей площадью ~98 тыс. гектаров, 870 тыс. членов, федеральная адвокация State of Nature, реинтродукции бобров, защиты ежей, политики «farming for nature».",
      "https://www.wildlifetrusts.org/donate", 110000000, 79, 1912, date(2024, 3, 31),
      ["wildlife-conservation", "biodiversity-defense", "conservation"],
      _uk_cc("207238"), "annual_report", _verify_uk()),

    E("bumblebee-conservation", "GB", "1115634", "animals",
      "Bumblebee Conservation Trust", "Bumblebee Conservation Trust",
      "UK charity dedicated to bumblebee science and recovery — 24 UK bumblebee species, 2 extinct.",
      "Британская организация, посвящённая бамблби-науке и восстановлению — 24 вида шмелей в Великобритании, 2 вымерли.",
      "Bumblebee Conservation Trust (Charity Commission #1115634, founded 2006 in Stirling Scotland) is the UK charity dedicated to bumblebees. The UK has 24 bumblebee species (2 already extinct, 8 in decline). BBCT funds research, runs BeeWalk (largest citizen-science bumblebee monitoring scheme in the world), pollinator-friendly gardening guidance, and reintroduction work for the short-haired bumblebee.",
      "Bumblebee Conservation Trust (Charity Commission #1115634, основан в 2006 году в Стерлинге, Шотландия) — британская благотворительная организация, посвящённая шмелям. В Великобритании 24 вида шмелей (2 уже вымерли, 8 в упадке). BBCT финансирует исследования, ведёт BeeWalk (крупнейшую в мире схему мониторинга шмелей методом гражданской науки), руководство по pollinator-friendly садоводству, реинтродукцию короткошёрстного шмеля.",
      "https://www.bumblebeeconservation.org/donate-now/", 2200000, 78, 2006, date(2024, 3, 31),
      ["pollinators", "biodiversity-defense", "wildlife-conservation"],
      _uk_cc("1115634"), "annual_report", _verify_uk(), "medium"),

    E("marine-conservation-society", "GB", "1004005", "animals",
      "Marine Conservation Society (UK)", "Marine Conservation Society",
      "UK marine charity — Beachwatch citizen science, Good Fish Guide, ocean advocacy.",
      "Британская морская благотворительная организация — Beachwatch гражданская наука, Good Fish Guide, океаническая адвокация.",
      "Marine Conservation Society (Charity Commission #1004005, founded 1983) is the UK's only charity solely focused on the sea. Runs Beachwatch — the UK's largest citizen-science marine-litter survey, the Good Fish Guide (sustainable-seafood ratings for UK consumers), and the Big Seaweed Search. Federal advocacy on marine-protected areas and the Marine and Coastal Access Act.",
      "Marine Conservation Society (Charity Commission #1004005, основан в 1983 году) — единственная в Великобритании благотворительная организация, исключительно сосредоточенная на море. Ведёт Beachwatch — крупнейшее в Великобритании citizen-science исследование морского мусора, Good Fish Guide (рейтинги устойчивых морепродуктов для британских потребителей), Big Seaweed Search. Федеральная адвокация морских охраняемых районов и Marine and Coastal Access Act.",
      "https://www.mcsuk.org/donate/", 8000000, 78, 1983, date(2024, 3, 31),
      ["ocean-protection", "marine-life", "biodiversity-defense"],
      _uk_cc("1004005"), "annual_report", _verify_uk(), "medium"),

    E("animal-legal-defense-fund", "US", "942681680", "animals",
      "Animal Legal Defense Fund (ALDF)", "Animal Legal Defense Fund (ALDF)",
      "Largest US animal-rights legal advocacy org — courtroom litigation against animal cruelty.",
      "Крупнейшая в США правозащитная юридическая организация животных — судебные процессы против жестокости.",
      "Animal Legal Defense Fund (EIN 94-2681680, founded 1979) is the largest US organisation dedicated to using the legal system to protect animals. Files impact-litigation against factory farms, puppy mills, roadside zoos; works with prosecutors on animal-cruelty cases; advocates for state-level cruelty-felony statutes. Runs the Animal Law Programme at law schools.",
      "Animal Legal Defense Fund (EIN 94-2681680, основан в 1979 году) — крупнейшая в США организация, посвящённая использованию правовой системы для защиты животных. Подаёт impact-иски против фабричных ферм, puppy-mills, придорожных зоопарков; работает с прокурорами по делам о жестокости к животным; адвокация штатных уголовных статей. Ведёт программу Animal Law в юрфакультетах.",
      "https://aldf.org/donate/", 25000000, 79, 1979, date(2024, 6, 30),
      ["animal-rights-legal", "animal-welfare"],
      _us_pp("942681680"), "irs_990", _verify_us(), "medium"),

    E("pheasants-forever", "US", "411431525", "animals",
      "Pheasants Forever and Quail Forever", "Pheasants Forever and Quail Forever",
      "US upland-game-bird and habitat conservation — chapter-based volunteer model; ~290 chapters.",
      "Сохранение охотничьих наземных птиц и среды обитания в США — модель на основе отделений; ~290 отделений.",
      "Pheasants Forever (EIN 41-1431525, founded 1982 in St. Paul Minnesota; Quail Forever sister org founded 2005) operates a chapter-based model — funds raised in each chapter stay in that chapter for local habitat work. ~290 chapters, ~150K members. Has worked on ~21M acres of habitat for upland game birds, pollinators, and grassland ecosystems.",
      "Pheasants Forever (EIN 41-1431525, основан в 1982 году в Сент-Поле, Миннесота; Quail Forever — сестринская организация, основана в 2005 году) работает по модели на основе отделений — средства, собранные в каждом отделении, остаются в этом отделении для местной работы по среде обитания. ~290 отделений, ~150 тыс. членов. Работали на ~21 млн акрах среды обитания для наземных охотничьих птиц, опылителей и луговых экосистем.",
      "https://www.pheasantsforever.org/Donate.aspx", 145000000, 82, 1982, date(2024, 12, 31),
      ["wildlife-conservation", "biodiversity-defense", "conservation"],
      _us_pp("411431525"), "irs_990", _verify_us()),

    # ============== PLANET (17) ==============
    E("national-park-foundation", "US", "521086761", "planet",
      "National Park Foundation", "National Park Foundation",
      "Official US National Parks charity — funds park projects across all 400+ National Park sites.",
      "Официальная благотворительная организация Национальных парков США — финансирует проекты в 400+ парках.",
      "National Park Foundation (EIN 52-1086761, chartered by Congress 1967) is the official charitable partner of the US National Park Service. Funds projects across all 400+ National Park sites — conservation, education, youth programmes, the Find Your Park / Encuentra Tu Parque campaign. Acts as private-philanthropy complement to NPS federal appropriations.",
      "National Park Foundation (EIN 52-1086761, утверждён Конгрессом в 1967 году) — официальный благотворительный партнёр US National Park Service. Финансирует проекты во всех 400+ парках — охрана природы, образование, молодёжные программы, кампания Find Your Park / Encuentra Tu Parque. Действует как дополнение частной филантропии к федеральным ассигнованиям NPS.",
      "https://www.nationalparks.org/donate", 145000000, 85, 1967, date(2024, 9, 30),
      ["national-parks-us", "conservation", "biodiversity-defense"],
      _us_pp("521086761"), "irs_990", _verify_us()),

    E("save-the-redwoods", "US", "940843915", "planet",
      "Save the Redwoods League", "Save the Redwoods League",
      "Protects coast redwoods and giant sequoias — California's most iconic forests.",
      "Защищает прибрежные секвойи и гигантские секвойи — самые знаковые леса Калифорнии.",
      "Save the Redwoods League (EIN 94-0843915, founded 1918) is the leading US redwoods-protection charity. Has helped establish 66 California State Parks and adds ~5K acres of redwood forest to public protection per year. The Coast Redwoods Initiative aims to triple redwood-forest acreage under protection. Funds Redwoods Research at the Redwoods Genetic Conservation Project.",
      "Save the Redwoods League (EIN 94-0843915, основан в 1918 году) — ведущая в США благотворительная организация по защите секвой. Помог создать 66 калифорнийских штатовских парков и добавляет ~5 тыс. акров секвойного леса в публичную охрану ежегодно. Coast Redwoods Initiative нацелена на утроение площади секвойного леса под охраной. Финансирует Redwoods Research в Redwoods Genetic Conservation Project.",
      "https://www.savetheredwoods.org/give/", 28000000, 81, 1918, date(2024, 6, 30),
      ["redwoods-old-growth", "forest-protection", "conservation"],
      _us_pp("940843915"), "irs_990", _verify_us()),

    E("yellowstone-forever", "US", "810541332", "planet",
      "Yellowstone Forever", "Yellowstone Forever",
      "Official non-profit partner of Yellowstone National Park — wildlife, trails, education.",
      "Официальный некоммерческий партнёр Йеллоустонского национального парка — дикая природа, тропы, образование.",
      "Yellowstone Forever (EIN 81-0541332, formed 2016 by merger of Yellowstone Park Foundation and Yellowstone Association) is the official non-profit partner of Yellowstone National Park. Funds park projects including wildlife monitoring, native cutthroat trout restoration, trails, educational visitor programmes. Operates the in-park stores whose revenue underwrites the donations.",
      "Yellowstone Forever (EIN 81-0541332, образован в 2016 году в результате слияния Yellowstone Park Foundation и Yellowstone Association) — официальный некоммерческий партнёр Йеллоустонского национального парка. Финансирует проекты парка, включая мониторинг дикой природы, восстановление местного cutthroat trout, тропы, образовательные программы для посетителей. Управляет магазинами в парке, доходы которых поддерживают пожертвования.",
      "https://www.yellowstone.org/donate/", 25000000, 78, 2016, date(2024, 9, 30),
      ["national-parks-us", "wildlife-conservation", "conservation"],
      _us_pp("810541332"), "irs_990", _verify_us(), "medium"),

    E("trees-for-the-future", "US", "521644869", "planet",
      "Trees for the Future", "Trees for the Future",
      "Forest Garden agroforestry programme — trains farmers in sub-Saharan Africa.",
      "Программа агролесоводства Forest Garden — обучает фермеров в Африке к югу от Сахары.",
      "Trees for the Future (EIN 52-1644869, founded 1989) runs the Forest Garden Program — a 4-year curriculum that teaches sub-Saharan African farmers (in Senegal, Mali, Tanzania, Kenya, Uganda and elsewhere) to plant ~6K agroforestry trees per acre, building income, food security, and soil health while sequestering carbon. ~37K family farms reached, ~340M trees planted.",
      "Trees for the Future (EIN 52-1644869, основан в 1989 году) ведёт программу Forest Garden — 4-летний учебный курс, обучающий фермеров Африки к югу от Сахары (в Сенегале, Мали, Танзании, Кении, Уганде и др.) сажать ~6 тыс. агролесоводственных деревьев на акр, наращивая доход, продовольственную безопасность и здоровье почвы при одновременном связывании углерода. Охвачено ~37 тыс. семейных ферм, посажено ~340 млн деревьев.",
      "https://trees.org/donate/", 18000000, 86, 1989, date(2024, 12, 31),
      ["reforestation", "climate", "poverty-reduction"],
      _us_pp("521644869"), "irs_990", _verify_us(), "medium"),

    E("one-tree-planted", "US", "464664562", "planet",
      "One Tree Planted", "One Tree Planted",
      "Plants trees worldwide — $1 plants 1 tree, partners with local reforestation orgs in 80+ countries.",
      "Сажает деревья по всему миру — $1 = 1 дерево, партнёры — местные организации лесовосстановления в 80+ странах.",
      "One Tree Planted (EIN 46-4664562, founded 2014 in Vermont) plants trees in 80+ countries through partnerships with local reforestation organisations. Iconic $1-plants-1-tree messaging makes giving accessible. Has planted ~120M+ trees since founding, including post-fire restoration in Australia, Canada, the US, and tropical-rainforest projects in Indonesia, Madagascar, Brazil.",
      "One Tree Planted (EIN 46-4664562, основан в 2014 году в Вермонте) сажает деревья в 80+ странах через партнёрства с местными организациями лесовосстановления. Знаковое сообщение «$1 = 1 дерево» делает дарение доступным. С момента основания посажено ~120+ млн деревьев, включая восстановление после пожаров в Австралии, Канаде, США, тропические проекты в Индонезии, Мадагаскаре, Бразилии.",
      "https://onetreeplanted.org/products/plant-trees", 50000000, 87, 2014, date(2024, 12, 31),
      ["reforestation", "climate", "forest-protection"],
      _us_pp("464664562"), "irs_990", _verify_us()),

    E("pacific-environment", "US", "943122859", "planet",
      "Pacific Environment", "Pacific Environment",
      "US-based environmental advocacy on Pacific Rim — China, Russia, Arctic, shipping pollution.",
      "Американская природоохранная адвокация в Тихоокеанском кольце — Китай, Россия, Арктика, загрязнение судоходства.",
      "Pacific Environment (EIN 94-3122859, founded 1987) is a US environmental advocacy NGO focused on the Pacific Rim. Works on shipping decarbonisation (Climate-Friendly Ports campaign), Arctic protection, plastic pollution at sea, and supports grassroots environmental advocates in China and the Russian Far East (now constrained post-2022).",
      "Pacific Environment (EIN 94-3122859, основан в 1987 году) — американская правозащитная природоохранная НПО, сосредоточенная на Тихоокеанском кольце. Работает по декарбонизации судоходства (кампания Climate-Friendly Ports), защите Арктики, пластиковому загрязнению в море, поддерживает низовых природоохранных адвокатов в Китае и на российском Дальнем Востоке (сейчас ограничено после 2022 года).",
      "https://www.pacificenvironment.org/donate/", 7500000, 80, 1987, date(2024, 9, 30),
      ["ocean-protection", "climate-policy", "marine-pollution"],
      _us_pp("943122859"), "irs_990", _verify_us(), "medium"),

    E("the-conservation-fund", "US", "530337293", "planet",
      "The Conservation Fund", "The Conservation Fund",
      "Conservation-and-economic-development land-trust — protects working forests, farms, parks.",
      "Земельный траст с подходом «охрана + экономическое развитие» — защищает работающие леса, фермы, парки.",
      "The Conservation Fund (EIN 53-0337293, founded 1985) is a top-ranked US land-trust that takes a market-based, conservation-plus-economic-development approach. Has protected ~9M acres in all 50 US states through acquisition + working-forest conservation easements. Major focus on Appalachian working forests, Pacific Northwest, and Great Plains grasslands.",
      "The Conservation Fund (EIN 53-0337293, основан в 1985 году) — высокорейтинговый американский земельный траст с подходом, основанным на рынке, «охрана плюс экономическое развитие». Защитили ~9 млн акров во всех 50 штатах США через покупку + сервитуты сохранения работающих лесов. Основной фокус: Appalachian working forests, Pacific Northwest, Great Plains grasslands.",
      "https://www.conservationfund.org/donate", 480000000, 91, 1985, date(2024, 9, 30),
      ["conservation", "forest-protection", "biodiversity-defense"],
      _us_pp("530337293"), "irs_990", _verify_us()),

    E("friends-of-the-earth-uk", "GB", "281681", "planet",
      "Friends of the Earth UK", "Friends of the Earth UK",
      "UK national member of Friends of the Earth International — climate, nature, environmental justice.",
      "Британский национальный член Friends of the Earth International — климат, природа, экологическая справедливость.",
      "Friends of the Earth Trust UK (Charity Commission #281681, founded 1971) is the UK national group of Friends of the Earth International (network of national groups in 73 countries). UK campaigns: climate policy, banning single-use plastics, restoring nature, environmental-justice work in low-income UK communities. Independent of Friends of the Earth Limited (the c4 campaigning entity).",
      "Friends of the Earth Trust UK (Charity Commission #281681, основан в 1971 году) — британская национальная группа Friends of the Earth International (сеть национальных групп в 73 странах). Британские кампании: климатическая политика, запрет одноразового пластика, восстановление природы, экологическая справедливость в малообеспеченных британских общинах. Независим от Friends of the Earth Limited (c4 кампанийная структура).",
      "https://friendsoftheearth.uk/donate", 12000000, 78, 1971, date(2024, 3, 31),
      ["climate", "environment", "biodiversity-defense"],
      _uk_cc("281681"), "annual_report", _verify_uk(), "medium"),

    E("cpre", "GB", "1089685", "planet",
      "CPRE — The Countryside Charity", "CPRE — Британская сельская благотворительная организация",
      "UK countryside-protection campaigning charity — planning advocacy, green-belt defence.",
      "Британская организация по защите сельской местности — адвокация градостроительства, защита green-belt.",
      "CPRE — The Countryside Charity (Charity Commission #1089685, founded 1926) campaigns to protect the English countryside from inappropriate development. Co-led the Green Belt legal-protection framework in the 1940s. Current campaigns: light-pollution / dark skies, hedgerow protection, brownfield-first housing policy, rural transport. ~40K members across 43 county/regional branches.",
      "CPRE — The Countryside Charity (Charity Commission #1089685, основан в 1926 году) ведёт кампании за защиту английской сельской местности от ненадлежащего освоения. Соруководил юридической рамкой Green Belt в 1940-х годах. Текущие кампании: световое загрязнение / тёмное небо, защита изгородей, политика жилищной застройки brownfield-first, сельский транспорт. ~40 тыс. членов в 43 окружных/региональных отделениях.",
      "https://www.cpre.org.uk/donate/", 6500000, 76, 1926, date(2024, 3, 31),
      ["rural-protection-uk", "conservation", "biodiversity-defense"],
      _uk_cc("1089685"), "annual_report", _verify_uk(), "medium"),

    E("rewilding-britain", "GB", "1159373", "planet",
      "Rewilding Britain", "Rewilding Britain",
      "UK charity championing rewilding — large-scale nature restoration via ecological processes.",
      "Британская организация, защищающая rewilding — крупномасштабное восстановление природы через экологические процессы.",
      "Rewilding Britain (Charity Commission #1159373, founded 2015) is the UK's leading rewilding-advocacy charity. Coordinates the Rewilding Network — 130+ projects covering ~205K hectares across the UK on large-scale nature recovery: beaver reintroduction, native woodland regeneration, wild deer/livestock management, lynx reintroduction feasibility studies.",
      "Rewilding Britain (Charity Commission #1159373, основан в 2015 году) — ведущая в Великобритании организация по адвокации rewilding. Координирует Rewilding Network — 130+ проектов общей площадью ~205 тыс. гектаров в Великобритании по крупномасштабному восстановлению природы: реинтродукция бобров, восстановление родных лесов, управление дикими оленями/скотом, исследования возможности реинтродукции рыси.",
      "https://www.rewildingbritain.org.uk/donate", 3500000, 79, 2015, date(2024, 3, 31),
      ["rewilding", "biodiversity-defense", "conservation"],
      _uk_cc("1159373"), "annual_report", _verify_uk(), "medium"),

    E("cool-effect", "US", "473581965", "planet",
      "Cool Effect", "Cool Effect",
      "Verified carbon-offset marketplace — vets each project's quality before it's sold to donors.",
      "Маркетплейс верифицированных углеродных офсетов — каждый проект проверяется на качество до продажи донорам.",
      "Cool Effect (EIN 47-3581965, founded 2015 by Dee Lawrence and Richard Lawrence) is a science-led carbon-offset non-profit. Strict project-quality screening (rejection rate ~94% of projects evaluated); only top-quality offsets across reforestation, cookstoves, methane-capture, blue-carbon and direct-air-capture make it onto the platform. Transparency reports for each project.",
      "Cool Effect (EIN 47-3581965, основан в 2015 году Ди Лоуренс и Ричардом Лоуренсом) — научно-ведомая некоммерческая организация углеродных офсетов. Строгий отбор проектов по качеству (отклоняет ~94% оцениваемых проектов); только топ-качественные офсеты в области лесовосстановления, кухонных печей, улавливания метана, blue-carbon и прямого захвата углерода попадают на платформу. Отчёты прозрачности для каждого проекта.",
      "https://www.cooleffect.org/donate", 9000000, 86, 2015, date(2024, 12, 31),
      ["carbon-offsetting", "climate", "reforestation"],
      _us_pp("473581965"), "irs_990", _verify_us(), "medium"),

    E("climate-action-network", "US", "843224418", "planet",
      "Climate Action Network (CAN International)", "Climate Action Network (CAN) — International",
      "World's largest network of climate-civil-society organisations — 1,900 members in 130+ countries.",
      "Крупнейшая в мире сеть климатических организаций гражданского общества — 1900 членов в 130+ странах.",
      "Climate Action Network International (EIN 84-3224418) is the world's largest network of climate civil society — 1,900 member organisations in 130+ countries. Coordinates civil-society engagement at UN climate negotiations (COPs), publishes the daily ECO newsletter during COPs, and convenes regional CAN nodes (CAN-Latin America, CAN-South Asia etc.). Headquarters in Bonn Germany; US 501(c)(3) is the fundraising arm.",
      "Climate Action Network International (EIN 84-3224418) — крупнейшая в мире сеть климатических гражданских обществ — 1900 организаций-членов в 130+ странах. Координирует участие гражданского общества в климатических переговорах ООН (COP), издаёт ежедневный новостной бюллетень ECO во время COP, объединяет региональные узлы CAN (CAN-Latin America, CAN-South Asia и др.). Штаб-квартира в Бонне, Германия; американская 501(c)(3) — фандрайзинговое крыло.",
      "https://climatenetwork.org/donate/", 8000000, 84, 1989, date(2024, 12, 31),
      ["climate-policy", "climate"],
      _us_pp("843224418"), "irs_990", _verify_us(), "medium"),

    E("earthwatch", "US", "237162696", "planet",
      "Earthwatch Institute", "Earthwatch Institute",
      "Citizen-science-driven field conservation — volunteers join scientists on research expeditions worldwide.",
      "Полевое сохранение природы через гражданскую науку — волонтёры участвуют в научных экспедициях по всему миру.",
      "Earthwatch Institute (EIN 23-7162696, founded 1971) is the largest US citizen-science conservation organisation. Citizens pay to join scientists on field expeditions — wildlife population studies, coral-reef monitoring, ocean acidification, archaeology. Has supported ~1,400+ research projects in 120 countries. UK and Australia offices also.",
      "Earthwatch Institute (EIN 23-7162696, основан в 1971 году) — крупнейшая в США природоохранная организация гражданской науки. Граждане платят за участие в научных экспедициях — исследования популяций дикой природы, мониторинг коралловых рифов, океаническое подкисление, археология. Поддержали ~1400+ исследовательских проектов в 120 странах. Также офисы в Великобритании и Австралии.",
      "https://earthwatch.org/donate/", 12000000, 78, 1971, date(2024, 9, 30),
      ["wildlife-conservation", "biodiversity-defense", "conservation"],
      _us_pp("237162696"), "irs_990", _verify_us(), "medium"),

    E("rocky-mountain-institute", "US", "742244146", "planet",
      "Rocky Mountain Institute (RMI)", "Rocky Mountain Institute (RMI)",
      "Climate-economy strategy non-profit — drives clean-energy transition via finance, industry, policy.",
      "Стратегическая организация климат-экономики — продвигает переход на чистую энергию через финансы, индустрию, политику.",
      "Rocky Mountain Institute (EIN 74-2244146, founded 1982 by Amory and Hunter Lovins) is one of the most influential US climate-strategy think-tanks. Programmes work to decarbonise buildings, electricity, heavy industry, mobility and shipping — focuses on the levers (finance, regulation, market signals) that move climate transitions at scale. ~700 staff across 5 continents.",
      "Rocky Mountain Institute (EIN 74-2244146, основан в 1982 году Эмори и Хантером Ловинсами) — один из самых влиятельных в США климатических стратегических think-tanks. Программы по декарбонизации зданий, электроэнергетики, тяжёлой промышленности, мобильности и судоходства — фокус на рычагах (финансы, регулирование, рыночные сигналы), которые двигают климатические переходы в масштабе. ~700 сотрудников на 5 континентах.",
      "https://rmi.org/donate/", 110000000, 86, 1982, date(2024, 6, 30),
      ["energy-efficiency", "climate-policy", "climate"],
      _us_pp("742244146"), "irs_990", _verify_us()),

    E("surfers-against-sewage", "GB", "1145877", "planet",
      "Surfers Against Sewage", "Surfers Against Sewage",
      "UK ocean charity campaigning against coastal pollution — Big Plastic Count, Million Mile Clean.",
      "Британская океаническая организация против прибрежного загрязнения — Big Plastic Count, Million Mile Clean.",
      "Surfers Against Sewage (Charity Commission #1145877, founded 1990 in Cornwall by surfers fed up with raw-sewage-polluted waves) is the UK's leading marine-pollution charity. Coordinates Million Mile Clean (UK's largest community beach-clean), the annual Big Plastic Count, lobbies federally for water-company pollution accountability — successfully drove the UK Water Bill 2023 reforms.",
      "Surfers Against Sewage (Charity Commission #1145877, основан в 1990 году в Корнуолле сёрферами, уставшими от волн, загрязнённых сырыми сточными водами) — ведущая в Великобритании благотворительная организация по морскому загрязнению. Координирует Million Mile Clean (крупнейшую общинную уборку пляжей Великобритании), ежегодный Big Plastic Count, лоббирует ответственность водопроводных компаний за загрязнение — успешно продвинул реформы UK Water Bill 2023.",
      "https://www.sas.org.uk/donate/", 6000000, 79, 1990, date(2024, 3, 31),
      ["marine-pollution", "ocean-protection", "climate-policy"],
      _uk_cc("1145877"), "annual_report", _verify_uk(), "medium"),

    E("wilderness-society-us", "US", "530167933", "planet",
      "The Wilderness Society (US)", "The Wilderness Society (США)",
      "Protects US public wild lands — Wilderness Act of 1964 advocate, federal land-management policy.",
      "Защищает дикие земли США — адвокат Wilderness Act 1964, политика управления федеральными землями.",
      "The Wilderness Society (EIN 53-0167933, founded 1935) is one of the US's oldest and most influential public-lands advocacy organisations. Co-authored and drove passage of the Wilderness Act of 1964 (which protects ~111M acres of US wilderness). Current campaigns: Antiquities Act monument designations, Arctic National Wildlife Refuge protection, climate-resilient land management.",
      "The Wilderness Society (EIN 53-0167933, основан в 1935 году) — одна из старейших и самых влиятельных в США организаций по защите общественных земель. Соавтор и движитель принятия Wilderness Act 1964 (защищает ~111 млн акров диких земель США). Текущие кампании: обозначения памятников по Antiquities Act, защита Arctic National Wildlife Refuge, климатоустойчивое управление землёй.",
      "https://www.wilderness.org/donate", 65000000, 80, 1935, date(2024, 9, 30),
      ["conservation", "biodiversity-defense", "climate-policy"],
      _us_pp("530167933"), "irs_990", _verify_us()),

    E("league-conservation-voters", "US", "521488851", "planet",
      "League of Conservation Voters Education Fund", "League of Conservation Voters Education Fund",
      "501(c)(3) educational arm of LCV — National Environmental Scorecard, voter education, civic engagement.",
      "Образовательное крыло LCV в форме 501(c)(3) — National Environmental Scorecard, образование избирателей, гражданская активность.",
      "League of Conservation Voters Education Fund (EIN 52-1488851, founded 1985 as the c3 arm of LCV) produces the annual National Environmental Scorecard rating every member of the US Congress on environmental votes (since 1970). Voter-education programmes, get-out-the-vote registration in environmentally-engaged communities, LCV Action Fund is the separate c4 entity for electioneering.",
      "League of Conservation Voters Education Fund (EIN 52-1488851, основан в 1985 году как c3 крыло LCV) выпускает ежегодный National Environmental Scorecard, оценивающий каждого члена Конгресса США по голосованиям по экологии (с 1970 года). Программы образования избирателей, регистрация get-out-the-vote в общинах, активных по экологии, LCV Action Fund — отдельная c4 структура для предвыборной работы.",
      "https://www.lcveducationfund.org/donate", 35000000, 78, 1985, date(2024, 12, 31),
      ["climate-policy", "civil-rights"],
      _us_pp("521488851"), "irs_990", _verify_us()),
]


def _financial_row(entry: dict) -> dict:
    return {
        "year": 2023, "total_revenue_usd": entry["total_revenue_usd"],
        "program_expenses_usd": None, "admin_expenses_usd": None,
        "fundraising_expenses_usd": None, "top_executive_comp_usd": None,
        "top_executive_name": "", "source_url": entry["source_url"],
        "source_label": (
            "IRS Form 990, FY 2023 (ProPublica)" if entry["country"] == "US"
            else "Annual report & accounts (Charity Commission UK)"
        ),
    }


def _source_doc(entry: dict) -> dict:
    if entry["country"] == "US":
        return {"kind": "irs_990", "filed_date": entry["last_filed_date"],
                "label": {"en": "IRS Form 990 (FY 2023)", "ru": "Налоговая форма IRS 990 (2023)"},
                "url": entry["source_url"], "source_label": "IRS Form 990 (ProPublica)",
                "file_format": "pdf"}
    return {"kind": "annual_report", "filed_date": entry["last_filed_date"],
            "label": {"en": "Annual report & accounts (FY 2023)", "ru": "Годовой отчёт и финансовая отчётность (2023)"},
            "url": entry["source_url"], "source_label": "Charity Commission UK — accounts page",
            "file_format": "html"}


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
            print(f"[migration 0050] BLOCKED {entry['slug']} ({entry['country']}/{entry['registration_id']}): {block}")
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
    print(f"[migration 0050] new charities upserted: {upserted}, blocked: {skipped_blocked}, total in DB now: {total}")


def backwards(apps, schema_editor):
    """No-op."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0049_backfill_v311_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]

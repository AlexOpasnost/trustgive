/**
 * ISO 3166-1 alpha-2 → human country name, EN + RU.
 *
 * Keep in sync with the Country enum in apps/charities/models.py — when a new
 * country is added to the seed migrations, add it here so charity cards stop
 * showing raw codes like "DE·..." for that locale.
 */

export const COUNTRY_LABEL_EN: Record<string, string> = {
  // Anglosphere + RU
  US: "United States", GB: "United Kingdom", RU: "Russia",
  CA: "Canada", AU: "Australia", NZ: "New Zealand",
  // Continental Europe
  DE: "Germany", NL: "Netherlands", CH: "Switzerland", SE: "Sweden",
  FR: "France", IT: "Italy", ES: "Spain", IE: "Ireland", NO: "Norway",
  BE: "Belgium", DK: "Denmark", PL: "Poland", FI: "Finland", AT: "Austria",
  // Asia
  JP: "Japan", SG: "Singapore", IN: "India", PH: "Philippines",
  ID: "Indonesia", VN: "Vietnam", TH: "Thailand", BD: "Bangladesh",
  // Africa
  KE: "Kenya", ZA: "South Africa", GH: "Ghana", MZ: "Mozambique",
  LS: "Lesotho", SN: "Senegal", TZ: "Tanzania", UG: "Uganda",
  // Latin America
  BR: "Brazil", AR: "Argentina", CL: "Chile", CO: "Colombia",
  MX: "Mexico", EC: "Ecuador", CR: "Costa Rica", PE: "Peru",
  // MENA
  LB: "Lebanon", EG: "Egypt", JO: "Jordan", TN: "Tunisia", IL: "Israel",
}

export const COUNTRY_LABEL_RU: Record<string, string> = {
  US: "США", GB: "Великобритания", RU: "Россия",
  CA: "Канада", AU: "Австралия", NZ: "Новая Зеландия",
  DE: "Германия", NL: "Нидерланды", CH: "Швейцария", SE: "Швеция",
  FR: "Франция", IT: "Италия", ES: "Испания", IE: "Ирландия", NO: "Норвегия",
  BE: "Бельгия", DK: "Дания", PL: "Польша", FI: "Финляндия", AT: "Австрия",
  JP: "Япония", SG: "Сингапур", IN: "Индия", PH: "Филиппины",
  ID: "Индонезия", VN: "Вьетнам", TH: "Таиланд", BD: "Бангладеш",
  KE: "Кения", ZA: "ЮАР", GH: "Гана", MZ: "Мозамбик",
  LS: "Лесото", SN: "Сенегал", TZ: "Танзания", UG: "Уганда",
  BR: "Бразилия", AR: "Аргентина", CL: "Чили", CO: "Колумбия",
  MX: "Мексика", EC: "Эквадор", CR: "Коста-Рика", PE: "Перу",
  LB: "Ливан", EG: "Египет", JO: "Иордания", TN: "Тунис", IL: "Израиль",
}

export function countryLabel(code: string, lang: "en" | "ru"): string {
  const dict = lang === "ru" ? COUNTRY_LABEL_RU : COUNTRY_LABEL_EN
  return dict[code] ?? code
}

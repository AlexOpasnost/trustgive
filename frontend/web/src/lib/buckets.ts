/**
 * Bucket → sub-cause filter mapping per DESIGN.md v3.1 §I, expanded in v3.4
 * to match the real cause-tag distribution after migrations 0008..0030.
 *
 * Each chip filters by ONE primary cause-tag (the dominant one for that
 * topic). Charities tagged with adjacent tags surface naturally because
 * curators tagged the dominant + secondary tags together (e.g. a child-
 * health org has both `global-health` and `child-nutrition`).
 *
 * Rule: every chip must match ≥3 charities. Tags with <3 are accessible
 * via "All" (the default no-filter view).
 */

import type { Bucket } from "@/types/api"

export type SubFilter = {
  /** null = "All" — clears the cause filter */
  slug: string | null
  labelEn: string
  labelRu: string
}

export const BUCKET_SUBFILTERS: Record<Bucket, SubFilter[]> = {
  // 75 People charities — top 9 chips
  people: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "global-health", labelEn: "Health", labelRu: "Здоровье" },
    { slug: "education", labelEn: "Education", labelRu: "Образование" },
    { slug: "poverty-reduction", labelEn: "Poverty", labelRu: "Бедность" },
    { slug: "civil-rights", labelEn: "Civil rights", labelRu: "Права человека" },
    { slug: "disaster-relief", labelEn: "Disaster relief", labelRu: "Помощь при катастрофах" },
    { slug: "child-nutrition", labelEn: "Children", labelRu: "Дети" },
    { slug: "mental-health", labelEn: "Mental health", labelRu: "Психическое здоровье" },
    { slug: "disability-services", labelEn: "Disability", labelRu: "Инвалидность" },
    { slug: "lgbt-rights", labelEn: "LGBT rights", labelRu: "Права ЛГБТ" },
    { slug: "womens-rights", labelEn: "Women's rights", labelRu: "Права женщин" },
    { slug: "effective-altruism", labelEn: "Effective altruism", labelRu: "Эффективный альтруизм" },
  ],
  // 28 Animals charities — 5 chips
  animals: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "animal-welfare", labelEn: "Pets & welfare", labelRu: "Приюты и забота" },
    { slug: "wildlife-conservation", labelEn: "Wildlife", labelRu: "Дикая природа" },
    { slug: "endangered-species", labelEn: "Endangered species", labelRu: "Исчезающие виды" },
    { slug: "biodiversity-defense", labelEn: "Biodiversity", labelRu: "Биоразнообразие" },
  ],
  // 35 Planet charities — 6 chips
  planet: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "climate", labelEn: "Climate", labelRu: "Климат" },
    { slug: "climate-policy", labelEn: "Climate policy", labelRu: "Климатическая политика" },
    { slug: "biodiversity-defense", labelEn: "Biodiversity", labelRu: "Биоразнообразие" },
    { slug: "forest-protection", labelEn: "Forests", labelRu: "Леса" },
    { slug: "ocean-protection", labelEn: "Oceans", labelRu: "Океаны" },
    { slug: "conservation", labelEn: "Conservation", labelRu: "Заповедники" },
  ],
}

/**
 * v3.7: regional groups instead of per-country chips. Catalog now spans
 * 15+ countries (was 3) — listing each as a separate chip would be
 * cluttered. Each region maps to a list of ISO codes that get joined as
 * `country=US,CA,...` for the v3.7 BaseInFilter on the backend.
 *
 * Russia stays as its own region (not grouped under Europe) per the
 * platform's RU-targeted donor focus and the legal blocklist context.
 */
export type RegionFilter = {
  /** null = "All" (no country filter) */
  slug: string | null
  labelEn: string
  labelRu: string
  /** ISO codes joined with commas in the API call. null for "All". */
  countries: string[] | null
}

export const REGION_FILTERS: RegionFilter[] = [
  { slug: null, labelEn: "All regions", labelRu: "Все регионы", countries: null },
  {
    slug: "americas",
    labelEn: "Americas",
    labelRu: "Америка",
    countries: ["US", "CA", "BR", "AR", "CL", "CO", "MX", "EC", "CR", "PE"],
  },
  {
    slug: "europe",
    labelEn: "Europe",
    labelRu: "Европа",
    // v3.10: +IT, +ES, +IE, +NO. v3.11: +BE, +DK. v3.14: +PL, +FI, +AT.
    countries: ["GB", "DE", "NL", "CH", "SE", "FR", "IT", "ES", "IE", "NO", "BE", "DK", "PL", "FI", "AT"],
  },
  { slug: "russia", labelEn: "Russia", labelRu: "Россия", countries: ["RU"] },
  {
    slug: "africa",
    labelEn: "Africa",
    labelRu: "Африка",
    countries: ["KE", "ZA", "GH", "MZ", "LS", "SN", "TZ", "UG"],
  },
  {
    slug: "mena",
    labelEn: "Middle East",
    labelRu: "Ближний Восток",
    // v3.14: +IL (Israel).
    countries: ["LB", "EG", "JO", "TN", "IL"],
  },
  {
    slug: "asia",
    labelEn: "Asia",
    labelRu: "Азия",
    countries: ["IN", "PH", "ID", "VN", "TH", "SG", "BD", "JP"],
  },
  {
    slug: "oceania",
    labelEn: "Oceania",
    labelRu: "Океания",
    countries: ["AU", "NZ"],
  },
]

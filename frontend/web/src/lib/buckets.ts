/**
 * Bucket → sub-cause filter mapping per DESIGN.md v3.1 §I.
 *
 * Drives the catalog page's cause-chip row when a `?bucket=` is active. Maps
 * user-friendly labels (Poverty, Health, Wildlife) to the underlying
 * `cause_tags` slugs used by Backend's filter.
 *
 * To add a new sub-filter: add an entry here AND make sure ≥1 charity in the
 * relevant bucket has that cause_tag. Backend auto-creates Cause rows via
 * get_or_create, so no Backend code change is required.
 */

import type { Bucket } from "@/types/api"

export type SubFilter = {
  /** null = "All" — clears the cause filter */
  slug: string | null
  labelEn: string
  labelRu: string
}

export const BUCKET_SUBFILTERS: Record<Bucket, SubFilter[]> = {
  people: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "poverty-reduction", labelEn: "Poverty", labelRu: "Бедность" },
    { slug: "global-health", labelEn: "Health", labelRu: "Здоровье" },
    { slug: "child-nutrition", labelEn: "Children", labelRu: "Дети" },
    { slug: "refugees", labelEn: "Refugees", labelRu: "Беженцы" },
    { slug: "homelessness", labelEn: "Homelessness", labelRu: "Бездомные" },
    { slug: "education", labelEn: "Education", labelRu: "Образование" },
    { slug: "food-security", labelEn: "Food & water", labelRu: "Пища и вода" },
  ],
  animals: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "wildlife-conservation", labelEn: "Wildlife", labelRu: "Дикая природа" },
    { slug: "animal-welfare", labelEn: "Pets & shelters", labelRu: "Приюты и питомцы" },
    { slug: "marine-life", labelEn: "Marine life", labelRu: "Морская жизнь" },
  ],
  planet: [
    { slug: null, labelEn: "All", labelRu: "Все" },
    { slug: "climate", labelEn: "Climate", labelRu: "Климат" },
    { slug: "conservation", labelEn: "Conservation", labelRu: "Заповедники" },
    { slug: "forest-protection", labelEn: "Forests", labelRu: "Леса" },
    { slug: "pollution-control", labelEn: "Pollution", labelRu: "Загрязнение" },
  ],
}

export const COUNTRY_FILTERS: { code: string | null; labelEn: string; labelRu: string }[] = [
  { code: null, labelEn: "All countries", labelRu: "Все страны" },
  { code: "US", labelEn: "United States", labelRu: "США" },
  { code: "GB", labelEn: "United Kingdom", labelRu: "Великобритания" },
  { code: "RU", labelEn: "Russia", labelRu: "Россия" },
]

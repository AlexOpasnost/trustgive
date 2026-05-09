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

export const COUNTRY_FILTERS: { code: string | null; labelEn: string; labelRu: string }[] = [
  { code: null, labelEn: "All countries", labelRu: "Все страны" },
  { code: "US", labelEn: "United States", labelRu: "США" },
  { code: "GB", labelEn: "United Kingdom", labelRu: "Великобритания" },
  { code: "RU", labelEn: "Russia", labelRu: "Россия" },
]

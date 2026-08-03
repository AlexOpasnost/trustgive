/**
 * Research index and the figures each article stands on.
 *
 * Prose lives in the locale files (`research.articles.<slug>.*`) so both
 * languages stay together with the rest of the site's copy. The numbers live
 * here, frozen, with the date they were measured — an article is a snapshot,
 * and a snapshot whose figures silently change is not a citable one. Anything
 * that should track the live catalogue belongs on a product page, not here.
 *
 * Every figure below is reproducible: `backend/research_query.py` prints them
 * from whatever database it is pointed at, and the raw records are in the public
 * API. The Canadian findings come from DATA_INTEGRITY.md §6 and §7, which record
 * the controls used.
 */

export type ResearchArticleMeta = {
  slug: string
  /** ISO date the figures were measured and the piece published. */
  published: string
  /** Rough reading time, minutes. */
  minutes: number
}

export const RESEARCH_ARTICLES: ResearchArticleMeta[] = [
  {
    slug: "what-we-could-not-verify",
    published: "2026-08-03",
    minutes: 6,
  },
]

/** Verification outcome per country, measured 2026-08-03 across 541 records. */
export type CountryRow = {
  code: string
  /** Organisations assembled for that country. */
  assembled: number
  /** Of those, how many could be linked to a document that opens. */
  verified: number
}

export const VERIFICATION_BY_COUNTRY: CountryRow[] = [
  { code: "US", assembled: 296, verified: 257 },
  { code: "GB", assembled: 77, verified: 77 },
  { code: "CA", assembled: 28, verified: 0 },
  { code: "AU", assembled: 25, verified: 16 },
  { code: "IT", assembled: 15, verified: 4 },
  { code: "ES", assembled: 14, verified: 6 },
  { code: "DE", assembled: 13, verified: 2 },
  { code: "NL", assembled: 9, verified: 1 },
  { code: "NZ", assembled: 7, verified: 0 },
  { code: "FR", assembled: 7, verified: 0 },
  { code: "IE", assembled: 6, verified: 0 },
  { code: "NO", assembled: 5, verified: 0 },
  { code: "BE", assembled: 5, verified: 0 },
  { code: "DK", assembled: 5, verified: 0 },
]

/** Headline figures, measured 2026-08-03. */
export const HEADLINE = {
  assembled: 541,
  verified: 369,
  unverified: 172,
  /** Of the unverified, how many had no obtainable document at all. */
  noDocumentAtAll: 170,
  /** …and how many had one whose link stopped resolving. */
  deadLink: 2,
  /** Canadian registration numbers tested against the CRA data endpoint. */
  canadaTested: 28,
  canadaGenuine: 6,
  canadaWrongEntity: 2,
  canadaUnresolvable: 20,
} as const

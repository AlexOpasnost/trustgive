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
    slug: "how-old-is-charity-financial-data",
    published: "2026-08-03",
    minutes: 5,
  },
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

/**
 * How old the freshest available filing is, measured 2026-08-03 across the 365
 * published charities that carry a filing date.
 *
 * The measure is the age of the fiscal period the filing *covers*
 * (`last_filed_date`, ProPublica's `tax_prd`), not the delay between a
 * regulator receiving a return and publishing it. We do not store publication
 * dates, so we cannot speak to regulator speed — only to what a reader can
 * actually get today, which is the question a donor has.
 */
export type AgeBucket = {
  /** Locale key suffix under research.articles.<slug>.bucket. */
  key: string
  count: number
}

export const FILING_AGE_BUCKETS: AgeBucket[] = [
  { key: "under12", count: 0 },
  { key: "from12to24", count: 21 },
  { key: "from24to36", count: 260 },
  { key: "from36to48", count: 82 },
  { key: "over48", count: 2 },
]

export const FILING_AGE = {
  /** Published charities carrying a filing date. */
  measured: 365,
  withoutDate: 4,
  medianMonths: 31,
  olderThan24Months: 344,
  /** Median months by country, for the countries with enough rows to say. */
  byCountry: [
    { code: "AU", n: 16, median: 25 },
    { code: "GB", n: 77, median: 28 },
    { code: "US", n: 253, median: 31 },
  ],
  /** The most common fiscal-period end dates — the clustering that shapes it. */
  commonPeriodEnds: [
    { date: "2023-12-31", count: 129 },
    { date: "2023-06-30", count: 68 },
    { date: "2024-03-31", count: 63 },
    { date: "2023-09-30", count: 30 },
  ],
  /** UK filings sit in a tight band; the US has a long tail. */
  gbRangeMonths: { min: 19, max: 31 },
  usRangeMonths: { min: 25, max: 85 },
} as const

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

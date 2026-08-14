/**
 * Evergreen guides — the top-of-funnel half of the content plan (STRATEGY §11).
 *
 * Deliberately a separate section from `/research`, and the difference is not
 * cosmetic. A research piece is a *snapshot*: its figures are frozen in
 * `content/research.ts` with the date they were measured, because a number that
 * shifts under a reader who cited it is not citable. A guide is the opposite —
 * it answers a question people ask every week and has to stay current, so it
 * carries no frozen statistics at all. Putting the two in one section would
 * force one of those properties to give way.
 *
 * What keeps these from being the same commodity text every charity site has:
 * every one of them is anchored in something this catalogue actually got wrong.
 * "An identifier that resolves is not proof" is a platitude; "we published Cure
 * Leukaemia on 1100994, which the Charity Commission answers with PAG (Parent
 * Action Group) Limited, removed in 2011" is a fact, and it is ours because we
 * are the ones who found it. Those cases live in `GUIDE_CASES` below with the
 * finding they come from, so a reader can follow any of them to the write-up.
 *
 * Structure lives here, prose lives in the locale files under `guides.articles.
 * <slug>.*` — same split as research, so both languages stay with the rest of
 * the site's copy. `GuidePage` renders the blocks generically; there is no
 * per-article component, because ten of them would be ten places for the same
 * layout to drift.
 */

/** One rendered element of a guide body. */
export type GuideBlock =
  /** Section heading. Key: `<n>Title`. */
  | { kind: "heading"; key: string }
  /** Paragraph. Key: `<n>`. */
  | { kind: "para"; key: string }
  /** Unordered list. Keys: `<n>.0`, `<n>.1`, … */
  | { kind: "list"; key: string; count: number }
  /** Numbered steps. Keys as for `list`. */
  | { kind: "steps"; key: string; count: number }
  /** A limitation or warning, set apart from the body. Key: `<n>`. */
  | { kind: "caution"; key: string }
  /**
   * Something that went wrong in this catalogue, named. `case` is the id in
   * `GUIDE_CASES`; the prose key carries the explanation around it.
   */
  | { kind: "case"; key: string; case: keyof typeof GUIDE_CASES }
  /** Question-and-answer pairs. Keys: `<n>.0.q` / `<n>.0.a`, … Feeds FAQPage. */
  | { kind: "faq"; key: string; count: number }

export type GuideMeta = {
  slug: string
  /** ISO date the guide was last reviewed against the sources it describes. */
  reviewed: string
  minutes: number
  body: GuideBlock[]
}

/**
 * Real cases from this catalogue's own audits.
 *
 * `href` points at the page a reader can check the claim on. `finding` is the
 * section of DATA_INTEGRITY.md that records how it was found and confirmed —
 * these are not anecdotes, and the reader should be able to get to the working.
 */
export const GUIDE_CASES = {
  wrongEntity: {
    /** DATA_INTEGRITY Finding 17. */
    finding: 17,
    identifier: "1100994",
    registryAnswer: "PAG (PARENT ACTION GROUP) LIMITED",
    href: "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/1100154/accounts-and-annual-returns",
    charitySlug: "cure-leukaemia",
  },
  deregistered: {
    /** Finding 17. Removed from the register 2023-09-15; company dissolved 2023-12-19. */
    finding: 17,
    identifier: "1049077",
    registryAnswer: "THE BIG ISSUE FOUNDATION",
    removedOn: "2023-09-15",
    companyDissolvedOn: "2023-12-19",
  },
  wrongRegister: {
    /** Finding 17. An English number for a Scottish charity. */
    finding: 17,
    identifier: "SC024414",
    registryAnswer: "Maggie Keswick Jencks Cancer Caring Centres Trust",
    href: "https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number=SC024414",
  },
  numberNotHeld: {
    /** Finding 17. Absent from the register in both scopes, registered and removed. */
    finding: 17,
    identifier: "264818",
    replacedBy: "1207593",
    charitySlug: "donkey-sanctuary",
  },
  statusCodeIsNotEvidence: {
    /** Findings 6, 10, 11 — CRA, ABR and the NZ register all answer 200 for a made-up id. */
    finding: 11,
    registries: ["CRA (Canada)", "ABR (Australia)", "Charities Services (New Zealand)"],
  },
  searchReturnsNeighbours: {
    /** Finding 17. Searching the number 219099 returns RSPCA branches ahead of the RSPCA. */
    finding: 17,
    identifier: "219099",
    registryAnswer: "ROYAL SOCIETY FOR THE PREVENTION OF CRUELTY TO ANIMALS",
  },
} as const

export const GUIDES: GuideMeta[] = [
  {
    slug: "how-to-check-if-a-charity-is-legitimate",
    reviewed: "2026-08-13",
    minutes: 8,
    body: [
      { kind: "para", key: "intro1" },
      { kind: "para", key: "intro2" },

      { kind: "heading", key: "s1" },
      { kind: "para", key: "s1p1" },
      { kind: "steps", key: "s1steps", count: 5 },
      { kind: "para", key: "s1p2" },

      { kind: "heading", key: "s2" },
      { kind: "para", key: "s2p1" },
      { kind: "case", key: "s2case", case: "statusCodeIsNotEvidence" },
      { kind: "para", key: "s2p2" },

      { kind: "heading", key: "s3" },
      { kind: "para", key: "s3p1" },
      { kind: "case", key: "s3case", case: "wrongEntity" },
      { kind: "para", key: "s3p2" },

      { kind: "heading", key: "s4" },
      { kind: "para", key: "s4p1" },
      { kind: "case", key: "s4case", case: "deregistered" },

      { kind: "heading", key: "s5" },
      { kind: "para", key: "s5p1" },
      { kind: "case", key: "s5case", case: "wrongRegister" },
      { kind: "list", key: "s5list", count: 5 },

      { kind: "heading", key: "s6" },
      { kind: "para", key: "s6p1" },
      { kind: "case", key: "s6case", case: "searchReturnsNeighbours" },
      { kind: "para", key: "s6p2" },

      { kind: "heading", key: "s7" },
      { kind: "list", key: "s7list", count: 6 },
      { kind: "caution", key: "s7caution" },

      { kind: "heading", key: "s8" },
      { kind: "faq", key: "faq", count: 5 },
    ],
  },
]

export const GUIDE_SLUGS = GUIDES.map((g) => g.slug)

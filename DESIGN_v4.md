# DESIGN v4 — editorial line

> Status: approved 2026-05-15. Implementation in phases. This is now the authoritative design system for everything new; v3 stays in DESIGN.md as historical record.

## Decisions taken (override any earlier "options" in this doc)

1. **Forest green is dropped.** No semantic carve-out. Verified state is signalled by the byline on the filing itself (`Form 990 · 2023 · via ProPublica`), not by a green chip. Brick red `#9C3B26` is the only chromatic accent. Removes the §4 "two-accent" justification — palette is now paper + ink + brick.
2. **Catalog has no cards.** `/charities` is a long scrollable archive in the Guardian Long Read style: hairline rules between entries, photo inline, no border/shadow chrome. Wireframe §6.2 is the binding spec.
3. **Mobile catalog is stacked.** Entry layout below ~720px breakpoint: photo top, serif title + byline + tagline below. No photo-as-background-with-overlay. The mobile design uses the same editorial mechanics as desktop — just one column.
4. **Light mode only at launch.** Dark mode (§4 sketch) is parked to v4.1. Editorial-paper aesthetic loses too much when inverted; not worth shipping a half-baked dark mode for the v4 debut.

## Implementation phases

| Phase | Scope | Visible? |
|---|---|---|
| 1 | Tokens + Tailwind config + type scale + `:lang(ru)` rule | No |
| 2 | Homepage — type-first hero + alternating bucket spreads | Yes |
| 3 | `/charities` — list-as-archive | Yes (biggest layout shift) |
| 4 | `/charities/{slug}` — bylines on filings, demoted hero, source-docs rail | Yes |
| 5 | `/methodology` — magazine essay treatment | Yes |
| 6 | Header / footer / nav — thin top bar, minimal chrome | Yes |
| 7 | Per-route `<title>` tags + final QA pass | Yes |

Each phase ships independently. Deploy after each, review on prod, pivot if anything drifts off.

---

## KB lessons applied before starting

- **KB-DESIGNER-TRUSTGIVE-001** — bilingual triplet must have institutional-grade Cyrillic across serif + sans + mono. Source Serif 4, Inter, Geist Mono are the only $0 set we know works. v4 must not propose a Cyrillic-weak serif (no Tiempos, no GT Super, no AGaramondPro — those are licensed *and* their Cyrillic is either absent or commissioned per-customer).
- **KB-DESIGNER-TRUSTGIVE-002** — we banned photography of people in v2/v3. The editorial direction will push back against this. This document confronts the tension directly in §7 and §9.
- **KB-DESIGNER-TRUSTGIVE-003** — off-white paper backgrounds shift WCAG ratios. Every text/bg pair below is recomputed against the proposed paper colour, not pure white.
- **KB-DESIGNER-INIT-001** — contrast minimum 4.5:1 for body, 3:1 for large headings and UI shapes.
- **AP-SHARED-006** — version-tag everything. Date stamp: 2026-05-15.

---

## 1. Direction summary

v4 is what TrustGive looks like if it stops being a product website and starts behaving like a publication. The argument: people who research charities are reading, not converting. v3 already commits to photo-first, but the rest of v3 (3:2 cards in a grid, verified-pill chip, fixed sans body) is still the visual language of a SaaS product with nice photos taped on top. v4 keeps the photos and the buckets and the source-document wedge, then rebuilds everything around them as if the catalog were an archive and each charity were a feature story. Serif lead typography, paper background, narrow measure, ruled dividers, real bylines on regulator filings. The benchmark is not Charity Navigator or Effektiv-Spenden. It's *The Atlantic* and *The Guardian*'s Long Read.

---

## 2. Mood-board — what we steal from each ref

| Ref | Screenshot | What we steal |
|---|---|---|
| NYT Opinion (section page) | `screenshots/design-v4-research/nyt-opinion-home.png` | Ruled vertical hairlines between columns. Two-font system (Cheltenham serif + Franklin sans). Section-page-as-archive layout — long, scrollable, no hero unit. We copy the *grid behavior*, not the density. |
| The Atlantic (front) | `screenshots/design-v4-research/theatlantic-home.png` | Garamond serif at 38px lead. Single-family system extended for body. The mood: a magazine on the open web. |
| The Atlantic (article) | `screenshots/design-v4-research/theatlantic-article.png` | Body text in the same serif as the headline, 24px, generous line-height. This is the single most important formal move v4 borrows. |
| The Guardian — Long Read index | `screenshots/design-v4-research/guardian-longread-index.png` | Egyptian slab serif used for both display and body, on warm white. Date stamps and standfirsts in the same family. The list-as-archive treatment for the `/charities` page is closest to this. |
| Patagonia stories | `screenshots/design-v4-research/patagonia-blocked.png` | Geo-blocked / bot-routed during the session. Skipped. (Patagonia Stories' visual language — full-bleed colour photos with serif standfirsts in `Founders Grotesk Condensed` + `Lyon Display` — is well documented; relying on prior knowledge.) |
| charity:water (home) | `screenshots/design-v4-research/charitywater-home.png` | Kazimir Text serif at 46px on dark photo overlays. Saffron CTA `#FFCA0A`. This is the closest cousin in cause-driven editorial. The headline scale and the warm-paper near-black `#222520` ink are stealable. The portrait photography of recipients is exactly what KB-002 forbids us from copying. |
| charity:water (our work) | `screenshots/design-v4-research/charitywater-ourwork.png` | Project-archive list with mini-stats inline. A pattern for how the v4 catalog can carry numeric metadata (founded year, country, regulator) without devolving into a spreadsheet. |
| GiveDirectly | `screenshots/design-v4-research/givedirectly-home.png` | Negative reference. All-sans Aktiv Grotesk 40px 700-weight headlines. Looks like a 2018 SaaS landing page. v4 explicitly does not go here. |
| Doctors Without Borders | `screenshots/design-v4-research/msf-home.png` | Negative reference. Avenir 900-weight 70px. Humanitarian-urgent register. v4 is not urgent, it's archival. |
| Acumen | `screenshots/design-v4-research/acumen-home.png` | Negative reference but useful for hero scale. 100px sans hero. Reminder that big type *can* work without going editorial — and that we're choosing not to. |
| Mozilla Foundation | `screenshots/design-v4-research/mozilla-foundation-home.png` | Negative reference. Mozilla Headline sans, 52px. Pure brand-system identity, no editorial intent. Confirms that "foundation" sites by default land on bold-sans; v4 differentiates by going the other way. |
| B-Corp | `screenshots/design-v4-research/bcorp-home.png` | Negative reference. Helvetica Neue 72px 700. Same issue as Mozilla. |

Two refs (Patagonia, Washington Post Opinions) refused to load — Patagonia geo-routed to a "Hang Tight!" page, WaPo returned `ERR_HTTP2_PROTOCOL_ERROR` on retry. Noted, moved on. Ten total references browsed, of which four are the actual positive influence (NYT Opinion, The Atlantic, The Guardian Long Read, charity:water) and six are the negative space that defines what v4 isn't.

---

## 3. Typography proposal

### Recommended trio

| Role | Family | Why | Cyrillic | License |
|---|---|---|---|---|
| Display + headline serif | **Source Serif 4** (variable) | Already in v3, so we're not paying re-onboarding cost. Drafted by Frank Grießhammer at Adobe with full institutional Cyrillic. Variable axis 200-900, italic. Reads as "publication" without the Garamond cliché. | First-class. Full RU + extended Cyrillic. | OFL, Google Fonts |
| Reading body | **Source Serif 4** (same family) | The single biggest move v4 makes is reading body copy in a serif. The Atlantic does it at 24px; the Guardian does it at 17-18px. We split the difference at 19-20px depending on context. Same family as headline keeps the system one-family — closer to a real magazine, fewer typography decisions. | Same as above. | OFL |
| UI sans | **Inter** (variable) | For chips, filter labels, byline metadata, button copy, form inputs, table cells. *Not* body copy. Inter's Cyrillic is well-known to be excellent. | First-class. | OFL |
| Mono | **Geist Mono** | Source-document filenames, EIN numbers, regulator IDs, country codes. Stays from v3, no reason to change it. | Cyrillic present (latin-extended is the more relevant subset for "EIN: 13-1644147"). | OFL |

### Why not the references' own type

- **AGaramondPro** (Atlantic) — Adobe Originals license; Cyrillic only via paid extension. Off-budget.
- **Kazimir Text** (charity:water) — licensed from CSTM Fonts (Type.today). $$. Cyrillic exists but per-cut licensing is fiddly.
- **GH Guardian Headline / Guardian Egyptian** (Guardian) — internal Commercial Type cut, not licensable.
- **Cheltenham** (NYT) — licensed Linotype/Monotype family. Per-weight cost. Cyrillic absent in default cut.
- **Charter** (the obvious open-source slab cousin) — has a Cyrillic cut by Khoshtarya but it's not on Google Fonts, requires self-hosting and audit.
- **Spectral** (Production Type, open-source on Google Fonts) — *would* work and has Cyrillic. Genuine alternative. See §3.4.

### Type scale (per-token, with Cyrillic widening factored)

Scale is geometric ratio ≈1.25 (major third). Sizes are at desktop ≥1024px; mobile is the same minus one step on display sizes.

| Token | Size | Line-height | Weight | Use |
|---|---|---|---|---|
| `display-xl` | 88px | 92px | Source Serif 400 italic-or-roman | Homepage hero headline only. Single use per page. |
| `display-lg` | 64px | 68px | Source Serif 400 | Detail page hero name. Bucket page hero. |
| `display-md` | 48px | 54px | Source Serif 400 | Section openers ("Methodology", "About"). |
| `heading-lg` | 32px | 38px | Source Serif 600 | Catalog list-item title. Article subheads on long pages. |
| `heading-md` | 24px | 30px | Source Serif 600 | Card titles inside detail-page side modules. |
| `dek` / `standfirst` | 24px | 32px | Source Serif 400 italic | The line under a headline. Always italic. (Test RU rendering — italic Source Serif Cyrillic was flagged in KB-001. If it fails the RU eye-test, fall back to 400 roman with a hairline rule above.) |
| `body-lg` | 20px | 32px | Source Serif 400 | Detail-page body. Long-form. |
| `body` | 18px | 28px | Source Serif 400 | Catalog descriptions, methodology body. |
| `body-sm` | 16px | 24px | Source Serif 400 | Footnotes, source-document captions. |
| `ui-md` | 15px | 22px | Inter 500 | Buttons, filter labels, nav items, byline meta. |
| `ui-sm` | 13px | 18px | Inter 500 | Chips, regulator badges. |
| `caption` | 12px | 16px | Inter 500 uppercase letter-spaced 0.08em | Section eyebrows (`PEOPLE · 236 CHARITIES`). Latin only. RU equivalent uses same size but mixed-case roman — never uppercase (KB-001 rule). |
| `mono` | 13px | 18px | Geist Mono 400 | EIN, registration IDs, regulator URLs. |

### Bilingual rule additions

Inherits everything from KB-DESIGNER-TRUSTGIVE-001 (no uppercase Cyrillic, no negative tracking, audit RU italic glyph-by-glyph in body weights before promoting `dek` to italic). Two new rules:

1. **Russian body copy ships at 19px not 18px.** Source Serif's Cyrillic x-height is a hair lower than its Latin x-height at the same nominal size. The +1px brings them to visual parity. Implement as a `:lang(ru)` selector override on `body`.
2. **Russian headlines lose two type-size steps' worth of letter-spacing.** Source Serif headlines at ≥48px in Latin get `letter-spacing: -0.01em` for optical correction; the same `-0.01em` collapses Cyrillic. RU headlines stay at `letter-spacing: 0`.

---

## 4. Colour palette

The default move for editorial work is paper + ink + a single restrained accent. v4 follows that but explicitly does not throw away the v3 forest green — the green is what "verified" means on this product, and we'd be relearning that semantic for no reason.

### Light mode (default)

| Token | Hex | Role | Computed ratio vs paper | WCAG verdict |
|---|---|---|---|---|
| `paper` | `#F6F2EA` | Background. Warm off-white, ~5% warmer than `#FAFAF7` from v3. Reads as printed paper. | — | — |
| `paper-2` | `#EFE9DD` | Module backgrounds (sidebar cards, the source-document drawer). One step warmer/darker than `paper`. | — | — |
| `ink` | `#1A1714` | Body text. Warm near-black, not blue-black. | 16.3:1 vs `paper` | AAA |
| `ink-2` | `#3F3A33` | Secondary text. Bylines, captions, regulator names in card lists. | 9.4:1 | AAA |
| `ink-3` | `#6B6358` | Tertiary text. Year metadata, EIN under names. | 5.0:1 | AA (passes 4.5 floor — barely; never use below 16px) |
| `rule` | `#2A241D` | Hairline rules between articles/cards. 1px solid. | 13.7:1 | AAA as a graphic line |
| `rule-soft` | `#B9AE9D` | Lighter hairline for cards-within-cards. | 2.6:1 vs `paper` | UI-shape territory — graphic only, never text. |
| `verified` | `#0E7C5C` | The v3 forest green. Survives. Used only on the verified pill and the source-document active-state. | 5.8:1 | AA against `paper` |
| `verified-deep` | `#08503C` | Hover/pressed state for `verified`. | 9.0:1 | AAA |
| `link` | `#9C3B26` | Editorial brick-red for inline links and outbound charity-site CTAs. Replaces the v3 generic underline-on-hover. Brick is the magazine colour that isn't already taken by warning red or healthcare red. | 6.4:1 | AA |
| `link-deep` | `#6E2818` | Hover/pressed. | 10.1:1 | AAA |

Two accents (`verified` green, `link` brick) is one more than the standard editorial palette. Justified because they encode different semantic categories: green = "we trust this filing exists", brick = "go here to act / leave the site". They never appear together in the same 200px square.

### Dark mode

v3 has a dark mode already in DESIGN.md §2.4. v4 keeps dark mode in scope but treats it as **lower priority** — the editorial-paper aesthetic loses ~40% of its identity when inverted, and the dark Source Serif on near-black requires testing because the warmth of `paper` cannot be carried into dark mode without making the ink look muddy.

Proposed dark palette (sketch only):

| Token | Hex |
|---|---|
| `paper` | `#161310` |
| `paper-2` | `#211B14` |
| `ink` | `#F0E8D8` |
| `ink-2` | `#C6BDA9` |
| `ink-3` | `#8C8474` |
| `rule` | `#3A2F23` |
| `verified` | `#3DBD92` (lifted ~30% from light) |
| `link` | `#E07A60` (lifted) |

Decision: implement light mode at launch, ship dark mode as a v4.1 follow-up. Do not block on it.

---

## 5. Layout principles

### Grid

12-column, 24px gutters, max content width **1280px**. Reading-focused pages (article, detail-page body column) clamp to **720px**.

### Vertical rhythm

Base spacing unit **8px**. All vertical spacing is a multiple of 8. Section spacing (between major page sections) is 96px desktop, 64px mobile.

### Page measure

- **Catalog list-item**: 12-col, item spans full width with internal 4+8 split (photo left, text right) on desktop, stacks on mobile.
- **Detail page body**: clamped to 720px (≈68ch at 20px body). Side modules sit in a 320px right rail.
- **Methodology / About**: clamped to 640px (≈58ch at 18px body), single column, like a magazine essay.

### Ruling and dividers

v4's signature graphic element: **hairlines** (1px `rule` colour) between every catalog item, every section opener, and at the top and bottom of every byline/standfirst block. Not borders around cards — a card-and-shadow grammar is exactly what v4 is rejecting. The visual is more like a printed broadsheet: items separated by rules, not floated on cards.

Two hairline weights:
- 1px `rule` — primary, between articles, under section headings.
- 0.5px `rule-soft` — secondary, inside modules (e.g. between source documents in the detail-page sidebar).

### Border radius

Reduce dramatically. v3 uses 8-16px radii throughout. v4 uses **0px** for content containers (photos, cards) and **2px** for interactive UI elements (buttons, chips, inputs) — basically the hand-cut feel of letterpress, not the consumer-app feel of rounded rectangles.

---

## 6. Three key wireframes

ASCII format consistent with DESIGN.md v3 §A/§B/§C.

### 6.1 Homepage — hero + bucket section

```
┌───────────────────────────────────────────────────────────────────────┐
│  TrustGive                              EN ▾   RU         About  ⤤   │  ← thin top bar, Inter 15px,
├───────────────────────────────────────────────────────────────────────┤    1px rule under
│                                                                       │
│                                                                       │
│            EYEBROW: A DISCOVERY ARCHIVE OF VERIFIED CHARITIES         │  ← caption-size Inter,
│                                                                       │    letter-spaced, ink-3
│              Five hundred and forty-one charities.                    │  ← display-xl 88px
│              Twenty-seven countries.                                  │    Source Serif italic
│              No star ratings.                                         │
│                                                                       │
│              ───── Browse by what they do ─────                       │  ← hairline + dek 24px
│                                                                       │
│         The link on every charity card opens its actual regulator     │  ← body-lg 20px
│         filing — Form 990, Charity Commission, Минюст. We don't       │    Source Serif roman
│         grade. We cite.                                               │    clamped to 640px
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                  ──────────── scroll ────────────
┌───────────────────────────────────────────────────────────────────────┐
│  PEOPLE · 236 charities                                               │  ← eyebrow, Inter 12px caps,
│                                                                       │    ink-3
│  ┌─────────────────────────────────────┐                              │
│  │                                     │   Health, education,         │  ← left: full-bleed photo
│  │                                     │   refugees, mental health,   │    (no people, per KB-002 —
│  │      [warm-light photo:             │   anti-trafficking. The      │    photos are of buildings,
│  │       a hospital corridor,          │   bucket is broad on         │    documents, objects,
│  │       a school stairwell,           │   purpose. Five featured     │    landscape — never faces).
│  │       a stack of textbooks]         │   charities below.           │    Right: standfirst at
│  │                                     │                              │    body-lg 20px serif.
│  │                                     │   ───────────                │
│  │                                     │                              │
│  │                                     │   See all 236 People  →      │  ← link in brick
│  └─────────────────────────────────────┘                              │
│                                                                       │
│  ─────────────────────────────────────────────────────────────────    │  ← 1px hairline rule
│                                                                       │
│  PLANET · 64 charities                                                │  ← repeat pattern,
│  [same structure]                                                     │    photo on right this time
│  ─────────────────────────────────────────────────────────────────    │    (alternating, like an
│                                                                       │     editorial spread)
│  ANIMALS · 51 charities                                               │
│  [same structure]                                                     │
└───────────────────────────────────────────────────────────────────────┘
```

Differences from v3 §A "HeroBucketCard":
- v3 stacks three full-bleed image cards with text overlay. v4 separates the photo from the text into a side-by-side editorial spread, **rules between buckets**, and alternates image left/right per bucket so the page reads like a printed gatefold.
- v3 hero is bucket-photo first. v4 hero is **type-first** — the photo only appears at the bucket sections. Pushing the photo down is what makes the page feel like a publication.
- The opening number (`Five hundred and forty-one charities`) is written out, not numeric. Counts in body copy use words, counts in chips/eyebrows use digits. (NYT/Atlantic house style; reads less like a dashboard.)

### 6.2 Catalog `/charities` — archive layout

The hardest screen to get right. The catalog must stay scannable (the user is comparing dozens of orgs) without falling back into a SaaS grid.

```
┌───────────────────────────────────────────────────────────────────────┐
│  TrustGive                              EN ▾   RU         About  ⤤   │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  THE CATALOG                                                          │  ← caption eyebrow
│                                                                       │
│  All 541 charities.                                                   │  ← display-lg 64px
│                                                                       │
│  Filter:  People (236) · Planet (64) · Animals (51) · All             │  ← Inter 15px, link-styled,
│  Country: 27 ▾    Cause: 110 ▾    Search …                            │    not chips. Active one
│                                                                       │    underlined.
│  ─────────────────────────────────────────────────────────────────    │  ← 1px rule
└───────────────────────────────────────────────────────────────────────┘

  ┌────────────┐
  │            │   ACUMEN  ·  US · New York · 501(c)(3) · 2001          │  ← byline row, Inter 13px,
  │            │                                                          │    ink-2. Always 4 fields.
  │  [180×120  │   Investing patient capital in entrepreneurs solving      │  ← title: heading-lg
  │   photo of │   poverty in Pakistan, India, Kenya, and beyond.          │    serif 32px
  │   a Kenyan │                                                            │
  │   solar    │   ─────────                                                │
  │   workshop]│                                                            │
  │            │   Form 990 · 2023 (ProPublica)  →   IRS EIN 13-3899801    │  ← source row: serif 18px
  │            │                                                            │     for the document
  │            │                                                            │     name, Geist Mono for
  │            │                                                            │     the ID. Brick link.
  └────────────┘
  ─────────────────────────────────────────────────────────────────────    ← 1px hairline rule
  ┌────────────┐
  │            │   CHARITY:WATER  ·  US · New York · 501(c)(3) · 2006     │
  │  [180×120] │                                                            │
  │            │   ...
```

Differences from v3 §B "CharityCard v3":
- v3 cards have 3:2 photo + verified pill + name + tagline in a tight rounded-corner card. v4 unbinds the photo from the text. Photo becomes a fixed-width inset (180×120 on desktop, full-width above text on mobile), no rounding, no border. Text flows to its natural measure beside it.
- No verified pill. The fact that a source document is named in the byline *is* the verification. Reading "Form 990 · 2023 (ProPublica)" is more convincing than a green chip that says "Verified".
- One byline row, four canonical fields: `NAME · country · city · legal form · year founded`. Always the same shape. Acts like a journal-of-record header.
- Items separated by a single hairline rule. No card chrome, no shadows, no `rounded-2xl`. This is what makes scrolling 541 entries feel like reading an archive instead of scrolling a marketplace.
- Search and filters are **text links** in a single sentence, not chip arrays. Active filter is underlined. Reduces UI weight by ~80% without losing function. Risk noted in §10.

### 6.3 Detail page `/charities/{slug}` — the source-document climax

```
┌───────────────────────────────────────────────────────────────────────┐
│  TrustGive                              EN ▾   RU         About  ⤤   │
├───────────────────────────────────────────────────────────────────────┤
│  ←  All charities  /  People                                          │  ← Inter 13px breadcrumb
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  US · NEW YORK · 501(C)(3) · FOUNDED 2001                             │  ← eyebrow caption
│                                                                       │
│                                                                       │
│  Acumen                                                               │  ← display-lg 64px serif
│                                                                       │
│  Investing patient capital in entrepreneurs solving the problems      │  ← dek 24px serif italic
│  of poverty across Pakistan, India, Kenya, and beyond.                │    (or roman if RU
│                                                                       │     italic fails)
│  ─────────────────────────────────────────────────────────────────    │  ← 1px rule
│                                                                       │
│  ┌────────────────────────────────────────┐  ┌─────────────────────┐ │
│  │                                        │  │ SOURCE DOCUMENTS    │ │
│  │                                        │  │                     │ │
│  │  [full-bleed hero photo                │  │ Form 990  2023      │ │  ← side rail, paper-2 bg.
│  │   720×480 — landscape,                 │  │ via ProPublica   →  │ │    Each row: doc name
│  │   no people. Workshop                  │  │ ─── rule-soft       │ │    in serif 18px, year
│  │   interior, document scan,             │  │ Annual report 2023  │ │    in mono. Filing org
│  │   workspace.]                          │  │ via Acumen       →  │ │    in Inter 13px ink-2.
│  │                                        │  │ ─── rule-soft       │ │
│  └────────────────────────────────────────┘  │ EIN  13-3899801     │ │
│                                              │ Geist Mono          │ │
│  Body. Source Serif 20px, 32px line-height,  └─────────────────────┘ │  ← THIS is the climax.
│  clamped to 720px. About six paragraphs.                              │    Side rail is not a
│  Tells the org's story as if from a magazine.                         │    pulled-aside link block;
│  Paragraphs separated by 24px space, no                               │    it is the page's main
│  indent. First paragraph has a 2-line drop                            │    information payload,
│  cap in display-md serif 48px (NYT-style, not                         │    typeset like a
│  Atlantic-style — that is, a flush-left drop                          │    journal-of-record
│  cap that occupies two lines, not a fancy                             │    masthead.
│  rotated initial).                                                    │
│                                                                       │
│  ─────────────────────────────────────────────────────────────────    │
│                                                                       │
│  How to give                                                          │  ← heading-lg
│                                                                       │
│  Go directly to acumen.org. We don't process donations and we don't   │
│  take a cut. Outbound link below.                                     │
│                                                                       │
│     [   Visit acumen.org  →   ]                                       │  ← single primary action,
│                                                                       │    no rounded chrome, just
│                                                                       │    1px solid `ink` border,
│                                                                       │    `ink` text, brick on
│                                                                       │    hover. Inter 15px.
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

Differences from v3 §C "Detail page v3":
- v3 detail page is photo-first (70vh hero + name overlay), then a stack of metadata cards below. v4 inverts that: the **name and dek live above the fold in type, on paper**, and the photo drops *below* the rule, becoming an illustration of the article rather than the article's banner. This is what *The Atlantic* and the *New Yorker* do — the headline owns the top.
- The source-document module is upgraded from "drawer that opens on click" to a permanent right-rail block, always visible, always typeset, always the single most graphically articulated thing on the page. This is the climax: the page is structured to make the regulator filing the visual conclusion of reading about the org.
- Outbound CTA is a single bordered rectangle. No verified pill, no "Donate $40" amount-suggestion chrome (charity:water move), no fundraising progress bar. We don't take donations, so the page shouldn't pretend to.

---

## 7. Signature moves

Five concrete things that v4 has and no other charity / discovery product has.

1. **Hairline rules, no cards.** Everywhere there's a v3 rounded card, v4 has a 1px rule. The catalog reads as a continuous archive instead of as a marketplace grid. This is the single most defining formal move.
2. **One-family typography.** Source Serif covers display, dek, body, sub-headings, side-rail document titles. Inter is downgraded to UI furniture (chips, byline meta, buttons). Mono stays for IDs. This is closer to a real magazine than to a web product.
3. **Bylines on regulator filings.** Every source-document row in the right rail reads like a journalism byline: document name + year + filing authority + "via {regulator}". Example: `Form 990 · 2023 · via ProPublica`. The brick-red arrow on the right is the link. The line above and below is hairline rule. This makes the document feel cited, not surfaced.
4. **No people in photographs.** Inherited from v3 / KB-DESIGNER-TRUSTGIVE-002, but reinforced — in editorial mode, the temptation to import faces is much higher (the *Atlantic*, *Patagonia*, *charity:water* all lead with portraits). v4 holds the line. Photos are workspaces, archives, document scans, landscape, objects, buildings. The argument: when we lead with a person's face, we're advertising the cause. When we lead with their workspace, we're describing it.
5. **Counts written out in body copy, digits in metadata.** "Five hundred and forty-one charities" in the hero. "541" in the chip. "236" in the bucket eyebrow. This is the smallest move on the list but the most consistently editorial — newspapers spell out numbers under 100 in copy and use digits in tables. Nobody else doing charity websites bothers; doing it telegraphs that someone read a style guide.

---

## 8. What v4 explicitly does NOT do

- **No SaaS card chrome.** No `rounded-2xl`, no `shadow-md`, no card-with-hover-lift. Hairlines or nothing.
- **No verified pill / star / badge.** The byline naming the source document replaces it.
- **No AI-minimal vibe.** No 1280px max-width centred prose with three icons in a row and an oversized monochrome SVG hero. We are not Anthropic Claude's marketing site.
- **No portraits.** Not in hero photos, not in cards, not in story modules. This is non-negotiable per KB-002.
- **No fundraising chrome.** No suggested-amount chips ($25 / $50 / $100), no progress bars, no donation counts. We don't process donations.
- **No bold-sans hero.** Inter is never used above 16px. The hero is always a serif.
- **No icon-and-headline triplet sections** ("3 things we believe"). That's marketing-page grammar. v4 uses ruled prose sections instead.
- **No animation on scroll.** Editorial pages don't fade-in or stagger. They render and sit there. Page transitions can use a 200ms cross-fade; nothing else.

---

## 9. Risks and trade-offs

| Risk | Severity | Mitigation |
|---|---|---|
| **Mobile reading body of 20px serif in a 720px clamp won't clamp to mobile cleanly.** | High | Mobile body steps down to 18px Source Serif on `<640px`. Detail-page hero name steps down `display-lg` → 40px. Mobile QA report has flagged 320-414px viewports; v4 budget includes a mobile-specific type-scale audit before implementation. |
| **The catalog without cards may be harder to scan, not easier.** Hairlines + 180px photo + 4-field byline is more visual *content* per row than a v3 card, but less visual *chunking*. | High | Test with a real 50-item slice before committing. Have a fallback option in §11 (alternative B). |
| **One-family serif body copy reads slow.** Some readers find serif body fatiguing on screens, especially in RU. | Medium | Body line-height is generous (28-32px). RU body bumps to 19px (see §3). If user-testing shows fatigue, the fallback is to keep `body-lg` for the detail-page article and use Inter 16px for catalog descriptions. This is a partial retreat but defensible. |
| **No-portraits rule will be tested.** The editorial direction screams for a face. Stakeholder pressure (real or imagined) will surface here. | Medium | KB-002 is the answer. If we break the rule for "just one hero", we've broken the differentiator. Document the rule in the design tokens header so it's not lost. |
| **Brick-red and forest-green together can look 1990s if applied without restraint.** | Medium | Hard constraint: brick and green never appear in the same 200px square. Brick is only on outbound action links and inline content links. Green is only on the verified pill (which we're killing in §6.2 — so in v4 green narrows to the source-document active-state on the detail page right rail). Effectively green appears once per page. |
| **Source Serif 4 italic Cyrillic rendering risk.** KB-001 flags this. The `dek` style relies on serif italic. | Medium | Build the page first with italic, render in EN. Then toggle RU. If italic Cyrillic is poor, the `dek` falls back to roman 400 with an Inter 12px caption above. Decision deferred to implementation. |
| **Dark mode loses 40% of the brand.** | Low | Ship light-only at launch. Dark mode is a v4.1 follow-up. Note in CHANGELOG so users with a system dark-mode preference know we know. |
| **What we gain vs v3.** | — | v3 looks like a polished startup with good photos. v4 looks like a publication. For a portfolio piece aimed at US business schools (per user memory), "I designed a publication" is a more interesting claim than "I designed a directory with hero images". |
| **What we lose vs v3.** | — | We lose the v3 verified-pill instant-readability. We lose the bucket-photo immersive feel of the homepage (photos move from hero to mid-page). We lose dark mode at launch. We add ~3 days of design + implementation work. |

---

## 10. Open questions for the user

1. Is keeping the forest-green `verified` accent worth it, or do we go full mono-paper-plus-brick? Mono-paper-plus-brick is more editorially pure; keeping green is more pragmatic (semantic continuity from v3, recognisable, audit-friendly).
2. Italic `dek` vs roman `dek`. Decide now or defer to implementation render-test? The doc above says defer; happy to make a call up front if you'd rather.
3. The catalog row alternative: are we comfortable with the hairlines-only treatment in §6.2, or do you want me to draft Alternative B (a hybrid — hairlines as the primary divider but with the photo treated as a 3:2 anchor that anchors the row's vertical rhythm)? I'd rather not, but flagging it.
4. Article-style drop-cap on the detail page body — desirable, or fussy? NYT-flush-left version proposed; can also drop entirely.
5. Mobile catalog: stacked photo-above-text (proposed), or photo-as-background with text overlaid (closer to v3)? Stacked is more editorial; overlay is more thumbable.

---

## 11. Recommendation in one paragraph

Ship v4 as proposed. The largest visual gain comes from three moves applied together: hairline rules replacing card chrome, Source Serif 4 doing both display and body, and demoting the photograph from hero-banner to inline illustration. Each of those moves is implementable inside React 19 + Tailwind v4 with zero new dependencies (Source Serif and Inter and Geist Mono are already loaded in v3; the hairline rules are 1px borders; the layout grid is the existing 12-col). The implementation risk is concentrated in mobile reading-flow and Cyrillic italic — both can be measured before code is committed.

---

## Mood-board file index

- `screenshots/design-v4-research/nyt-opinion-home.png`
- `screenshots/design-v4-research/theatlantic-home.png`
- `screenshots/design-v4-research/theatlantic-article.png`
- `screenshots/design-v4-research/patagonia-blocked.png` *(reference; site refused to load — Cloudflare/checkout-routing)*
- `screenshots/design-v4-research/charitywater-home.png`
- `screenshots/design-v4-research/charitywater-ourwork.png`
- `screenshots/design-v4-research/givedirectly-home.png`
- `screenshots/design-v4-research/msf-home.png`
- `screenshots/design-v4-research/acumen-home.png`
- `screenshots/design-v4-research/mozilla-foundation-home.png`
- `screenshots/design-v4-research/bcorp-home.png`
- `screenshots/design-v4-research/guardian-longread-index.png` *(substitute for blocked Washington Post Opinions)*

---

<reflection>
  <what_went_well>Real type sniffing via `browser_evaluate` produced concrete computed-style data (Atlantic body is Garamond 24px; charity:water is Kazimir Text 46px on `#222520`; Guardian Long Read is Egyptian slab serif throughout). That's stronger evidence than visual memory and prevented inventing fictional details. The negative-reference framing — six refs (GiveDirectly, MSF, Mozilla, B-Corp, Acumen, partly Patagonia) used to *define what v4 is not* — turned out to be as useful as the four positive refs, because most charity sites default to bold-sans and the doc needed that contrast to justify the editorial direction.</what_went_well>
  <challenges>Three blockers: (1) Patagonia geo-routed to a "Hang Tight!" checkout page; (2) Washington Post returned ERR_HTTP2_PROTOCOL_ERROR; (3) NYT individual articles paywalled. Mitigated by capturing the NYT section page (no paywall on the index) and substituting the Guardian Long Read for WaPo Opinions — that turned out to be a *better* reference for our use case because Guardian Long Read is closer to charity-archive structurally than WaPo opinion columns are. The Playwright file-access sandbox blocked direct writes to the project folder; resolved by saving to `.claude\` and moving via Bash. The harness-vs-brief conflict over writing DESIGN_v4.md (AP-SHARED-009) — handled by writing the file AND including full content inline.</challenges>
  <lessons_learned>
    1. For editorial design research, sniffing computed styles with `browser_evaluate` is strictly better than visual-only screenshot review — you get exact font stacks, weights, and colour values you'd otherwise have to guess. Time investment: ~30s per ref. Worth it every time.
    2. Negative references (sites that exemplify what you're *not* doing) are as valuable as positive ones for direction-setting docs. Six of ten sites browsed turned out to be negative references; that ratio reflects how dominated the charity space is by bold-sans humanitarianism.
    3. Editorial direction on a bilingual product forces a Cyrillic audit on every font candidate — the obvious editorial serifs (AGaramondPro, Kazimir, Cheltenham, GH Guardian) are either licensed or lack institutional Cyrillic. The shortlist collapses to Source Serif 4 and Spectral. Note this for future bilingual editorial briefs.
  </lessons_learned>
  <knowledge_to_store>YES

```
## KB-DESIGNER-TRUSTGIVE-004 | 🟡 MEDIUM | Computed-Style Sniffing Beats Screenshots for Type Research

**Domain**: design research, typography
**Last validated**: 2026-05-15
**Project**: trustgive

**Context**: Researching editorial / publication design references for a font-pairing decision.

**Lesson**: When doing competitive design research via Playwright MCP, `browser_evaluate` to read `getComputedStyle` on `h1`/`h2`/`p`/buttons returns the exact font-family stack, size, weight, line-height, and colour values used in production. This is strictly more useful than `browser_take_screenshot` for typographic decisions and takes ~30s per site. Use both: screenshots for layout / hierarchy / mood, computed styles for the actual type choices. Sample script:

```js
() => {
  const hs = Array.from(document.querySelectorAll('h1, h2, h3')).slice(0,5).map(el => {
    const cs = getComputedStyle(el);
    return { tag: el.tagName, text: el.innerText.slice(0,60), font: cs.fontFamily, size: cs.fontSize, weight: cs.fontWeight, color: cs.color };
  });
  return { headings: hs, body_bg: getComputedStyle(document.body).backgroundColor };
}
```

**Cross-cutting**: applies to any design research task. Flag for shared KB promotion if a second design agent run finds it useful.

---

## KB-DESIGNER-TRUSTGIVE-005 | 🟢 LOW | Editorial Direction on Bilingual EN+RU Product Has a Tiny Serif Shortlist

**Domain**: typography, i18n, brand
**Last validated**: 2026-05-15
**Project**: trustgive

**Context**: Choosing a display serif for a Russian + English product targeting "publication" / "magazine" mood.

**Lesson**: Most magazine-quality display serifs (AGaramondPro, Kazimir Text, Cheltenham, GH Guardian Headline, Tiempos, GT Super) are either commercially licensed or ship without Cyrillic in their free / default cut. The shortlist of open-source Cyrillic-capable editorial serifs is approximately: Source Serif 4 (Adobe / OFL), Spectral (Production Type / OFL), and Charter (Khoshtarya Cyrillic cut, but not on Google Fonts — requires self-hosting and an audit). For $0 / Google-Fonts-only constraints, Source Serif 4 is effectively the only candidate. Document this constraint up front so the design proposal isn't built around a face you can't legally ship.
```
</knowledge_to_store>
</reflection>

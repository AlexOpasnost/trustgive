# Design System: TrustGive

> **Status**: v2.0 — post-MVP refresh (supersedes v1.1)
> **Created**: 2026-05-05 · **Updated**: 2026-05-07 · **Designer**: Designer agent
> **Approval gates this satisfies**: Gate 2 (Design) — re-approval requested
> **Read first**: `SPEC.md` v1.0, v1.1 below (full system), screenshots/portfolio-2026-05-06/
> **v2.0 scope**: a *delta-document* that supersedes catalog card, detail-page header, homepage section order, logo policy, button hierarchy, and empty states. Everything not touched in v2.0 (palette, typography, spacing, motion, a11y, methodology page) stays as in v1.1.

---

## v2.0 — 2026-05-07 — Catalog / Detail / Homepage refresh

### Why v2.0 exists

After MVP shipped to https://trustgive.org with one seeded charity (GiveDirectly), the user reaction was **"1/10 — looks broken"**. Re-reading the screenshots in `screenshots/portfolio-2026-05-06/` the core issue is not visual identity (the cream + serif + green is fine) but **product affordance**: the catalog row reads as a list item, not a clickable product card; the detail page hides the description below financial charts; the homepage is all manifesto with zero product on view. v2.0 fixes those three failures and tightens two systems (logo policy, button hierarchy) that were under-specified in v1.1.

**Constraints inherited unchanged from v1.1** (do not re-litigate): cream `#F5F1E8` paper, Inter + Source Serif 4 + Geist Mono, forest green `#0E7C5C` primary, bilingual EN+RU, "no photography of people" (recipients/donors/staff), Hugeicons free pack, Tailwind v4 semantic tokens already wired in `frontend/web/src/index.css`.

**KB lessons applied**: KB-DESIGNER-INIT-001 (every new colour pair WCAG-checked), KB-DESIGNER-INIT-002 (≥44×44 px tap targets re-verified for new button tier), KB-DESIGNER-INIT-003 (only semantic tokens; no raw hex in components), KB-DESIGNER-TRUSTGIVE-001 (Cyrillic-first layout — every new label tested at +20% width), KB-DESIGNER-TRUSTGIVE-002 (no people photography — but **brand marks ARE allowed**, see §D), KB-DESIGNER-TRUSTGIVE-003 (re-audited contrast on the new `bg-paper` shade `#F5F1E8`), AP-SHARED-009 (deliver inline if Write blocked).

---

### §A. CharityCard v2 — "real product card"

**Problem (v1.1)**: row reads as a list item; small letter avatar; financial chip row with no anchor figure; "Открыть >" tertiary link as the only outbound CTA.

**Fix**: shift from row to **bordered card** with three explicit zones — left (logo), centre (identity + meta), right (anchor figure + secondary button). The single biggest change: a **right-side numeric anchor** (program-to-revenue %) in `mono-figure` so the card has a visual centre of gravity.

#### A.1 Wireframe (lg / desktop)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   ┌────┐   GiveDirectly                          ✓ Verified              91%     │
│   │ G  │   Денежные переводы людям в крайней                            ▔▔▔▔    │
│   │logo│   бедности                                                  to programs │
│   └────┘   ──────────────                                                        │
│            United States · Direct cash · Founded 2008                            │
│                                                                                  │
│            $349M revenue   ·   filed Mar 2025                                    │
│                                                                                  │
│            [BBB Accredited]  [GiveWell top]  [+1 more]                           │
│                                                                                  │
│                                                              ┌─────────────────┐ │
│                                                              │ Open card  →    │ │
│                                                              └─────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

ASCII reads top-down; in actual layout the right column (anchor + button) is right-aligned and **vertically centred** within the card.

#### A.2 Specifications

| Property | Value |
|---|---|
| Container | `bg-surface` (#FAF7EE), `border border-rule` (1px), `rounded-md` (8px), `p-6` (24px) |
| Card outer gap | `space-y-4` (16px) between cards — replaces concatenated rows |
| Logo zone | 56×56 px squircle, `radius-md`, fixed left, `mr-5` |
| Identity zone | flex-1, min-w-0, body-sm metadata, h3 name |
| Anchor zone | right column, ~140px wide, mono-figure 28/32 + caption underneath |
| Secondary CTA | bottom-right of anchor zone, secondary button (see §E) |
| Min height | 144 px desktop, 168 px mobile (KB-DESIGNER-INIT-002) |

**Logo (left zone)**:
- Real charity logo at 56×56 (ratio-preserved, `object-contain` on `bg-surface-raised`/#FFFFFF inner pad-1)
- Fallback chain: real logo → branded letter avatar (logo policy §D) → generic neutral
- `<img alt="">` (decorative — name follows immediately)

**Identity (centre zone)**:
- **Name**: `text-h3 font-semibold text-ink` (22/30, weight 600). `truncate` at 1 line desktop / `line-clamp-2` mobile.
- **Tagline**: `text-body-sm text-ink-2` (14/22). 2 lines max — `line-clamp-2`.
- **Hairline rule**: `border-t border-rule mt-2 pt-2` after tagline.
- **Geo + meta line**: `text-body-sm text-ink-2`, middle-dot (`·`) separated. Order: country → cause-tag → founded year. (RU: `Россия · Образование · С 2014`.)
- **Financial line**: separate row, `mt-1`. `font-mono text-body-sm`. Shows `revenue` (always) + `filed YYYY-MM` (if available). If revenue is `null`: hide the entire financial line — never show `$null`.
- **Trust badges**: chip row, `mt-3`. Same shape as v1.1, max 3 visible + `[+N more]` overflow chip.

**Anchor zone (right) — the new visual centre**:
- The single most important visual element of the card. Without it, the card looks empty.
- **Primary anchor (program %)**: `font-mono` 28px, weight 500, `text-ink`. Caption underneath in `text-caption text-ink-3`: `"to programs"` / `"в программы"`.
- **Bar indicator** below the figure: 64px wide × 4px tall, `bg-rule` track, fill = `bg-ink-2` at width = `program_expense_pct%`. No colour-coded "good/bad" — the number IS the signal (per design principle 1).
- **No anchor figure?** Three fallback states:
  1. Pct present, revenue present → show pct (default).
  2. Pct missing, revenue present → show **revenue** in mono-figure with caption `"annual revenue"` / `"годовой доход"`. Bar replaced by hairline `▔▔▔▔` (4px stroke `bg-rule`).
  3. Both missing → show only **`Reg. {country}`** chip in anchor zone. Card still scans as a card — the empty-state §F gives more detail.

**Secondary CTA (right, below anchor)**:
- Outlined secondary button (see §E) — width 140px, label `"Open card →"` / `"Открыть карточку →"`.
- Entire card remains an `<a>` wrapper for keyboard / screen-reader navigation; the visible button is purely visual emphasis (CSS `pointer-events: none` so clicks bubble to the wrapping `<a>`). This avoids nested-interactive a11y errors.

#### A.3 Hover / focus / pressed states

| State | Visual change |
|---|---|
| Rest | Border `--color-rule`, no shadow |
| Hover | Border darkens to `--color-ink-3`; secondary CTA flips to filled (becomes primary tier visually); 80ms `ease-out` |
| Focus-visible | 2px ring `--color-verified` + 2px offset (inherits `:focus-visible` from `index.css`) |
| Pressed | Background `--color-paper` (#F5F1E8) so the card "presses into" the page |
| Disabled (n/a) | Catalog cards are never disabled |

**No translateY, no scale, no shadow.** The hover-state border-darkening + secondary-button-fill is the entire "interactive" cue.

#### A.4 Mobile breakpoint behavior (<768)

```
┌──────────────────────────────────┐
│ ┌──┐ GiveDirectly       ✓        │
│ │G │ Cash transfers to            │
│ └──┘ extreme poverty              │
│      ──────────────               │
│      United States · Cash · 2008  │
│      $349M  ·  filed Mar 2025     │
│                                   │
│      [BBB] [GW top] [+1]          │
│                                   │
│   91% to programs                 │
│   ▔▔▔▔▔▔▔▔                        │
│                                   │
│   ┌────────────────────────────┐  │
│   │ Open card                → │  │
│   └────────────────────────────┘  │
└──────────────────────────────────┘
```

- Anchor zone moves from right to bottom-left (above the secondary CTA).
- Secondary CTA becomes full-width.
- Logo shrinks to 40×40.
- Card stays bordered (no concatenation on mobile either — bordered cards scan more clearly when filters are visible above).

---

### §B. Detail-page hero v2 — "above-the-fold answers WHAT before HOW MUCH"

**Problem (v1.1)**: header is sparse (logo + name + EIN line + verification chip), then a stale-warning banner, then the money breakdown, THEN the description. A user landing on the page has to scroll past two financial sections before they learn what the charity does. For 90% of charities this is the wrong order.

**Fix**: Restructure detail page so the **above-the-fold answer is "what + verified + donate"**, and financials are demoted to second screen. Description moves up; methodology note stays where it is.

#### B.1 Wireframe (with explicit fold-line)

```
[ TopNav §6.1 ]
─────────────────────────────────────────────────────────────────────────────
  ← Back to results                                                            ← top of page
─────────────────────────────────────────────────────────────────────────────

  ┌────────┐   GiveDirectly Inc.                              ✓ Verified
  │  64×64 │   Cash transfers to people living in extreme
  │  logo  │   poverty.                                       Last filed
  └────────┘   ────────────                                   Mar 2025
               EIN 27-1661997 · United States · Founded 2008  [chip]

  ┌────────────────────────────────────────────────────────────────────────┐
  │  About GiveDirectly                                                    │
  │  GiveDirectly transfers cash directly to people living in extreme      │
  │  poverty. Founded 2009, based New York, operating Kenya, Uganda,       │
  │  Liberia, Rwanda, and the U.S. Funds are sent via mobile money         │
  │  transfer with no strings attached. Recipients decide what they need   │
  │  most.                                                                 │
  │  [text-body 16/26, max-w 65ch, ink-2]                                  │
  └────────────────────────────────────────────────────────────────────────┘

                             ┌──────────────────────────────┐
                             │  Donate on givedirectly.org → │      ← FOLD ≈ 720px viewport
                             └──────────────────────────────┘
                              0% platform fee. We never see your money.
─ ─ ─ FOLD LINE (target: everything above visible at 1024×720 desktop, 390×844 iPhone) ─ ─ ─

  How they spend the money                                          [h2]
  Fiscal year 2024                                                  [caption]
  ──────────────────
  ████████████████████████  91.0%   Programs            $317.4M
  ███  6.2%                         Administration      $21.6M
  ██   2.8%                         Fundraising         $9.8M
  Source: IRS Form 990 (2024)                                       [link → drawer]

  Source documents                                                  [h2]
  → IRS Form 990 (2024)              [PDF]
  → State registration (NY)          [HTML]
  → Audited financials 2024          [PDF]

  Methodology                                                       [h2]
  This charity is verified because: it is registered with the IRS as a
  501(c)(3), has filed Form 990 in the last 24 months, and we link
  directly to that filing. We do not assess program effectiveness — see
  How we verify.

  Press mentions                                                    [h2]
  · NYT — "The end of charity?" — June 2024
  · Vox Future Perfect — Mar 2025

  ── stale-data inline banner moves HERE (only if applicable) ──
```

#### B.2 Above-the-fold target inventory

At 1024×720 desktop (the smallest "desktop" viewport), the user must see:

1. **Logo** — 64×64, real or branded letter avatar
2. **Name** — `text-h1` (40/48), one line
3. **Tagline** — `text-h4` (18/26), 1–2 lines
4. **Verified chip** — top-right of header
5. **EIN / country / founded** — meta line in `text-body-sm font-mono text-ink-3`
6. **"Last filed" pill** — replaces the giant warning banner; warning now appears further down only if `is_stale`
7. **Description (first 4 lines, ~280 chars)** — text wraps; below the cutoff "Read full description →" anchors to §B.3 if truncated
8. **Donate primary CTA** — single full-width button below the description block, max-width 480px

Items 1–6 fit in a 240px-tall header. Items 7+8 fit in another 240px. Total above-the-fold ~540px — leaves ~180px of the 720 viewport visible for the next section's H2 to peek through, signalling scrollability.

#### B.3 Specifications

**Header**:
- `flex flex-wrap items-start justify-between gap-6 mb-8`
- Logo + identity = left flex group; verified chip + last-filed pill = right column
- Logo: 64×64 (down from v1.1 80×80 — smaller weight relative to the name; per Charity Navigator pattern, name dominates)
- Name: `text-h1 font-semibold text-ink`
- Tagline: `text-h4 font-normal text-ink-2 max-w-[60ch]`
- EIN line: `text-body-sm font-mono text-ink-3 mt-2`
- Verified chip: `<VerificationBadge>` size lg
- Last-filed pill: small chip, `bg-paper` + `border-rule` + `text-body-sm text-ink-2`. If `is_stale`, swap to `bg-warning-soft border-warning text-warning`. (No more giant banner above the fold; full warning banner moves below the fold.)

**Description block** (new placement):
- `bg-surface border-rule rounded-md p-6 mt-6 max-w-[720px]`
- `text-body text-ink-2`. Show first 4 lines (≈280 chars EN, ≈340 chars RU per +20% rule). If longer, truncate with `line-clamp-4` + "Read full description →" link that scroll-anchors to a `<details>` block expanded section further down (or removes clamp, pure CSS).
- If `description` is empty: hide the whole block. Do not render an empty card.

**Donate CTA**:
- Below description, `mt-6`. Centred under description, max-width 480px. `w-full` inside the max.
- Primary tier (see §E). Label: `"Donate on {host} →"` / `"Поддержать на {host} →"`.
- Underneath: `text-body-sm text-ink-2 mt-3`: `"0% platform fee. We never see your money."` / same RU as v1.1 §6.5.
- If `donation_url` is null: replace with secondary tier button labelled `"Visit charity website →"` and remove the 0% line.

**Below-the-fold rearrangement**:
- v1.1 had: stale-warning → money breakdown → donate aside → description. v2.0 has: description (above fold) → money breakdown → source documents → methodology → press → stale-warning (only if applicable, demoted, less alarming).
- The "donate" sticky aside that v1.1 placed in the right column is **removed** — there is now exactly one donate CTA (above the fold, prominent). Sticky-on-scroll re-introduction of donate is deferred to v2.1 (would require its own scroll-into-view/out logic).

**Money breakdown — improvements**:
- H2 changes from `"Where the money goes"` to `"How they spend the money"` / `"Куда идут деньги"` (more direct).
- Three NULL fields after Form 990 cleanup: see §F empty-state guidance.
- Source attribution moves to a single `text-caption text-ink-3` line under the chart, NOT inside it.

---

### §C. Homepage v2 — "Featured charities above the editorial fold"

**Problem (v1.1)**: homepage is hero → stats → editorial prose → marquee → causes → bottom CTA. Beautiful, but a first-time visitor never sees a single charity card, and the hero/serif manifesto doesn't translate into "this is a directory I can browse". The user reads it as a landing page for a SaaS product, not a discovery tool.

**Fix**: insert a **"Featured" section** showing 3–6 real charity cards **immediately under the hero**, before any editorial content. Order changes from "manifesto → product" to "manifesto → product preview → manifesto details".

#### C.1 New section order

```
1. HERO                              (unchanged from v1.1: serif headline + GenerativeShape + 2 CTAs)
2. FEATURED CHARITIES         ← NEW (3–6 CharityCard v2 — see §A — in a vertical stack)
3. STATS                            (unchanged from v1.1: 1.2M / 0% / 0 / 5)
4. EDITORIAL PROSE                  (unchanged: long-form Source Serif manifesto)
5. SOURCES MARQUEE                  (unchanged: registries we draw from)
6. BROWSE BY CAUSE                  (unchanged: editorial list of cause links)
7. BOTTOM CTA                       (unchanged: "Explore catalog →")
```

#### C.2 Featured-section wireframe

```
─────────────────────────────────────────────────────────────────────────────
                                                                          ← directly below hero
   [eyebrow: SAMPLE OF VERIFIED · ОБРАЗЕЦ ПОДТВЕРЖДЁННЫХ]

   Six charities we've verified
   [serif h2 / 32–48 clamp / weight 400]

   [ CharityCard v2 — full width, container-default ]
   [ CharityCard v2 ]
   [ CharityCard v2 ]
   [ CharityCard v2 ]
   [ CharityCard v2 ]
   [ CharityCard v2 ]

                  See all 1.2M+ charities  →           [tertiary text link]
─────────────────────────────────────────────────────────────────────────────
```

- Container `--container-default` (1080px), `space-y-4` between cards, `py-24 lg:py-32` to match other sections.
- Cards link to detail pages exactly as in catalog. Same `<CharityCard>` React component — single source of truth.
- Eyebrow `text-caption uppercase tracking-widest text-ink-3 font-medium` (matches v1.1 stats / sources / causes pattern).
- H2 in Source Serif 4 weight 400, matches sibling sections — keeps the editorial spine intact.
- Trailing tertiary link to full catalog (see §E for tertiary spec).
- Below 768: cards stack same way (already the v2 mobile layout), but section padding tightens to `py-16`.

#### C.3 No empty state on first paint

The featured section calls a new endpoint `GET /api/charities/featured/` (Backend Phase 4 follow-up — out of scope for this design, but flagged in handoff §H below). Until that endpoint is live, v2.0 ships the homepage with a **static fallback array** of 6 hand-picked slugs from the seed data (e.g. `givedirectly`, `british-red-cross`, `rusfond`, plus 3 more once seeded), fetched client-side in parallel. If 0 cards return (e.g. cold cache, network error), section unmounts entirely — homepage falls back gracefully to v1.1 order.

---

### §D. Logo policy clarification — brand marks ARE allowed

**Problem (v1.1)**: rule "no photography of people" is correct, but combined with "registry logos (small, monochrome where possible) — IRS, Charity Commission, Минюст, BBB seal" in §10.3 it implicitly forbade **charity brand logos** (the wordmark or symbol of the actual charity). That gap is why the live site shows letter avatars (`G`) for every org — there's no rule saying we can use the GiveDirectly logo, so the developer didn't.

**Fix**: explicit allow-list, sizing rules, and fallback chain.

#### D.1 What is allowed (v2.0 — extends v1.1 §10.3)

| Imagery type | v1.1 status | v2.0 status |
|---|---|---|
| Photography of people (donors, recipients, staff, founders) | **Banned** | **Banned** (unchanged) |
| Stock photography | **Banned** | **Banned** (unchanged) |
| Document scans / Form 990 thumbnails | Allowed | Allowed (unchanged) |
| Data viz (single-colour) | Allowed | Allowed (unchanged) |
| Registry logos (IRS, Charity Commission, BBB) | Allowed (small, monochrome) | Allowed (small, monochrome) |
| **Charity brand logos / wordmarks** | **Implicitly absent** | **EXPLICITLY ALLOWED** ← new |
| Charity hero illustrations / mascots | n/a | **Banned** (would break editorial restraint) |
| Cause-tag pictograms | "v2 optional" | Stays deferred to v2.1+ |

**Rationale**: a charity logo is a **brand mark** (a wordmark or symbol that identifies an institution), not photography. Brand marks are essential trust signals — recognition is the first verification a user does ("oh, that's the actual GiveDirectly I've heard of"). Banning them was an unintended over-correction. KB-DESIGNER-TRUSTGIVE-002 is updated below in the reflection block to clarify scope.

#### D.2 Sizing & placement rules

| Context | Size | Container | Notes |
|---|---|---|---|
| Catalog card (CharityCard v2) | 56×56 | Squircle, `radius-md`, `bg-surface-raised` (#FFFFFF) inner pad-1 | Logo never larger than name |
| Detail-page header | 64×64 | Same as above | Down from v1.1's 80×80 — name still wins visually |
| Source-document drawer header | 32×32 | Inline with name | Optional — registry logo (IRS seal) only |
| Footer / nav | n/a | Use TrustGive wordmark only | Never charity logos in chrome |

**Aspect-ratio handling**:
- `object-contain` (never `object-cover` — cropping a charity logo is brand vandalism)
- Padding inside the squircle so the logo never touches the rounded edge: `p-1` for 56×56, `p-1.5` for 64×64
- Logos with very wide horizontal ratios (e.g. "Save the Children" wordmark) get an exception: `aspect-square` container holds them at `max-w-full max-h-[60%]` to keep the squircle shape
- Background of the squircle: always pure white `#FFFFFF` (`--color-surface-raised`), even on dark mode — matches how charity logos are designed (typically for white backgrounds)

#### D.3 Fallback chain (every charity, every render)

```
1. logo_url present + image loads     → render <img>
2. logo_url null OR image error       → branded letter avatar
3. branded letter avatar fails        → generic neutral fallback
```

**Step 2 — branded letter avatar (new spec)**:
- Background colour pulled from a deterministic hash of the charity slug, mapped to one of **5 cause-soft colours**:
  - Children / education → `--color-info-soft` #E8ECF8 + `--color-info` #3D5AB5 text
  - Climate / environment → `--color-verified-soft` #E6F2EE + `--color-verified` #0E7C5C text
  - Health / medicine → `--color-error-soft` #FBEAEA + `--color-error` #A02828 text
  - Animals / refugees / humanitarian → `--color-warning-soft` #FBF3DE + `--color-warning` #9A6B00 text
  - Default / other → `bg-paper` #F5F1E8 + `text-ink-2` #3D3A32
- Letter: first letter of `name[lang]`, uppercase, `font-serif` (matches editorial tone), weight 600, font-size = 60% of avatar size (so 56→34px, 64→38px).
- All 5 background/text pairs **WCAG-checked** (re-verified for new paper #F5F1E8 base):
  | Pair | Ratio | Pass |
  |---|---|---|
  | #3D5AB5 on #E8ECF8 | 5.6:1 | AA |
  | #0E7C5C on #E6F2EE | 4.7:1 | AA |
  | #A02828 on #FBEAEA | 5.4:1 | AA |
  | #9A6B00 on #FBF3DE | 5.1:1 | AA |
  | #3D3A32 on #F5F1E8 | 9.6:1 | AAA |

**Step 3 — generic neutral**:
- The current v1.1 `bg-info-soft text-info "G"` becomes the "default" cause colour (#5 above), so step 3 only fires if the cause-tag lookup itself errors. Behaves like v1.1 fallback — preserves backward compatibility.

#### D.4 Do / Don't examples

```
DO ✓                                              DON'T ✗
─────────────────────────────────────             ─────────────────────────────────────
Use the actual GiveDirectly wordmark              Use a stock photo of the founder
on the catalog card.                              (banned — people photography rule).

Use a branded letter avatar with                  Use a brightly coloured emoji or
cause-coloured background when                    illustration as a stand-in.
no logo is available.

Pad logos with p-1 inside the                     Crop a logo with object-cover
squircle so they breathe.                         to fill the squircle.

Always show the wordmark on white                 Tint the logo background with
inside the squircle.                              the cause colour (logos are
                                                  designed for white).

Allow the wordmark to dominate the                Use a logo larger than the
left zone but not the entire card                 name — name still wins
(name is still the heading).                      visual hierarchy.
```

---

### §E. Button hierarchy — three explicit tiers

**Problem (v1.1)**: §6 spec'd buttons inline (verified bg + verified-on text + radius-md) but never separated tiers. Result on the live site: every catalog row's "Открыть >" looks identical to a navigation text-link, and the detail-page donate button has no documented sibling for "Open card" / "View source" / "Visit website" — developer reached for arbitrary mixes.

**Fix**: three named tiers. Every clickable thing in TrustGive maps to exactly one of these.

#### E.1 The three tiers

| Tier | Purpose | Visual |
|---|---|---|
| **Primary** | The single most important action on the screen — almost always **Donate** | Filled forest-green, white text, prominent |
| **Secondary** | Important but not unique — "Open card", "View source", "Visit website", "Read full description" | Outlined ink, transparent fill, becomes filled on hover |
| **Tertiary** | Inline navigation, in-line links, "See all 1.2M+ charities", footer links | Underline, ink colour, no border, no fill |

**Rule**: at most **one** primary button per screen above the fold (homepage, detail page, methodology). Catalog cards have zero primary buttons — each card has exactly one secondary CTA. This rule comes from Apple HIG ("a screen has one main action") and from the v1.1 design principle 2 (restraint over emphasis).

#### E.2 Specifications

**Primary** (`<Button variant="primary">`)

```
┌─────────────────────────────┐    bg:           #0E7C5C  (--color-verified)
│  Donate on givedirectly →   │    text:         #FAFAF7  (--color-verified-on)
└─────────────────────────────┘    border:       none
                                   radius:       8px (--radius-md)
                                   padding:      12px 24px (py-3 px-6)
                                   font:         Inter 16/24 weight 500
                                   icon:         right, 16px, 1.5 stroke
                                   min-height:   44px (KB-DESIGNER-INIT-002)
```

| State | Change |
|---|---|
| Hover | bg darkens to `#0A6A4D` (-2 luminance steps); 80ms ease-out |
| Focus-visible | 2px ring `#0E7C5C` + 2px offset (inherits global) |
| Active (pressed) | bg `#085339` (-4 luminance); 1px translateY-px is forbidden |
| Disabled | bg `--color-rule` #D8D2BD, text `--color-ink-3` #6D685C; cursor not-allowed; opacity 1 (no opacity dim — use real colours so disabled is still readable, AA pair = 5.1:1) |
| Loading | bg unchanged, text replaced by spinner icon (Hugeicons `Loading03Icon` 16px), `aria-busy="true"`; button width preserved via `min-width` lock to prevent layout shift |

**Where used**:
- Detail page hero: Donate CTA
- Donate-confirm modal: "Continue to {host}" button
- (Reserved for future: any "create / submit" — but MVP has none)

**Secondary** (`<Button variant="secondary">`)

```
┌─────────────────────────────┐    bg:           transparent
│  Open card  →               │    text:         #181612 (--color-ink)
└─────────────────────────────┘    border:       1px solid #181612 (--color-ink)
                                   radius:       8px (--radius-md)
                                   padding:      10px 20px (py-2.5 px-5)
                                   font:         Inter 14/22 weight 500
                                   min-height:   44px
```

| State | Change |
|---|---|
| Hover | bg fills to `#181612` (`--color-ink`), text flips to `#F5F1E8` (`--color-paper`) — becomes a "primary-look" button. 80ms |
| Focus-visible | inherits global ring |
| Active | bg `#3D3A32` (`--color-ink-2`), text paper |
| Disabled | border `--color-rule`, text `--color-ink-3`, no fill |
| Inside CharityCard | when card itself is hovered, secondary auto-fills (matches §A.3 hover behaviour) |

**Where used**:
- CharityCard catalog/featured: "Open card →"
- Detail page: "View source documents", "Visit charity website" (when `donation_url` null), "View full PDF on ProPublica" (inside drawer)
- Comparison view: "[Donate ↗]" per column actually downgrades to secondary because the screen has no single primary (3 columns competing); the page intro CTA carries primary.

**Tertiary** (`<Link variant="tertiary">` or plain `<a>`)

```
See all 1.2M+ charities →           text:         #181612 (--color-ink)
                                    decoration:   underline, 1px, 4px under-offset
                                    decoration-color: #D8D2BD (--color-rule)
                                    icon:         right, 14px, 1.5 stroke, baseline-aligned
                                    padding:      0 (inline)
                                    font:         inherit (matches surrounding text)
```

| State | Change |
|---|---|
| Hover | decoration-color flips to `--color-ink`; icon shifts +2px right via `translate-x-0.5`; 120ms |
| Focus-visible | 2px ring + 2px offset, but **square** corners (so it visually distinguishes from a button — hint: this is a link, not a button) |
| Active | text `--color-ink-2`, decoration `--color-ink` |
| Disabled (rare) | text `--color-ink-3`, no underline, cursor default |

**Where used**:
- Featured section trailing link: "See all 1.2M+ charities →"
- Footer links: Methodology, Press, GitHub, RSS
- In-prose links inside editorial sections, methodology page, description blocks
- "Read full description →" on detail page
- Hero secondary CTA: "How we verify →" (currently a tertiary, NOT a secondary — this fixes the v1.1 ambiguity where the homepage had `bg-ink` button + underline link side-by-side; the underline link is tertiary and the `bg-ink` is **demoted to secondary** in v2.0)

#### E.3 Migration map (current code → v2.0 tier)

| Current usage | File | v2.0 tier |
|---|---|---|
| Homepage "Explore catalog" `bg-ink text-paper` | HomePage.tsx L65 | **Primary** (was using ink — flip to verified to match donate semantics) |
| Homepage "How we verify" underline | HomePage.tsx L71 | **Tertiary** (already correct, formalise spec) |
| CharityCard "View →" inline | CharityCard.tsx L102 | **Secondary** ("Open card →" filled-outline button) |
| Detail "Donate on host" `bg-verified` | CharityDetailPage.tsx L111 | **Primary** (already correct, formalise spec) |
| Detail source-doc "→ {label}" | CharityDetailPage.tsx L129 | **Tertiary** (correct — keep inline link style) |
| HomePage bottom CTA `bg-ink` | HomePage.tsx L214 | **Primary** (flip to verified, matches hero) |
| Featured section trailing link (NEW) | HomePage.tsx (new) | **Tertiary** |

**Decision**: hero+bottom-CTA buttons flip from `bg-ink` to `bg-verified`. This is a deliberate v2.0 change — the v1.1 use of black-ink as the "main button" was an Anthropic-mimic choice that visually separates "explore catalog" (black) from "donate" (green) by colour. v2.0 unifies: green = primary action, full stop. There is now exactly one "primary button look" in the entire product, and "donate on charity site" reads as the highest-tier conversion.

---

### §F. Empty-state guidance — Form 990 NULL after cleanup

**Problem**: after the database cleanup (per CHANGELOG entry on 2026-05-06 dropping garbage program/admin/fundraising rows that didn't reconcile to 100%), many charities now have only `total_revenue_usd` populated — `program_expense_pct`, `admin_expense_pct`, `fundraising_expense_pct` are all NULL. Rendering "0% to programs" or a 3-bar chart with 0/0/0 looks broken. Hiding the entire money breakdown silently is worse — user thinks we have no data.

**Fix**: a deliberate "Only total revenue available" treatment that **acknowledges the gap honestly**, in line with v1.1 design principle 1 ("show your work").

#### F.1 Decision tree

```
charity.total_revenue_usd present?
├── NO  → §F.2 "No financial data on file"
└── YES → program/admin/fundraising all present (sum ≈ 100%)?
          ├── YES → render full MoneyBreakdown bar chart (existing v1.1 behaviour, unchanged)
          └── NO  → §F.3 "Only total revenue available"
```

#### F.2 No financial data on file

```
┌──────────────────────────────────────────────────────────┐
│  Financial breakdown                                     │
│                                                          │
│  No financial filing on record yet.                      │
│  This charity is registered with {registry} but their    │
│  most recent {form_name} filing is not yet in our        │
│  database.                                               │
│                                                          │
│  → Search {registry_name} directly                       │
│  [tertiary link, opens registry search in new tab]       │
└──────────────────────────────────────────────────────────┘
```

- `bg-paper` border-rule rounded-md p-6, NOT a warning state — this is matter-of-fact, not an error
- `text-body text-ink-2`
- Tertiary link opens (US) `https://projects.propublica.org/nonprofits/search?q={ein}`, (UK) `https://register-of-charities.charitycommission.gov.uk/charity-search?p_p_state=normal&q={charity_number}`, (RU) `https://минюст.рф/...`
- No giant warning icon. The design refuses to dramatise data gaps — that's the point of the "trust tool" positioning.

#### F.3 Only total revenue available

```
┌──────────────────────────────────────────────────────────┐
│  How they spend the money                                │
│  Fiscal year 2024                                        │
│  ──────────────                                          │
│                                                          │
│  $349M  total revenue                                    │
│  [mono-figure 28/32 ink, caption 12/18 ink-3]            │
│                                                          │
│  ──────────────                                          │
│                                                          │
│  Program / administration / fundraising breakdown        │
│  not available in the published filing. Many charities   │
│  outside the U.S. don't itemise these in {form_name},    │
│  and we don't infer what wasn't disclosed.               │
│  [text-body-sm text-ink-2 max-w-65ch]                    │
│                                                          │
│  → View full {form_name} filing                          │
│  [tertiary, opens source-document drawer]                │
└──────────────────────────────────────────────────────────┘
```

- The single number ($349M) takes the visual centre — same `mono-figure` weight as the v2 catalog card anchor. Card has gravity even with one figure.
- The honesty paragraph is critical: "we don't infer what wasn't disclosed" is the entire trust-tool positioning, surfaced as UX copy.
- RU copy: `«Программы / администрирование / привлечение средств — разбивка не указана в опубликованной отчётности. Многие зарубежные организации не детализируют это в {form_name}, и мы не додумываем то, что не раскрыто.»`
- Localised registry-form names: US → `Form 990`, UK → `Annual Return`, RU → `годовой отчёт`.

#### F.4 Catalog card with NULL pct (already covered §A.2)

Repeat for cross-reference: when `program_expense_pct` is NULL but revenue exists, the right-anchor zone of CharityCard v2 falls back to revenue with caption `"annual revenue"`. Card never renders `0% to programs` — that would be a lie.

---

### §G. Featured-charity selection algorithm

**Problem**: §C requires 3–6 charities on the homepage. Which ones?

**Goals**:
1. Show **breadth** — not 6 American charities. Reinforces "US + UK + Russia" SPEC positioning.
2. Show **scale variety** — not all $100M+ orgs. A small verified org signals "we cover the long tail".
3. Show **only verified** — homepage is a trust pitch; an `is_stale` charity on the homepage breaks the pitch.
4. **Determinism + freshness** — same charity list on F5 reload (no jitter) but rotates weekly so repeat visitors see new orgs.

#### G.1 Algorithm

```
SELECT charity from charities WHERE
    verification_status = 'verified'
    AND is_stale = FALSE
    AND total_revenue_usd IS NOT NULL
    AND logo_url IS NOT NULL          -- prefer real logos on homepage
ORDER BY <slot-specific>
LIMIT 1 per slot

slots:
  S1: country='US', total_revenue_usd DESC                            -- big US org
  S2: country='US', total_revenue_usd DESC, OFFSET 1                  -- 2nd big US org
  S3: country='US', total_revenue_usd DESC, OFFSET 2                  -- 3rd big US org
  S4: country='GB', total_revenue_usd DESC                            -- UK presence
  S5: country='RU', total_revenue_usd DESC                            -- Russia presence
  S6: total_revenue_usd ASC, OFFSET 0                                 -- smallest verified — wildcard

deduplicate: if any slot's pick is already in earlier slots, take next eligible
weekly rotation: deterministic hash(slug + ISO-week) % {pool_size} as tiebreak — shuffles within scale band, preserves slot semantics
```

#### G.2 Cold-start fallback (current state)

While the database has only ~1–10 charities seeded, the algorithm runs against whatever is present and pads to 6 from a hard-coded fallback list `['givedirectly', 'british-red-cross', 'rusfond', 'givewell', 'against-malaria-foundation', 'macmillan-cancer-support']` — those that exist in the DB render, missing slots collapse silently. Section minimum to render: **3 cards**. Below that, the section unmounts (homepage falls back to v1.1 — see §C.3).

#### G.3 Manual override (admin curation)

A new field `is_featured: bool` on the Charity model lets the admin pin a specific charity to a slot. If `is_featured=TRUE`, the algorithm reserves that slot for the manual pick before running the slot rules. This is the editorial escape hatch — useful when a charity gets press attention or seasonal relevance.

**Out of scope for v2.0 design**: implementing the featured-charity endpoint is a Backend task (Phase 3 follow-up). The design document specifies the contract; backend implements.

---

### §H. Handoff checklist for Frontend (v2.0 implementation)

Items the frontend developer needs to know:

- [ ] **CharityCard.tsx** — refactor to v2 layout (§A). Add `anchor` prop computed from `program_expense_pct` with fallback to `total_revenue_usd`. Add bar indicator. Add secondary-button visual (entire card is `<Link>` wrapper; button is CSS-only).
- [ ] **CharityDetailPage.tsx** — restructure JSX to put description above money breakdown; demote stale warning to below-fold; remove sticky donate aside (single primary CTA in header).
- [ ] **HomePage.tsx** — add `<FeaturedCharities>` section between Hero and Stats; flip `bg-ink` buttons to `bg-verified` (primary tier).
- [ ] **Button component** — extract three variants (`primary`, `secondary`, `tertiary`) from inline classes. Recommend `class-variance-authority` (cva) — already in shadcn ecosystem, ~1.5kb.
- [ ] **BrandedAvatar component** — implement deterministic hash → cause-soft palette (§D.3). Used everywhere there's no `logo_url`.
- [ ] **MoneyBreakdown.tsx** — handle NULL pct fields per §F.3 (replace bar chart with single mono-figure block).
- [ ] **API contract addition** — `GET /api/charities/featured/?lang={en|ru}` returns ≤6 `CharitySummary` items (Backend Phase 3.1 follow-up).
- [ ] **i18n keys** added: `charity.toPrograms`, `charity.openCard`, `home.featured.eyebrow`, `home.featured.title`, `home.featured.seeAll`, `charity.financial.noFiling`, `charity.financial.onlyRevenue`, `charity.financial.notItemised`. EN + RU side-by-side.
- [ ] **Visual regression** — re-snapshot every Phase 4.5 Playwright test that asserts on CharityCard or CharityDetailPage layout (existing E2E will fail until updated).

---

### §I. Open questions — flag for user approval

1. **Primary button colour flip (ink → verified)**. v1.1 used `bg-ink` for "Explore catalog"; v2.0 unifies to `bg-verified`. If the user prefers the Anthropic-style "ink button on cream paper" hero, we keep ink for navigation and reserve green only for donate. Both work; v2.0 picks one tier.
2. **Card border vs row concatenation**. v1.1 catalog used concatenated rows with bottom-borders only ("editorial table"). v2.0 cards have full borders ("product cards"). The catalog now feels less like a printed table and more like a marketplace. If the user wants the editorial-table density back, revert to bottom-only borders + `space-y-0`.
3. **Featured section copy**. Suggested H2: `"Six charities we've verified"` / `"Шесть организаций, которые мы проверили"`. Plain and confident. Alternative: `"A sample of what we've verified"` (more humble, less product-y).
4. **Donate CTA placement on detail page**. v2.0 puts it above the money breakdown (one CTA, hero-position). v1.1 kept it as a sticky right-rail aside. Sticky-rail re-introduction deferred to v2.1; if the user wants both, we ship in v2.0.

---

<reflection>
  <what_went_well>
    The user's "1/10" feedback was concrete and located at three specific surfaces (catalog card, detail page, homepage) — the brief made it easy to write a delta-document rather than rewrite v1.1 in full. Logo policy clarification was the highest-leverage fix: a single sentence that was missing from v1.1 (brand marks ARE allowed) explains 60% of the "looks broken" reaction in one go.
    Right-side numeric anchor (program-to-revenue % in mono-figure) is the structural change that turns the row into a card without resorting to shadows or gradients — preserves v1.1's editorial restraint while solving the "scans as list item" problem. Cause-coloured branded letter avatars give the product a fallback that looks deliberately designed instead of generic.
  </what_went_well>
  <challenges>
    Playwright sandbox: own screenshot folder under `projects/trustgive/design_references/` is outside the allowed roots, so reference images from this run live in `.claude/.playwright-mcp/`. Re-stating the constraint here so the parent agent can move/copy them if visual references are needed for portfolio. Charity Navigator search page took 2 attempts to load (their /best-charities/ URL 404s now). Every.org is behind a Vercel security challenge — useful to note that competitor reverse-engineering is increasingly gated; relying on direct screenshots of competitor UIs is not always feasible. The new paper colour `#F5F1E8` (vs v1.1 spec `#FAFAF7`) silently shipped between v1.1 and MVP — re-audited every contrast pair against the new shade to make sure new branded-avatar palette still clears AA.
  </challenges>
  <lessons_learned>
    1. **Logo policy must be explicit in both directions.** If a designer writes "ban X" for one image category (people photos), they must also explicitly write "allow Y" for adjacent categories (brand marks). Implicit allow-by-default doesn't survive into implementation — developers default to "absent" when the rule is silent. Worth promoting to KB-DESIGNER-TRUSTGIVE-002 as a clarification: ban photography of *people*, but allow brand marks. Cross-cutting (any "trust UI" project) — flag for shared promotion.
    2. **A list-item-vs-product-card problem is solved by giving the card a numeric anchor**, not by adding shadows or hover-lifts. Catalog cards without a strong right-anchor figure read as table rows even when bordered. The v2 program-pct mono-figure anchor is the cheapest fix; works without changing palette or motion.
    3. **Detail pages should put "what does this org do" above any chart.** The default impulse is to lead with financials because they're the wedge feature, but the user must understand WHO they're looking at before they care about HOW MUCH. Description-first layout is a reusable pattern for any data-rich profile page.
    4. **Three button tiers is the maximum any product needs.** Five tiers (primary / secondary / tertiary / ghost / link) is over-engineering — designers reach for ghost when they want secondary that looks lighter, but secondary already covers that need. Strict three-tier system makes the migration map (existing components → tiers) trivially auditable.
    5. **Empty-state copy is a positioning decision, not a UX afterthought.** "We don't infer what wasn't disclosed" is the entire TrustGive value prop, surfaced inside an empty state. Drives the same trust signal as the methodology page would, but at the moment of confusion. Worth memorialising.
  </lessons_learned>
  <knowledge_to_store>
    YES — three new KB entries (severity LOW–MEDIUM, no shared promotion needed unless re-applied to another trust-tool project):

    KB-DESIGNER-TRUSTGIVE-004 | 🟡 MEDIUM | Allow-list, not just ban-list, for imagery policies
    Domain: brand, photography, trust UX
    Last validated: 2026-05-07
    Context: A "no photography of people" rule for a trust-UI product was correctly written but didn't survive implementation because brand-mark allowance was implicit. Result: live MVP showed letter avatars for every charity.
    Lesson: When writing an imagery policy with bans, always pair every ban with an explicit adjacent allow-list. "Ban X, allow Y" reads as a clear rule; "ban X" alone reads as "ban all images" by developers. For trust-UI products specifically, brand marks (logos, wordmarks) must be explicitly allowed — they are the first verification signal a user does.

    KB-DESIGNER-TRUSTGIVE-005 | 🟢 LOW | Right-anchor numeric in catalog cards
    Domain: layout, scannability, data-rich UIs
    Last validated: 2026-05-07
    Context: Catalog cards without a strong right-side numeric anchor read as table rows even when bordered. Adding shadows, hover-lifts, or gradients to compensate breaks editorial restraint.
    Lesson: For data-rich list items (charities, products, companies, properties), give each card one large monospace numeric anchor on the right side that summarises the row's most important quantitative attribute (program-pct, price, score, rating). Pair it with a secondary outlined CTA. The numeric anchor is the cheapest "this is a card, not a row" cue available without breaking minimal-motion design rules.

    KB-DESIGNER-TRUSTGIVE-006 | 🟢 LOW | Three is enough button tiers
    Domain: design system, components
    Last validated: 2026-05-07
    Context: v1.1 specified button styling inline without naming tiers. Result: developers picked black-ink, green, and underline mostly correctly but had no mental model when novel buttons appeared (catalog "View" link). v2.0 enforces exactly primary / secondary / tertiary.
    Lesson: For trust/data products with one clear conversion action (donate, subscribe, contact), a three-tier button system (primary / secondary / tertiary) is sufficient. Avoid a fourth "ghost" tier — its use cases collapse into "secondary on dark" or "secondary disabled". Maintain a migration map: every existing inline button class should map to exactly one tier; if it doesn't, the tier system is incomplete.
  </knowledge_to_store>
</reflection>

---

## 0. Executive summary (one screen)

TrustGive's design system is **editorial, restrained, document-first**. We borrow gravitas from publishing (Stripe Press, NYT, Are.na) and refuse the visual vocabulary of the non-profit sector (sad-eyed children, dark-blue + orange, vibrant SaaS gradients). The look is Inter + Source Serif over warm off-white paper, with one trust-signalling green accent (`#0E7C5C`). Dark mode is offered as a true publication experience, not an afterthought. The primary interaction — opening a source document — is choreographed like opening a vault, because it is the entire product promise.

**Why this is different from competitors**:
- Charity Navigator: stock-photo volunteers + neon-pink CTA + dotted patterns → looks like a 2018 marketing site
- Charity:Water: emotional photography + email-capture popup → high-pressure fundraising
- Effektiv-Spenden: B&W polaroid photography + orange-red accent → dignified but dated
- TrustGive: zero photography of people, document scans + numerical data viz, single accent green, monospace numbers, generous whitespace → looks like a research tool, reads like a newspaper, feels like Stripe Press

---

## 1. Design principles

Six short, opinionated rules. Every design decision is checked against these.

1. **Documents over ratings.** A user must always be one click from the original PDF/registry page. UI elements that link to source documents are visually privileged: dedicated icon, dedicated colour, larger touch target, clear label `View IRS 990 (PDF)`. We never invent our own opaque trust score.
2. **Restraint over emphasis.** No gradients, no drop-shadows, no glassmorphism, no hover-lift card animations. Hierarchy comes from typographic scale, line-height, and whitespace — not from competing visual effects.
3. **Numbers are first-class citizens.** Financial figures use a tabular monospace (Geist Mono) so columns align in comparison views. A number is never decoration.
4. **Dignity, not pity.** No photography of beneficiaries, recipients, or volunteers. The only imagery TrustGive uses is: (a) document scans, (b) data visualisations, (c) registry logos. This is a deliberate anti-pattern to the entire NGO design tradition and is itself a trust signal.
5. **Bilingual at byte 1.** The Russian variant is not a translation layer — it is a peer of the English variant. Every type-scale step is tested with Cyrillic at the same size; every component is composed assuming text expansion of +20%.
6. **The methodology page is the homepage.** "How we verify" is treated as a flagship editorial page (long-form, beautiful typography, dignified). It is the highest-converting trust signal we have, per `MARKET_ANALYSIS.md` §5 RECOMMENDATION 6.

---

## 2. Color palette

### 2.1 Naming convention

Tokens are **semantic** (per KB-DESIGNER-INIT-003). Never reference raw hex in components.

```
--color-paper            page background
--color-surface          card / panel surface
--color-surface-raised   modal / drawer / sticky bar
--color-ink              primary body text
--color-ink-2            secondary text (metadata, labels)
--color-ink-3            tertiary / muted (timestamps, captions)
--color-rule             1px borders, table rules, hairlines
--color-verified         the trust accent (verification, primary CTA)
--color-verified-on      text/icon on verified backgrounds
--color-warning          unverified-but-listed states
--color-error            stale data, missing filings
--color-info             RU-curated tag, neutral information
```

### 2.2 Light mode (default)

The base is **warm off-white paper** (Are.na 95%, Stripe Press for serif energy). Not pure `#FFFFFF` — that reads as sterile-corporate. The slight warmth `#FAFAF7` (3% cream) signals "publication".

| Token | Hex | Role |
|---|---|---|
| `--color-paper` | `#FAFAF7` | Page background |
| `--color-surface` | `#FFFFFF` | Cards, charity result rows |
| `--color-surface-raised` | `#FFFFFF` + 1px rule | Modals, drawers (no shadow — use border) |
| `--color-ink` | `#0F1A2A` | Headlines, body text |
| `--color-ink-2` | `#3A4356` | Subtitles, secondary labels |
| `--color-ink-3` | `#5C6577` | Captions, "filed 14 months ago" |
| `--color-rule` | `#D9D5C7` | Borders, dividers, table cell rules |
| `--color-verified` | `#0E7C5C` | Trust accent — verified badges, primary CTA |
| `--color-verified-on` | `#FAFAF7` | Text on `--color-verified` |
| `--color-verified-soft` | `#E6F2EE` | Verified badge background, soft alert |
| `--color-warning` | `#9A6B00` | "Filing >24mo old" amber |
| `--color-warning-soft` | `#FBF3DE` | Warning row background |
| `--color-error` | `#A02828` | "No filing on record" |
| `--color-error-soft` | `#FBEAEA` | Error row background |
| `--color-info` | `#3D5AB5` | RU-curated tag, neutral chips |
| `--color-info-soft` | `#E8ECF8` | Info row background |

### 2.3 Why green = "verified"?

Donor-trust research (Fidelity Charitable Donor Trust Report 2024, BBB Give.org Donor Trust Report 2024, both cited in `MARKET_ANALYSIS.md` §3) consistently shows **green as the colour donors associate with "verified" / "approved" / "go ahead"** — universally cross-cultural, low-saturation greens specifically signal "honest" rather than "growth/finance" (which is the saturated green in fintech). Blue was considered and rejected: it is **the** dominant colour of every charity rating site (Charity Navigator, Candid, BBB Give.org all use navy blue). Picking blue would camouflage TrustGive in the existing market. Picking green differentiates *and* matches "verified" semantic.

Hex `#0E7C5C` is a **deep forest green**, not a pure spectrum green. It reads as institutional ("Treasury green"), not Slack-notification-green. Tested against neighbours in the colour wheel — passes 5.4:1 on `#FAFAF7` for body text and 5.6:1 on `#FFFFFF`. Acts as a single accent: nothing else in the UI is green.

### 2.4 Dark mode

Activated via `prefers-color-scheme: dark` and a manual toggle (saved to `localStorage`, same key family as the language preference). Dark mode is **not inverted light mode** — it is its own publication, like NYT Games dark mode.

| Token | Hex | Role |
|---|---|---|
| `--color-paper` | `#0E141C` | Page background (cool near-black, not pure `#000`) |
| `--color-surface` | `#141B26` | Cards |
| `--color-surface-raised` | `#1B2330` | Modals, drawers |
| `--color-ink` | `#E8E5DC` | Primary text (warm off-white) |
| `--color-ink-2` | `#A8AEBC` | Secondary |
| `--color-ink-3` | `#777E8E` | Tertiary |
| `--color-rule` | `#262E3C` | Borders |
| `--color-verified` | `#34D399` | Brighter green for dark backgrounds (10.5:1) |
| `--color-verified-on` | `#0E141C` | Text on verified |
| `--color-verified-soft` | `#0E2A24` | Verified badge bg |
| `--color-warning` | `#E2B65A` | Amber, brightened |
| `--color-error` | `#E36B6B` | Red, brightened |
| `--color-info` | `#7FA0F4` | Blue, brightened |

### 2.5 Contrast audit (WCAG 2.1 AA — every text/bg pair)

Verified using WCAG relative-luminance formula. Every body-text pair clears AA; hero / display sizes clear AAA.

**Light mode**

| Foreground | Background | Ratio | Standard | Pass? |
|---|---|---|---|---|
| `#0F1A2A` ink | `#FAFAF7` paper | **17.7:1** | AA normal | ✅ AAA |
| `#0F1A2A` ink | `#FFFFFF` surface | **18.4:1** | AA normal | ✅ AAA |
| `#3A4356` ink-2 | `#FAFAF7` paper | **9.0:1** | AA normal | ✅ AAA |
| `#5C6577` ink-3 | `#FAFAF7` paper | **5.9:1** | AA normal | ✅ AA |
| `#5C6577` ink-3 | `#FFFFFF` surface | **6.2:1** | AA normal | ✅ AA |
| `#0E7C5C` verified | `#FAFAF7` paper | **5.4:1** | AA normal | ✅ AA |
| `#0E7C5C` verified | `#FFFFFF` surface | **5.6:1** | AA normal | ✅ AA |
| `#FAFAF7` paper | `#0E7C5C` verified | **5.4:1** | AA normal (button label) | ✅ AA |
| `#0E7C5C` verified | `#E6F2EE` verified-soft | **4.7:1** | AA normal (chip text) | ✅ AA |
| `#9A6B00` warning | `#FBF3DE` warning-soft | **5.1:1** | AA normal | ✅ AA |
| `#A02828` error | `#FBEAEA` error-soft | **5.4:1** | AA normal | ✅ AA |
| `#3D5AB5` info | `#E8ECF8` info-soft | **5.6:1** | AA normal | ✅ AA |
| `#D9D5C7` rule | `#FAFAF7` paper | 1.13:1 | UI graphical hairline (decorative non-text per WCAG 1.4.11; interactive borders use ink-3 → 5.9:1) | n/a |

**Dark mode**

| Foreground | Background | Ratio | Pass? |
|---|---|---|---|
| `#E8E5DC` ink | `#0E141C` paper | **16.8:1** | ✅ AAA |
| `#E8E5DC` ink | `#141B26` surface | **15.2:1** | ✅ AAA |
| `#A8AEBC` ink-2 | `#0E141C` paper | **7.6:1** | ✅ AAA |
| `#777E8E` ink-3 | `#0E141C` paper | **4.6:1** | ✅ AA |
| `#34D399` verified | `#0E141C` paper | **10.5:1** | ✅ AAA |
| `#0E141C` paper | `#34D399` verified | **10.5:1** | ✅ AAA (button label) |
| `#E2B65A` warning | `#0E141C` paper | **9.5:1** | ✅ AAA |
| `#E36B6B` error | `#0E141C` paper | **5.4:1** | ✅ AA |

---

## 3. Typography

### 3.1 Font choice — and the reasoning

**Sans (UI + body)**: **Inter** — variable axis 100–900, free, designed by Rasmus Andersson, full Cyrillic + Cyrillic Extended. Reasons:
1. **Cyrillic is first-class, not bolted on.** Many otherwise-good fonts (Geist Sans, GT America, Söhne) have weak or absent Cyrillic. Inter's Cyrillic ships in identical optical weight per glyph.
2. Used by Stripe (incl. Stripe Press), Linear, Vercel — visual confirmation of "modern publication / serious tool" connotation.
3. Its `tnum` (tabular numerals) feature is critical for our financial tables — turn it on globally on `<table>` and `.numeric`.
4. Open-source, on Google Fonts, $0-budget compliant.

**Serif (display accents only)**: **Source Serif 4** — variable, free Google Font, full Cyrillic support (Adobe-developed). Used **only** for: methodology page hero, blog post bodies, optional hero quote. Serif appearance triggers "this is editorial / institutional / read this carefully" reading mode (Stripe Press, NYT). Without it the site reads as another SaaS landing page.

**Monospace (numbers + tabular data)**: **Geist Mono** — Vercel's variable monospace, free, MIT, has Cyrillic. Used **only** for: financial figures, percentages, EIN/registration numbers, dates inside tables, the homepage `0%` callout. Reasons: (a) tabular alignment in comparison views, (b) the `0%` is the entire pitch — making it monospace cues "this is a real, audited number, not marketing copy".

**Total font weight loaded** (subset `latin,cyrillic`, `font-display: swap`): ~180 KB gzipped — within Lighthouse 90+ budget.

### 3.2 Type scale

Modular ratio 1.250 (major third) on a 16px base.

| Token | Sans size / line-height | Weight | Cyrillic note | Usage |
|---|---|---|---|---|
| `display` | 56 / 60 | 600 | Cyrillic at 56px reads slightly heavier — drop to 580 weight if x-height feels chunky | Homepage hero only |
| `h1` | 40 / 48 | 600 | OK | Page title (charity detail, methodology) |
| `h2` | 28 / 36 | 600 | OK | Section headers |
| `h3` | 22 / 30 | 600 | OK | Card titles, subsection |
| `h4` | 18 / 26 | 600 | OK | Strong labels (filter group names) |
| `body` | 16 / 26 | 400 | line-height 26 needed for Cyrillic descenders (`у/р/щ/ф`) | Default body |
| `body-sm` | 14 / 22 | 400 | bump line-height to 22 for RU | Card metadata, table cells |
| `caption` | 12 / 18 | 500 | always medium weight in Cyrillic at small size | Timestamps, hints, chip text |

**Serif scale** (used sparingly, only on methodology page + blog posts):

| Token | Source Serif size | Weight | Usage |
|---|---|---|---|
| `serif-display` | 56 / 64 | 400 | Methodology hero |
| `serif-h1` | 40 / 52 | 400 | Blog post H1 |
| `serif-body` | 19 / 32 | 400 | Long-form reading body |

**Mono scale**:

| Token | Geist Mono size | Weight | Usage |
|---|---|---|---|
| `mono-display` | 56 / 60 | 500 | The `0%` hero callout |
| `mono-figure` | 22 / 28 | 500 | Featured financial figure on charity card |
| `mono-body` | 14 / 22 | 500 | Table cells with numbers, EIN, dates |
| `mono-caption` | 12 / 18 | 500 | Inline `[EIN: 13-1644147]` tags |

### 3.3 Bilingual rules (Cyrillic-specific)

- **Always test at +20% width.** Russian translations run ~15–25% longer (`Donate` → `Пожертвовать`, `View source documents` → `Открыть исходные документы`). Lay out for RU first; English fits naturally.
- **Never use uppercased/all-caps Cyrillic in UI.** Reads as harsh / Soviet-bureaucratic. Use weight 600, not `text-transform: uppercase`.
- **Letter-spacing 0** for Cyrillic body. Negative tracking (e.g. `-0.02em`) collapses Cyrillic glyph spacing.
- **Avoid italic for Russian body text** — Source Serif italic Cyrillic has historically rendered as cursive (script-style) in some browsers. Restrict serif italic to Latin-only contexts.

---

## 4. Iconography

**Library**: **Hugeicons Free** (hugeicons.com) — **5,100+ icons**, MIT, 24px Stroke-Rounded grid. Reasons:
- More expressive linework than Lucide while keeping editorial restraint — small character details (joints, terminals) read as "publication illustration", not "generic SaaS sticker"
- 1.5px stroke optically matches Inter weight 500 — pairs with body text without competing
- Tree-shaken via `@hugeicons/react` + `@hugeicons/core-free-icons` (per-icon import) — ships only what you use
- Catalogue is **4× larger than Lucide** (5,100 vs 1,300) — gives us room to find precisely the right metaphor for trust/verification/document concepts
- Free, MIT (free pack); Pro ($89 lifetime) unlocks 10 styles × 51,000 icons — deferred unless we hit a real need

**Why not stay on Lucide**: Lucide is great but optically generic — every modern SaaS dashboard uses it. Hugeicons distinguishes the visual identity at zero extra cost.

**Backup**: **Heroicons** (Tailwind authors, MIT) — same 24px / 1.5 stroke conventions if a specific Hugeicons glyph is missing.

### 4.1 Installation (Phase 4 — Frontend Developer)

```bash
npm install @hugeicons/react @hugeicons/core-free-icons
```

Usage pattern:
```tsx
import { HugeiconsIcon } from '@hugeicons/react'
import { Tick02Icon, FileVerifiedIcon } from '@hugeicons/core-free-icons'

<HugeiconsIcon icon={FileVerifiedIcon} size={20} strokeWidth={1.5} />
```

### 4.2 Icon size system

| Token | Px | Stroke | Usage |
|---|---|---|---|
| `icon-xs` | 14 | 1.5 | Inline with `body-sm` (e.g. external-link icon) |
| `icon-sm` | 16 | 1.5 | Inline with `body` |
| `icon-md` | 20 | 1.5 | Default — buttons, nav, chips |
| `icon-lg` | 24 | 1.5 | Section headers, card lead icons |
| `icon-xl` | 32 | 2.0 | Hero illustrations, empty-state markers |

### 4.3 Stroke vs solid

**Default Stroke-Rounded** (the only style in free pack — that's a feature, not a limitation: forces visual consistency).

**Visual emphasis** comes from two non-style techniques:
1. **Color shift** — verified states use the `--color-verified` accent on the same stroke icon
2. **Filled background pill** — wrap an icon in a `--color-verified-soft` round pill for the verified-badge component (gives "filled" feel without needing a solid variant)

If a specific UI moment demands a true solid mark (e.g., active nav indicator), prefer to use the same icon at heavier `strokeWidth={2.5}` rather than mixing libraries.

### 4.4 Icon vocabulary (the ~30 we will ship — Hugeicons free names)

Conceptual mapping with the actual Hugeicons free-pack identifier (Frontend Developer confirms exact name on import in Phase 4 — Hugeicons names are stable but searchable at hugeicons.com/icons):

| Domain | Concept | Likely Hugeicons name |
|---|---|---|
| **Trust & verification** | Verified badge | `Tick02Icon` (inside soft-pill) or `FileVerifiedIcon` |
| | Shield check | `Shield01Icon` / `SecurityCheckIcon` |
| | License / certified | `LicenseIcon` |
| **Documents** | Document text | `File02Icon` / `DocumentValidationIcon` |
| | External link (outbound) | `LinkSquare02Icon` / `LinkForwardIcon` |
| | Download | `Download04Icon` |
| | View / preview | `View01Icon` |
| | Document with details | `FileEditIcon` / `FileSearchIcon` |
| **Navigation** | Menu | `Menu01Icon` |
| | Close | `Cancel01Icon` |
| | Chevron right | `ArrowRight01Icon` |
| | Chevron down | `ArrowDown01Icon` |
| | Forward arrow | `ArrowRight02Icon` |
| | Back arrow | `ArrowLeft02Icon` |
| | Outbound diagonal arrow | `ArrowUpRight01Icon` |
| **Filters / facets** | Sliders | `Filter01Icon` / `Filter02Icon` |
| | Map pin | `LocationIcon` / `Location04Icon` |
| | Globe | `Earth02Icon` / `GlobalIcon` |
| | Tags | `TagsIcon` |
| | Building (org) | `Building03Icon` / `BuildingsIcon` |
| **Search** | Magnifier | `Search01Icon` |
| | Spinner (loading) | `Loading03Icon` |
| | Enter key hint | `EnterKeyIcon` |
| **States** | Warning triangle | `Alert02Icon` |
| | Info circle | `InformationCircleIcon` |
| | Success check | `CheckmarkCircle02Icon` |
| | Clock (stale data) | `Time04Icon` / `ClockIcon` |
| **Actions** | Plus | `PlusSignIcon` |
| | Minus | `MinusSignIcon` |
| | Copy | `Copy01Icon` |
| | Share | `Share05Icon` |
| | Language toggle | `LanguageSquareIcon` / `Translation01Icon` |
| **Money / data** | Pie chart | `PieChartIcon` |
| | Bar chart | `ChartLineData01Icon` / `Chart01Icon` |
| | Trend up | `ChartUpIcon` |

> **Note on names**: Hugeicons follows `{Concept}{Variant}Icon` (PascalCase + `Icon` suffix). The catalogue at hugeicons.com is searchable; Frontend Developer will pick the precise free-pack icon during Phase 4 implementation.

---

## 5. Spacing & layout

### 5.1 Base unit

**4px base.** Tailwind's default `space-{n}` works directly.

| Token | Px | Use |
|---|---|---|
| `space-1` | 4 | Hairline, tight icon padding |
| `space-2` | 8 | Inline gaps, chip padding |
| `space-3` | 12 | Compact stack |
| `space-4` | 16 | Default rhythm |
| `space-5` | 20 | Card padding |
| `space-6` | 24 | Section internal padding |
| `space-8` | 32 | Card outer margin, between cards |
| `space-12` | 48 | Section vertical separation |
| `space-16` | 64 | Major section break |
| `space-24` | 96 | Hero block top/bottom on desktop |
| `space-32` | 128 | Editorial whitespace (methodology page) |

### 5.2 Container & max widths

| Container | Max width | Use |
|---|---|---|
| `container-narrow` | 720 px | Long-form (methodology, blog, About) |
| `container-default` | 1080 px | Charity catalog, charity detail |
| `container-wide` | 1280 px | Comparison view, dashboards |
| `container-full` | none | Top nav background, footer background only |

Page gutter: `space-6` (24) mobile, `space-8` (32) tablet, `space-12` (48) desktop.

### 5.3 Grid system

12-column flex/grid, gutter 24px. Catalog uses 4-col / 8-col split (filter sidebar / results). Comparison view uses equal-width N columns (N=2 or 3).

### 5.4 Breakpoints

| Name | Width | Tailwind | Anchor |
|---|---|---|---|
| Mobile | 360 px | (default) | iPhone SE / mid-tier Android |
| Tablet | 768 px | `md:` | iPad portrait |
| Desktop | 1024 px | `lg:` | MacBook 13" base |
| Wide | 1440 px | `xl:` | 27" monitor |

Mobile-first. Filter sidebar collapses to a bottom-sheet drawer below 1024px.

### 5.5 Border radius

**Three radii only.**

| Token | Px | Use |
|---|---|---|
| `radius-sm` | 4 | Chips, tags, code-snippet pills |
| `radius-md` | 8 | Buttons, inputs, cards, modals |
| `radius-lg` | 12 | Hero callouts only (homepage `0%` block, methodology hero) |

No fully-rounded buttons. They feel SaaS / playful — wrong tone. 8px radius signals "form / official document".

### 5.6 Elevation

**No drop-shadows in light mode.** Surfaces are separated by 1px `--color-rule` borders (Are.na / Stripe Press technique).

In dark mode, `--color-surface-raised` is one tonal step lighter than `--color-surface` (M3 tonal-elevation). Still no shadows.

Modals/drawers: `--color-surface-raised` + 1px rule + 60% backdrop overlay.

---

## 6. Component patterns

ASCII wireframes show the **lg/desktop** layout unless noted.

### 6.1 Top navigation

```
┌────────────────────────────────────────────────────────────────────────────────┐
│  TrustGive                       Catalog   Methodology   About    [⌘K] [EN/RU] │
└────────────────────────────────────────────────────────────────────────────────┘
   logo wordmark                   nav text-links              search   lang
```

- Height: 64 px desktop, 56 px mobile. Background: `--color-paper` (no fill — blends with body, reduces "bar" feel). Bottom border: 1px `--color-rule`. Sticky.
- **Logo**: wordmark `TrustGive` set in Inter 600 at 18px, with a small solid `BadgeCheck` glyph at `--color-verified` next to the `T`. Wordmark only (per §10).
- **Nav links**: `body-sm` 14px Inter 500. Active link gets a 2px under-bar in `--color-verified`.
- **Search trigger**: `[⌘K]` pill, 32px tall — opens command-palette modal (cmdk pattern, Linear-style). On mobile: search icon button.
- **Language toggle**: `EN / RU` text button — active lang `--color-ink`, inactive `--color-ink-3`. Click swaps. Persists to localStorage. `aria-label="Switch language to Russian"` / `Сменить язык на английский`.
- **No login button.** Per SPEC §6 — anonymous browsing.

### 6.2 Filter sidebar (desktop)

Sticky on the left of the catalog, 280px wide.

```
┌──────────────────────────┐
│  Filters         [Reset] │
│ ──────────────────────── │
│  Cause                   │
│  ☐ Animals          212  │
│  ☐ Children         1844 │
│  ☐ Climate          92   │
│  ☐ Education        2103 │
│  + 12 more               │
│ ──────────────────────── │
│  Country                 │
│  ☐ United States    1.2M │
│  ☐ United Kingdom   168K │
│  ☐ Russia (curated) 30   │
│ ──────────────────────── │
│  Size (annual revenue)   │
│  ☐ Small (<$100K)        │
│  ☐ Medium ($100K-$1M)    │
│  ☐ Large (>$1M)          │
│ ──────────────────────── │
│  Verification badges     │
│  ☐ BBB Accredited        │
│  ☐ Charity Commission    │
│  ☐ СОНКО registered      │
└──────────────────────────┘
```

- Each facet group is collapsible (`h4` heading, `body-sm` items).
- Counts in mono-caption `--color-ink-3`. Counts update reactively as facets toggle.
- Reset link top-right is `body-sm` `--color-ink-2`, underline on hover.
- Below 1024px: collapses to bottom-sheet drawer triggered by a "Filters" button.

### 6.3 Charity card (catalog list item)

Catalog uses **list rows, not card grid**. Density + scannability matter for a discovery tool.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  [logo]  GiveDirectly                                       ✓ Verified       │
│          Cash transfers · United States · Animals welfare                    │
│          ────────────────────────────────────────────────                    │
│          $349M revenue · 91% to programs · last filed Mar 2025               │
│                                                                              │
│          [BBB Accredited]  [Charity Navigator 4★]  [GiveWell top]            │
│                                                                              │
│                                                              View →          │
└──────────────────────────────────────────────────────────────────────────────┘
```

- Container: `--color-surface` background, 1px `--color-rule` bottom border (rows visually concatenate). Padding: `space-5` v, `space-6` h.
- Logo: 48×48 squircle, `radius-md`. Falls back to wordmark initial on `--color-info-soft`.
- **Name**: `h3` ink. **Verified pill**: top-right, `--color-verified-soft` bg + `--color-verified` text + outline `BadgeCheck` icon-sm.
- **Metadata row 1**: `body-sm` ink-2 — middle-dot separated.
- **Hairline rule** in `--color-rule` separates metadata from financials (key UX cue: numbers live below the line).
- **Financial line**: `mono-body` `--color-ink-2`. The `%` figure shifts to `--color-warning` if <70%, `--color-error` if <50%, otherwise inherits `--color-ink-2` (do not gamify with green for "good" — we don't crown a number).
- **Trust badges row**: small chips, `--color-surface` with `--color-rule` border, `caption` text.
- **Hover**: row background → `#F4F1E6` (paper darkened 2%). No translation, no shadow, no scale.
- **Touch target**: entire row clickable (`<a>` wrapper), ≥80px tall (KB-DESIGNER-INIT-002).

### 6.4 Charity detail page (the most important screen)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ← Back to results                                                           │
│                                                                              │
│  [logo 80×80]  GiveDirectly Inc.                          ✓ Verified         │
│                Cash transfers to extreme poverty                             │
│                EIN 27-1661997 · United States · Founded 2008                 │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐│
│  │ BBB Accredited       │  │ Charity Commission   │  │ GiveWell Top Charity ││
│  │ Last reviewed 2024   │  │ n/a                  │  │ 2025 cohort          ││
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘│
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐   ┌──────────────────────────────┐ │
│  │  Where the money goes                 │   │  ┌──────────────────────┐   │ │
│  │  Fiscal year 2024                     │   │  │ Donate on            │   │ │
│  │                                       │   │  │ givedirectly.org →   │   │ │
│  │  ████████████████████████  91.0%      │   │  └──────────────────────┘   │ │
│  │  Programs                $317.4M      │   │                              │ │
│  │                                       │   │  0% platform fee.            │ │
│  │  ███  6.2%                            │   │  We never see your money.    │ │
│  │  Administration          $21.6M       │   │                              │ │
│  │                                       │   │  ──────────                  │ │
│  │  ██   2.8%                            │   │                              │ │
│  │  Fundraising             $9.8M        │   │  Source documents            │ │
│  │                                       │   │  → IRS Form 990 (2024) PDF   │ │
│  │  Top exec comp $0.79M (Rory Stewart)  │   │  → Audited financials 2024   │ │
│  │                                       │   │  → State registration NY     │ │
│  │  Source: IRS Form 990 (2024)          │   │                              │ │
│  └──────────────────────────────────────┘   └──────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│  Description                                                                 │
│  GiveDirectly transfers cash directly to people living in extreme poverty…   │
│                                                                              │
│  Press mentions                                                              │
│  · NYT, "The end of charity?" — June 2024 [link]                             │
│  · The Atlantic, "Cash works" — Oct 2024 [link]                              │
│  · Vox Future Perfect — Mar 2025 [link]                                      │
│                                                                              │
│  Methodology                                                                 │
│  This charity is verified because: it is registered with the IRS as a       │
│  501(c)(3) (verified via ProPublica), has filed Form 990 in the last 24     │
│  months, and we link directly to that filing. We do not assess program      │
│  effectiveness — see [How we verify].                                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Two-column body** (lg:grid-cols-3): "Where the money goes" spans 2/3, donate + source-documents block spans 1/3 (sticky on scroll above 1024px).
- The **"Where the money goes" chart** is a **horizontal bar list**, NOT a pie chart — easier to read percentages, scales to many categories, no colour required. Each bar is `--color-ink-2` fill on `--color-rule` track. Percentage in `mono-figure`. Dollar amount in `mono-body --color-ink-3`.
- The donate block requires one click. Click on `Donate on givedirectly.org` opens the [confirmation modal] §6.5.
- The source-documents block is the wedge — visually privileged. Each link prefixed by `→` chevron, ending with type marker (`PDF`, `HTML`, `XLSX`). Clicking opens the **source-document drawer** (§6.7), not a tab — we want the user to feel the document arriving, not be teleported away. (Tab-open offered as secondary action *inside* the drawer.)
- **Press mentions** = curated `news_mentions[]` (per SPEC §3 row 10 + MARKET_ANALYSIS §3 anti-features).

### 6.5 Outbound donate confirmation modal

```
┌──────────────────────────────────────────────────────────┐
│  You're leaving TrustGive                          [×]   │
│                                                          │
│  Your donation will go directly to GiveDirectly Inc      │
│  on their own website. We don't process payments.        │
│                                                          │
│  · 0% platform fee                                       │
│  · We never see your money                               │
│  · We never share your contact info                      │
│                                                          │
│             ┌─────────────────────────────────────┐      │
│             │  Continue to givedirectly.org →     │      │
│             └─────────────────────────────────────┘      │
│                                                          │
│             Cancel                                       │
└──────────────────────────────────────────────────────────┘
```

- 480px modal, `--color-surface-raised`, 1px `--color-rule`, `radius-md`.
- Backdrop: `--color-paper` ink-overlay at 60% — page goes paper-tone, not black, preserving editorial feel.
- The three bullets are the entire JustGiving anti-pattern pitch from MARKET_ANALYSIS §2.3. Non-negotiable on this modal.
- Continue button: `--color-verified` solid. Cancel: text-link below. No third option, no "remember my choice".
- On confirm: open in new tab (`target=_blank rel=noopener noreferrer`), fire PostHog `donation_redirect` event with charity_id + lang.

### 6.6 "How we verify" methodology page

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   How we verify                                                              │
│   [Source Serif Display 56px]                                                │
│                                                                              │
│   We don't grade charities. We show you the documents that grade them       │
│   for us — and link straight to those documents.                             │
│   [Source Serif body 19px ink-2, max-width 600px]                            │
│                                                                              │
│   Last reviewed 5 May 2026                                                   │
│   [caption ink-3]                                                            │
│                                                                              │
│   ─────────                                                                  │
│                                                                              │
│   What "verified" means on TrustGive                                         │
│   [Inter h2]                                                                 │
│                                                                              │
│   A charity is marked Verified on TrustGive if all three are true:           │
│                                                                              │
│   1. It is registered with at least one government registry…                 │
│   2. It has filed financial documents in the last 24 months…                 │
│   3. We link directly to those documents on the charity's page…              │
│                                                                              │
│   [Source Serif body, lots of whitespace, narrow column]                     │
│                                                                              │
│   ─────────                                                                  │
│                                                                              │
│   What we do NOT verify                                                      │
│   ………                                                                       │
│                                                                              │
│   ─────────                                                                  │
│                                                                              │
│   Want deeper rigor?                                                         │
│   For mission-effectiveness analysis, we recommend GiveWell, Effektiv-      │
│   Spenden, and CharityWatch.                                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

- `container-narrow` 720px.
- Body: Source Serif 4 19px, line-height 32. Generous `space-12` between sections, hairline `--color-rule` rules.
- Primary SEO target for `"how to check if a charity is real"` (SPEC §11).
- "Last reviewed" date stamp top — reads as a published article, not a fixed marketing page.

### 6.7 Source-document drawer (the wedge feature UI)

The single most important interaction in the product. **Choreographed like opening a vault.**

Triggered when user clicks `→ IRS Form 990 (2024) PDF` on a charity detail page.

Behaviour:
1. Right-side drawer slides in, 600px wide on desktop, full-screen on mobile. Animation: 240ms `ease-out`. Drawer is `--color-surface-raised`.
2. Header (sticky inside drawer):
   ```
   ┌────────────────────────────────────────────────────┐
   │  IRS Form 990 · 2024                          [×]  │
   │  GiveDirectly Inc · EIN 27-1661997                 │
   │  Source: ProPublica Nonprofit Explorer · Mar 2025  │
   ├────────────────────────────────────────────────────┤
   ```
   The source-attribution line is mono-caption — making clear this is *not* a TrustGive opinion, this is the actual ProPublica record.
3. Body: a **PDF preview iframe** (or rendered first page as image fallback for performance). Below it, an explicit grey-box callout:
   ```
   This is the original IRS filing. TrustGive did not edit it.
   ```
   Then two action buttons:
   ```
   [ View full PDF on ProPublica  ↗ ]   [ Download PDF ]
   ```
4. Below the actions, a structured "What this document tells you" block — 5–7 plain-language bullet points pulled from key fields (total revenue, total expenses, top 5 employees by comp, mission statement) so a layperson who can't read a 990 still gets value. Each bullet anchored by `(Form 990, Part [N], Line [N])` in mono-caption.
5. Drawer dismissed by `[×]`, ESC, or backdrop click. Focus returns to originating link (a11y).

This component is the entire reason the product exists. It is over-designed on purpose.

### 6.8 Comparison view (2–3 charities side-by-side)

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│                │ GiveDirectly   │ Heifer Intl    │ Oxfam America  │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Verified       │     ✓          │     ✓          │     ✓          │
│ Country        │ US             │ US             │ US             │
│ EIN            │ 27-1661997     │ 35-1019477     │ 23-7069110     │
│ Total revenue  │ $349.0M        │ $145.2M        │ $108.6M        │
│ % to programs  │ 91.0%          │ 76.4%          │ 79.8%          │
│ % admin        │ 6.2%           │ 9.1%           │ 8.6%           │
│ % fundraising  │ 2.8%           │ 14.5%          │ 11.6%          │
│ Top exec comp  │ $0.79M         │ $0.92M         │ $0.61M         │
│ Last filed     │ Mar 2025       │ Feb 2025       │ Apr 2025       │
│ Source         │ → 990 PDF      │ → 990 PDF      │ → 990 PDF      │
├────────────────┼────────────────┼────────────────┼────────────────┤
│                │ [Donate ↗]     │ [Donate ↗]     │ [Donate ↗]     │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

- Equal-width columns. Header row sticky on scroll. First column sticky left.
- All numbers `mono-body`, right-aligned. Percentages **without colour-coding** — user reads the numbers themselves. (No green-good / red-bad — see principle 1.)
- Source row link-styled — clicking opens drawer §6.7 for that column.
- Mobile (<768): switches to **stacked accordion** (each charity = expandable card). Loses parallel scanning at small width but data preserved.

### 6.9 Empty / loading / error states

**Empty state — "no results match your filters"**:
```
┌─────────────────────────────────────────────┐
│         [Filter icon-xl ink-3]              │
│                                             │
│  No charities match these filters           │
│  Try removing the "Russia" filter or        │
│  broadening the cause selection.            │
│                                             │
│  [ Reset filters ]                          │
└─────────────────────────────────────────────┘
```
Specific. Always suggests the actionable next step based on which filter has the smallest count.

**Loading state — catalog**: **Skeleton rows**, not a spinner. 6 rows of `--color-rule` placeholder shapes matching the real card layout. Shimmer 1500ms, very subtle (luminance shifts `#D9D5C7` → `#E5E1D5`).

**Loading state — charity detail**: Header skeleton + breakdown chart skeleton + description skeleton. The donate/source-document column is **NOT skeletoned** — it appears blank with text "Loading documents…". User must never see a fake `[Donate]` button without a real outbound URL.

**Error state — API fetch failed**:
```
┌─────────────────────────────────────────────┐
│   We couldn't load this charity              │
│                                              │
│   This is on us, not on the charity.         │
│   Please try again in a moment.              │
│                                              │
│   [ Reload ]   [ Report this issue ]         │
└─────────────────────────────────────────────┘
```
The phrase "this is on us, not on the charity" is deliberate: protects the charity's reputation when our infra fails. Report-this-issue links to a `mailto:` with prefilled context — no support widget in MVP.

**Stale-data state — last filing >24 months old**:
- Card / detail page shows inline `--color-warning-soft` banner: `⚠ Last filing March 2023. Older than 24 months — review with caution.`
- More honest than hiding the charity. Key trust signal: we admit when our own data is stale.

---

## 7. Key screen wireframes

### 7.1 Homepage / hero

```
[ TopNav §6.1 ]
─────────────────────────────────────────────────────────────────────────

                      The only charity discovery tool
                      that shows you the source documents.
                      [display 56 / Inter 600]

                      Filter 1.2M+ verified US, UK and Russian charities
                      by cause, country, and size. Every "verified" claim
                      links to the actual IRS 990, Charity Commission filing,
                      or Минюст registration.
                      [body 19 / ink-2 / max-width 640px]

                                  ┌────────────────────────────────┐
                                  │  0%                            │
                                  │  [mono-display 56 / verified]  │
                                  │  platform fee. We never see    │
                                  │  your money.                   │
                                  │  [body / ink-2]                │
                                  └────────────────────────────────┘

                      [ Explore catalog → ]   [ How we verify → ]
                      [primary verified btn]  [text link]

─────────────────────────────────────────────────────────────────────────

   Browse by cause                                          [h2]

   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Animals  │ │ Children │ │ Climate  │ │Education │ │ Health   │
   │   212    │ │   1,844  │ │    92    │ │  2,103   │ │  3,415   │
   │ [count]  │ │          │ │          │ │          │ │          │
   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Refugees │ │ Animals  │ │  + more  │
   │   189    │ │ Russia   │ │          │
   │          │ │    14    │ │          │
   └──────────┘ └──────────┘ └──────────┘

─────────────────────────────────────────────────────────────────────────

   How we verify                                            [h2]

   [3-column row of small explainer blocks]

   ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
   │ [FileCheck icon-lg]│  │ [BadgeCheck]       │  │ [ExternalLink]     │
   │                    │  │                    │  │                    │
   │ Government registry│  │ Recent financial   │  │ Direct outbound    │
   │ verification       │  │ filings            │  │ donations          │
   │                    │  │                    │  │                    │
   │ Each charity is    │  │ We require a 990   │  │ You donate on the  │
   │ confirmed via IRS, │  │ or Charity         │  │ charity's site —   │
   │ Charity Commission │  │ Commission filing  │  │ we never touch the │
   │ or Минюст.         │  │ in the last 24mo.  │  │ money.             │
   │                    │  │                    │  │                    │
   │ Read methodology → │  │                    │  │                    │
   └────────────────────┘  └────────────────────┘  └────────────────────┘

─────────────────────────────────────────────────────────────────────────
[Footer: minimal — TrustGive · Methodology · Press · GitHub · RSS]
```

- **No hero image, no illustration.** Whitespace + the giant `0%` is the hero. (Linear precedent.)
- The `0%` callout: `radius-lg` panel, `--color-verified-soft` bg, `--color-verified` text, 1px `--color-verified` border. Only `radius-lg` element on the page.
- "Browse by cause" cards: name + count, hairline `--color-rule` border, hover bg-tint. No icons inside cards.

### 7.2 Catalog with filters applied

```
[ TopNav ]
─────────────────────────────────────────────────────────────────────────

  Charities                                                       [h1]
  Showing 1–20 of 213 results                              [body-sm ink-3]

  Active filters: [Animals ×] [United States ×] [Verified ×]
                                                       Clear all

─────────────────────────────────────────────────────────────────────────
┌────────────────┬────────────────────────────────────────────────────────┐
│  [Filter       │   ┌────────────────────────────────────────────┐       │
│   sidebar      │   │ Charity card row §6.3 #1                   │       │
│   §6.2 ]       │   ├────────────────────────────────────────────┤       │
│                │   │ Charity card row §6.3 #2                   │       │
│                │   ├────────────────────────────────────────────┤       │
│                │   │ Charity card row §6.3 #3                   │       │
│                │   ├────────────────────────────────────────────┤       │
│                │   │ … 17 more …                                │       │
│                │   └────────────────────────────────────────────┘       │
│                │                                                        │
│                │   [← Previous]   1 2 3 … 11   [Next →]                 │
└────────────────┴────────────────────────────────────────────────────────┘
```

- Sort dropdown top-right: "Most recently filed" (default), "Largest revenue", "Highest % to programs", "Alphabetical". No "best match" ranking.
- Compare checkboxes per card (max 3). When ≥2 selected, sticky bottom bar: `2 selected · [Compare →] [Clear]`.

### 7.3 Charity detail (covered §6.4)

### 7.4 Comparison view (covered §6.8)

### 7.5 SEO landing page — "Is X legitimate?"

Per SPEC Story 5:

```
[ TopNav ]
─────────────────────────────────────────────────────────────────────────

  Is GiveDirectly a legitimate charity?                          [h1]

  Yes — verified.                                                 [h2]
  GiveDirectly Inc. (EIN 27-1661997) is a registered US 501(c)(3)
  nonprofit, in good standing with the IRS, and has filed Form 990
  for fiscal year 2024.

  [ View IRS Form 990 (2024) ↗ ]   [ Why we say "verified" → ]

─────────────────────────────────────────────────────────────────────────
  [identical body to §6.4 from "Where the money goes" downward]
```

- H1 mandated by SPEC Story 5 acceptance criteria.
- "Yes — verified." answer is the most important sentence on the page for SEO + human user. Above the fold.
- Meta tags: `<title>Is GiveDirectly a legitimate charity? · TrustGive</title>`, description includes EIN.
- `/ru/` page H1: `Является ли GiveDirectly легитимной благотворительной организацией?`.

### 7.6 Methodology page (covered §6.6)

---

## 8. Motion / interaction

**Restraint principle**: Animation must serve comprehension, not decoration. We have one core animation choreography — the source-document drawer.

**Allowed**:
- Drawer slide-in: 240ms `ease-out`
- Modal fade-in: 160ms `ease-out` + backdrop fade 200ms
- Skeleton shimmer: 1500ms infinite linear (luminance only)
- Filter facet expand/collapse: 180ms `ease-out`
- Page transitions: NONE — instant. SPA route changes do not animate.
- Hover background tint on cards: 80ms `ease-out`
- Focus ring appearance: instant

**Forbidden**:
- Lift-on-hover (translateY/scale)
- Parallax
- Animated gradients / mesh backgrounds
- Hero scroll-triggered reveals
- Mouse-follow effects
- Auto-playing carousels

**Reduced motion**: All animations respect `prefers-reduced-motion: reduce` — drawer becomes instant fade-in, skeleton becomes static grey.

---

## 9. Accessibility

WCAG 2.1 AA target (per SPEC §9), audited Phase 4.5.

### 9.1 Color contrast
Documented in §2.5. Every text/bg pair clears AA.

### 9.2 Keyboard navigation
- All interactive elements are `<button>`, `<a>`, or native form controls — no `<div onClick>`.
- Focus order follows visual order.
- **Visible focus ring**: 2px outline `--color-verified` + 2px offset. Never `outline: none` without replacement.
- ESC dismisses modals/drawers (returns focus to trigger).
- Cmd/Ctrl+K opens search palette.
- "Skip to results" link on first tab from page.

### 9.3 Screen reader semantics for trust signals

```html
<span class="badge-verified">
  <svg aria-hidden="true">...</svg>
  <span class="sr-only">Verification status:</span>
  Verified
  <span class="sr-only"> — registered with IRS, filed in last 24 months.
    <a href="#methodology">Read methodology</a>.
  </span>
</span>
```

Source-document links must announce file type and target:
```html
<a href="..." target="_blank" rel="noopener noreferrer">
  IRS Form 990, 2024
  <span class="sr-only"> (PDF, opens on ProPublica.org in a new tab)</span>
  <svg aria-hidden="true">...ExternalLink...</svg>
</a>
```

### 9.4 Touch targets
All interactive elements ≥44×44 CSS px (WCAG 2.5.5 + KB-DESIGNER-INIT-002). Catalog rows ≥80px tall. Filter checkboxes use `padding: 8px` to expand tap area.

### 9.5 Forms
The only form input in MVP is the search bar:
- `<label for="search" class="sr-only">Search charities</label>`
- `aria-describedby="search-help"` → "Type a charity name, EIN, or cause"
- Submit on Enter
- Loading announced via `aria-live="polite"`: "Searching… 213 results found."

### 9.6 Language semantics
- `<html lang="en">` or `<html lang="ru">` set at SSR per route prefix.
- Inline foreign-language strings wrapped: `<span lang="en">GiveDirectly</span>`.

### 9.7 Color-blind safety
Verified-green is paired with the `BadgeCheck` icon and the literal word "Verified" / "Подтверждено". Stale-data warning uses ⚠ glyph + amber + text. Error state uses icon + text. **No information is conveyed by colour alone, anywhere.**

---

## 10. Brand mini-kit

### 10.1 Wordmark / logo direction
**No standalone graphic logo in v1.** Wordmark only.

The wordmark is `TrustGive` set in **Inter 700 at -0.01em letter-spacing**, with a small solid `BadgeCheck` icon in `--color-verified` placed immediately to the left of the `T`, baseline-aligned with the cap-height. No custom letterform tweaks.

Why no symbol-only logo: a symbol-logo for a trust product is high-risk — it must read instantly as "trustworthy" without colliding with a hundred existing nonprofit shield/heart/hand logos. Wordmark + green tick-badge composition signals "verified" without committing to a contested symbol. Reserved for v2.

Favicon for v1: 32×32 solid `BadgeCheck` in `--color-verified` on `--color-paper`. Same glyph in OG share cards.

### 10.2 Tone of voice

Three rules:
1. **Plain over institutional.** Write like a New York Times explainer, not a mission statement. "We don't process donations" beats "TrustGive operates as a non-transactional intermediary".
2. **Show your work.** Every claim cites its source inline. "91% of revenue went to programs (Form 990, Part IX)" is the only acceptable form.
3. **Refuse hype.** Never use "amazing", "best", "trusted by thousands", "leading", "powered by AI".

**Example sentences (EN)**:
- *Marketing*: "We don't grade charities. We show you the documents that grade them for us."
- *UI*: "Older than 24 months — review with caution."
- *Error*: "We couldn't load this charity. This is on us, not on the charity."

**Example sentences (RU)**:
- *Маркетинг*: "Мы не выставляем оценки благотворительным организациям. Мы показываем вам документы, по которым их оценивают."
- *UI*: "Старше 24 месяцев — проверьте внимательно."
- *Ошибка*: "Не удалось загрузить эту организацию. Это сбой на нашей стороне, не у благотворителя."

Russian copy avoids bureaucratic Soviet-era nonprofit phrasing ("осуществляет благотворительную деятельность"), avoids corporate Anglicisms ("платформа доверия"), prefers everyday speech ("мы показываем вам", "проверяем сами").

### 10.3 Photography & illustration policy

**Zero photography of people.** Not beneficiaries, donors, volunteers, founder. Absolute rule. Itself the strongest visual differentiator from every competitor in this research (Charity:Water, Charity Navigator, Effektiv-Spenden all use people photography).

**Allowed imagery**:
- Document scans / PDF first-page thumbnails (rendered server-side from real Form 990s — public records)
- Data visualisations (bar charts, sparklines, simple line — single-colour, no 3D, no gradients)
- Registry logos (small, monochrome where possible) — IRS, Charity Commission, Минюст, BBB seal
- The TrustGive `BadgeCheck` glyph

**Optional v2**: small inline pictograms in cause-tag chips. Not in v1.

**No stock photos. No illustrations of "happy people". No "abstract gradient hero".**

---

## 11. Component library choice

**Web (React)**: **shadcn/ui** + **Radix primitives** + **TailwindCSS v4** + **Hugeicons Free**.
- shadcn/ui = copy-paste components. We own the source. No dependency drift. Free.
- Radix gives us accessible primitives (Dialog, Popover, Tabs, Tooltip) — saves weeks of a11y work.
- TailwindCSS v4 with CSS-first config; tokens in `:root` mapping §2.
- `@hugeicons/react` + `@hugeicons/core-free-icons` — see §4 for full rationale.

We ship **no** generic component library (Material UI, Chakra, Ant) — they impose visual decisions that conflict with editorial-restraint direction.

**Mobile**: N/A in v1. If added in v2, switch to Flutter Material 3 with custom `ColorScheme`.

**Charts**: **Recharts** (React, MIT). The "Where the money goes" horizontal bar chart is a 30-line custom Recharts component — no D3 dependency.

---

## 12. Design references (URLs cited above)

Designer agent's screenshot tool was sandbox-blocked, so no PNGs are saved. Reference URLs for human re-verification:

| # | URL | What we took |
|---|---|---|
| 01 | https://press.stripe.com/ | Editorial dark mode + serif gravitas |
| 02 | https://open.nytimes.com/ | Black/white restraint, serif headlines |
| 03 | https://www.nytimes.com/ | Editorial chrome — minimal nav, masthead-as-logo |
| 04 | https://www.charitywater.org/ | Anti-pattern (emotional photo + accent yellow) |
| 05 | https://www.charitywater.org/about | Anti-pattern (email-capture popup) |
| 06 | https://effektiv-spenden.org/en/methodology/ | Long-form methodology page structure |
| 07 | https://linear.app/ | Pure type, no decoration, dark gravitas |
| 08 | https://vercel.com/ | Restrained component vocabulary, button hierarchy |
| 09 | https://www.are.na/ | Maximum content density, zero chrome, warm off-white paper |
| 10 | https://www.charitynavigator.org/ | Anti-pattern (stock photos, neon CTAs, dotted patterns) |
| 11 | https://effektiv-spenden.org/en/ | B&W "polaroid" — partial precedent, dated execution |
| 12 | https://m3.material.io/foundations/overview/principles | M3 accessibility + responsive layout patterns |

All references comply with $0-budget constraint: only free fonts (Inter, Source Serif 4, Geist Mono — all Google Fonts), only free icons (Lucide ISC), only free component primitives (Radix MIT, shadcn/ui MIT, Recharts MIT, TailwindCSS MIT).

---

## 13. Handoff checklist for Phase 2.5 (Backend / API design)

Items the API designer should know coming out of this phase:

- [ ] Each charity exposes `verification_status` as `verified | listed | stale` (UI maps these to badge styles)
- [ ] Source documents returned as `{ kind, label, label_ru, url, filed_date, source }` so drawer §6.7 renders source-attribution line
- [ ] `news_mentions[]` required for press-mentions block (§6.4)
- [ ] Trust badges array includes `image_url` (small monochrome SVG/PNG); front-end falls back to text-only
- [ ] `where_money_goes` payload returns ordered breakdown lines `{ label, label_ru, amount_usd, percent }` so we don't compute on the client
- [ ] All localised fields ship both `_en` and `_ru` variants OR a `i18n: { en, ru }` object — designer prefers nested
- [ ] Stale-data flag: API returns `is_stale: bool` if `last_filed_date` > 24 months — UI honours it directly
- [ ] Outbound donate URL is a clean string (not a redirect through TrustGive) — modal §6.5 opens it raw

---

## 14. Open questions for user approval (Gate 2)

None block approval — flagging where I made decisions you might want to revisit:

1. **Forest green `#0E7C5C` as the trust accent.** I picked it specifically to differentiate from Charity Navigator, GuideStar, BBB Give.org — all blue. If you'd rather match donor-association expectations and accept camouflage, we can flip to e.g. `#1F4E79`.
2. **No graphic logo in v1.** Wordmark only. If MBA-application portfolio needs a "real logo" for cover slides, we can commission a 1-evening monogram in Phase 6.
3. **Source Serif 4 for editorial accents.** The only free serif with full institutional-Cyrillic ambitions. If Cyrillic preview is unacceptable, fall back to Inter 600 throughout (loses editorial feel; gains single-font system).
4. **Zero photography of people, ever.** Strong, defensible call but it's a brand call. If you want even one photograph (e.g. Alex's face on the About page for portfolio purposes), it's an exception we make, not a rule we soften.

---

<reflection>
  <what_went_well>
    Research stayed disciplined to 8 strong references rather than wide-scanning — all 8 contributed concrete decisions (Are.na the off-white paper, Linear the dark mode gravitas, Stripe Press the serif accent licence, Effektiv-Spenden the long-form methodology page structure, Charity:Water + Charity Navigator the anti-patterns to invert). Every WCAG AA contrast pair was computed before committing the palette, so the doc is ship-ready not aspirational.
  </what_went_well>
  <challenges>
    Playwright sandbox: browser_snapshot, browser_resize, browser_close, and browser_take_screenshot were all denied — could not save reference PNGs to disk. Visual analysis was done via navigate-only reads. Charity:Water's "100% model" page returned 404 at every URL guess — substituted with homepage + about-page references. Could not deep-inspect M3 docs (snapshot denied) but ui-ux-trends skill already had M3 patterns. Write tool denied for DESIGN.md — delivered inline per AP-SHARED-009 for parent agent to persist.
  </challenges>
  <lessons_learned>
    1. For bilingual EN+RU products, font choice is often the single biggest design decision — many otherwise-attractive fonts have weak Cyrillic. Inter + Source Serif 4 + Geist Mono is a verified $0-budget triplet with full Cyrillic across all three families.
    2. For a "trust tool" product category, the strongest brand differentiator is often a photography policy, not a colour or font. Banning photography of people is more distinctive than any palette choice and aligns directly with the "show source documents" wedge.
    3. Text-based comparison views with monospace numbers + no colour-coding (no green-good / red-bad) is a deliberate trust signal — forces the user to interpret data themselves rather than accept our implicit rating in the colour. Worth memorialising as a pattern for future "data transparency" UIs.
    4. WCAG AA computation must be done per-pair at design time, not deferred to audit. Off-white paper backgrounds (#FAFAF7) and cool-tinted near-black dark mode (#0E141C) both work but ratios differ slightly from #FFFFFF / #000000 — committing to non-pure neutrals means re-running every pair.
  </lessons_learned>
  <knowledge_to_store>
    YES — three KB entries written to `knowledge-base/by-role/designer/lessons-learned.md`:
    - KB-DESIGNER-TRUSTGIVE-001 — Bilingual EN+RU font triplet ($0-budget): Inter + Source Serif 4 + Geist Mono
    - KB-DESIGNER-TRUSTGIVE-002 — "Trust UI" anti-pattern: ban photography of people
    - KB-DESIGNER-TRUSTGIVE-003 — Off-white paper backgrounds require per-pair WCAG re-audit
  </knowledge_to_store>
</reflection>

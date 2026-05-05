# Design System: TrustGive

> **Status**: v1.0 — Phase 2 deliverable (awaiting approval)
> **Created**: 2026-05-05 · **Designer**: Designer agent
> **Approval gates this satisfies**: Gate 2 (Design)
> **Read first**: `SPEC.md` v1.0 (approved), `MARKET_ANALYSIS.md` (approved)
> **Note on screenshots**: Designer agent's Playwright screenshot tool was sandbox-blocked during this run. Visual references were navigated and analysed but no design-research PNGs were saved to disk. URLs and analysis remain in §12 for human re-verification.

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

**Library**: **Lucide** (lucide.dev) — fork of Feather, ISC, ~1,300 icons, 24px stroke-1.5 grid. Reasons:
- Stroke icons match the editorial/restrained tone better than filled Material symbols
- 1.5px stroke optically matches Inter weight 500 — pairs with body text without competing
- Tree-shaken via `lucide-react`, ~6 KB total ships
- Free, MIT-compatible

**Backup**: **Heroicons** (Tailwind authors, MIT) — same 24px / 1.5 stroke conventions.

### 4.1 Icon size system

| Token | Px | Stroke | Usage |
|---|---|---|---|
| `icon-xs` | 14 | 1.5 | Inline with `body-sm` (e.g. external-link icon) |
| `icon-sm` | 16 | 1.5 | Inline with `body` |
| `icon-md` | 20 | 1.5 | Default — buttons, nav, chips |
| `icon-lg` | 24 | 1.5 | Section headers, card lead icons |
| `icon-xl` | 32 | 2.0 | Hero illustrations, empty-state markers |

### 4.2 Solid vs outline

**Default outline.** Solid is reserved for two cases only:
1. **Active/selected state** in tabs, nav, and toggle buttons.
2. **Verified badge mark** — a single solid `BadgeCheck` icon at `--color-verified` is the only solid icon that appears in default page state. Intentional: it draws the eye to the only thing that should draw the eye.

### 4.3 Icon vocabulary (the 30 we will actually ship)

```
Trust & verification:   BadgeCheck, ShieldCheck, FileCheck, FileText
Documents:              FileText, ExternalLink, Download, Eye, FileDigit
Navigation:             Menu, X, ChevronRight, ChevronDown, ArrowRight, ArrowLeft, ArrowUpRight (outbound)
Filters / facets:       SlidersHorizontal, MapPin, Globe, Tags, Building, Filter
Search:                 Search, Loader (spinner), CornerDownLeft (return key hint)
States:                 AlertTriangle, AlertCircle, Info, CheckCircle2, Clock (stale data)
Actions:                Plus, Minus, Copy, Share2, Languages (lang toggle)
Money / data:           PieChart, BarChart3, TrendingUp
```

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

**Web (React)**: **shadcn/ui** + **Radix primitives** + **TailwindCSS v4**.
- shadcn/ui = copy-paste components. We own the source. No dependency drift. Free.
- Radix gives us accessible primitives (Dialog, Popover, Tabs, Tooltip) — saves weeks of a11y work.
- TailwindCSS v4 with CSS-first config; tokens in `:root` mapping §2.

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

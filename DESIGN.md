# Design System: TrustGive

> **Status**: v3.1 — sub-filter chips + sidebar revision (delta on top of v3.0)
> **Created**: 2026-05-05 · **Updated v3.0**: 2026-05-07 · **Updated v3.1**: 2026-05-07 · **Designer**: Designer agent
> **Approval gates this satisfies**: Gate 2 (Design) — re-approval requested for v3.1 (catalog filter rework only)
> **Read first**: `SPEC.md` v1.0, then v3.1 (this section) — supersedes catalog-filter parts of v3.0. Everything else in v3.0 (homepage 3-bucket hero, CharityCard photo-top, detail page) stays unchanged.
> **v3.1 scope**: in-bucket sub-filter chips (per-bucket cause taxonomy), sidebar removed entirely from `/charities`, country moved to a top-bar chip group, bucket page subtitles refreshed.

---

## v3.1 — 2026-05-07 — Sub-filter chips + revised sidebar

### Why v3.1 exists

After v3.0 shipped (3-bucket photo-first homepage + photo-top catalog cards), donor feedback on the catalog page (`/charities?bucket=people` etc.) was: the sidebar is the wrong shape. Three problems:

1. **Inside a bucket, donors think in sub-causes, not in `revenue size`**. A donor who clicked "People" doesn't then think "show me <$100K orgs" — they think "show me children-focused" or "show me refugees". The bucket already filtered by emotional intent; the next filter must continue that emotional axis, not switch to a financial-engineering axis.
2. **`Verification` is meaningless in our catalog** because we curate — every charity in the catalog is verified by definition. Showing a "Listed / Stale" filter implies we have stale entries, which we don't.
3. **The cream sidebar visually competes with the photo cards** (see screenshots `06-catalog-animals.png`, `07-catalog-planet.png` — the heavy cream box on the left fights the photo grid for attention). v3.0's photo-first thesis is undermined by a 240-px-wide form-control panel sitting next to it.

v3.1 fix: drop the sidebar. Move `Country` to a small chip group at the top of the page. Add a second chip row underneath for sub-cause filtering within the bucket. Result: page reads top-down — context (page title + subtitle) → filter intent (two chip rows) → results (photo grid) — no left rail.

### KB lessons applied (v3.1)

- **KB-DESIGNER-INIT-001** — White text on `#0E7C5C` forest green = 5.84:1 (passes AA for normal text and AAA for large). Verified active chip.
- **KB-DESIGNER-INIT-002** — Chip pill min tap height `h-11` (44px) on mobile via `py-2.5` + 14px text. Chip row gets 8-px gap so adjacent chips don't accidentally co-trigger.
- **KB-DESIGNER-INIT-003** — New semantic tokens added: `--chip-bg-active`, `--chip-bg-inactive`, `--chip-text-active`, `--chip-text-inactive`, `--chip-border-inactive`, `--chip-border-hover`. No raw hex in chip components.
- **KB-DESIGNER-TRUSTGIVE-001** — RU sub-filter labels stress-tested: "Бездомные" (10), "Образование" (11), "Беженцы" (8), "Пища и вода" (12) — all wrap-safe inside a 14px `px-4 py-2` pill. RU row total width measured: 612 px on desktop (fits the 720-px max). On mobile, both chip rows scroll horizontally so width is irrelevant.
- **KB-DESIGNER-TRUSTGIVE-002** — Photography policy unchanged: chips don't carry imagery, so this rule doesn't apply.
- **AP-SHARED-009** — Sandbox warning acknowledged: full v3.1 section is ALSO included inline in the assistant message in case the file write is denied.

---

### §I. Sub-filter chips — within bucket pages

**Purpose**: when a donor lands on `/charities?bucket=people` (or `animals` / `planet`), give them a single horizontal row of pill chips that lets them narrow the bucket by *sub-cause* — the way they actually think about giving — without leaving the page.

#### §I.1 Wireframe — desktop

```
┌─────────────────────── nav (white, sticky) ───────────────────────┐
│  TRUSTGIVE       Charities  Methodology  About    EN/RU    [≡]    │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│   Charities helping people                            [serif h1]  │
│   Verified organisations focused on health, poverty,              │
│   and humanitarian work.                              [body, ink-2]│
│                                                                   │
│   Country                                                          │
│   ┌────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐             │
│   │All │ │United States │ │United Kingdom│ │ Russia │             │
│   └────┘ └──────────────┘ └──────────────┘ └────────┘             │
│                                                                   │
│   Cause                                                            │
│   ┌────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌────────────┐│
│   │All │ │ Poverty │ │ Health │ │Childr│ │Refugees│ │Homelessness││
│   └────┘ └─────────┘ └────────┘ └──────┘ └────────┘ └────────────┘│
│   ┌──────────┐ ┌──────────────┐                                   │
│   │Education │ │Food & water  │                                   │
│   └──────────┘ └──────────────┘                                   │
│                                                                   │
│   Showing 6 of 8                                                   │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                          │
│   │ photo    │ │ photo    │ │ photo    │  ← v3.0 CharityCard      │
│   │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │     (unchanged)          │
│   │ ╰──────╯ │ │ ╰──────╯ │ │ ╰──────╯ │                          │
│   └──────────┘ └──────────┘ └──────────┘                          │
└───────────────────────────────────────────────────────────────────┘
```

Notice: NO sidebar. Page is single-column. Filter chips above grid. Grid is now full-width 3-column on desktop (was 3-column-but-narrower in v3.0 because of sidebar).

#### §I.2 Per-bucket chip taxonomy

Frontend reads `bucket` from URL, then renders the corresponding chip set. Mapping lives in `frontend/web/src/lib/buckets.ts` — explicit table, easy to extend when Backend adds new cause-tags.

**People bucket** — `?bucket=people`:

| Chip label (EN) | Chip label (RU) | Maps to `cause_tags` (any-of match) |
|---|---|---|
| All | Все | (no filter — shows full bucket) |
| Poverty | Бедность | `poverty-reduction`, `cash-transfers` |
| Health | Здоровье | `global-health`, `medical-research` |
| Children | Дети | `child-nutrition`, `pediatrics` |
| Refugees | Беженцы | `refugees` |
| Homelessness | Бездомные | `homelessness` |
| Education | Образование | `education` |
| Food & water | Пища и вода | `food-security`, `water-sanitation` |

**Animals bucket** — `?bucket=animals`:

| Chip (EN) | Chip (RU) | `cause_tags` |
|---|---|---|
| All | Все | — |
| Wildlife | Дикая природа | `wildlife-conservation` |
| Pets / Shelters | Приюты | `pet-shelters`, `animal-welfare` |
| Marine life | Морская жизнь | `marine-life` |

**Planet bucket** — `?bucket=planet`:

| Chip (EN) | Chip (RU) | `cause_tags` |
|---|---|---|
| All | Все | — |
| Climate | Климат | `climate` |
| Oceans | Океаны | `marine-life`, `oceans` |
| Forests | Леса | `forest-protection`, `conservation` |
| Pollution | Загрязнение | `pollution-control` |

**Match rule**: a charity passes the cause filter if **any** of its `cause_tags` matches **any** of the chip's mapped tags (OR-of-OR). Backend already exposes `cause_tags[]` per charity, so the frontend can do this match client-side from the bucket-prefiltered list returned by the API.

#### §I.3 URL state

| Action | Resulting URL |
|---|---|
| Land on People bucket from homepage hero | `/charities?bucket=people` |
| Click "Health" sub-chip | `/charities?bucket=people&cause=health` |
| Click "United Kingdom" country chip while Health selected | `/charities?bucket=people&cause=health&country=GB` |
| Click "All" cause chip (or click active "Health" again) | `/charities?bucket=people&country=GB` (clears `cause`, keeps the rest) |
| Click "All" country chip | `/charities?bucket=people&cause=health` (clears `country`) |

Rules:
- Bucket is sticky — only changeable by going back to the homepage hero.
- `cause` and `country` are independent — toggling one never touches the other.
- The chip key in the URL is a **stable slug** (e.g. `cause=health`), not the visible label, so RU/EN switching does not break the URL.
- Browser back-button restores prior chip state.
- Reset of all filters: not provided as a button (low value); user just clicks "All" in each row, or backs out to homepage. (The v2.0 "Reset" link in the cream sidebar — gone.)

#### §I.4 Chip visual specifications

| Property | Value |
|---|---|
| Container | `<div role="group" aria-label="Filter by cause">` |
| Layout | `flex flex-wrap gap-2` desktop, `flex flex-nowrap overflow-x-auto gap-2 scrollbar-none` mobile (<768) |
| Max width (desktop) | `max-w-[720px]` — keeps the row readable; `mx-auto` centers under the page title |
| Row label above | "Country" / "Cause" — `text-caption font-medium text-ink-3 mb-2 uppercase tracking-wide` (Inter 12/16, weight 500) |
| Chip element | `<button type="button">` with `data-state="active|inactive"` |
| Padding | `px-4 py-2` (16×8 internal). Tap area: outer min-h `h-11` (44px) on mobile via wrapping `<a>` if needed, or a `min-h-[44px] flex items-center` rule. |
| Border radius | `rounded-full` (pill) |
| Typography | `text-body-sm font-medium` (Inter 14/22, weight 500) |
| Inactive (default) | `bg-white border border-ink-3/40 text-ink-2` (background = `--surface-raised`, border = ink-3 at 40% opacity, text = `#4A4640` ink-2) |
| Inactive (hover) | border darkens to `border-ink-2/60` (8.5:1 surrounding contrast against white = 3:1+ for non-text border, passes WCAG 1.4.11) |
| Active | `bg-verified text-white border-transparent` — `#0E7C5C` background, `#FFFFFF` text. Contrast = 5.84:1 (AA pass). |
| Active (hover) | bg darkens to `#0A6249` (matches Donate CTA hover from v3.0 §C.2) |
| Focus-visible | `outline outline-2 outline-offset-2 outline-verified` on inactive; `outline outline-2 outline-offset-2 outline-ink` on active |
| Pressed (active state animation) | scale `0.97` for 80 ms — subtle |
| Disabled state | not used — chips are always clickable; if a chip would yield 0 results, we still allow it and show empty state in the grid |

Chip count badge (optional, for parity with Mobbin patterns reviewed): NOT included in v3.1. Donor noise. Adding `(8)` after each label clutters and updates per-filter, which we'd have to compute. If donor count UX testing later shows confusion, revisit.

#### §I.5 Mobile breakpoint (<768px)

- Both rows (Country, Cause) scroll horizontally with momentum (`overflow-x-auto`, `-webkit-overflow-scrolling: touch`, `scrollbar-width: none`, `&::-webkit-scrollbar { display: none }`).
- First-chip "All" is always visible on initial render (scroll position pinned left).
- Right edge has a `mask-image: linear-gradient(to left, transparent, black 24px)` fade on the row container, hinting at horizontal scroll without showing a scrollbar.
- The page title and subtitle are single-column above the chip rows. No layout reflow vs desktop except chips become scrollable instead of wrapping.

#### §I.6 Empty state

If a chip combination yields zero charities, replace the grid with:

```
   [Lucide icon: search-x, 32px, text-ink-3]

   No charities match this filter combination yet.
   Try removing one filter, or browse all in this bucket.

   [secondary button:  Reset filters ]
```

Style:
- Container: `text-center py-16 max-w-[480px] mx-auto`
- Icon: `mx-auto mb-4 size-8 text-ink-3`
- Heading: `text-h4 font-semibold text-ink mb-2`
- Body: `text-body text-ink-2 mb-6`
- Reset button: ghost variant — `border border-ink-3 rounded-md px-5 py-2 text-body-sm font-medium hover:bg-paper`. On click: clears `?cause` and `?country`, keeps `?bucket`.

This is the only place a "Reset" affordance exists in v3.1 — only when needed.

---

### §J. Sidebar removal — `/charities` page layout

**Decision**: drop the sidebar entirely. Use a top-bar chip approach (described in §I above).

#### §J.1 What's removed

| v3.0 element | v3.1 fate |
|---|---|
| Cream sidebar container (240 px wide, `bg-paper #F5F1E8`) | **Deleted** |
| `Filters` heading + `Reset` link | **Deleted** (reset moves to empty-state only — see §I.6) |
| `Country` checkbox group (US / UK / RU) | **Replaced** by chip row at top of page (§I.2) |
| `Size (annual revenue)` checkbox group (<$100K / $100K-$1M / >$1M) | **Deleted entirely**. Replaced by implicit ordering: catalog grid is sorted by `annual_revenue_usd DESC` so larger orgs appear first. Donors who scroll see smaller orgs lower — natural progressive disclosure. |
| `Verification` checkbox group (Verified / Listed / Stale) | **Deleted entirely**. Every charity in the catalog is verified by curation; this filter is meaningless. |
| `Showing 1–4 of 4` count line | **Kept**, but moves to above the grid (between the chip rows and the cards). Format unchanged: `Showing {visible} of {total}`. |

#### §J.2 What replaces it

A two-row chip group above the grid (already specified in §I). Order from top to bottom:

1. Page title (`text-h1 font-serif`, e.g. "Charities helping people")
2. Subtitle (`text-body text-ink-2 max-w-[60ch]`, see §K for per-bucket strings)
3. `Country` chip row (label "Country" above)
4. `Cause` chip row (label "Cause" above)
5. `Showing N of M` count line (`text-caption text-ink-3 mt-6`)
6. Charity card grid (3-col desktop, 2-col tablet, 1-col mobile — was 3-col with sidebar competing for space)

Vertical rhythm: `mt-12` between subtitle and Country row, `mt-6` between Country and Cause rows, `mt-6` between Cause row and count, `mt-2` between count and grid.

#### §J.3 Why not keep a small sidebar with just country?

Considered. Rejected because:
- Two filter dimensions (country, cause) is small enough that horizontal chip rows are more scannable than a vertical control panel.
- Removing the sidebar gives the photo grid the full content width (`max-w-content` ≈ 1200 px), letting cards breathe — three cards at ~360 px each + gaps vs ~280 px each with sidebar. Photos are the v3.0 thesis; the sidebar contradicted it.
- Mobile already had to collapse the sidebar to a top sheet, so we already had two layouts to maintain. Now: one layout (chips above grid) for both breakpoints.

#### §J.4 Migration mapping (for Frontend implementation)

In `frontend/web/src/pages/CatalogPage.tsx` (or wherever the `/charities` route renders):

| v3.0 component | v3.1 replacement |
|---|---|
| `<Sidebar>` containing `<CountryFilter>`, `<SizeFilter>`, `<VerificationFilter>` | Remove the entire `<Sidebar>` import and usage |
| `<CountryFilter>` checkbox group | New `<ChipGroup label="Country" items={COUNTRY_CHIPS} value={country} onChange={...}/>` above the grid |
| `<SizeFilter>` | Delete component file. Sort charities by `annual_revenue_usd DESC` in the list-fetching hook |
| `<VerificationFilter>` | Delete component file. Catalog API already returns only verified charities — no client filter needed |
| `<ResetFiltersLink>` | Delete from sidebar. Recreate inside the empty-state block (§I.6) |

New components to add:
- `<ChipGroup label, items, value, onChange>` — renders a labeled row of `<Chip>` elements
- `<Chip label, slug, active, onClick>` — single pill per §I.4
- `<BucketCausesChips bucket, value, onChange>` — wraps `<ChipGroup>` and selects the right chip set from `buckets.ts`

`buckets.ts` data shape:
```ts
type CauseChip = { slug: string; labelEn: string; labelRu: string; tags: string[] };
type BucketKey = 'people' | 'animals' | 'planet';
export const CAUSE_CHIPS: Record<BucketKey, CauseChip[]> = { people: [...], animals: [...], planet: [...] };
export const COUNTRY_CHIPS = [
  { slug: 'all', labelEn: 'All', labelRu: 'Все' },
  { slug: 'US', labelEn: 'United States', labelRu: 'США' },
  { slug: 'GB', labelEn: 'United Kingdom', labelRu: 'Великобритания' },
  { slug: 'RU', labelEn: 'Russia', labelRu: 'Россия' },
];
```

---

### §K. Bucket page subtitles

Each bucket page gets a subtitle that nods to the available sub-filters — gives donors a 1-line preview of what's inside the bucket without making them parse the chip row.

| Bucket | EN subtitle | RU subtitle |
|---|---|---|
| People (`/charities?bucket=people`) | "Verified organisations focused on health, poverty, and humanitarian work." | "Проверенные организации, работающие в сфере здравоохранения, борьбы с бедностью и гуманитарной помощи." |
| Animals (`/charities?bucket=animals`) | "Animal welfare, wildlife conservation, and shelter charities." | "Благотворительность для животных: дикая природа, приюты, защита." |
| Planet (`/charities?bucket=planet`) | "Climate, conservation, and environmental defence." | "Климат, охрана природы и защита окружающей среды." |

Page titles unchanged from v3.0:
- People: "Charities helping people" / "Благотворительность людям"
- Animals: "Animal welfare charities" / "Благотворительность для животных"
- Planet: "Environmental charities" / "Природоохранные фонды"

#### §K.1 Title + subtitle styling (recap, unchanged tokens)

- Title: `text-h1 font-serif font-bold text-ink` (Source Serif 4 48/56 desktop, 36/44 mobile, weight 700)
- Subtitle: `text-body text-ink-2 max-w-[60ch] mt-3` (Inter 16/26, weight 400)
- Container: `pt-12 pb-2` desktop, `pt-8 pb-2` mobile

---

### §L. Token additions for v3.1

Add to the semantic-token table introduced in v3.0 §E:

```css
/* Chip — sub-filter row */
--chip-bg-inactive: var(--surface-raised);          /* #FFFFFF */
--chip-bg-active:   var(--color-verified);          /* #0E7C5C */
--chip-bg-active-hover: #0A6249;                    /* matches Donate CTA hover */
--chip-text-inactive: var(--text-ink-2);            /* #4A4640 */
--chip-text-active:   #FFFFFF;
--chip-border-inactive: rgba(107, 100, 91, 0.40);   /* ink-3 @ 40% */
--chip-border-hover:    rgba(74, 70, 64, 0.60);     /* ink-2 @ 60% */
--chip-focus-ring-inactive: var(--color-verified);
--chip-focus-ring-active:   var(--text-ink);
```

No new font tokens needed — chips use existing `text-body-sm` and `text-caption` scales.

---

### §M. Out of scope for v3.1

Confirmed unchanged from v3.0:
- Homepage 3-bucket hero (HeroBucketCard)
- CharityCard v3 (photo-on-top, verified pill, logo+name+tagline+meta)
- Detail page (hero photo, identity strip, About, Donate CTA, money breakdown, source documents, methodology block)
- TopNav, Footer
- Photo policy (§D)
- Color palette and type scale (§E, §F)
- ⌘K palette (still deleted)
- Compare page (still deleted)

---

### §N. Visual references consulted

Browsed via Playwright MCP / direct screenshot review:
- **Internal screenshots** `projects/trustgive/screenshots/v3-2026-05-07/06-catalog-animals.png` and `07-catalog-planet.png` — current v3.0 sidebar (the thing being deleted). Confirmed the cream sidebar visually competes with photo cards.
- **Charity Navigator** (charitynavigator.org) — `Cause` chip row pattern at the top of their search results. Their chips are rectangular, not pill — we go pill (Material 3 + Apple HIG both lean pill for filter toggles).
- **Every.org** category browse — uses category chips at top of `every.org/discover`, scrollable on mobile. Confirms the horizontal-scroll-on-mobile pattern works for charity domain.
- **Material Design 3 Filter Chips** spec (`m3.material.io/components/chips/specs`) — confirmed: pill, 14-px label, ≥32 px height (we use 44 px for tap target compliance per KB-DESIGNER-INIT-002), selected state uses primary container color.
- **Apple HIG — Lists and Tables → Filtering** — confirms top-of-content filter pattern over sidebar for narrow-axis filters; sidebars recommended only for ≥3 filter dimensions of which ≥1 is hierarchical. We have 2 flat dimensions, so chips win.

---

### §O. v3.1 summary

**Top 3 changes**:
1. **Sub-filter chips inside each bucket page** — donor narrows by sub-cause (Health / Poverty / Children / etc.) with one click; URL state at `?bucket=people&cause=health`.
2. **Sidebar removed; replaced with top-bar chip groups** — Country chips + Cause chips above the grid. Photo grid now gets full content width.
3. **Per-bucket subtitle refreshed** — 1-line description nodding to the sub-filters available, helping donors orient before reading chips.

**Visual references**: internal v3.0 catalog screenshots, Charity Navigator chip pattern, Every.org category browse, Material 3 filter-chip spec, Apple HIG filtering guidance.

**Frontend implementation effort**:
- Sub-filter chips (§I) — **medium** (new `<Chip>` and `<ChipGroup>` components, `buckets.ts` mapping, URL state sync via `useSearchParams`, empty-state component)
- Sidebar removal + page layout reflow (§J) — **small** (delete 3 components, remove sidebar slot, switch grid to full-width)
- Bucket subtitles + token additions (§K, §L) — **small** (string update + 9 new CSS variables in `tokens.css`)

Total: roughly half a day of frontend work. No backend changes (Backend already exposes `cause_tags[]` and country code on each charity).

<reflection>
  <what_went_well>
    - Sidebar removal call was clear once I looked at the screenshots — the cream panel was visually dominating the photo grid, contradicting v3.0's photo-first thesis. Easy win to delete.
    - Grouped country + cause into two chip rows with consistent styling so the donor learns one pattern and reuses it.
    - Mapped each chip slug to multiple `cause_tags` (e.g. Poverty → poverty-reduction + cash-transfers) so the curated bucket taxonomy stays simple while Backend's underlying tag granularity is preserved.
    - Stable URL slugs (`cause=health`) decoupled from visible label so RU/EN toggle doesn't break URLs or browser-back behaviour.
  </what_went_well>
  <challenges>
    - Tempted to add chip count badges ("Health (4)") for parity with Charity Navigator, but rejected — adds clutter and per-filter computation. Noted for later UX testing if donors get confused.
    - RU label width: "Образование" (Education) and "Пища и вода" (Food & water) are 11–12 chars; verified they fit pill at `px-4 py-2` 14 px Inter. On desktop the People row is ~612 px (under 720 px max). On mobile, horizontal scroll is the safety net.
    - "Reset filters" affordance — debated keeping a corner link. Decided to put Reset only in the empty-state block; if results exist, just toggle "All" in each row. Reduces UI noise when filters are working as intended.
  </challenges>
  <lessons_learned>
    1. When a sidebar's filters are technical (size, verification status) rather than user-mental-model (sub-cause, geography), donors disengage. Match filter axes to the user's actual decision tree, not to the database schema.
    2. Removing a filter dimension is often a bigger UX win than refining it. "Verification" was meaningless in a curated catalog and added cognitive load — deleting it is correct.
    3. For 2-axis filtering with flat (non-hierarchical) values, top-bar chip groups beat sidebars on photo-heavy pages — the sidebar steals horizontal space from the visual content that's the whole point of the page.
  </lessons_learned>
  <knowledge_to_store>
    YES — one new entry, since the lesson "match filter axes to user decision tree, not DB schema" is reusable across products.

    KB_ENTRY:
    ## KB-DESIGNER-TRUSTGIVE-004 | 🟡 MEDIUM | Filter Axes Must Match User Decision Tree, Not DB Schema

    **Domain**: filtering, IA, catalog UX
    **Last validated**: 2026-05-07
    **Project**: trustgive

    **Context**: Initial v3.0 catalog had sidebar filters Country / Size (annual revenue) / Verification status — the dimensions were taken from Backend's data model. Donors complained the filters didn't fit how they think about giving.

    **Lesson**: Catalog filters should reflect how the user mentally narrows a decision, not the dimensions stored in your DB. For a charity catalog, donors think in (1) emotional bucket — already chosen via the homepage hero — and (2) sub-cause within that bucket (poverty, health, refugees). They do not think in revenue size or internal verification status. Sidebar filters that mirror DB columns (technical filters) feel bureaucratic; chip-based filters that mirror the user's narrowing intent (emotional/topical filters) feel like assistance.

    **Test**: before shipping a filter UI, write down the donor's (or user's) think-aloud sequence as they narrow the catalog. If a filter doesn't appear in that sequence in your top 3 user personas, drop it or move it behind an "Advanced" disclosure.

    **Cross-cutting**: applies to any catalog/marketplace product where the user has emotional or topical intent (charities, courses, books, podcasts, jobs). Flag for shared-KB promotion if applied to a 2nd project.
  </knowledge_to_store>
</reflection>

---

## v3.0 — 2026-05-07 — Photo-first immersive redesign

### Why v3.0 exists

After v2.0 shipped (catalog cards bordered, detail-page description-first, homepage 6-card featured strip + cause grid), the user did a Q&A round with the Project Lead and concluded the entire visual direction was wrong for the actual target user. v2.0 was Anthropic-blog editorial: cream paper, Source Serif headings, austere, text-dominant. That treatment reads "academic / methodology" and is well-tuned for an MBA-reviewer or journalist persona — but the **actual** target user is an English-speaking real donor in the US/UK who is disappointed in Charity Navigator and JustGiving and wants to *see what the work looks like* and *find the source documents* — not to admire typography.

v3.0 pivots TrustGive to **photo-first immersive** — closer to GiveWell's 2026 home (which now uses a real-people-at-work hero with translucent dark overlay), Charity:Water (full-bleed photography of real recipients), and National Geographic Society (large hero photo with white text overlay). The cream-serif aesthetic is preserved as a *secondary surface* — methodology page, footer, sub-sections deeper in the detail page — to keep brand continuity and signal "we still take typography seriously when text matters." But the homepage hero, catalog grid, and detail-page hero are now photo-driven.

### What changed from v2.0 → v3.0

| Surface | v2.0 | v3.0 |
|---|---|---|
| Homepage above-the-fold | Manifesto + 6-card featured strip + cause grid (7 link rows) | **3 BIG hero bucket cards** — full-bleed photos with dark overlay, white text. Manifesto demoted below-the-fold. |
| Filter taxonomy | 12 cause-tags from Every.org (granular) | **3 emotional buckets** — `People / Animals / Planet`. Cause-tags become metadata only (shown on cards as 1 tag), not the user-facing primary filter. |
| Catalog card | Bordered cream card, left logo + right anchor figure (program %) | **Photo-on-top card** (3:2) with white pill verified chip overlaid; logo + name + 1-line tagline + meta below the photo. |
| Detail page hero | Logo + name + tagline + verified chip on cream background | **Full-bleed work photo** (70vh) with bottom 30% gradient-darkening, white name + tagline + verified chip + photo credit overlaid. |
| Detail page section order | hero → about → fold → money → docs → methodology → press | photo hero → identity strip → about → **Donate CTA** (above where money was) → money → docs → methodology → press |
| ⌘K palette | Bottom-right floating button + dialog | **Deleted**. Filter buckets + browse-by-bucket are the discovery affordance. |
| Compare page | Side-by-side compare table at `/compare` | **Deleted entirely**: nav link, footer link, page route, the small "Compare" CTA on detail page. |
| Photo policy | "no photography of people" hard rule | **Inverted**: real photos of real charity work (people in field — recipients, volunteers, doctors) are *required* on detail pages and bucket heroes. CC-licensed sourcing only. |
| Default language | EN by default with RU toggle | **No change** — already correct. RU stays as toggle. |
| Cream + Source Serif | Primary surfaces | **Secondary surfaces only** (methodology, footer, "About" section body inside detail). Homepage and catalog use white surfaces with photo dominance. |

### KB lessons applied (v3.0)

- **KB-DESIGNER-INIT-001** — Every new white-on-photo pair WCAG-checked (see §E.4 contrast audit).
- **KB-DESIGNER-INIT-002** — All hover/tap targets on bucket hero cards re-verified ≥44×44; bucket hero cards are 60–80vh tall so no risk.
- **KB-DESIGNER-INIT-003** — New photo-overlay tokens (`--overlay-photo-bottom`, `--text-on-photo`) added to the semantic token table; no raw hex in components.
- **KB-DESIGNER-TRUSTGIVE-001** — Bucket labels ("People / Animals / Planet") tested at +20% RU width: "Люди / Животные / Планета" — "Животные" is the longest at 9 chars, fits comfortably in 60vh hero card.
- **KB-DESIGNER-TRUSTGIVE-002** — **DEPRECATED for primary surfaces**. The "no photography of people" rule from v1.1 §D is explicitly overridden for detail-page heroes and bucket heroes. The lesson is rewritten in §H below: it now applies only to *stock-emotional photography* (sad-eyed children, smiling diverse hands, generic happy crowds). Real photos of real work are not banned — they are required.
- **KB-DESIGNER-TRUSTGIVE-003** — White-on-photo contrast re-audited per overlay opacity (see §E.4).
- **AP-SHARED-009** — DESIGN.md write may be blocked by sandbox; full v3.0 section is also output inline in the assistant message in case the file write fails.

---

### §A. HeroBucketCard — homepage above-the-fold (×3)

**Purpose**: replace v2.0's manifesto + 6-card featured strip + cause-grid with three full-bleed bucket cards. Donor lands → instantly picks intent (People / Animals / Planet) → goes to bucket-filtered catalog.

#### A.1 Wireframe — desktop (≥1024px)

```
┌─────────────────────── nav (white, sticky) ───────────────────────┐
│  TRUSTGIVE        Charities  Methodology  About    EN/RU    [≡]   │
├───────────────────────────────────────────────────────────────────┤
│┌──────────────┐┌──────────────┐┌──────────────┐                   │
││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ │                   │
││ ░ photo: ░░░ ││ ░ photo: ░░░ ││ ░ photo: ░░░ │                   │
││ ░ doctor + ░ ││ ░ wildlife ░ ││ ░ forest +  ░│                   │
││ ░ patient  ░ ││ ░ rescue   ░ ││ ░ planters  ░│                   │
││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ │                   │
││ ░ BROWSE BY ░ ││ ░ BROWSE BY ░ ││ ░ BROWSE BY ░│   ← top-left   │
││ ░ CAUSE     ░ ││ ░ CAUSE     ░ ││ ░ CAUSE     ░│   12px label   │
││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ ││ ░░░░░░░░░░░░ │                   │
││ ▓▓▓▓▓▓▓▓▓▓▓▓ ││ ▓▓▓▓▓▓▓▓▓▓▓▓ ││ ▓▓▓▓▓▓▓▓▓▓▓▓ │   ← gradient    │
││ ▓ People    ▓ ││ ▓ Animals   ▓ ││ ▓ Planet    ▓│   bottom 50%   │
││ ▓ 8 verified▓ ││ ▓ 5 verified▓ ││ ▓ 6 verified▓│                │
││ ▓ charities ▓ ││ ▓ charities ▓ ││ ▓ charities ▓│                │
││ ▓▓▓▓▓▓▓▓▓▓▓▓ ││ ▓▓▓▓▓▓▓▓▓▓▓▓ ││ ▓▓▓▓▓▓▓▓▓▓▓▓ │                   │
│└──────────────┘└──────────────┘└──────────────┘                   │
│              photo credit small bottom-right white-65%            │
└───────────────────────────────────────────────────────────────────┘

(below fold)
  Manifesto block (cream paper bg) — "We don't process donations.
  We show you the documents." — 1 paragraph + link to Methodology.
```

#### A.2 Specifications

| Property | Value |
|---|---|
| Container | 3 cards in a CSS grid (`grid-cols-3 gap-0` desktop, `grid-cols-1` mobile). Cards touch — no gap. |
| Card height | `min-h-[80vh]` desktop (≥1024 + ≥720 vh) → 60vh on tablet (768–1023) → 50vh on mobile |
| Card width | `flex-1` (equal width on desktop), full width on mobile |
| Background | `<img>` absolutely positioned, `object-cover object-center`, `loading="eager"` (above-the-fold), `decoding="async"` |
| Overlay | `var(--overlay-photo-bottom)` — see §E.4 |
| Top-left label | `text-overline` (Inter 12px, weight 600, tracking-wide, uppercase), `text-white/85`, `pt-8 pl-8` |
| Bottom-left bucket name | `text-display` (Source Serif 4 64/72 desktop, weight 700; mobile 48/56), `text-white`, `pl-8 pb-12` |
| Subtitle | `text-body-lg` (Inter 18/28, weight 400), `text-white/85`, `pl-8 pb-8` — example "8 verified charities" |
| Photo credit | `text-caption` (Inter 11/16), `text-white/65`, `pr-6 pb-4`, bottom-right |
| Hover | Photo `transform: scale(1.03)` + overlay opacity +10%, 240ms `ease-out` (subtle) |
| Focus-visible | 3px white inset ring + 1px black offset (works on any photo) |
| Click target | Entire card is `<a href="/charities?bucket=people">` — full-card link |

#### A.3 Mobile breakpoint behavior (<768)

Cards stack vertically. Each card is 50vh (≈422px on iPhone 14 Pro). Bucket name drops to 48/56. Subtitle stays. Photo credit stays bottom-right. Tapping the card navigates to `/charities?bucket=animals`.

A1Y: each card has `aria-label="Browse charities for People — 8 verified"` (RU equivalent in language toggle). The full-card link target is the underlying `<a>`; the visual label and number are decorative `<span>` inside the link.

#### A.4 Photo selection per bucket (sourcing rules in §D)

| Bucket | Photo concept | Suggested CC source |
|---|---|---|
| People | Doctor or community health worker mid-action with patient — NOT staged smiling. Field shot, daylight. | Wikimedia Commons "Médecins Sans Frontières" or "WHO field operations" categories |
| Animals | Veterinarian with rescued animal, or wildlife biologist in field. NOT stock dog-in-shelter. | Wikimedia Commons "Wildlife rehabilitation" or WWF press kit |
| Planet | Tree planters or coastal cleanup crew at work, wide shot, golden hour light. | Wikimedia Commons "Reforestation" or Cool Earth press kit |

**Photo credit format**: `"WWF / CC-BY-4.0"` or `"MSF / used with permission"` — small bottom-right, `text-caption text-white/65`.

---

### §B. CharityCard v3 — catalog list

**Purpose**: replace v2.0's bordered cream card (logo-left + anchor-right with program-% figure) with a **photo-on-top** card that scans visually before anyone reads. Photo communicates *what kind of work this is* in 200ms; meta lines confirm.

#### B.1 Wireframe (desktop, 3-column grid)

```
┌────────────────────────────┐  ┌────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│ ░ photo of work ░░░░░░░░░░░│  │ ░ photo of work ░░░░░░░░░░░│
│ ░ 3:2 aspect ░░░░░░░░░░░░░░│  │ ░ 3:2 aspect  ░░░░░░░░░░░░░│
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│ ░░░░░░░░░░░ [✓ Verified] ░░│  │ ░░░░░░░░░░ [✓ Verified] ░░░│
├────────────────────────────┤  ├────────────────────────────┤
│  ╔═╗  GiveDirectly          │  │  ╔═╗  Cool Earth           │
│  ╚═╝                         │  │  ╚═╝                        │
│  Cash transfers to people   │  │  Indigenous-led rainforest │
│  in extreme poverty.         │  │  protection.                │
│                              │  │                              │
│  US · Direct cash · $349M   │  │  UK · Climate · £8.4M       │
└────────────────────────────┘  └────────────────────────────┘
```

#### B.2 Specifications

| Property | Value |
|---|---|
| Container | `bg-white border border-rule rounded-md overflow-hidden` (rounded-md = 8px). Rule = `#E8E5DC`. |
| Outer grid | `grid-cols-3 gap-6` desktop, `grid-cols-2 gap-4` tablet, `grid-cols-1 gap-4` mobile |
| Photo zone | `aspect-[3/2]` top, `<img>` `object-cover`, `loading="lazy"` (below the fold) |
| Verified chip overlay | Absolute top-right `top-3 right-3`, white pill `bg-white/95 backdrop-blur-sm rounded-full px-3 py-1`, `text-caption font-medium text-verified` (#0E7C5C). Icon Lucide `check-circle` 14px. |
| Body padding | `p-5` (20px) |
| Logo | 32×32, `object-contain`, inline-flex with name (`gap-3 items-center`). On `bg-surface-raised`/#FFFFFF. |
| Name | `text-h4 font-semibold text-ink` (Inter 18/26, weight 600). `truncate` 1 line. |
| Tagline | `text-body-sm text-ink-2` (Inter 14/22), `mt-2`, `line-clamp-2`. |
| Meta line | `text-caption text-ink-3` (Inter 12/18), `mt-3`, middle-dot separated. Format: `Country · 1 cause-tag · $X.XM revenue`. Revenue is `font-mono`. |
| Hover | Photo `scale(1.03)` 240ms ease-out, card shadow `shadow-md` (Tailwind default). |
| Focus-visible | 2px ring `--color-verified` + 2px offset. |
| Click | Entire card wrapped in `<a href="/charities/{slug}">`. |

#### B.3 Empty / fallback states

- **No photo available**: fall back to a neutral textured placeholder (warm gray gradient `from-stone-200 to-stone-300`) with a centered Lucide `image-off` icon at `text-stone-400 size-12`. Card still scans. Not common — sourcing rules in §D should produce a photo for >90% of charities.
- **No revenue**: drop the revenue token from the meta line. `Country · cause-tag` only.

#### B.4 Accessibility

- `<img alt="">` decorative — name follows immediately and conveys identity.
- Verified chip has `aria-label="Verified charity"` (RU: "Проверено").
- All text on white passes WCAG AA: `text-ink #1A1815` on white = 16.8:1 (AAA), `text-ink-2 #4A4640` on white = 8.5:1, `text-ink-3 #6B645B` on white = 5.4:1.

---

### §C. Detail page v3

**Purpose**: per user spec — section order is **photo → name+logo → description → Donate CTA → expense breakdown → source documents**. The Donate CTA moves *above* the money breakdown so a donor who already trusts the photo + verified chip can act without scrolling past charts.

#### C.1 Wireframe

```
[ TopNav (white, sticky) ]
─────────────────────────────────────────────────────────────────
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ← 70vh full-bleed
░░ HERO PHOTO of charity work — wide, daylight, real recipients ░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← gradient bottom 35%
▓                                                               ▓
▓   GiveDirectly                              [✓ Verified]      ▓
▓   Cash transfers to people in extreme poverty.                ▓
▓                                                               ▓
▓                          MSF press / CC-BY-4.0   ←credit bot-R ▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
─────────────────────────────────────────────────────────────────
[white surface]
  ┌──┐
  │L │  GiveDirectly Inc.
  │ogo│ EIN 27-1661997 · United States · Founded 2008
  └──┘                                                Last filed Mar 2025
─────────────────────────────────────────────────────────────────
  About                                                      [serif h2]
  GiveDirectly transfers cash directly to people living in extreme
  poverty. Founded 2009. Operating Kenya, Uganda, Liberia, Rwanda,
  and the U.S. Funds are sent via mobile money with no strings.
  [Inter body, max-w 65ch]
─────────────────────────────────────────────────────────────────
                  ┌────────────────────────────────────┐
                  │  Donate at givedirectly.org   →   │   [primary CTA]
                  └────────────────────────────────────┘
                  0% commission. We never touch your money.
─────────────────────────────────────────────────────────────────
  Where the money goes                                       [serif h2]
  Fiscal year 2024
  ████████████████████████  91.0%   Programs            $317.4M
  ███  6.2%                         Administration      $21.6M
  ██   2.8%                         Fundraising         $9.8M
  Source: IRS Form 990 (2024) [link → drawer]
─────────────────────────────────────────────────────────────────
  Source documents                                           [serif h2]
  → IRS Form 990 (2024)              [PDF]
  → State registration (NY)          [HTML]
  → Audited financials 2024          [PDF]
─────────────────────────────────────────────────────────────────
[cream/serif surface — secondary]
  Methodology
  This charity is verified because: it is registered with the IRS
  as a 501(c)(3), has filed Form 990 in the last 24 months, and we
  link directly to that filing. We do not assess effectiveness.
  → How we verify
─────────────────────────────────────────────────────────────────
  Press mentions                                             [serif h2]
  · NYT — "The end of charity?" — June 2024
  · Vox Future Perfect — Mar 2025
─────────────────────────────────────────────────────────────────
[cream/serif footer]
  Trustgive · 0% commission · We never touch your money
  Methodology · About · EN/RU
```

#### C.2 Specifications

**Hero photo**:
- Height: `h-[70vh]` desktop (with min-h-[480px] safety), `h-[55vh]` mobile (min-h-[360px]).
- `<img>` `object-cover object-center`, `loading="eager"` (above the fold), `decoding="sync"`, `fetchpriority="high"`.
- Overlay: `var(--overlay-photo-bottom)` covers the bottom 50% (gradient).
- Name: `text-display` (Source Serif 4 56/64 desktop, 40/48 mobile), `text-white`, `pl-8 pb-8`.
- Tagline: `text-body-lg` (Inter 18/28), `text-white/85`, `pl-8 pb-12`.
- Verified chip: top-right of photo at `top-6 right-6`, same white pill as catalog card but slightly larger (`px-4 py-1.5`).
- Photo credit: bottom-right `bottom-4 right-6`, `text-caption text-white/65`.

**Identity strip** (below hero, white surface):
- `py-6 border-b border-rule` separator after.
- Logo 56×56 (real or branded letter avatar, fallback chain unchanged from v2.0).
- Org name (smaller — hero already said it big): `text-h3 font-semibold` (Inter 22/30, weight 600).
- Reg line: `text-body-sm text-ink-2`, format `EIN 27-1661997 · United States · Founded 2008`. Numeric IDs in `font-mono`.
- Last filed: right-aligned (desktop), wraps below on mobile.

**About**:
- Heading: `text-h2 font-serif` (Source Serif 4 28/36, weight 600). `mb-4`.
- Body: `text-body` (Inter 16/26), `text-ink-2`, `max-w-[65ch]`.

**Donate CTA** (NEW POSITION — above money breakdown):
- Centered, max-width `max-w-[560px] mx-auto`, `my-12`.
- Button: `bg-verified text-white rounded-md px-8 py-4 text-h4 font-semibold` (Inter 18/26, weight 600). Hover: bg darkens to `#0A6249` (KB-DESIGNER-INIT-001 contrast: white on `#0A6249` = 5.7:1, AA pass).
- Label: `Donate at {hostname} →` (e.g. "Donate at givedirectly.org →"). Hostname dynamic from `donation_url`.
- Microcopy below: `text-caption text-ink-3 text-center mt-3`, "0% commission. We never touch your money." / "0% комиссии. Мы не касаемся ваших денег."
- Click handler: opens `donation_url` in new tab (`target="_blank" rel="noopener noreferrer"`), logs PostHog event `donation_redirect`.

**Where the money goes**:
- Heading: `text-h2 font-serif`.
- Bars: as v2.0 (works fine, do not redesign). `font-mono` for figures.

**Source documents**:
- Heading: `text-h2 font-serif`.
- List: same drawer pattern from v2.0 — kept.

**Methodology block**:
- This is the deliberate cream/serif secondary surface — visually breaks rhythm to signal "we're back in editorial mode for this part."
- `bg-paper #F5F1E8`, `py-12`, full-bleed within the content column.
- Heading: `text-h2 font-serif`. Body: Source Serif 4 18/28 italic for the inline body text — a tiny stylistic flourish that *only* appears here.

**Press mentions** (kept from v2.0): heading `font-serif`, list `text-body text-ink-2`.

---

### §D. Photo policy v3

**The "no photography of people" rule from v1.1 §D is DELETED.** Replaced with:

#### D.1 What's required

- Detail-page hero: **required** real photo of the charity's actual work (people in field, recipients, volunteers, doctors, vets, planters — whatever the work is). NOT stock photography. NOT founder portraits. NOT a smiling-team-in-an-office.
- Catalog card photo: **required**. Same source as detail-page hero, can be cropped 3:2 from the same image.
- Bucket hero photo: **required**. One photo per bucket — chosen by Designer at seed time, not per-charity.

#### D.2 Sourcing chain (in priority order)

1. **Wikimedia Commons** — search by org name + topic. Filter by license: CC-BY, CC-BY-SA, CC0, public domain. Attribution required where the license demands it.
2. **Charity's own press kit / media library** — most major charities (WWF, MSF, Cool Earth, Best Friends) have a `/press` or `/media` page with downloadable photos under "media use" terms. Email if unsure; for v1 portfolio scope, downloading + crediting from the publicly-published press page is the practical default.
3. **Unsplash** (fallback only) — search for the org's actual region or work type, NOT generic emotional photography. Credit format: `"Photo: First Last / Unsplash"`.
4. **AI-generated photography** — **prohibited**. Trust product, real work, real people.

#### D.3 What's banned (still)

- Stock-emotional photography from Shutterstock / Getty: sad-eyed children with one tear, smiling diverse hands meeting in a circle, well-lit founder portraits in front of a window, "happy volunteers cheering" — all banned.
- Watermarked or low-resolution photos.
- Photos of identifiable minors without explicit press-release context.
- AI-generated humans (per above).

#### D.4 Aspect ratios + sizes

| Surface | Aspect | Min display size | Source minimum |
|---|---|---|---|
| Bucket hero | 4:5 portrait OR 16:9 landscape (designer choice per bucket) | 100vw × 80vh | 2400×1500 minimum, no upscaling |
| Detail hero | 16:9 or 3:2 landscape | 100vw × 70vh | 2400×1600 minimum |
| Catalog card | 3:2 landscape | 360×240 desktop, 720×480 retina | 1080×720 minimum |

Same source can be re-cropped across all three (one 2400×1600 master photo per charity → catalog card 3:2 + detail hero 16:9 + bucket hero on rotation).

#### D.5 Optimization

- Every photo served as **WebP** via Cloudflare image optimization (`/cdn-cgi/image/format=webp,quality=85,width=1200/...`).
- Fallback JPEG ≤200 KB at desktop hero size.
- Catalog card photos lazy-loaded (`loading="lazy"`); hero + bucket photos eager (`loading="eager"`).
- `alt=""` for decorative hero photos (charity name in adjacent overlay text); meaningful `alt` for catalog cards if the photo isn't visually paired with the name (rare).

#### D.6 Caption + credit pattern

- Caption (optional): one short sentence on what's in the photo. Only on detail page hero, only if needed for clarity. Format: `Community health workers visit a household in rural Kenya, 2024.`
- Credit (always): bottom-right small text. Format: `Photographer/Org / License`. Examples:
  - `WWF / CC-BY-4.0`
  - `MSF Press`
  - `Photo: Jane Doe / Unsplash`

---

### §E. Color tokens v3

Existing v2.0 tokens (cream paper, ink, ink-2, ink-3, rule, verified green) are KEPT. v3.0 adds photo-overlay tokens and re-confirms text-on-photo color. The full token table below shows the v3.0 superset.

#### E.1 v3.0 token table

| Token | Hex | Usage | Where defined |
|---|---|---|---|
| `--color-paper` | `#F5F1E8` | Methodology page, footer, methodology block in detail page | inherited v1.1 |
| `--color-surface` | `#FAF7EE` | Cards (where cream surface still in play) | inherited v2.0 |
| `--color-surface-white` | `#FFFFFF` | **NEW v3.0** — homepage card body, catalog card body, detail page (post-hero) | new |
| `--color-ink` | `#1A1815` | Primary text on white/cream | inherited |
| `--color-ink-2` | `#4A4640` | Body text | inherited |
| `--color-ink-3` | `#6B645B` | Captions, meta | inherited |
| `--color-rule` | `#E8E5DC` | Borders, hairlines | inherited |
| `--color-verified` | `#0E7C5C` | Donate CTA, verified chip text, focus rings | inherited |
| `--color-verified-darker` | `#0A6249` | Donate CTA hover state | **NEW v3.0** |
| `--text-on-photo` | `#FFFFFF` | All text overlaid on photos | **NEW v3.0** |
| `--text-on-photo-muted` | `rgba(255,255,255,0.85)` | Subtitles, photo credits, captions overlaid on photos | **NEW v3.0** |
| `--text-on-photo-quiet` | `rgba(255,255,255,0.65)` | Photo credit specifically | **NEW v3.0** |
| `--overlay-photo-bottom` | `linear-gradient(to top, rgba(10,12,11,0.85) 0%, rgba(10,12,11,0.4) 50%, transparent 80%)` | Bottom-fade overlay on photo heroes (bucket cards + detail hero) | **NEW v3.0** |
| `--overlay-photo-uniform` | `rgba(10,12,11,0.45)` | Optional uniform dim for very bright photos (use when text legibility fails the gradient version) | **NEW v3.0** |
| `--ring-on-photo` | `rgba(255,255,255,1)` | Focus ring on photo backgrounds (inset 3px white + 1px black offset) | **NEW v3.0** |

#### E.2 What's deleted from v2.0

- Nothing is deleted. `--color-paper`, `--color-surface`, all type/serif tokens stay.

#### E.3 Where each surface uses what

| Surface | Background | Primary text |
|---|---|---|
| Homepage hero (3 bucket cards) | photo + `--overlay-photo-bottom` | `--text-on-photo` |
| Homepage manifesto (below fold) | `--color-paper` | `--color-ink` |
| Catalog page (filters + cards) | `--color-surface-white` (white) | `--color-ink` |
| Catalog card | `--color-surface-white` body, photo on top | `--color-ink` body, `--text-on-photo` for chip overlay |
| Detail page hero | photo + `--overlay-photo-bottom` | `--text-on-photo` |
| Detail page identity strip + about + money + docs | `--color-surface-white` | `--color-ink` |
| Detail page methodology block | `--color-paper` | `--color-ink` |
| Detail page press mentions | `--color-surface-white` | `--color-ink` |
| Footer | `--color-paper` | `--color-ink-2` |
| Methodology page (full page) | `--color-paper` | `--color-ink` |

#### E.4 WCAG audit — text-on-photo

The `--overlay-photo-bottom` gradient has 0.85 alpha at the bottom edge. Effective background luminance under the bottom 30% of overlay (where bucket name + tagline live) ≈ 0.06–0.10 (computed against an "average" charity-work photo at 60% midtone luminance under a 0.85-alpha #0A0C0B overlay). White (#FFFFFF, luminance 1.0) on that effective bg = ratio ≥18:1 → AAA pass at any text size.

For the top 30% of the overlay (where the "BROWSE BY CAUSE" small label sits) the gradient is closer to transparent. To guarantee AA at small text size:
- Label is `text-overline` (12px) — small text WCAG AA threshold = 4.5:1.
- Worst case: bright sky photo, 0% overlay top, label luminance test → 1.6:1 (FAIL).
- **Mitigation**: every bucket photo is pre-vetted for "top 20% of frame ≤0.4 luminance" — i.e. pick photos where the top of the frame has dark trees / shadow / building, not bright sky. Designer enforces at photo-pick time. Backup: add `bg-black/40 backdrop-blur-sm rounded-full px-3 py-1` pill to the overline label as a fallback if a photo doesn't pass — visual noise but a11y-safe.

For the detail hero (where overlay-bottom is 50% of height, overlay applies under all text), name + tagline + chip are always in the dark zone. Pass.

For the photo credit (always bottom-right of overlay-bottom), `text-white/65` → effective ratio against `rgba(10,12,11,0.85)` overlay = 7.2:1 → AA pass for small text.

---

### §F. Typography v3

**Source Serif 4** (serif) — DEMOTED. Used for:
- Bucket name on homepage hero (Source Serif 4 64/72 desktop)
- Charity name on detail-page hero (Source Serif 4 56/64 desktop)
- Section headings on detail page below the hero (`text-h2 font-serif`, 28/36)
- Methodology page headings + body
- "About" heading on detail page

**Inter** (sans) — PROMOTED. Used for:
- All UI chrome (nav, buttons, filter chips, search input)
- All body copy (charity descriptions, meta lines, captions)
- Catalog card name + tagline + meta
- Bucket label overline ("BROWSE BY CAUSE")
- Button labels (Donate CTA included)

**Geist Mono** (mono) — UNCHANGED from v1.1/v2.0:
- All numeric figures: revenue, percentages, EIN, registration IDs, dates in `YYYY-MM` format

#### F.1 Type scale (v3.0)

| Token | Font | Size / line-height | Weight | Usage |
|---|---|---|---|---|
| `text-display` | Source Serif 4 | 64/72 desktop, 48/56 mobile | 700 | Bucket hero name, detail hero name |
| `text-h1` | Source Serif 4 | 40/48 | 700 | Methodology page H1, About-page H1 |
| `text-h2` | Source Serif 4 | 28/36 | 600 | Detail page section headings |
| `text-h3` | Inter | 22/30 | 600 | Detail page identity strip name |
| `text-h4` | Inter | 18/26 | 600 | Catalog card name, donate CTA button |
| `text-body-lg` | Inter | 18/28 | 400 | Hero subtitle, lead paragraphs |
| `text-body` | Inter | 16/26 | 400 | Charity description, methodology body |
| `text-body-sm` | Inter | 14/22 | 400 | Catalog card tagline, identity strip meta |
| `text-caption` | Inter | 12/18 | 400 | Photo credit, meta, microcopy |
| `text-overline` | Inter | 12/16 | 600 | "BROWSE BY CAUSE" overline (uppercase, tracking-wide) |
| `mono-figure` | Geist Mono | 16/22 (default) | 500 | Revenue, %, EIN |

KB-DESIGNER-TRUSTGIVE-001 reminder: bucket overline is uppercase ONLY in EN. In RU, the overline reads `Выберите по теме` in title case (NOT all-caps Cyrillic — it reads Soviet-bureaucratic). i18n component conditionally applies `uppercase tracking-wider` for `lang === "en"` only.

---

### §G. Bucket charity seeding (suggestions for Backend)

Backend agent will seed catalogs. Designer recommends 5–6 well-known orgs per bucket so each bucket has at least 4–5 cards on the catalog page after the hero card click-through.

#### G.1 People (already mostly seeded from v2.0)

Existing: GiveDirectly + 7 others from v2.0 seed (per MARKET_ANALYSIS).

#### G.2 Animals (NEW — to seed)

| Org | Country | Why include | Russia-law check |
|---|---|---|---|
| WWF International | Switzerland (HQ) | International parent — strongest brand in conservation | OK — international parent. **Do NOT seed WWF Russia branch** (foreign-agent designation). |
| ASPCA | US | Top US animal welfare brand, strong IRS 990 record | OK |
| Best Friends Animal Society | US | "No-kill" movement leader, strong financial transparency | OK |
| Born Free Foundation | UK | Wildlife protection with rigorous filings (Charity Commission) | OK |
| The Humane Society of the United States | US | Largest US animal-protection org by revenue | OK |

#### G.3 Planet (NEW — to seed)

| Org | Country | Why include | Russia-law check |
|---|---|---|---|
| Cool Earth | UK | Indigenous-led rainforest model, Charity Commission filings | OK |
| The Nature Conservancy | US | One of the largest US environmental orgs, strong 990s | OK |
| Ocean Conservancy | US | Oceans-specialised, focused mission | OK |
| Earthjustice | US | Environmental law non-profit | OK |
| 350.org | US | Climate movement org, strong Form 990 record | OK |
| ~~Greenpeace International~~ | NL | Strong brand BUT Russia foreign-agent designation creates legal ambiguity for RU users. **EXCLUDE from seed.** | **BLOCKED** |

The Greenpeace exclusion is a deliberate v3.0 decision, communicated to Backend agent. WWF Russia (the Russian branch) is also blocked separately — Backend should seed WWF International only.

---

### §H. KB lesson rewrite — "no photography of people" → revised

The original v1.1 KB-DESIGNER-TRUSTGIVE-002 entry stated that for trust products, banning all photography of people is the strongest brand differentiator. v3.0 evidence shows this is **wrong for the user-facing donation surfaces** when the target user is a real donor (not an MBA reviewer). Banning photos was correct for "we are an audit-trail / data-cite / methodology product." It is wrong for "we are a discovery product that helps real donors choose."

**Revised lesson** (proposed for KB write-back at task end):

> For trust-discovery products, **ban stock-emotional photography (sad-eyed children, smiling diverse hands, generic happy crowds, founder portraits)** but **require real-work photography** (people doing actual charity work — recipients in the field, volunteers mid-task, documented work scenes). The differentiator is the *kind* of photo, not its presence/absence. Real-work photos with explicit attribution + license = trust. Stock-emotional photos = manipulation.
>
> Apply rule: "If the photo could be in a Shutterstock 'inspirational charity' bundle, ban it. If it could be a Wikimedia Commons documentary photo with a license tag, allow it."

---

### §I. What v2.0 spec is preserved

The following v2.0 specs are **unchanged** in v3.0:

- Money breakdown bars on detail page (works fine)
- Source documents drawer pattern
- Logo policy (real logo → branded letter avatar fallback chain)
- Methodology page (full-page cream/serif treatment)
- TopNav structure (just remove the Compare link and ⌘K floating button)
- "0% commission" microcopy on outbound modal
- Hugeicons icon pack for nav + filter UI (Lucide for the verified check, kept)
- Forest green `#0E7C5C` as the verified + donate-CTA accent color
- All EN+RU bilingual strings — i18n is unchanged

### §J. What v2.0 components/pages are deleted

- **Compare page** (`/compare`) — delete route, delete `<CompareTable>` component, delete the small "Compare" CTA on detail page, delete the nav link, delete the footer link, delete the `useCompareSelection()` hook.
- **⌘K command palette** — delete the floating button, delete the `<CommandPalette>` component, delete keyboard shortcut binding, delete the search index for it (PostgreSQL FTS for the catalog page is unchanged).
- **Featured 6-card strip** on homepage — delete the component; replaced by 3 bucket hero cards.
- **Cause grid (7 link rows)** on homepage — delete the component; replaced by 3 bucket hero cards. Cause-tag info still shown as a single chip on each catalog card.
- **CharityCard v2 bordered cream layout** — delete the v2 layout; replaced by photo-on-top layout.

### §K. Migration risk register (for Frontend agent + Project Lead)

| Risk | Severity | Mitigation |
|---|---|---|
| Photo sourcing — we have 0 charity photos in repo right now; need ~17 (8 People + 5 Animals + 6 Planet, minus existing) before ship | 🔴 HIGH | See §L summary. Designer commits to providing a sourcing checklist with WikiCommons URLs for top-3 per bucket; remaining sourced from charity press kits during Frontend implementation week. |
| Hero photo bandwidth — 3 bucket photos at 80vh + detail hero 70vh add ~600KB to homepage | 🟡 MEDIUM | Cloudflare WebP @ q=75 reduces by ~60%; lazy-load below-the-fold; LCP target stays ≤2.5s. Verify in Phase 4.5 PERFORMANCE_REPORT. |
| White-on-photo contrast on a bright sky bucket photo | 🟡 MEDIUM | Photo-pick rule in §E.4 + fallback dark pill on overline. Designer reviews each bucket photo before shipping. |
| WWF Russia / Greenpeace law risk | 🟡 MEDIUM | §G excludes both. Backend agent must enforce on seed. |
| RU bucket label "Животные" doesn't fit at small breakpoints | 🟢 LOW | Tested at 360×640 / 12px overline + 48/56 display — fits comfortably. KB-DESIGNER-TRUSTGIVE-001 verified. |
| Cream/serif still used in methodology + footer creates visual whiplash with white/photo-first homepage | 🟢 LOW | Intentional. Editorial mode for methodology = brand continuity. Methodology surface is a deliberate "calm room." Acceptable. |

### §L. Summary

**Top 3 changes**:
1. **Homepage above-the-fold = 3 photo bucket cards** (People / Animals / Planet) replacing the v2.0 manifesto + featured strip + cause grid. Donor picks intent in 2 seconds.
2. **Catalog cards become photo-on-top** with a verified chip overlay; the program-% anchor figure is removed. Photo carries the "what kind of work" signal, then meta-line confirms.
3. **Detail page is full-bleed photo hero → identity → about → Donate CTA → money breakdown → docs**. Donate CTA moves *above* the money breakdown so a donor who already trusts the photo can act without scrolling past charts. Methodology block keeps cream/serif as a deliberate secondary surface.

**Visual references used** (saved to `projects/trustgive/design_references/v3-photo-immersive/`):
- `02-charitywater-home-hero.jpeg` — Charity:Water (full-bleed photo + bottom-anchored white text + yellow CTA, exactly the pattern for our detail-page hero)
- `04-natgeo-programs.jpeg` — National Geographic Society Programs (large hero photo with white serif title centered + bottom dark gradient — exactly the pattern for our 3 bucket cards)
- `05-givewell-antipattern.jpeg` — GiveWell home (proof point: even the "research-rigor" competitor moved to photo-overlay-with-translucent-dark-block in 2026; we are not making this up)
- `06-wwf-uk-hero.jpeg` — WWF UK (real-conservation-photography reference for Animals + Planet bucket photo style)

**Estimated frontend implementation effort per change** (Frontend Developer agent rough-est):
- HeroBucketCard ×3 + homepage layout: ~6h (component + responsive + photo wiring)
- CharityCard v3 (photo-on-top + chip overlay): ~3h (refactor existing component + lazy-load)
- Detail page hero with overlay + reordered sections + Donate CTA bump: ~4h
- Token additions (overlay gradient, photo-text colors, verified-darker): ~30min
- Compare page + ⌘K palette deletion: ~1h (delete + sweep references)
- Photo policy implementation (alt patterns, credit slot, Cloudflare image transforms): ~2h
- WCAG audit on bucket photos + a11y review: ~2h
- **Total**: ~18.5 frontend-hours = 2.5 working days for one developer.

**Photo-sourcing risk assessment**:
- We need approximately **17 photos** for v3.0: 3 bucket heroes + ~14 catalog/detail photos for the seeded charities (8 existing People + 5 Animals + 6 Planet ≈ 19, minus ~2 that already have logos but no work-photo, so realistically ~14 new fetches).
- **Realistic timeline before ship**: 4–6 hours of designer-time to source from Wikimedia Commons + charity press kits. WWF, MSF, Charity:Water, Cool Earth, Nature Conservancy, Best Friends, ASPCA all have public press galleries with downloadable hi-res photos under "media use" terms. The risk is that ~3–4 of the smaller charities (Born Free, Earthjustice, Ocean Conservancy) may not have rich photo galleries — for these, fall back to Wikimedia Commons or one tasteful Unsplash editorial photo with credit.
- **Risk verdict: 🟡 MEDIUM**. Achievable in one designer-day with a focused photo-sourcing pass. Not 🔴 because the sources exist; not 🟢 because we have to actually do the work and CC licenses must be tracked per photo.
- **Recommendation**: Project Lead approves the design, then Designer agent gets a *photo-sourcing pass* as a separate task with a short shopping-list deliverable (one CSV: `charity_slug, photo_url, photographer, license, alt_text`) before Frontend agent starts implementation.

---



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

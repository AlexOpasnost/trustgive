# Frontend — TrustGive

> **Status**: Phase 4 deliverable (awaiting Gate 4 / Phase 4.5 review)
> **Stack**: React 19 + TypeScript + Vite + TailwindCSS v4 + Hugeicons Free + i18next
> **Target**: Web-first responsive (no mobile native in MVP per SPEC §4)
> **Read first**: [`DESIGN.md`](DESIGN.md) v1.1 (especially §2 colors + §3 typography + §6 components), [`API_SPEC.md`](API_SPEC.md)

---

## 1. Project layout

```
frontend/web/
├── package.json            # 16 prod + 16 dev dependencies, all pinned
├── vite.config.ts          # Vite + Tailwind plugin + dev proxy + manual chunks
├── tsconfig.{json,app,node}
├── index.html              # Google Fonts preconnect + meta tags + OG cards
├── README.md               # quickstart for frontend dir
├── .env.example
├── .gitignore
└── src/
    ├── main.tsx            entry — initialises i18n, mounts App
    ├── App.tsx             react-query + react-router-dom
    ├── index.css           Tailwind v4 + design tokens (per DESIGN.md §2)
    ├── components/
    │   ├── layout/         Layout, TopNav (logo + nav + lang toggle), Footer
    │   └── charity/        VerificationBadge, CharityCard, MoneyBreakdown,
    │                       SourceDocumentDrawer (the wedge UI), DonateConfirmModal
    ├── pages/              HomePage, CatalogPage, CharityDetailPage,
    │                       MethodologyPage, NotFoundPage
    ├── lib/                api (fetch wrapper), utils (cn, formatUsd, formatPercent),
    │                       i18n (i18next setup)
    ├── store/              preferences (zustand persist — lang, color scheme)
    ├── types/api.ts        Hand-written types matching API_SPEC §2 (replace via gen-api)
    └── locales/            en.json + ru.json (i18next resources)
```

## 2. Design system implementation

All design tokens from `DESIGN.md` v1.1 §2 (colors), §3 (typography), §5 (spacing) are encoded as **Tailwind v4 CSS variables in `src/index.css`** under the `@theme { ... }` directive.

### Colors → Tailwind utility classes

| Token | Class | Used where |
|---|---|---|
| `--color-paper` | `bg-paper` | `<body>` background, hover backgrounds |
| `--color-surface` | `bg-surface` | Cards, charity rows |
| `--color-surface-raised` | `bg-surface-raised` | Modals, drawers |
| `--color-ink` | `text-ink` | Primary text |
| `--color-ink-2` | `text-ink-2` | Secondary text |
| `--color-ink-3` | `text-ink-3` | Captions |
| `--color-rule` | `border-rule` | All hairline borders |
| `--color-verified` | `text-verified`, `bg-verified` | Trust accent + primary CTA |
| `--color-verified-soft` | `bg-verified-soft` | Verified badge bg |
| `--color-warning`, `--color-error`, `--color-info` | `text-warning`, etc. | Semantic states |

Dark mode is activated via `<html class="dark">` toggle (per DESIGN.md §2.4); the `.dark { ... }` block in `index.css` overrides every token. A `usePreferences().colorScheme` zustand slice persists user choice — Phase 4.5 wires it to the toggle UI.

### Typography

Three free Google Fonts loaded once in `index.html` with `display=swap`:
- **Inter** (sans) — UI + body
- **Source Serif 4** (serif accents) — methodology page hero, blog
- **Geist Mono** — financial figures, EIN, the homepage `0%` callout

All three ship the `latin,cyrillic` subset for full RU rendering (per KB-DESIGNER-TRUSTGIVE-001).

### Iconography

`@hugeicons/react` + `@hugeicons/core-free-icons`. Used per-component:
- `Tick02Icon` — verified badge mark
- `Search01Icon` — search trigger pill
- `Menu01Icon` — mobile nav
- `ArrowRight01Icon`, `ArrowLeft02Icon`, `ArrowUpRight01Icon` — directional
- `Cancel01Icon` — modal/drawer close
- `LinkSquare02Icon` — outbound links in source-doc drawer
- `Download04Icon` — download action
- `FileVerifiedIcon` — homepage explainer

Tree-shaken — only the icons we import ship in the final bundle (~6KB total).

## 3. Routing + data fetching

- **react-router-dom v7** for client-side routing
- **TanStack Query v5** for data fetching, caching, dedup
- All pages co-located with their queries: `useQuery({ queryKey, queryFn: api.getCharity })`
- API client (`src/lib/api.ts`) is a thin fetch wrapper with structured types
  - When the backend is live, regenerate `src/api/schema.d.ts` via `npm run gen-api` and refactor to typed `openapi-fetch` client (Phase 4.5)

## 4. Implementation of DESIGN.md component patterns

| DESIGN.md § | Component | File |
|---|---|---|
| §6.1 Top navigation | `TopNav.tsx` | logo + nav links + ⌘K placeholder + EN/RU toggle |
| §6.2 Filter sidebar | inline in `CatalogPage.tsx` | sticky on lg+, collapses on mobile (Phase 4.5 polish) |
| §6.3 Charity card | `CharityCard.tsx` | list-row layout, hairline rule between metadata + financials |
| §6.4 Charity detail | `CharityDetailPage.tsx` | 3-col grid: money breakdown 2/3, donate+source-docs 1/3 |
| §6.5 Donate modal | `DonateConfirmModal.tsx` | 3-bullet anti-JustGiving pitch, fires donation_redirect event |
| §6.6 Methodology page | `MethodologyPage.tsx` | Source Serif body, 19px / 32px line-height, narrow column |
| §6.7 Source-doc drawer ⭐ | `SourceDocumentDrawer.tsx` | The wedge UI — Radix Dialog right-side drawer, source-attribution, PDF iframe |
| §6.8 Comparison view | not yet implemented | Phase 4.5 deliverable |
| §6.9 Empty/loading/error | inline in pages | skeletons via `.skeleton` CSS class |

## 5. i18n

`i18next` + `react-i18next` + `i18next-browser-languagedetector`. Locale files in `src/locales/{en,ru}.json` keyed by feature areas (`nav`, `home`, `catalog`, `charity`, `methodology`, `common`, `footer`).

Detection order: `localStorage` → `navigator`. Persisted under `trustgive.lang`. UI toggle in `TopNav` calls both `i18n.changeLanguage()` and the zustand `setLang()` so two state stores stay in sync.

## 6. State management

- **TanStack Query** — server state (charities, causes, source documents)
- **zustand** — minimal global UI state (`lang`, `colorScheme`)
- **react-router** — URL-as-state for filters (`?cause=animals&country=US&page=2`) so deep-linkable
- No Redux. No Context-mania. The filter state lives in URL; the user state lives in localStorage; everything else is server state.

## 7. SEO + accessibility

### SEO
- Meta tags + OG cards in `index.html`
- Per-charity SEO page payload exists at backend `/api/seo/charities/{slug}/` (Phase 3) — frontend will SSR/SSG render those in Phase 4.5+
- `index.html` has hreflang-ready meta but no SSR yet — current MVP serves a SPA; static export via `react-snap` or migration to **Vike** is a Phase 4.5 task

### Accessibility (per DESIGN.md §9)
- Visible focus ring (2px verified outline, 2px offset) baked into global `:focus-visible`
- All interactive elements are `<button>` or `<a>` — never `<div onClick>`
- Source-document drawer uses Radix `Dialog` — gives focus trap, ESC dismiss, ARIA labels for free
- `<span lang="en">` / `<span lang="ru">` wrap inline foreign-language strings (e.g. on the catalog → news mention list)
- `prefers-reduced-motion` honoured globally — animations become instant
- Skeleton loaders use luminance shifts only (no scaling/translation)
- WCAG 2.1 AA contrast preserved per DESIGN.md §2.5; full audit in Phase 4.5 by Accessibility Auditor

## 8. Bundle size strategy

`vite.config.ts` declares manual chunks for vendors so the initial JS download stays small:
- `react-vendor` (~150KB gzipped — react + react-dom + react-router-dom)
- `query-vendor` (~30KB — tanstack/react-query + openapi-fetch)
- `ui-vendor` (~40KB — radix primitives)
- `icons-vendor` (~6KB — hugeicons subset)
- `charts-vendor` (~80KB — recharts) — lazy-loaded when needed
- `i18n-vendor` (~30KB — i18next + react-i18next)

Target Lighthouse Performance ≥ 90 (per SPEC §9). Phase 4.5 Performance Engineer benchmarks.

## 9. Open items for Phase 4.5

- **Comparison page** — DESIGN.md §6.8 (max-3 charity table); not in MVP-essential first cut
- **Search palette (⌘K cmdk)** — placeholder pill in TopNav, real cmdk modal Phase 4.5
- **Mobile nav drawer** — bottom sheet on <1024px (DESIGN.md §6.2 collapsed)
- **Filter sidebar mobile drawer** — collapses to a drawer trigger on mobile
- **Dark mode toggle UI** — token system supports it; toggle component pending
- **Cause taxonomy fetch** — currently homepage hardcodes 7 causes; switch to `useCauses()` hook
- **SSR/SSG for SEO** — `react-snap` or Vike migration
- **PostHog client analytics** — wire `posthog-js` and emit pageview/filter events
- **Sentry frontend** — wire `@sentry/react`
- **`openapi-typescript` typed client** — replace hand-written types in `src/types/api.ts`
- **Tests** — Testing Engineer (Phase 4.5) writes Vitest + RTL component tests
- **E2E** — E2E Engineer (Phase 4.5) writes Playwright tests for critical journeys
- **Accessibility audit** — Accessibility Auditor (Phase 4.5) runs axe-core

## 10. Local development workflow

```bash
# In two terminals:

# Terminal 1 — backend
cd projects/trustgive/backend
python manage.py runserver

# Terminal 2 — frontend
cd projects/trustgive/frontend/web
npm install                    # first time only
npm run dev
# → http://localhost:5173 with backend proxy at /api/*
```

## 11. Deployment plan (Cloudflare Pages — finalized in Phase 7)

```
Build command:   npm run build
Output dir:      dist/
Environment:
  VITE_API_BASE_URL = https://api.trustgive.org
  VITE_POSTHOG_API_KEY = phc_...
  VITE_SENTRY_DSN = ...
Headers:         Cloudflare default (frontend bundle is fully cacheable)
```

The `/api/*` paths route to Railway-hosted Django via DNS — Cloudflare Pages proxies nothing. CORS is handled at the Django side (Phase 4.5 wires it once we know the domain).

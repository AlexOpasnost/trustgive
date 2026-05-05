# TrustGive web frontend

React 19 + TypeScript + Tailwind v4 + Vite + Hugeicons + i18next.

## Quickstart

```bash
cd frontend/web
cp .env.example .env.local       # edit if backend is not on localhost:8000
npm install
npm run dev                      # http://localhost:5173
```

The dev server proxies `/api/` to `VITE_API_BASE_URL` (default `localhost:8000`) so the SPA can call the Django backend without CORS setup.

## Useful scripts

```bash
npm run build         # production build to dist/
npm run preview       # preview built bundle
npm run typecheck     # tsc --noEmit
npm run lint          # eslint
npm run gen-api       # regenerate src/api/schema.d.ts from running backend
npm test              # vitest (Phase 4.5 adds tests)
```

## Layout

```
src/
├── main.tsx             entry
├── App.tsx              router + react-query provider
├── index.css            Tailwind v4 + design tokens (per DESIGN.md §2)
├── components/
│   ├── layout/          TopNav, Footer, Layout
│   └── charity/         CharityCard, MoneyBreakdown, SourceDocumentDrawer,
│                        DonateConfirmModal, VerificationBadge
├── pages/               HomePage, CatalogPage, CharityDetailPage,
│                        MethodologyPage, NotFoundPage
├── lib/                 api, utils, i18n
├── store/               preferences (zustand persist — lang, color scheme)
├── types/api.ts         Hand-written API types (replace via `npm run gen-api`)
└── locales/             en.json, ru.json (i18next resources)
```

## Design system

All colors, fonts, and sizing come from CSS custom properties defined in
`src/index.css` under `@theme { ... }` (Tailwind v4 CSS-first config). Edit
those tokens to update the design system globally.

Fonts loaded from Google Fonts:
- **Inter** (sans, full Cyrillic)
- **Source Serif 4** (display accents, full Cyrillic)
- **Geist Mono** (numbers + tabular data)

Icons: `@hugeicons/react` + `@hugeicons/core-free-icons` — 5,100+ free icons.

## Deployment (Cloudflare Pages — planned for Phase 7)

- Build command: `npm run build`
- Output directory: `dist/`
- Environment variable: `VITE_API_BASE_URL=https://api.trustgive.org`
- Caching: Cloudflare default; backend `/api/*` requests cached separately at the API origin (per ADR-007).

## SSR / SSG note

Phase 4 ships a **client-rendered SPA**. SEO landing pages (the `Is X legitimate?` story per SPEC §11) are crawlable via the API endpoint `/api/seo/charities/{slug}/` but full SSG is a Phase 4.5+ task — likely via `react-snap` or migrating to Vike.

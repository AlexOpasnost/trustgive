# Mobile QA + Lighthouse Audit — v3.14.1

**Date:** 2026-05-11
**Commit:** a5aec69 · `latest_migration=0056_backfill_v314_logos`
**Catalog state:** 541 charities, 27 countries
**Auditor:** Project Lead, via Playwright MCP + npx lighthouse (Chrome headless)

---

## Executive summary

The site has a strong foundation — accessibility and best-practices both score 100/100, console is clean on normal pages, the **8 region chips wrap cleanly** at every tested viewport (the original concern is resolved), and the photo-first immersive design holds up at 320 px (smallest tested). However, the audit uncovered **three production bugs that visibly affect users and four polish issues**:

| Severity | Count |
|---|---|
| 🔴 Critical | 3 |
| 🟡 Major | 3 |
| 🟢 Minor | 6 |

The most consequential finding is that **241 of the 541 seeded charities are unreachable through the UI** — `/charities` renders the first 300 with no pagination control. Combined with the bucket-count bug ("6 verified charities" on the homepage, while the buckets actually hold 62-393), this means the homepage shows a number 60× smaller than the actual catalog and the catalog page is missing ~45% of inventory. For a portfolio piece whose differentiator is "541 verified charities", that is a quality gap worth fixing before any further outreach.

---

## Viewports tested

| Viewport | Device class | Pages |
|---|---|---|
| 360 × 800 | Android (Pixel-ish) | `/`, `/charities`, `/charities/givewell`, `/methodology` |
| 414 × 896 | iPhone 11 / 12 Pro | `/` |
| 320 × 568 | iPhone SE / smallest | `/`, `/charities`, `/charities/givewell`, `/methodology` |
| 1440 × 900 | Desktop / portfolio | `/`, `/charities?region=europe`, `/charities/nami-national` |

All screenshots saved to `screenshots/mobile-qa-2026-05-11/` and `screenshots/portfolio-2026-05-11/`.

---

## 🔴 Critical findings

### C-1 — Homepage bucket counts are stale (shows "6", actual is hundreds)

**Where:** Homepage, all viewports. Each of the three bucket cards (People / Animals / Planet) shows the subtitle "6 verified charities" / "6 проверенных фондов".

**Reality (API, today):**
- `?bucket=people` → **393** charities
- `?bucket=planet` → **86** charities
- `?bucket=animals` → **62** charities

**Root cause:** [HomePage.tsx:73-74](frontend/web/src/pages/HomePage.tsx#L73-L74)
```ts
const first: CharitySummary | undefined = data && data.length > 0 ? data[0] : undefined
const count = data?.length ?? 0
```
The `count` is the length of the **featured charities array** (capped server-side at 6), not the total bucket size. This was correct when the catalog had ~18 charities (3 buckets × 6). With 541 charities, it under-reports by a factor of ~60.

**Fix path:**
- **Option A** (server-side, recommended): extend the `/api/charities/featured/?bucket=X` response with a `total_count` field. Single round-trip stays.
- **Option B** (client-side): fire a separate `HEAD`-style fetch per bucket (`?bucket=X&page_size=1` and read `data.count`). Three extra round-trips on home page load.

**Recommendation:** Option A — backend change to `FeaturedCharitiesView` to wrap response in `{featured: [...], total_count: N}` or add a `meta` object.

---

### C-2 — `/charities` only renders the first 300 of 541 charities

**Where:** `/charities`, all viewports. Subheader explicitly says "Showing 1–300 of 541". After the 300th card, the footer appears — no Load-more button, no pagination control, no infinite scroll, no `?page=2` URL handling.

**Effect:** 241 charities (44.5% of catalog) are invisible to discovery via the catalog page. Users can still reach them via direct slug URLs, but there is no UI surface.

**Root cause:** [CatalogPage.tsx:53-55](frontend/web/src/pages/CatalogPage.tsx#L53-L55)
```ts
// Render the full catalog without paginate-controls UI. Bumped to 300
page_size: 300,
```
The "render full catalog without pagination" approach was reasonable when total < 300. Now broken.

**Fix paths (pick one):**
- **A** — Bump `page_size: 600` (quick fix, still capped, future-proof for ~12 months at current growth rate).
- **B** — Add a "Load more" button at the bottom that pages `?page=2`, `?page=3` (idiomatic, scales).
- **C** — Implement infinite scroll with `IntersectionObserver` (slicker but more code).

**Recommendation:** **B** (Load-more button). Simplest, fewest moving parts, works without JS scroll listeners, doesn't change SEO crawl pattern.

---

### C-3 — Hero photos broken in Chrome on detail pages (ORB block)

**Where:** Many `/charities/{slug}` pages on desktop and likely mobile. Verified broken: `msf-usa`, `save-the-children`. Verified working: `nami-national`, `givewell`.

**Network trace** (Save the Children, Chrome 1440 viewport):
```
[GET] https://images.weserv.nl/?url=upload.wikimedia.org%2Fwikipedia%2F
      commons%2F6%2F67%2FProviding_check-ups_for_newborn_children...
      .jpg&w=1600&q=80&output=webp&fit=cover
      => [FAILED] net::ERR_BLOCKED_BY_ORB
```

**Root cause:** Chrome's [Opaque Response Blocking (ORB)](https://chromestatus.com/feature/4933964059377664) silently blocks `image/webp` responses from cross-origin URLs that look like they may be data exfiltration. The `output=webp` parameter on `images.weserv.nl` + the Wikimedia source URL triggers this. NAMI (Unsplash source) works because Unsplash sets the right cross-origin headers and weserv proxies them through.

**Fix paths:**
- **A** — Drop `output=webp` from the weserv URL template for the hero variant; let weserv default to source mime (`image/jpeg` from Wikimedia). Loses ~30% size savings but unblocks rendering.
- **B** — Add `&we=*` (CORS) or `&af=1` (force ASCII output) to weserv URL — neither will help with ORB directly, but `af=1` removes some attack signals.
- **C** — Add `crossorigin="anonymous"` to the `<img>` tag — sometimes prevents ORB.
- **D** — Switch image proxy: Cloudflare Images, imagekit.io, or self-host via a Cloudflare Worker.

**Recommendation:** **A** as quick fix today (10-line change, instant restore). **D** as proper long-term fix (Cloudflare Worker → already on Cloudflare for the frontend, zero new dependencies).

**Affected charities (estimate):** ~280 of ~340 with hero photos use Wikimedia source — so potentially ~80% of hero photos are broken in Chrome.

---

## 🟡 Major findings

### M-1 — Photo credit overlay overlaps subtitle at 320px on detail page

**Where:** `/charities/{slug}` at 320 × 568. The white photo-credit microtext (`Cover: ... — Photo: Source: ...`) renders on top of the subtitle ("Independent research finding the best giving opportunities").

**Fix:** push photo credit to a fully-discrete bottom row or move into a small footer band beneath the hero. Or apply `min-width: 360px` styling and reduce font size further at <360px. Check `CharityDetail` hero component for absolute positioning at small breakpoints.

---

### M-2 — Mobile Lighthouse LCP at 6.2s (poor)

**Lighthouse mobile** (slow 4G + CPU throttle simulation):

| Category | Score |
|---|---|
| Performance | **71** (poor) |
| Accessibility | **100** ✅ |
| Best Practices | **100** ✅ |
| SEO | **92** |

Core Web Vitals — mobile:
- **LCP: 6.2 s** (score 11) — well above the 2.5 s good threshold
- FCP: 2.8 s (score 56) — needs improvement
- TBT: 50 ms (score 100) ✅
- CLS: 0 (score 100) ✅
- Speed Index: 4.2 s (score 77)

Lighthouse desktop is healthier: **Performance 89**, LCP 1.8s.

**Action items:**
- Add `<link rel="preload" as="image">` for the above-the-fold hero photo on `/`
- Cap hero image width via responsive `srcset` (currently always w=1600 even on mobile)
- Code-split: Lighthouse reports **112 KB unused JS** in `index-BG8cU6lK.js`
- Eliminate legacy JS polyfills via Vite `target: 'es2020'` if not already set

---

### M-3 — 404 detail page shows generic error, not "Not found"

**Where:** `/charities/nonexistent-slug` → "Something went wrong. This is on us, not on the charity. Please try again in a moment."

**Issue:** A 404 (charity slug doesn't exist) is treated as a 5xx-style retryable error. Real users hitting an old link or typo will see a misleading message and may report it as broken when it's just a stale URL.

**Fix:** in the detail page error handler, branch on `error.response?.status === 404` and render a distinct "Charity not found" page with a link back to /charities.

---

## 🟢 Minor findings

### N-1 — Bucket card aria-label missing "BROWSE BY CAUSE" overline

Lighthouse `label-content-name-mismatch` rule fires on all 3 bucket cards: the aria-label is `"People — 6 verified charities"` but the visible text includes "BROWSE BY CAUSE". Fix: wrap overline in `aria-hidden="true"` (decorative anyway).

[HeroBucketCard.tsx:108-114](frontend/web/src/components/home/HeroBucketCard.tsx#L108-L114)

### N-2 — Detail page has duplicate H2 in "Where the money goes" section

Two `<h2>` elements stacked: "Where the money goes" (section) and "How they spend the money" (card inside). Semantically odd. Demote the inner one to `<h3>` or `<p>` with display-heading typography.

### N-3 — robots.txt is not valid

Lighthouse SEO audit flags malformed `robots.txt`. -8 SEO points. Check `frontend/web/public/robots.txt`.

### N-4 — Unused JS bundle: 112 KB

Lighthouse reports `index-BG8cU6lK.js` ships 112 KB the user never executes on home page. Candidates: react-router routes that aren't used on `/`, charts/icons libraries imported eagerly. Run `vite build --report` or `npx vite-bundle-visualizer` to drill in.

### N-5 — Homepage People bucket has no hero photo

Desktop and mobile both show the dark stone-gradient fallback for the People bucket. The featured charity for People apparently has no `hero_photo_url`. Either: (a) re-rank `FeaturedCharitiesView` to prefer charities with `hero_photo_url IS NOT NULL`, or (b) backfill the featured charity's hero photo manually.

### N-6 — Page title is identical on every route

All pages show `<title>TrustGive — Verified charity discovery</title>`. Consider per-route titles for SEO + browser tab UX: `Charities · TrustGive`, `{Charity name} · TrustGive`, `Methodology · TrustGive`.

---

## ✅ What's working well

- **8 region chips wrap cleanly** at all 3 mobile viewports (the original concern that triggered this audit). 360px → 3 rows. 320px → 4 rows. 414px → 2 rows. No horizontal scroll. No overflow.
- **Header at all widths** is clean — logo + EN/RU toggle + hamburger fit at 320px without wrap.
- **/methodology** is excellent at every viewport — readable serif headings, scan-able structure, no overflow.
- **Bilingual EN/RU** language toggle visible and functional everywhere.
- **A11y baseline: 100/100** (with one minor finding above).
- **Best practices: 100/100**.
- **CLS: 0** at all viewports — no layout shift after first paint.
- **Zero console errors** on `/`, `/charities`, `/charities/{valid-slug}`, `/methodology` in Chrome.
- **CDN caching** working — pages load <1s on warm cache (desktop FCP 0.9 s).

---

## Lighthouse — full breakdown

### Mobile (slow 4G + CPU throttle)
```
performance      71
accessibility    100
best-practices   100
seo               92

FCP   2.8 s   (poor)
LCP   6.2 s   (poor)   ← M-2
TBT    50 ms  (good)
CLS    0      (good)
SI    4.2 s   (poor)
TTI   6.2 s   (poor)
```

### Desktop
```
performance      89
accessibility    100
best-practices   100
seo               92

FCP   0.9 s   (good)
LCP   1.8 s   (needs-improvement)
TBT    0 ms   (good)
CLS    0      (good)
SI    1.7 s   (needs-improvement)
TTI   1.8 s   (good)
```

Raw JSON saved to `screenshots/mobile-qa-2026-05-11/lh-mobile-real.json` and `lh-mobile.json` (desktop preset, naming-mismatch — first run was desktop).

---

## Screenshots index

### Mobile QA (`screenshots/mobile-qa-2026-05-11/`)
- `home-360x800.png` · `home-414x896.png` · `home-320x568.png`
- `charities-360x800.png` · `charities-360x800-bottom.png` · `charities-320x568.png`
- `charities-360x800.snapshot.md` (accessibility tree)
- `detail-360x800.png` · `detail-320x568.png`
- `detail-360x800.snapshot.md` · `detail-360x800-console.log`
- `methodology-360x800.png` · `methodology-320x568.png`
- `home-360x800.snapshot.md`

### Portfolio (`screenshots/portfolio-2026-05-11/`)
- `portfolio-home-desktop.png` — 1440×900 homepage (3-bucket hero strip)
- `portfolio-catalog-europe-desktop.png` — 1440×900 /charities filtered to Europe (172 orgs)
- `portfolio-detail-desktop.png` — 1440×900 NAMI detail page (working hero photo)
- `portfolio-detail-desktop-full.png` — 1440×900 NAMI full-page (above + below the fold)

---

## Recommended fix order (next session)

1. **C-3 hero photo ORB block** — quick fix, restores visible quality. Drop `output=webp` from weserv URL template.
2. **C-2 catalog pagination** — add Load-more button. Unblocks 241 invisible charities.
3. **C-1 bucket counts** — backend tweak to featured endpoint to return `total_count`.
4. **M-3 404 page** — UX correctness.
5. **M-1 photo credit overlap at 320px** — small CSS fix.
6. **M-2 LCP optimization** — bigger effort. Image preload + responsive srcset + bundle split.

Items N-1 through N-6 are polish; do in a single sweep after M-2.

---

## <reflection>
<what_went_well>
  - Playwright MCP unblocked this session — first mobile QA pass ever performed on TrustGive.
  - Caught three production bugs that would have made the catalog look 60× smaller and 44% incomplete on a portfolio review. Worth the audit time.
  - 8 region chips concern (the original trigger) is comprehensively resolved — wraps cleanly at 320, 360, 414. No CSS work needed there.
  - Lighthouse a11y 100 / BP 100 / CLS 0 are real wins — the photo-first design didn't trade off basics.
</what_went_well>
<challenges>
  - Playwright MCP file-output sandbox restricted writes to .claude/ — had to move screenshots via Bash after each capture. Workaround works but adds 1 step per shot.
  - PageSpeed Insights API quota is 0/day without API key for anonymous IPs — fell back to local npx lighthouse, which works but EPERMs on cleanup (Windows tempdir lock). JSON was complete despite the error.
  - Three different charity slug guesses (doctors-without-borders, save-the-children, msf-usa) failed before NAMI gave a working hero photo for the portfolio screenshot — wikimedia-source heroes are broken at large widths.
</challenges>
<lessons_learned>
  - When the homepage subtitle shows `data?.length`, it works at small scale and silently goes wrong at scale. Future similar fields should explicitly fetch totals, not derive from arrays. KB-WORTHY.
  - "Render full catalog without pagination" works until catalog crosses the page_size cap, then silently truncates. Always test scroll-to-end on catalog pages after each large seed batch. KB-WORTHY.
  - weserv.nl + Chrome ORB + webp output is a known cross-origin trap. Document the working URL pattern (Unsplash sources OK, Wikimedia sources blocked at w=1600 webp). KB-WORTHY.
  - Lighthouse desktop preset is a more honest baseline for portfolio audiences (they're mostly on desktop), but mobile preset is the SEO/Core Web Vitals score Google's crawler uses.
</lessons_learned>
<knowledge_to_store>
  YES — three KB entries worth: (1) catalog page_size cap silently truncates without pagination UI, (2) `data?.length` as count is footgun at scale, (3) weserv.nl + webp + Wikimedia → ORB block in Chrome.
</knowledge_to_store>
</reflection>

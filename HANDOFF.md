# HANDOFF — tasks that need you

These are the things I can't finish from the codebase alone — they need your
accounts, your dashboards, or a decision only you can make. Each one has: what
it is, why it matters, exact steps, and a rough time estimate.

Ordered by impact. Top one is the biggest single win still on the table.

---

## 1. Make the API edge-cacheable — fixes the mobile performance score

**Status:** 🔴 highest-leverage perf fix left. ~20 min.

**The problem.** `GET /api/charities/featured/?bucket=people` takes ~0.9 s.
The Django backend *does* set `Cache-Control: s-maxage=120` on it, but the
response reaches the browser with no `Cache-Control` header at all, and
Cloudflare reports `cf-cache-status: DYNAMIC` — i.e. it's not edge-cached.
Every homepage load waits ~0.9 s for that API call before it even knows which
hero image to load. That's why Lighthouse mobile LCP is ~8 s.

**Two things to check / fix:**

### 1a. Why is the `Cache-Control` header missing from the response?

The middleware at `backend/apps/core/middleware.py` sets `Cache-Control` by
URL name, and `backend/trustgive/settings/base.py` has the right directive
(`"charity-featured": "public, s-maxage=120, ..."`). But the live response has
no such header. Likely causes to check, in order:

1. The middleware ordering in `settings/base.py` `MIDDLEWARE` — the
   Cache-Control middleware has to run *after* the view, i.e. be near the top
   of the list (middleware runs bottom-up on the response).
2. The URL name resolution — DRF `@action(url_name="charity-featured")`
   resolves to a URL name that might be namespaced (e.g. `api:charity-featured`
   or `charities:charity-featured`). Add a `print(resolve(request.path).url_name)`
   in the middleware temporarily and hit the endpoint to see the real name,
   then make sure the `CACHE_CONTROL_BY_NAME` dict key matches it exactly.

To test locally:
```bash
cd backend
RAILWAY_TOKEN=<token> railway run python manage.py runserver
# then in another shell:
curl -sD - http://localhost:8000/api/charities/featured/?bucket=people | grep -i cache-control
```

### 1b. Add a Cloudflare Cache Rule so the edge actually caches it

Even with the header fixed, Cloudflare won't cache `api.*` JSON by default —
it needs an explicit rule.

1. Cloudflare dashboard → your `trustgive.org` zone → **Caching → Cache Rules**.
2. **Create rule**, name it `API — featured + catalog`.
3. **When incoming requests match:**
   `URI Path` `starts with` `/api/charities/featured` — then add an "Or" row:
   `URI Path` `starts with` `/api/charities/` (this also covers catalog +
   detail; fine, they all have `s-maxage` set).
4. **Then:**
   - Cache eligibility → **Eligible for cache**
   - Edge TTL → **Use cache-control header if present, bypass cache if not**
     (so a missing header fails safe rather than caching forever)
   - Browser TTL → **Respect origin**
5. Deploy.

**Verify:** `curl -sD - https://api.trustgive.org/api/charities/featured/?bucket=people | grep -i cf-cache-status`
— first hit `MISS` or `EXPIRED`, second hit within 120 s `HIT`. The endpoint
should drop from ~900 ms to ~20 ms on a hit.

**Then:** purge the CF cache once and re-run Lighthouse — mobile Performance
should jump back up (the ~0.9 s API wait is most of the current LCP).

---

## 2. Wire up Sentry — currently disabled

**Status:** 🟡 the health endpoint reports `sentry: disabled`. ~15 min.

The backend has the Sentry SDK integrated in code — it's just not getting a
DSN, so it no-ops. Right now if the API throws a 500 in production, you find
out only if you happen to check Railway logs.

1. Go to [sentry.io](https://sentry.io) → create a free account if you don't
   have one (the free tier is 5k errors/month — plenty).
2. **Create project** → platform **Django** → name it `trustgive-backend`.
3. Copy the **DSN** (looks like `https://abc123@o12345.ingest.sentry.io/678`).
4. Railway dashboard → `trustgive` service → **Variables** → add:
   `SENTRY_DSN` = `<the DSN>`
5. Railway redeploys automatically. Verify: the health endpoint
   (`https://trustgive-production.up.railway.app/api/health/`) should now show
   `"sentry": "ok"` instead of `"disabled"`.
6. Optional sanity check: temporarily add a `/api/debug-sentry/` view that
   does `raise Exception("sentry test")`, hit it once, confirm it shows up in
   Sentry, then remove it.

---

## 3. Submit the sitemap to Google Search Console

**Status:** 🟡 the site is invisible to Google search until you do this. ~10 min.

`https://trustgive.org/sitemap.xml` is now live (544 URLs, regenerated from the
API every 6 hours). Google won't find it on its own for a fresh domain.

1. [search.google.com/search-console](https://search.google.com/search-console)
   → **Add property** → `https://trustgive.org`.
2. Verify ownership — easiest is the **DNS TXT record** method: Search Console
   gives you a `google-site-verification=...` string, you add it as a TXT
   record in the Cloudflare DNS dashboard for `trustgive.org`, wait a few
   minutes, click verify.
3. Once verified → **Sitemaps** (left sidebar) → enter `sitemap.xml` → Submit.
4. Same for **Bing Webmaster Tools** ([bing.com/webmasters](https://www.bing.com/webmasters))
   if you want — Bing also feeds DuckDuckGo. Bing can import directly from
   Search Console, so it's a 2-minute add once GSC is done.

This is what gets the 541 charity pages indexed — each one is a long-tail
search target ("is X charity legitimate", "X charity 990").

---

## 4. Fix the backend test suite — it points at the production database

**Status:** 🟡 `pytest` currently can't run. ~30 min, and it needs a decision from you.

When I tried to run the backend tests, pytest-django connected to the **live
Neon production database** and tried to apply all 57 migrations on top of the
real 541-charity data — which fails on a duplicate-slug constraint. The tests
need their own throwaway database.

The app uses Postgres-specific features (full-text search, `pg_trgm`, JSONB),
so SQLite-in-memory won't work as the test DB. You need a real Postgres for
tests. Two options — pick one:

**Option A — local Docker Postgres (recommended, fully offline):**
1. Add to `backend/docker-compose.test.yml`:
   ```yaml
   services:
     test-db:
       image: postgres:17
       environment:
         POSTGRES_DB: trustgive_test
         POSTGRES_USER: trustgive
         POSTGRES_PASSWORD: trustgive
       ports: ["5433:5432"]
   ```
2. Create `backend/trustgive/settings/test.py` that reads a
   `TEST_DATABASE_URL` env var (default `postgres://trustgive:trustgive@localhost:5433/trustgive_test`).
3. `backend/pytest.ini` → `DJANGO_SETTINGS_MODULE = trustgive.settings.test`.
4. Run: `docker compose -f docker-compose.test.yml up -d && pytest`.

**Option B — a Neon branch (uses the cloud, zero local setup):**
1. Neon dashboard → your project → **Branches** → create a branch called
   `test` off `main`. You get a separate connection string.
2. Set `TEST_DATABASE_URL` to that branch's connection string.
3. Same `settings/test.py` + `pytest.ini` as Option A.
4. The branch is isolated — pytest can drop/recreate freely without touching
   production.

I can write the `settings/test.py` + `pytest.ini` + `docker-compose.test.yml`
for you in the next session — just tell me A or B. The reason it's a "you"
task is the decision (local vs cloud) and, for B, creating the Neon branch.

---

## 5. The LinkedIn / portfolio write-up

**Status:** 🟢 needs your voice and your account. The repo is ready to point at.

The project is in a good state to write about now — README is clean, the
CHANGELOG tells the real story, the site is live and fast enough. What I can't
do is post as you or invent your personal angle. Here's a skeleton you can
fill in — the facts are all accurate, the voice needs to be yours:

> I spent a week building **TrustGive** — a discovery platform for 541
> verified charities across 27 countries. The idea: instead of a star rating
> you can't audit, it links you straight to the regulator's filing (IRS 990,
> UK Charity Commission, etc.).
>
> What surprised me most: the infrastructure — Django + React + Cloudflare +
> Postgres — was maybe a day of work. The other six days were *curation*.
> Finding the right regulator URL for a charity in Finland. Getting the EIN
> right. Writing a two-sentence description in English *and* Russian that
> doesn't read like marketing. That's the part that doesn't scale, and it's
> the part that makes the catalog worth anything.
>
> [your angle here — why charity transparency, what you'd do differently,
> what the MBA connection is]
>
> Live: trustgive.org · Code: github.com/AlexOpasnost/trustgive

Things worth showing in the post: a screenshot of the homepage (the three
photo buckets look good), and maybe the CHANGELOG — a 2000-line decision log
is unusual and reads as "this person actually thinks about trade-offs."

If you want, I can draft 2-3 full versions in the next session and you pick
one — but the *posting* and the personal-narrative paragraph are yours.

---

## 6. Optional / lower priority

- **Token rotation.** The Cloudflare and Railway API tokens were pasted into
  chat earlier. You said you don't want to rotate them — your call, just be
  aware they're recoverable from chat history if it ever leaks. If you change
  your mind: CF → My Profile → API Tokens → Roll; Railway → Account → Tokens.
- **`og:image` backfill for the ~200 photo-less charities.** Sites like NAMI,
  ALS, Komen block bots, so the scraper can't get their `og:image`. Not a
  "you" task exactly — I can do batches of manual press-photo backfill in a
  future session — but *picking which 10-20 orgs are most worth it* is a
  judgment call you might want in on.
- **Cloudflare Image Transformations** — if you ever want true on-the-fly
  resize for *non-Wikimedia* images (charity-site photos at arbitrary widths),
  CF has a built-in feature (Speed → Optimization → Image Transformations →
  enable). Free tier is 5,000 transformations/month. Not needed right now —
  the Worker handles Wikimedia fine and non-Wikimedia images already come
  pre-sized — but it's the escape hatch if image sourcing changes.

---

## Quick reference — what's already done (v3.17, 2026-05-14)

So you don't redo any of it:

- ✅ Image proxy (`/img/v1`) — Wikimedia thumbnails, edge-cached, ORB-safe
- ✅ `/sitemap.xml` — live, 544 URLs, auto-regenerated
- ✅ `robots.txt` — valid
- ✅ Responsive `srcset` on all images
- ✅ Per-route page titles
- ✅ Homepage bucket counts honest (236 / 51 / 64, not "6")
- ✅ Catalog pagination — all 541 reachable
- ✅ Hero photos render in Chrome (the ORB bug is fixed)
- ✅ Migration 0057 — the 3 photo-less featured charities backfilled
- ✅ README rewritten in a human voice
- ✅ Accessibility 100, Best-practices 100, SEO 100 (Lighthouse mobile)

The one number still soft is **mobile Performance (~67)** — and item #1 above
is the fix for it.

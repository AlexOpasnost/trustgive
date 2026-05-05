# ADR-002 — Authentication strategy: NO auth in MVP

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer, per SPEC.md §3 + §6 + MARKET_ANALYSIS.md §5 RECOMMENDATION 1
- **Supersedes**: —

## Context

TrustGive's MVP is a **public, anonymous charity discovery tool**. Per SPEC §6:
- No user accounts
- No payments
- No personalisation (favourites, history, recommendations)
- No notifications

User preference state (language, dark mode) lives entirely in `localStorage` (DESIGN.md §6.1). We have only two principal types in MVP:

1. **Anonymous public users** — the entire SPEC user-story set (Stories 1–6) is performable without any account.
2. **Internal operators** (Alex, manually) — run management commands to ingest charities, edit curated RU records, regenerate sitemaps. Access is via SSH/Railway shell, never via the public API.

## Decision

**Ship MVP with zero user-facing authentication.** No `/api/auth/login/`, no JWT, no sessions for public users. Public API endpoints are all `permissions.AllowAny`. Internal admin access uses the standard Django admin with **session-based auth** restricted to staff users on a dedicated subdomain (`admin.trustgive.org`) protected by Railway IP allowlist + Cloudflare Access if traffic warrants it.

The single write endpoint exposed to the public — `/api/events/donation-redirect/` — is unauthenticated but heavily rate-limited (10/min per IP, ADR-007).

## Consequences

### Positive
- **~1 week of dev time saved**: no login UI, no password-reset flow, no email-verification, no GDPR consent banners for account data, no account-deletion flow, no session storage, no JWT refresh logic.
- **Reduced attack surface**: no credential-stuffing, no password leaks, no account-enumeration, no JWT-secret rotation.
- **Aligned with positioning** (MARKET_ANALYSIS §5): JustGiving and Charity Navigator complaints frequently cite forced sign-up.
- **Privacy-first**: we store no PII for users; GDPR exposure is limited to IP addresses in 7-day rolling logs (see ADR-008).
- **Simpler caching**: every catalog request is the same for every user → CDN cacheable for everyone (ADR-007).

### Negative
- **Bookmarking via account is impossible.** Mitigated by SPEC's "saved-search via shareable URL" Could-Have feature (filters in URL params).
- **Migration path required for v2** if/when accounts arrive — documented below.
- **No per-user analytics**: PostHog distinct_id falls back to anonymous device ID (cookie-less mode). Acceptable for funnel analysis, not for cohort analysis.

### Neutral
- Frontend never needs an `Authorization` header in MVP. TypeScript SDK generated from OpenAPI never sets one.

## v2 migration path (when accounts ship)

If/when SPEC v2 reintroduces accounts (favourites, custom feeds, donation history aggregation):

1. Add `apps.users` Django app with custom `User` model (not `AbstractUser` — give us flexibility on identifier choice).
2. Adopt **`djangorestframework-simplejwt`** for stateless JWT auth (access + refresh tokens). Choice committed now to avoid bikeshedding later. Reasons: stateless (no session table), industry-standard, plays well with separate React frontend, supports refresh-token rotation, supported by drf-spectacular OpenAPI security schemas.
3. Add OAuth via `django-allauth` for Google/GitHub login — defer email/password if possible, since password storage is dead weight.
4. New endpoints (`/api/auth/...`, `/api/users/me/...`, `/api/favorites/...`) live under `permissions.IsAuthenticated`.
5. **Existing 10 public endpoints stay anonymous-readable** — DRF `AllowAny` on read methods, `IsAuthenticated` on any new write methods.
6. Argon2 password hasher (`PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher', ...]`) per backend-developer security rules.
7. Rate-limit auth endpoints aggressively (5/min/IP for login, 3/hour/IP for password reset).

This roadmap is a **plan, not a commitment** — accounts only ship if user research after launch shows demand.

## Internal operator auth (current)

| Path | Access |
|---|---|
| `/admin/` Django admin (charity curation, RU manual records) | Staff session login, restricted to `admin.trustgive.org` if separated |
| `python manage.py ingest_*` management commands | Run via Railway CLI shell or GitHub Actions (cron); not exposed via HTTP |
| Sentry, Railway, PostHog dashboards | Vendor-side OAuth |

Production `SECRET_KEY`, `DATABASE_URL`, `SENTRY_DSN`, `EVERY_ORG_PRIVATE_KEY` live only in Railway Variables (DEVOPS.md §"Secrets management"). `.env.example` ships placeholder values per backend-developer rules.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **Build full account system in MVP** (`djangorestframework-simplejwt` + email/password) | Adds ~1 week of work for zero MVP feature unlocked. SPEC explicitly puts accounts in "Won't Have v1". |
| **OAuth-only (Google/GitHub login) in MVP** | Same dev cost as JWT (less, even), but still no MVP user-story benefit. Could be a candidate if a future Should-Have requires it. |
| **API key per consumer** (e.g. for partner integrations) | No partner integrations in MVP; the API is meant for our own frontend + crawlers. |
| **Anonymous session cookies + CSRF** | Adds complexity for catalog browsing where we have no per-session state worth tracking. localStorage covers UI prefs. |
| **Auth0 / Clerk / Supabase Auth** | Vendor lock-in for a feature we don't have. $0-budget compatible but adds an unnecessary vendor. |

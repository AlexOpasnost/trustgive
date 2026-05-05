# ADR-001 — Database: PostgreSQL 17 with charity-specific indexing

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer (Phase 2.5), per SPEC.md §6 + DEVOPS.md
- **Supersedes**: —

## Context

TrustGive aggregates ~1.2M charity records from three external registries (ProPublica, Every.org, CharityBase) plus 30 manually curated RU charities. The dataset is **read-heavy** (catalog browsing, faceted filtering, single-charity detail views, SEO landing pages crawled by Google), with periodic batch writes from nightly ETL jobs. We need:

- Geo-faceted filtering (`country`)
- Multi-cause facet (`cause_tags[]`) — array containment
- Verification + size + badge filters
- Alphabetical sort + financial-metric sort
- Slug-based URL lookups (SEO requires stable, human-readable URLs)
- Full-text search on charity name + description (English **and** Russian)
- Composite year-based queries on `Financial(charity_id, year)` for historical breakdowns
- Bilingual (EN+RU) data storage — see ADR-006

Hosting is locked to **Railway** with PostgreSQL 17 already provisioned (Project ID `09bd8e82-2325-4e13-8404-fe3f1832a0dd`, see DEVOPS.md). $0/mo budget rules out managed alternatives.

## Decision

Use **PostgreSQL 17** as the single source of truth for all application data. Schema-level commitments:

**Indexes (created in initial migration unless noted)**:
- `Charity.slug` — UNIQUE btree (URL lookup; SEO landing pages)
- `Charity.country` — btree (catalog facet)
- `Charity.verification_status` — btree (catalog facet)
- `Charity.cause_tags` — **GIN** (multi-value containment: `cause_tags && ARRAY['animals','climate']`)
- `Charity.size_bucket` — btree (small/medium/large filter; computed at ingestion)
- `Charity.is_stale` — btree (>24mo filing flag, used in default sort + UI banner per DESIGN.md §6.9)
- `Charity.last_filed_date` — btree DESC (default catalog sort: "most recent filing")
- `Charity.total_revenue_usd` — btree DESC (sort: "largest revenue")
- `Financial(charity_id, year DESC)` — composite btree (charity detail page pulls latest filing first)
- `SourceDocument(charity_id, kind)` — composite btree (drawer queries by document type)
- `IngestionLog(source, started_at DESC)` — composite btree (ops audit)
- `Charity.search_vector` — **GIN** on tsvector column populated via trigger (FTS — see ADR-005)
- `Charity.name_trgm` — **GIN** with `gin_trgm_ops` for typo-tolerant search (extension `pg_trgm`)

**Extensions enabled at migration time**:
- `pg_trgm` (fuzzy matching for ETL deduplication and search)
- `unaccent` (Cyrillic + diacritic-insensitive FTS)
- `btree_gin` (allows mixed btree+GIN composite indexes if needed later)

**Connection management**: `psycopg[binary]` 3.x driver, connection pooling via `CONN_MAX_AGE=300`. Railway Postgres on hobby tier supports ~100 concurrent connections — sufficient for SPEC §9 target of 200 concurrent users (most are CDN-cached catalog requests, see ADR-007).

## Consequences

### Positive
- **One database** simplifies ops, backups (Railway nightly), schema migrations.
- GIN on `cause_tags` makes multi-cause filters (≤30ms typical) without a separate join table.
- `pg_trgm` later enables ETL deduplication (ADR-004) and fuzzy search (ADR-005) **for free** — same extension, two use cases.
- Composite `(charity_id, year DESC)` index makes "latest filing" lookup an index-only scan.
- PostgreSQL on Railway is the lowest-friction option in our stack — no separate provider, no egress between DB and app.

### Negative
- GIN indexes are larger and slower to write than btree — acceptable since writes happen only during nightly ETL, not user requests.
- Postgres FTS is slightly less ergonomic than dedicated search engines; we accept this until v2 (see ADR-005).
- Hobby-tier Railway Postgres has 1GB storage cap on the lowest plan; ~1.2M charities at ~5KB/row ≈ 6GB; we'll need the $5/mo Pro plan once we ingest beyond ~150K records. Documented as a Phase-7 budget reserve, not a blocker.

### Neutral
- All migrations forward + reverse, per backend-developer migration safety rules. No `null=True` on string fields (use `default=''`).
- Slug uniqueness uses Django's `SlugField(unique=True)` + ETL fallback (`{base-slug}-{ein}`) to avoid collisions.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **SQLite** | Not viable for concurrent reads at SPEC's 200-concurrent-user target; no JSONB, no GIN, weak FTS. Useful only for local dev fixtures. |
| **MySQL / MariaDB** | No native array type → cause-tag faceting needs a join table (slower, more code); no `tsvector` (would need ElasticSearch); GIS extensions less mature. |
| **MongoDB** | We have *strongly relational* data (charity ⟷ financials ⟷ source docs ⟷ news mentions). JSONB on Postgres handles the few schemaless fields without giving up SQL. |
| **Supabase** | Adds a vendor on top of Postgres for features (auth, realtime) we don't need. Increases lock-in without budget benefit. |
| **DuckDB** | Embedded analytics DB; not designed for OLTP. |

## Notes / forward references

- Postgres FTS strategy detailed in **ADR-005**.
- Caching layer (cachalot ORM cache) detailed in **ADR-007** — read-heavy workload makes ORM-level caching disproportionately valuable here.
- Schema details (full Django model definitions) ship in BACKEND.md (Phase 3) — this ADR locks the index commitments only.

# ADR-004 — Charity data ingestion architecture

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer, per MARKET_ANALYSIS.md §4 + SPEC.md §3 row 1 + §3 row 2
- **Supersedes**: —

## Context

The product depends on data from four sources (MARKET_ANALYSIS §4):

| Source | Coverage | API key | Format | Freshness |
|---|---|---|---|---|
| **ProPublica Nonprofit Explorer API v2** | 1.8M US 501(c)(3)s + Form 990 | None | JSON REST | Updated as IRS releases (monthly) |
| **Every.org Charity API** | 1M+ US 501(c)(3)s + 66 cause taxonomy + logos | Public + private key (free, signup) | JSON REST | Continuous |
| **CharityBase.uk** | 168K UK charities + 360Giving grant data | None | GraphQL | Daily |
| **Минюст СОНКО реестр** | RU registered NKOs (manual subset) | None | XML download | Manual curation |

Each source has a different identifier:
- US: **EIN** (e.g. `27-1661997`)
- UK: **Charity Number** (e.g. `1108458`)
- RU: **ОГРН** (e.g. `1037739037170`)

A single charity can appear in multiple sources (Every.org and ProPublica both cover GiveDirectly with different field shapes; some UK charities have US-affiliate 501(c)(3)s with different EINs but the same name). Deduplication is essential.

This ETL is **the single most failure-prone subsystem** of TrustGive. It runs unattended, against rate-limited third-party APIs, and partial corruption could ship bad data to SEO landing pages.

## Decision

### Pipeline shape: Django management commands + cron

```
GitHub Actions cron (nightly 02:00 UTC)
        │
        ▼
$ railway run python manage.py ingest_propublica --since=24h
$ railway run python manage.py ingest_every_org   --since=24h
$ railway run python manage.py ingest_charitybase --since=24h
        │
        ▼
For each command:
  1. Fetch raw payload from source
  2. Append RAW payload to IngestionLog (audit + replay)
  3. For each record:
     a. Identify canonical Charity (dedup, see below)
     b. select_for_update() within atomic transaction
     c. UPSERT Charity, Financial, SourceDocument, TrustBadge
     d. Recompute search_vector (Postgres trigger handles this)
  4. Emit IngestionLog.status = succeeded | partial | failed
  5. Sentry breadcrumb on any partial/failed
```

Initial bulk load (Week 1 of SPEC timeline) runs `--bootstrap` flag: top 1K US charities by revenue, all UK charities, the curated 30 RU records.

Manual RU curation goes through Django admin (no command) — Alex pastes Минюст data into a simple ModelForm; we do not automate Минюст scraping.

### Storage: raw + normalised

**`IngestionLog` table** — raw payloads preserved verbatim:
```
id              UUID PK
source          enum [propublica | every_org | charitybase | manual_ru]
fetched_at      timestamptz
status          enum [succeeded | partial | failed | running]
records_seen    int
records_upserted int
records_skipped int
errors          jsonb (array of {ein/registration_id, error_class, message})
raw_payload     jsonb (full response body, for replay)
```
Retention: 30 days rolling (cron-deleted) to control storage. Bulk-load entries kept indefinitely.

**`Charity` table** — normalised (full schema in BACKEND.md Phase 3). Key dedup fields:
- `country` (US/GB/RU)
- `registration_id` (EIN / Charity Number / ОГРН) — country-scoped UNIQUE constraint
- `slug` — derived from name, see ADR-001

**`SourceMapping` table** — per-source provenance:
```
charity_id     FK → Charity
source         enum
source_id      string (source-native primary key, e.g. ProPublica's `id`)
last_synced_at timestamptz
raw_data_hash  bytea (sha256 of canonicalised raw record — short-circuits identical re-imports)
PRIMARY KEY (charity_id, source)
```
This lets a single charity be enriched by multiple sources (Every.org logo + ProPublica financials) without losing track.

### Deduplication algorithm

For each incoming record from source `S` with country `C` and registration ID `R`:

```python
def find_or_create_charity(country, registration_id, name, source) -> Charity:
    # 1. Hard match on (country, registration_id)
    charity = Charity.objects.filter(
        country=country, registration_id=registration_id
    ).select_for_update(skip_locked=True).first()
    if charity:
        return charity

    # 2. Fuzzy match on name within country (pg_trgm similarity > 0.85)
    candidates = Charity.objects.annotate(
        sim=TrigramSimilarity('name_en', name)
    ).filter(country=country, sim__gte=0.85).order_by('-sim')
    if candidates.exists():
        # Conservative: require >=0.92 to auto-merge; 0.85-0.92 → flag for review
        top = candidates.first()
        if top.sim >= 0.92:
            log_dedup_match(top, source, score=top.sim, action='merged')
            return top
        else:
            log_dedup_match(top, source, score=top.sim, action='flagged')
            # Continue to create — Alex reviews flagged duplicates weekly via admin

    # 3. No match → create new
    return Charity.objects.create(...)
```

Cross-country merging is **never automatic** — a US charity and its UK affiliate stay separate records linked via `affiliated_charities` M2M (curated manually).

### Rate-limit handling

| Source | Documented limit | Our throttle |
|---|---|---|
| ProPublica | None published | 5 req/sec self-imposed (politeness + ToU attribution) |
| Every.org | Per developer-portal docs (not public, soft ~60/min) | 1 req/sec |
| CharityBase | Documented in their docs | Respect their `Retry-After` |

Implementation: a `ThrottledHTTPClient` wrapper using `requests` + `tenacity` exponential backoff. Each `ingest_*` command uses its own throttle. On `429` or `5xx`: exponential backoff up to 5 retries (1, 2, 4, 8, 16 s).

### Failure modes & idempotency

**Partial-failure protection**: each charity processed in its own atomic transaction (`@transaction.atomic` decorator on the per-record loop body). A single bad record never corrupts the batch.

**`select_for_update(skip_locked=True)`** on the Charity row ensures parallel ingestion runs (e.g. if cron and a manual run overlap) don't clobber each other.

**Replay**: any `IngestionLog` row can be replayed via `python manage.py replay_ingestion --log-id=<uuid>` — re-applies the raw payload from `IngestionLog.raw_payload`. Useful when a transformation bug is fixed.

**`raw_data_hash` short-circuit**: if `SourceMapping.raw_data_hash` matches the incoming record hash, skip processing entirely — turns a 1.8M record incremental sync into a ~5K-record diff on most nights.

### Status semantics
- `succeeded` — all records processed, zero errors
- `partial` — ≥1 record errored but ≥1 succeeded (most common; e.g. a malformed Form 990)
- `failed` — entire batch couldn't run (auth, network, schema-change at the source)

Sentry alert on `failed`. PostHog alert on `partial > 1% of records_seen`.

## Consequences

### Positive
- **Idempotent** — replays produce same result.
- **Auditable** — every ingestion produces a row + raw payload, replayable if needed.
- **Resilient** — single-record errors don't poison the batch.
- **Cheap** — runs on Railway via cron; no Celery worker needed in MVP (Celery deferred until we need real-time tasks).
- **Cross-source enrichment** — `SourceMapping` table allows adding new sources (Canadian CRA, German Transparenzregister) in v2 without reshuffling Charity rows.

### Negative
- **No streaming**: we batch nightly, not real-time. Acceptable: charity data changes monthly at most.
- **`raw_payload` JSONB grows fast**: 30-day retention controls it. Bootstrap entries retained forever as historical record.
- **Fuzzy-match flags require human review**: Alex reviews weekly; flagged-duplicates queue surfaced in Django admin.
- **Cron via GitHub Actions** has 6-hour max runtime — fine for nightly delta (~5–10 min); bulk runs might exceed it for full UK ingestion, so bulk runs split into 100K-record chunks via `--limit` flag.

### Neutral
- ETL code lives under `apps/ingestion/` with one module per source. Source-specific transformation lives in `apps/ingestion/transformers/{source}.py` — tested independently.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **Real-time webhook ingestion** | None of the sources offer webhooks. Polling is the only option. |
| **Celery + Redis for async tasks** | Adds Redis as a paid Railway service (no managed Redis on free tier). Nightly cron via GitHub Actions is sufficient. Revisit when we need real-time tasks. |
| **Airflow / Prefect / Dagster** | Operational overhead too high for 3 sources. Django commands + cron is a 1-evening setup. |
| **dbt for transformations** | Useful for analytics; we're doing operational ETL. Mismatched tool. |
| **Materialised views on raw JSONB** | We'd still need normalised tables for indexes (cause_tags GIN). Mat views add a refresh layer. |
| **Stream-process via Kafka/Redpanda** | Vast overkill for nightly batch of <2M records. Free-tier ceiling exceeded immediately. |
| **Hash-based exact dedup only (no fuzzy)** | Misses obvious cases ("GiveDirectly Inc" vs "GiveDirectly" — different EINs are caught by fuzzy match). |
| **Embedding-based semantic dedup** | Overkill + introduces a model dependency + non-deterministic. pg_trgm gets us 90% of the way for free. |
| **Trust the source — store everything verbatim, no normalisation** | Catalog filters need indexed columns. JSONB queries on 1.2M rows would be slow. |

## Notes / forward references

- Search index built on top of normalised `Charity.search_vector`: ADR-005
- Cache invalidation when ingestion changes a charity: ADR-007 (use cachalot's `invalidate_model` post-save signal)
- Health endpoint reports last successful ingestion per source: ADR-008 / API_SPEC §2 (`HealthStatus.db` covers DB; future enhancement adds `data_freshness` field)

# ADR-005 — Search strategy: PostgreSQL full-text search + pg_trgm

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer, per SPEC.md §6 row "Search engine"
- **Supersedes**: —

## Context

Catalog search must:
- Match charity names, descriptions, EIN/registration numbers
- Tolerate typos ("givedirectl" → "GiveDirectly")
- Work for **English and Russian** equally — no second-class language
- Stay within $0/mo budget — no Algolia, no managed Elasticsearch
- Respond in <300ms server-side per SPEC §9
- Plug into the same `/api/charities/?q=...` endpoint defined in API_SPEC.md

We have ~1.2M records in the worst-case scenario (full ProPublica + CharityBase load). Even read-heavy, this fits comfortably in Postgres on Railway.

## Decision

Use **PostgreSQL native full-text search (`tsvector` + `tsquery`)** combined with **`pg_trgm`** for typo tolerance. Both ship with Postgres 17 (ADR-001).

### Schema commitment

`Charity` gets two FTS-supporting columns:

```python
# apps/charities/models.py
search_vector = SearchVectorField(null=True)         # GIN index
name_trgm     = models.CharField(max_length=300)     # GIN(gin_trgm_ops) index
```

`search_vector` is populated by a Postgres trigger so application code never has to remember to update it. **Note**: per ADR-006, `Charity.name` and `Charity.description` are JSONB columns (`{en, ru}`), so the trigger reads via the JSONB key-access operator `->>`:

```sql
CREATE OR REPLACE FUNCTION trustgive_charity_tsvector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('simple', unaccent(coalesce(NEW.name->>'en', ''))), 'A') ||
    setweight(to_tsvector('simple', unaccent(coalesce(NEW.name->>'ru', ''))), 'A') ||
    setweight(to_tsvector('simple', unaccent(coalesce(NEW.description->>'en', ''))), 'C') ||
    setweight(to_tsvector('simple', unaccent(coalesce(NEW.description->>'ru', ''))), 'C') ||
    setweight(to_tsvector('simple', coalesce(NEW.registration_id, '')), 'B');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;
```

We use the **`simple` text search configuration** (no language stemming) deliberately:
- Charity names rarely benefit from stemming (proper nouns)
- A single config works across English + Russian without language detection
- `unaccent` strips diacritics and Cyrillic-Latin transliteration noise
- Empirically faster (no dictionary lookup)

If post-launch search relevance feels weak, the simple→language-specific upgrade is a single trigger rewrite + reindex — no API change.

### Query strategy (in `CharityViewSet.list` `?q=...`)

```python
# Simplified — full version with `prefetch_related` etc. in Phase 3
def filter_search(queryset, q: str):
    if not q:
        return queryset
    if len(q) < 3:
        # Short queries: prefer trigram (better for partial words)
        return queryset.annotate(
            sim=TrigramSimilarity('name_trgm', q)
        ).filter(sim__gte=0.3).order_by('-sim')

    # Long queries: tsvector match, ranked by ts_rank, fallback to trigram for typo tolerance
    ts_q = SearchQuery(q, search_type='websearch', config='simple')
    return queryset.annotate(
        rank=SearchRank('search_vector', ts_q),
        sim=TrigramSimilarity('name_trgm', q),
    ).filter(
        Q(search_vector=ts_q) | Q(sim__gte=0.4)
    ).order_by('-rank', '-sim')
```

`websearch` parser handles user-style queries ("animal welfare -dogs" syntax).

### Cyrillic specifics

Russian is harder because:
- No widely-deployed Russian stemmer ships with Postgres (`russian` config exists but stems aggressively, hurting proper-noun recall on charity names)
- Word boundaries differ subtly

Decision: stick with `simple` config + `unaccent` + trigram fallback. Test with a fixture set of 30 RU charities (we have them). If post-launch users report "Минюст" not matching "минюст" (case) or "Россия" / "россия" (it shouldn't, but `simple` is case-folded), the fix is `lower()` in the trigger — non-breaking.

### Performance budget

Catalog search target: **<200ms p95 server-side** (gives us 100ms headroom under SPEC's 300ms target).

Postgres FTS on a GIN-indexed `tsvector` over 1.2M rows: typical 20–80ms for matched-and-ranked queries (validated against synthetic data in similar projects). Trigram fallback: 30–150ms — slightly slower, only triggers on short queries / typos.

If observed p95 exceeds 250ms after launch (Performance Engineer in Phase 4.5 measures this), the v2 upgrade kicks in.

## Consequences

### Positive
- **$0/mo** — Postgres 17 already provisioned, extensions free.
- **No new service** to deploy, monitor, or back up.
- **Atomic with data** — a charity ingested at T also gets searchable at T (trigger-driven).
- **Bilingual at zero cost** — same column handles EN + RU.
- **Typo tolerance** via trigram fallback.
- **Familiar tooling** — Django ORM has `SearchVector`, `SearchRank`, `TrigramSimilarity` in `django.contrib.postgres.search`.

### Negative
- **No fuzzy phrase matching** beyond trigram + tsquery — no synonyms, no learned-rank, no faceted search engine features.
- **No multi-language stemming** — long-tail Russian morphology may suffer (acceptable for proper nouns; revisit per query logs).
- **Index maintenance**: GIN inserts are 10× slower than btree, but ETL writes are nightly so the cost is invisible to users.
- **Search relevance is untunable in production** — no equivalent of Algolia's per-record `customRanking`. We compensate via deterministic `ts_rank` weighting in the trigger.

### Neutral
- Ranking order is deterministic — same inputs, same output. CDN-cacheable.
- All search runs in the same DB connection as the rest of the request — no network hop.

## v2 cutover threshold (when to migrate to dedicated search)

Move to **Meilisearch** (self-hosted on Railway, free, lightweight) when ANY of the following triggers fire post-launch, and Performance Engineer concurs in a Phase 4.5+ revisit:

| Trigger | Threshold |
|---|---|
| **Volume** | Charity records exceed **1M** AND search p95 > 250ms |
| **Latency target tightens** | We commit to <100ms p95 (e.g. for instant-search dropdown UX) |
| **Multilingual quality** | Real users report "Cyrillic search misses obvious matches" with logged examples |
| **Typo tolerance gap** | We need configurable typo distance per word position |

The migration is **non-breaking** at the API level — `/api/charities/?q=...` returns the same shape, the implementation swaps. Cutover is ~1 week of work: index sync from Postgres → Meilisearch via a management command, dual-read with feature flag, atomic switch.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **Elasticsearch / OpenSearch** | $$ on managed (Bonsai, Elastic Cloud) or operational nightmare on self-host. Overkill for 1.2M small documents. |
| **Algolia** | Free tier (10K records, 10K searches/mo) doesn't fit our 1.2M record size; paid tier outside budget. |
| **Typesense** | Self-host viable but adds another Railway service (memory + cron sync). Strong v2 candidate alongside Meilisearch. |
| **Meilisearch in MVP** | Adds a service before we know we need it. Postgres FTS handles 1.2M rows; cutover-when-needed is the right call. |
| **`LIKE '%term%'` queries** | Sequential scan on 1.2M rows = seconds. No GIN, no ranking. Categorically wrong. |
| **`pg_trgm` only (no tsvector)** | Loses ranking quality and phrase support. Trigram works for fuzziness, not relevance. |
| **OpenAI embeddings + pgvector** | Requires LLM API (cost), adds latency, loses determinism. Reserve for v2 "semantic search" if a use case emerges. |

## Implementation hooks (Phase 3)

- Migration: `CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS unaccent;`
- Migration: `CREATE INDEX charity_search_vector_idx ON charities_charity USING GIN(search_vector);`
- Migration: `CREATE INDEX charity_name_trgm_idx ON charities_charity USING GIN(name_trgm gin_trgm_ops);`
- Migration: trigger function + trigger as above (uses JSONB `->>` operator per ADR-006)
- Note in BACKEND.md: rebuilding index = `REINDEX INDEX CONCURRENTLY charity_search_vector_idx`

## Notes / forward references

- API endpoint: `GET /api/charities/?q=...` — see `API_SPEC.md` §2 endpoint #2
- Index choices documented in **ADR-001**
- ETL deduplication uses the same `pg_trgm` extension — see **ADR-004**
- Storage shape (JSONB for `name`, `description`) — see **ADR-006**

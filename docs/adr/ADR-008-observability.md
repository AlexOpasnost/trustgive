# ADR-008 — Observability: Sentry + structured JSON logs + minimal health check

- **Status**: Accepted
- **Date**: 2026-05-05
- **Deciders**: Backend Developer, per DEVOPS.md "Observability (planned for Phase 3)" + SPEC.md §9
- **Supersedes**: —

## Context

We need to know:
1. **When the production app breaks** — exception-level visibility, with stack traces and request context
2. **What users do** — funnel from landing → catalog → detail → donate-redirect (the core SPEC Story 4 conversion)
3. **Whether the service is alive** — Railway deploy healthcheck + uptime monitoring
4. **What ETL did last night** — visible status of the four data ingestion pipelines (ADR-004)

We have $0/mo budget, no DevOps team, and a single deploy environment (Railway production) for MVP.

## Decision

### Three pillars

#### 1. Errors — Sentry (free tier)

`pip install sentry-sdk[django]==2.x`. Configured in `settings/production.py`:

```python
sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    environment='production',
    release=os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
    integrations=[DjangoIntegration(transaction_style='url'), LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
    traces_sample_rate=0.0,             # No performance monitoring on free tier — burns the quota
    send_default_pii=False,             # Strip request body, headers
    before_send=scrub_sensitive_fields,  # Custom scrubber
)
```

Free tier: 5K errors/month — sufficient for an MVP launch. Sentry alerts to Alex's email on any new error grouping.

`scrub_sensitive_fields` strips:
- `Authorization` header (defence-in-depth even though we don't use one)
- `Cookie` header
- Any field with `key`, `secret`, `token`, `password` in its name (regex)

#### 2. Logs — structured JSON via `python-json-logger`

`pip install python-json-logger==2.0.7`. Configured in `settings/base.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(request_id)s %(charity_slug)s',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'json'},
    },
    'loggers': {
        '': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.db.backends': {'level': 'WARNING'},  # Don't log every SQL query
    },
}
```

Every log record is one JSON object on one line. Railway captures stdout and provides a searchable log viewer; we can upgrade to a log drain (e.g. BetterStack free tier) post-MVP if needed.

**Mandatory log fields** (added via `RequestIDMiddleware` and contextvars):
- `request_id` — UUID4 generated per HTTP request, also returned as `X-Request-ID` response header (API_SPEC.md §5)
- `path`, `method`, `status_code`, `duration_ms` — per request access log
- `user_id` — always `null` in MVP (no auth) but reserved for v2
- `charity_slug` — present on charity-specific endpoints

Log level conventions:
- `DEBUG` — disabled in production
- `INFO` — request-completed lines, ETL progress, cache invalidations
- `WARNING` — slow queries, throttle trips, partial-ingestion outcomes
- `ERROR` — exceptions; mirrored to Sentry automatically via `LoggingIntegration`

#### 3. Health endpoint — `GET /api/health/`

Per API_SPEC.md endpoint #1. Returns `200` with `{status, db, sentry, version, timestamp}` when healthy, `503` when degraded.

```python
# apps/core/views.py
class HealthView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []  # Don't throttle uptime monitor

    def get(self, request):
        db_ok = check_db()       # SELECT 1
        sentry_ok = check_sentry()  # sentry_sdk.Hub.current.client is not None
        status_ok = db_ok                          # Sentry being down ≠ service unhealthy
        body = {
            'status': 'ok' if status_ok else 'fail',
            'db': 'ok' if db_ok else 'fail',
            'sentry': 'ok' if sentry_ok else ('disabled' if not settings.SENTRY_DSN else 'fail'),
            'version': settings.APP_VERSION,
            'timestamp': timezone.now().isoformat(),
        }
        return Response(body, status=200 if status_ok else 503)
```

Used by:
- Railway healthcheck (auto-restart on 503)
- External uptime monitor — UptimeRobot free (50 monitors, 5-minute interval) on `https://api.trustgive.org/api/health/`

### Analytics — PostHog client-side, server-side mirror only for `/api/events/donation-redirect/`

PostHog is configured in the **frontend only** with the public project key. The backend never holds the PostHog API key in the public surface.

**Single exception**: the `/api/events/donation-redirect/` endpoint server-side mirrors the event to PostHog using a server-only API key (kept in Railway Variables as `POSTHOG_SERVER_KEY`):

```python
# apps/events/views.py
@throttle_classes([DonationRedirectThrottle])
def post(self, request):
    serializer = DonationRedirectEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    posthog_capture.delay(serializer.validated_data)  # async via lightweight queue (see below)
    return Response({'status': 'accepted'}, status=202)
```

Why mirror server-side: the donation-redirect is the **single most important conversion event** (SPEC Story 4). Client-only tracking would miss events when adblockers strip PostHog JS (significant for our privacy-conscious target audience). Server-side mirror makes it ad-blocker-resistant.

`posthog_capture.delay(...)` uses a tiny **threading.Thread + queue.Queue** worker, not Celery — keeps us off Redis until we genuinely need it. ~50 lines of code; failure to deliver to PostHog is logged but does not affect the user response.

### What we do NOT add in MVP

- **Performance monitoring (Sentry/Tracing)** — burns quota, defer to Phase 4.5 when Performance Engineer profiles
- **Distributed tracing (OpenTelemetry)** — single-service architecture; overkill
- **Metrics (Prometheus / OTEL metrics)** — Railway dashboard + Sentry are sufficient
- **Datadog / Honeycomb / New Relic** — paid; scope creep
- **Custom dashboards / Grafana** — Railway's built-in deploys/logs UI suffices

These join in v2 if we have real signal that they unblock something.

## Consequences

### Positive
- **Catches real production failures** via Sentry without a paid plan.
- **Logs are machine-parseable** — useful for ad-hoc grep + future log drain.
- **Health endpoint** integrates with Railway, UptimeRobot, and any future load balancer.
- **Conversion event is ad-block resistant** thanks to server-side mirror.
- **Zero ops burden** — three vendors total (Sentry, Railway, UptimeRobot), all free tier, all email-alerts.
- **Request ID in every log line + every error response** makes debugging from a user-supplied `X-Request-ID` trivial.

### Negative
- **No tracing** in MVP — when a request is slow, we know which endpoint, not which DB query (mitigated by Phase 4.5 Performance Engineer profiling).
- **No metrics/dashboards** — Sentry's release-health dashboard is what we have.
- **Threading-based PostHog capture** is best-effort — if the worker thread crashes, we lose at most the current event. Acceptable given the analytics nature.
- **Free-tier limits** on Sentry (5K errors/mo) — if a buggy deploy spams errors, we can blow the quota in a day. Mitigated by Sentry's per-issue rate limiting + alerts on quota near-empty.

### Neutral
- All four observability decisions are isolated; replacing any single one (e.g. Sentry → BugSnag) is a config change, not an architectural one.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **ELK stack (Elastic + Logstash + Kibana)** | Multi-service deploy, paid managed tier, excessive for ~10 endpoints. |
| **Datadog / New Relic / Honeycomb** | Paid. Free tiers have low quotas + slow ingestion. Outside budget. |
| **Self-hosted Grafana + Loki** | Adds two services on Railway, ~$10/mo extra, requires log-drain config. Fits a v2 scenario, not MVP. |
| **Plain text logs (no JSON)** | Future log drain consumers (BetterStack, Datadog) need structured input; cheap to do correctly now. |
| **Tracking PostHog from the client only** | Adblocker miss rate on conversion event compromises the most-important metric for the project portfolio narrative. |
| **No health endpoint, rely on Railway TCP probe** | TCP-up does not mean app-healthy (DB could be unreachable, app would still bind port). HTTP healthcheck is the standard. |
| **OpenTelemetry instrumentation** | Single-service deployment + no downstream services to trace. Adds setup cost + library footprint for no MVP value. |

## Implementation hooks (Phase 3)

- `pip install sentry-sdk[django]==2.* python-json-logger==2.0.7`
- `apps/core/middleware.py` — `RequestIDMiddleware` (UUID4 per request → contextvar → log record + response header `X-Request-ID`)
- `apps/core/exceptions.py` — DRF custom exception handler attaches `request_id` and Sentry event ID to error envelopes
- `apps/core/views.py` — `HealthView`
- `apps/core/posthog.py` — minimal background-thread capture worker
- `settings/production.py` — Sentry init with `before_send` scrubber
- README.md — document `X-Request-ID` header + `request_id` in error responses for support workflow
- `.env.example` — `SENTRY_DSN=`, `POSTHOG_SERVER_KEY=`, `APP_VERSION=` placeholders

## Notes / forward references

- Health endpoint contract: API_SPEC.md endpoint #1 (`HealthStatus` schema)
- Error envelope referencing `request_id`: API_SPEC.md §5
- Throttling exemption for `/api/health/`: ADR-007
- ETL ingestion logging: ADR-004 (writes `IngestionLog` row + emits structured log line + Sentry breadcrumb)

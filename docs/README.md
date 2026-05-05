# TrustGive Documentation

Confluence-ready, structured documentation for the TrustGive charity discovery platform.

## Contents

| # | Document | What's inside |
|---|---|---|
| 01 | [Project overview](01-overview.md) | Problem, target users, positioning, success criteria |
| 02 | [Architecture](02-architecture.md) | System overview, request flow, data flow, technology choices |
| 03 | [API reference](03-api-reference.md) | All 10 endpoints, error envelope, throttling, examples |
| 04 | [Local setup](04-setup.md) | Backend + frontend + Postgres dev workflow |
| 05 | [Deployment](05-deployment.md) | Railway (backend) + Cloudflare Pages (frontend) + DNS + monitoring |
| 06 | [Operations runbook](06-operations.md) | Common ops: deploy, rotate secrets, restore DB, replay ingestion, scale |

## Source-of-truth artifacts

These docs **summarise + integrate** authoritative artifacts that live elsewhere in the repo:

- [`SPEC.md`](../SPEC.md) — product spec v1.0
- [`MARKET_ANALYSIS.md`](../MARKET_ANALYSIS.md) — competitor analysis
- [`DESIGN.md`](../DESIGN.md) — design system v1.1
- [`API_SPEC.md`](../API_SPEC.md) — OpenAPI 3.1 contract
- [`docs/adr/`](../docs/adr/) — 8 Architecture Decision Records
- [`BACKEND.md`](../BACKEND.md), [`FRONTEND.md`](../FRONTEND.md), [`DEVOPS.md`](../DEVOPS.md) — per-area technical docs
- [`TEST_REPORT.md`](../TEST_REPORT.md), [`PERFORMANCE_REPORT.md`](../PERFORMANCE_REPORT.md), [`ACCESSIBILITY_REPORT.md`](../ACCESSIBILITY_REPORT.md) — Phase 4.5 reports
- [`REVIEW_REPORT.md`](../REVIEW_REPORT.md) — Phase 5 code review
- [`CHANGELOG.md`](../CHANGELOG.md) — chronological project log

## Audience

- **Onboarding engineers** start at [04-setup.md](04-setup.md)
- **Product / business folks** start at [01-overview.md](01-overview.md)
- **Anyone deploying** read [05-deployment.md](05-deployment.md) + [06-operations.md](06-operations.md)
- **Frontend integrators** read [03-api-reference.md](03-api-reference.md)

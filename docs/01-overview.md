# 01 — Project overview

## What TrustGive is

**TrustGive** is a web-first charity discovery platform that helps donors find verified charity organizations through powerful filters and direct links to source documents (IRS Form 990, UK Charity Commission filings, Минюст registrations).

It is a **discovery layer**, not a payment processor. Users find charities here, then donate on the charity's own website. TrustGive never handles money.

## Problem statement

Donors worldwide want to give but are held back by:
1. Lack of trust in charity organizations
2. Confusion about which charities are legitimate
3. No clear way to see where money actually goes
4. Existing services are either:
   - Opaque rating aggregators (Charity Navigator dropped overhead-ratio scoring in 2023 because nonprofits gamed it)
   - Donation platforms with hidden fees (JustGiving's 17.5% default "tip" is its #1 Trustpilot complaint)
   - Country-locked (no platform shows Russian charities to English-speaking donors with verification proof)

## Solution

A discovery platform built on free public data — IRS 990 filings (via ProPublica), UK Charity Commission register (via CharityBase.uk), Минюст СОНКО registry — that links donors **directly** to source documents. No platform fee. No money handling.

## Target users

- **Primary**: globally distributed donors, English + Russian speakers, $30K–$150K/yr income
  - Both first-time donors exploring options and experienced donors frustrated by opaque platforms
- **Secondary**: researchers and journalists checking charity legitimacy; Effective Altruism community members evaluating non-EA causes with rigor

## Positioning

> **The only charity discovery tool that shows you the source documents — not a star rating you can't audit.**
> Filter 1.2M+ verified US, UK and Russian charities by cause, country, and size. Every "verified" claim links to the actual IRS 990, Charity Commission filing, or Минюст registration. **0% platform fee.** We never see your money.

## Differentiators

1. **Source-document transparency** — one click reveals the actual government filing
2. **Bilingual EN+RU coverage** — no platform bridges these markets today
3. **No money handling** — direct outbound to charity sites, anti-pitch to JustGiving's hidden tips

## Success criteria

- Find 3 trustworthy charities matching preferences in **under 90 seconds**
- One-click reveal of source document for every "verified" claim
- NPS ≥ 40 from first 100 users
- Featured on Product Hunt; shared in r/EffectiveAltruism, EA Forum, Indie Hackers
- 50K monthly organic visits by month 4 (auto-generated SEO long-tail pages)

## Constraints

| | |
|---|---|
| **Budget** | $0/month strictly (free tiers only) |
| **Timeline** | 8-week MVP from kickoff |
| **Team** | Solo developer + AI agent system |
| **Platform** | Web-first responsive (no mobile native in v1) |
| **Languages** | English + Russian at launch |

## Source artifacts

- Full spec: [`SPEC.md`](../SPEC.md)
- Market research: [`MARKET_ANALYSIS.md`](../MARKET_ANALYSIS.md)
- Promotion strategy: [`MARKET_ANALYSIS.md` §6](../MARKET_ANALYSIS.md)

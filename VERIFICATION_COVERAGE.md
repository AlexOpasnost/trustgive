# Verification Coverage Report

> Worldwide catalogue coverage: how many charities carry a **confirmation**
> (verified status) backed by a **report** (a live regulator source document).
> Generated from the production API (`api.trustgive.org`) on 2026-07-12.

---

## Executive summary

| Metric | Value |
|---|---|
| Total charities | **541** |
| Verified (confirmed + live source document) | **351** → **366** after applying this session's US batch |
| Listed (no confirmed source yet) | **190** → **175** |
| Countries | 27 |

The catalogue is genuinely worldwide, but **35% of it (190 orgs) had no confirmed
regulator document** after the v3.18 source-link audit demoted every unverifiable
claim. This report inventories that gap by country and gives the exact registry +
recovery path for each, so coverage can be raised honestly (no fabricated IDs —
every identifier is checked against the live registry at write time).

---

## Coverage by country (before this session)

| Country | Verified | Total | Coverage |
|---|---:|---:|---:|
| 🇬🇧 United Kingdom | 77 | 77 | **100%** |
| 🇺🇸 United States | 237 | 296 | 80% |
| 🇦🇺 Australia | 17 | 25 | 68% |
| 🇮🇳 India | 3 | 3 | 100% |
| 🇷🇺 Russia | 2 | 2 | 100% |
| 🇧🇷 Brazil | 2 | 2 | 100% |
| 🇪🇸 Spain | 6 | 14 | 43% |
| 🇮🇹 Italy | 4 | 15 | 27% |
| 🇩🇪 Germany | 2 | 13 | 15% |
| 🇳🇱 Netherlands | 1 | 9 | 11% |
| 🇨🇦 Canada | **0** | 28 | **0%** |
| 🇫🇷 🇮🇪 🇧🇪 🇳🇴 🇩🇰 🇨🇭 🇫🇮 🇦🇹 🇵🇱 🇸🇪 (rest of Europe) | 0 | ~55 | ~0% |
| 🇳🇿 New Zealand | 0 | 7 | 0% |
| 🇮🇱 Israel | 0 | 3 | 0% |
| 🇨🇱 🇯🇵 🇰🇪 🇹🇭 (misc) | 0 | 4 | 0% |

**The 190 unverified, by country:** US 59 · CA 28 · DE 11 · IT 11 · NL 8 · ES 8 · AU 8 · NZ 7 · FR 7 · IE 6 · BE 5 · NO 5 · DK 5 · CH 4 · FI 3 · IL 3 · AT 3 · PL 3 · SE 2 · CL/JP/KE/TH 1 each.

---

## This session — US manual batch (+15 verified)

The US `listed` set was the "manual" tier from the v3.18 EIN re-sourcing: federated
orgs (many namesake chapters) + no-candidate cases that the auto-resolver couldn't
disambiguate. 15 were resolved to their **national head entity** and **each EIN was
verified live against ProPublica** (name match + recent Form 990 with real revenue):

| slug | EIN | ProPublica entity | latest 990 |
|---|---|---|---|
| twloha | 260789229 | Twloha Inc | FY2023 · $3.9M |
| sesame-workshop | 132655731 | Sesame Workshop | FY2023 · $187M |
| the-conservation-fund | 521388917 | The Conservation Fund | FY2023 · $327M |
| dav-charitable-trust | 521521276 | DAV Charitable Service Trust | FY2023 · $20M |
| childrens-tumor-foundation | 132298956 | Childrens Tumor Foundation | FY2023 · $16M |
| greater-good-charities | 204846675 | Greater Good Charities | FY2023 · $154M |
| hias | 135633307 | HIAS Inc | FY2023 · $88M |
| proliteracy | 166076384 | ProLiteracy Worldwide | FY2023 · $10.5M |
| bob-woodruff-foundation | 261441650 | Bob Woodruff Family Foundation | FY2023 · $39M |
| born-free-usa | 946187633 | Born Free USA (w/ Animal Protection Inst.) | FY2023 · $2.7M |
| friends-of-animals | 136018549 | Friends Of Animals Inc | FY2024 · $5.5M |
| pan-na | 942949686 | Pesticide Action Network North America | FY2023 · $3.3M |
| tunnel-to-towers | 20554654 | Stephen Siller Tunnel To Towers Foundation | FY2023 |
| united-cerebral-palsy | 203568840 | United Cerebral Palsy Inc | FY2023 |
| year-up | 43534407 | Year Up Inc | FY2023 |

**Deliberately excluded** (the no-fabrication rule in action):
- `creative-commons` (EIN 320821840) — resolves to a **filing-less namesake** (0 Form 990s). Including it would create a false "verified".
- `lcv-education-fund` — its correct EIN (521379661) is already held by `league-conservation-voters`; the unique-registration constraint means one catalogue entry must stay listed.
- `rainn`, `code-org`, `equal-justice-initiative`, `trans-lifeline`, `climate-reality-project` — the guessed national EINs returned 404 on ProPublica, so they were left out rather than applied blind.

**To apply** (agent env has no Railway auth; run locally against prod via `.env`):
```bash
cd backend
python manage.py fix_us_eins --file=../us_manual_eins.json --dry-run   # preview
python manage.py fix_us_eins --file=../us_manual_eins.json             # apply
# then: railway redeploy  (clear cachalot LocMem)  +  Cloudflare cache purge
```
`fix_us_eins` re-verifies each EIN against ProPublica at apply time, pulls the real
revenue/exec-comp, and rebuilds the IRS-990 source document. Curated content
(name/tagline/description/photo) is never touched.

---

## Recovery roadmap for the remaining ~175

Ordered by return on effort (gap size × registry tractability).

| # | Country | Gap | Registry / source | Tractability | Tooling |
|---|---|---:|---|---|---|
| 1 | 🇨🇦 Canada | 28 | **CRA "List of charities"** — per-BN page verified 200 (`rgstrdChrtsInf?charityId={BN}`) | Medium — need to resolve each slug→BN from CRA search or the T3010 open dataset | **`fix_ca_bns.py` shipped this session** (mirrors `fix_au_abns`); just needs the `{slug: BN}` mapping |
| 2 | 🇺🇸 US (remaining) | 44 | ProPublica | Mixed — federated orgs (ducks-unlimited, pflag, folds-of-honor, volunteers-of-america) need the national-parent EIN; several "no-candidate" orgs need a manual ProPublica search | Extend `us_manual_eins.json`, apply with `fix_us_eins` |
| 3 | 🇦🇺 Australia | 8 | ACNC / ABR | Medium — 4 are sub-entity mis-matches (Salvation Army → "Salvation Army Housing" etc.), need the head-org ABN; 6 unmatched | Extend `au_abns.json`, apply with `fix_au_abns` |
| 4 | 🇳🇿 New Zealand | 7 | **Charities Services register** (register.charities.govt.nz — has an OData/open-data API) | Medium — API blocks HEAD (403) but serves data via its documented endpoints | Needs a `fix_nz_ccnumbers.py` (mirror the AU/CA pattern once the per-charity URL is confirmed) |
| 5 | 🇪🇺 Europe | ~90 | No single API — national registers (DE Transparenzregister, IT RUNTS, NL ANBI, FR JOAFE, etc.) are heterogeneous; many small orgs have only their **own audited annual report** | Hard — largely manual. Realistic outcome: attach an `annual_report` source document where one exists (→ verified); orgs with no public filing stay honestly `listed` | Manual curation |

**Honest ceiling.** UK (100%) + US (~95% achievable) + CA/AU/NZ via their registries
gets the catalogue to roughly **440–460 verified (~85%)**. The remaining European
long-tail often has no machine-readable public filing at all — for those, "listed"
(honestly labelled, no false badge) is the correct end state, exactly as the v3.18
audit intended.

---

## Method note

All numbers pulled live from `GET /api/charities/?page_size=500` (paged). Every US
EIN in this session was confirmed via
`GET https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json`
(free, no key) — a candidate was accepted only when the returned legal name matched
the charity and it had at least one recent Form 990 with data. This enforces the
project's standing rule: **never seed a registry identifier without verifying it
against the live source at write time.**

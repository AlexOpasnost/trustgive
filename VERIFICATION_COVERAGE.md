# Verification Coverage Report

> Worldwide catalogue coverage: how many charities carry a **confirmation**
> (verified status) backed by a **report** (a live regulator source document).
> Generated from the production API (`api.trustgive.org`); last updated 2026-08-04.
>
> **The catalogue is verified-only as of 2026-07-27.** Rows that could not be
> confirmed are hidden from the public API rather than shown with a caveat, and
> stay in the database so they return automatically once verified. The numbers
> below therefore describe what is *published*, not what exists in storage.

---

## Executive summary

| Metric | Value | Was 2026-07-27 |
|---|---|---|
| Rows in the database | **541** | 541 |
| **Published** (verified + live regulator document) | **400** | 371 |
| Hidden (no confirmed source yet — retained, not deleted) | **141** | 170 |
| Published without a source document | **0** | 0 |
| Countries represented in the database | 27 | 27 |
| Countries actually published | **11** | 10 |

Published by country, 2026-08-04: US 278 · GB 77 · **AU 23** · ES 6 · IT 4 ·
IN 3 · **NZ 3** · RU 2 · DE 2 · NL 1 · BR 1.

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

## 2026-08-04 — the hidden US set, re-searched by name (+21 published)

Block E opens with the US because ProPublica needs no key. The 39 US rows still
hidden all carried a registration number, so the first question was whether those
numbers were real. **37 of the 39 returned HTTP 404** — the identifiers were
wrong, not the organisations. (The other two failed with a dropped connection;
those were retried rather than counted as absent, which is the distinction §8
below is about.)

Each was then re-searched on ProPublica by name. A candidate had to clear three
gates before it was written:

1. the EIN resolves;
2. a name the registry returns — legal **or** IRS trade name — matches the
   catalogue entry on its identifying words, exactly;
3. the organisation has a Form 990 carrying real revenue, and the document page
   the profile will link to opens **and contains the organisation's name**.

Gate 3's second half is checked on page content, never on status code — the
lesson from Finding 6.

**21 recovered.** Every one re-verified at write time by `fix_us_eins`:

| slug | corrected EIN | ProPublica record | latest filing |
|---|---|---|---|
| als-tdi | 043462719 | Als Therapy Development Foundation Inc | FY2023 · $11.6M |
| american-foundation-for-blind | 135562161 | American Foundation For The Blind Inc | FY2023 · $8.6M |
| center-for-victims-of-torture | 363383933 | Center For Victims Of Torture | FY2023 · $31.1M |
| code-org | 460858543 | Code Org | FY2023 · $42.8M |
| cure-alzheimers-fund | 522396428 | *Alzheimers Disease Research Foundation* / **Cure Alzheimers Fund** | FY2023 · $37.7M |
| equal-justice-initiative | 631135091 | Equal Justice Initiative | FY2023 · $67.3M |
| frac-food-policy | 237200739 | Food Research & Action Center Inc | FY2023 · $16.6M |
| fsc-us | 030355315 | *Us Working Group Inc* / **Forest Stewardship Council Us** | FY2023 · $1.9M |
| lirs | 132574854 | Lutheran Immigration And Refugee Service | FY2023 · $232.8M |
| movember-foundation-us | 770714052 | Movember Foundation | FY2024 · $16.8M |
| oats-tech | 550882599 | Older Adults Technology Services Inc | FY2023 · $13.3M |
| pacific-environment | 942628924 | Pacific Environment And Resources Center | FY2023 · $5.5M |
| pheasants-forever | 411429149 | Pheasants Forever Inc | FY2023 · $89.6M |
| rainn | 521886511 | *Rape Abuse And Incest National Network Inc* / **Rainn** | FY2024 · $24.2M |
| reading-is-fundamental | 520976257 | Reading Is Fundamental Inc | FY2023 · $11.2M |
| sickle-cell-disease-association | 237175985 | Sickle Cell Disease Association Of America Inc | FY2022 · $1.1M |
| sustainable-conservation | 943232437 | Sustainable Conservation | FY2023 · $5.4M |
| the-end-fund | 273941186 | End Fund Inc | FY2023 · $56.4M |
| uscri | 131878704 | U S Committee For Refugees And Immigrants Inc | FY2023 · $291.9M |
| whale-dolphin-conservation-us | 020749188 | Whale And Dolphin Conservation Inc | FY2023 · $1.1M |
| whale-sanctuary-project | 812276219 | Whale Sanctuary Project | FY2023 · $1.8M |

Rows in *italic / **bold*** matched on the IRS **trade name**, not the legal one.
That field (`sort_name`) turned out to matter: three charities are legally
something unrecognisable and are known publicly only by the trade name the same
registry publishes. Checking only the legal name would have been rejecting the
registry's own answer about its own entity.

`pheasants-forever` was the one federated pick accepted, and only after checking
all 28 namesake entities: the Saint Paul body reports $89.6M and the next largest
$356K, a 250× gap that leaves no ambiguity about which is the national one.

### The 18 that stay hidden, and why

| Reason | Rows |
|---|---|
| **Duplicate of an already-published record** — merge, don't verify | `jdrf-breakthrough-t1d` (= `jdrf`), `sea-shepherd-conservation-society` (= `sea-shepherd`), `lcv-education-fund` (= `league-conservation-voters`), `whale-and-dolphin-conservation-usa` (= `whale-dolphin-conservation-us`) |
| **Federated — name cannot pick the national body** | `ducks-unlimited` (25 namesakes, none with filing data), `pflag` (25 chapters, none with filing data), `volunteers-of-america` (the largest exact match is *VOA National Services*, a subsidiary, not the national body) |
| **Resolves and the name matches, but zero filings with data** | `save-the-elephants-usa` — registry presence alone does not meet the published methodology, exactly as `creative-commons` was excluded in July |
| **Distinct organisation with a near-identical name** | `climate-action-network` (the US match is *US Climate Action Network*, a different entity from CAN International), `educate-girls` (*Educate Girls Globally* is not *Educate Girls*), `neighborworks-america`, `humane-society-international` |
| **No search result under any phrasing tried** | `carbon180`, `earthday-org`, `trans-lifeline`, `vibrant-emotional-health`, `climate-reality-project`, `nclr` |

The four duplicates are the actionable item here: they are not a verification
problem but a data-model one, and they inflate the "unverified" count with rows
that should not exist separately.

---

## 2026-08-04 — Australia, on evidence this time (+7 published, 1 badge corrected)

Australia was next in Block E because the ABR publishes a per-charity page. On
opening `fix_au_abns` it turned out its check was the CRA trap again: it accepted
an ABN whenever `abr.business.gov.au/ABN/View?abn={abn}` returned **HTTP 200**,
and that URL returns 200 for invented numbers too — 99999999999, 12345678901 and
00000000000 each answer with an 8,777-byte "not found" body and a 200 status.

Unlike CRA, the ABR body *does* discriminate, so the check moved onto the content.
Three conditions now, all read out of the page:

1. the register lists a name for this ABN;
2. one of those names is the charity — the page carries the entity name plus any
   business and trading names, and any one of them may be the familiar one;
3. the page says the entity is **registered as a charity with the ACNC** — an ABN
   alone is issued to any business and is not the claim the badge makes.

**All 25 Australian rows were then re-checked on that basis.** The 16 already
carrying a badge every one held up — the old check had been getting the right
answer for the wrong reason, because the ABNs had been sourced by hand from the
ACNC register.

**7 newly published**, each ABN found by name search on ABN Lookup and confirmed
on its own record page:

| slug | ABN | Register entity | Note |
|---|---|---|---|
| acrf-australia | 27076461360 | Australian Cancer Research Foundation | |
| asrc-refugee | 64114965815 | Asylum Seeker Resource Centre Inc. | |
| mater-foundation-au | 96723184640 | The Trustee for Mater Foundation | |
| oz-harvest | 33107782196 | Oz Harvest Limited / OzHarvest | |
| vinnies-australia | 50748098845 | St Vincent de Paul Society National Council of Australia | **stored ABN was right all along** — it had simply never been checked |
| walter-eliza-hall-institute | 12004251423 | The Walter and Eliza Hall Institute of Medical Research | |
| wilderness-society-australia | 18611229086 | The Wilderness Society Ltd. | |

**1 badge corrected.** `rfds-australia` presents the national Royal Flying Doctor
Service, and its verified ABN 71004196230 belongs to *Royal Flying Doctor Service
of Australia (Victorian Section)*. A live wrong-entity badge, the same shape as
the Canadian "Salvation Army Comox Valley" case. Re-pointed to **74438059643**,
the national body in the ACT.

### The 2 that stay hidden

- **`salvation-army-australia`** — every ABN under that name is a state property
  trust. There is no single national entity to point at, so the row would have to
  claim one state's registration for a national organisation.
- **`kids-helpline-yourtown`** — the register knows the entity as *yourtown*;
  Kids Helpline is the service it runs. The name check rejects it, correctly:
  confirming a name the registry does not carry would be inventing the link. The
  fix is a decision about the catalogue entry's own name, not a verification step.

---

## 2026-08-04 — New Zealand: a new country, and four numbers belonging to strangers (+3 published)

The Charities Register turned out to be usable after all: the July roadmap had it
as "API blocks HEAD", but the per-charity page at
`register.charities.govt.nz/Charity/{CC}` is plain server-rendered HTML carrying
the legal name, the registration number and the current status. It also returns
**HTTP 200 for CC99999999 and for ZZ12345**, so — third registry running — the
status code says nothing and the content says everything.

New command `fix_nz_ccnumbers`, same shape as the US and AU ones. It requires
three things off the record: the legal name is this charity, the registration
number on the page is the one asked for, and the status is **Registered**.

Checking all 7 stored numbers against that produced this:

| slug | stored | the register answers | |
|---|---|---|---|
| forest-and-bird-nz | CC26943 | Royal Forest & Bird Protection Society of New Zealand Inc | ✅ correct |
| salvation-army-nz | CC37312 | The Salvation Army New Zealand | ✅ correct |
| nz-cancer-society | CC23722 | **The Fred Hollows Foundation (NZ)** | ❌ another catalogue entry's number |
| fred-hollows-foundation-nz | CC36306 | **Society of St Vincent de Paul, Hutt Valley** | ❌ |
| canteen-nz | CC11146 | **Ashburton Seniors Centre Trust** | ❌ |
| world-vision-nz | CC36358 | **Society of St Vincent de Paul, Kaiapoi** — *Deregistered* | ❌ |
| nz-red-cross | CC11663 | not in the register | ❌ |

**Five of seven stored a number that is not theirs.** None was published, so
nothing false was ever shown — the `listed` status was doing its job again — but
the figures were sitting in the database as fact. This is Finding 7's Canada
result repeating in a second country, which says the defect is in how the seed
data was assembled rather than in any one registry.

`world-vision-nz` is the one that justifies the status gate on its own: CC36358 is
a real record for a real organisation that was **deregistered**. A check that
stopped at "the page exists and names someone" would have passed it.

**3 published.** Two were already correct and had simply never been checked;
`fred-hollows-foundation-nz` was given CC23722 — the number `nz-cancer-society`
had been holding, which the register says is Fred Hollows'. Taking it required
clearing the wrong value off the Cancer Society row first, because
`(country, registration_id)` is unique.

### Still open in New Zealand

- `canteen-nz`, `nz-red-cross`, `world-vision-nz` still store a number that is
  demonstrably not theirs. They should be cleared, but only one row per country
  can hold an empty `registration_id` under the current unique constraint — so
  the model needs a nullable identifier before the other two can be emptied.
- `nz-cancer-society` now stores nothing, which is the honest state. Its real
  number has to come from the register's own search, which is POST-driven and
  reCAPTCHA-fronted, so it is not scriptable from here.

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

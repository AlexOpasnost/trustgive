# Data Integrity Report

> How TrustGive audits its own factual layer, what that audit found, and what now
> prevents the same class of defect from returning.
> Audit run: **2026-07-27**, against the production database and live registries.

TrustGive's entire premise is that it does not ask to be trusted — it shows the
regulator's document. That premise fails the moment the site states a fact it
cannot source. This report exists because a self-audit found exactly that, and the
findings are published rather than quietly patched.

---

## Finding 1 — Fabricated filing dates (severity: high, fixed)

**What was wrong.** `fix_us_eins.py` derived the "last filed" date arithmetically:

```python
charity.last_filed_date = date(year + 1, 1, 1)   # FY2023 -> 2024-01-01
```

That value is not a date on any filing. It is 1 January of the year following the
fiscal year. **71 charities (13% of the catalogue)** carried such a date, and the
detail page rendered it to users as a factual "Last filed 2024-01-01".

**Why it survived.** The value is well-formed and plausible, so schema checks,
tests, and visual review all pass. Only a comparison against the upstream source
exposes it — the same lesson recorded after the v3.18 source-link audit
(*never store a fact you have not read back from the source*), applied to a field
nobody had re-audited.

**The fix.**
- Root cause removed: the date now comes from ProPublica's `tax_prd` (`202312`
  → `2023-12-31`), the real fiscal-period end. When `tax_prd` is absent the field
  is set to **null** — an absent fact is honest, an invented one is not.
- New idempotent command **`refresh_us_filings.py`** repaired the catalogue and
  keeps it current: 67 fabricated dates corrected, 173 dates reconciled to the
  source, 164 financial records refreshed, 6 cleared to null.
- Remaining: **4** rows still carry a 1-January date because no resolvable EIN
  backs them; they are tracked, not silently kept.

**Consequence worth stating plainly.** With real dates, the honest count of
charities whose newest filing is over 24 months old rose from 258 to **429 of 541**.
The catalogue did not get worse — the fabricated dates had been masking how far
regulator publication lags reality.

---

## Finding 2 — A freshness stamp that would have lied (severity: high, fixed pre-release)

The API already computed `data_freshness.last_synced_at`, but no page displayed it.
While surfacing it as "Re-checked by TrustGive {date}", the stamp proved wrong:
Django does **not** refresh an `auto_now` field unless it is named in
`update_fields`, so rows re-verified today still reported their original seed date.

Caught before release. `updated_at` is now bumped on every successful re-check —
including checks where nothing changed, because the stamp means *"we looked at the
registry on this date"*, not *"something changed"*.

---

## Finding 3 — Unsupported "Verified" badges (severity: medium, partly fixed)

All **252** verified US charities were re-checked against ProPublica. **10** could
not fully support their badge:

| Cause | Count | Status |
|---|---:|---|
| EIN stored without its leading zero (`20554654` → `020554654`) | 4 | **Fixed** — padded and re-verified against the registry |
| Resolves, but ProPublica exposes no filing with financial data | 6 | Open — badge rests on registry presence alone |

The 4 padding cases were a display-accuracy defect: the identifier printed on the
page did not exist in that form. The remaining 6 need a decision — under the
published methodology ("filed financial documents in the last 24 months"), a
registry entry without a retrievable filing does not meet the bar.

---

## Finding 4 — The nightly refresh had never run (severity: medium, fixed)

`.github/workflows/etl.yml` invoked `ingest_propublica --since=24h`. No such
management command exists in the repository, so the "Nightly ETL" had been failing
without refreshing anything — which is why the catalogue was still a seed-time
snapshot. Replaced with the commands that are actually implemented:
`refresh_us_filings` (data currency) and `audit_source_links` (link rot).

---

## Finding 5 — Contradictory EINs in curated prose (severity: critical, fixed)

The most damaging defect found, and the one a careful reader would have hit first.

**27 US charities** stated an EIN inside their description that **contradicted the
verified identifier shown in the same page's identity strip**:

| Charity | Verified record | Prose claimed |
|---|---|---|
| Sesame Workshop | 13-2655731 | 13-1973898 |
| National MS Society | 13-5661935 | 13-3143009 |
| Tunnel to Towers | 02-0554654 | 02-0599710 |
| The Conservation Fund | 52-1388917 | 53-0337293 |
| …23 more | | |

These prose identifiers were written at seed time and never reconciled when
`fix_us_eins` later corrected each record against ProPublica. The result: a page
promising "check the regulator's file yourself" printed two different government
identifiers for the same organisation — one of them fictitious.

**The fix.** New command **`strip_false_eins.py`** removes the contradicting
identifier from the prose rather than rewriting it: the verified EIN is already
displayed authoritatively in the identity strip, and deleting a false claim is
safer than editing curated copy to insert a new one. A prose EIN that *matches* the
record is deliberately left in place. Applied to all 27 in both languages, with 0
residual contradictions; sentences remain intact — *"Sesame Workshop (founded 1968
as Children's Television Workshop) produces…"*.

**Verification after remediation:** fabricated dates `0`, prose/record EIN
contradictions `0`.

---

## Finding 6 — An unsound verification check, caught before use (severity: critical, disabled)

`fix_ca_bns.py` (written earlier the same day, never run) accepted a Canadian BN as
verified if the CRA charity URL returned HTTP 200. Tested against controls:

| BN | Real? | CRA response |
|---|---|---|
| 119304923RR0001 (World Vision Canada) | yes | 200, 55,230 bytes |
| 119304954RR0001 (WWF-Canada) | yes | 200, 55,230 bytes |
| **999999999RR0001** | **fabricated** | 200, 55,230 bytes |
| **123456789RR0001** | **fabricated** | 200, 55,230 bytes |

The endpoint is an Angular shell that returns a byte-identical response for every
input, so the check proved nothing — it would have stamped "Verified" on all 28
Canadian charities regardless of whether their numbers were real. Loading the same
URL in a browser reveals a further problem: it renders **HTTP 500**, so it could not
serve as the public source document either. Donors would have been sent to an error
page from a "Verified" badge.

The command now **fails closed** with an explanation and cannot be run until a
genuine evidence source is wired.

**Why this matters more than the bug itself:** a status-code check is the intuitive
way to validate a link, and it is wrong for any JavaScript-rendered registry. The
same trap applies to NZ, several EU registers, and any future source. The standing
rule is now: *validate against data the registry returns about the entity, never
against the transport status of a page.*

---

## Finding 7 — 22 of 28 Canadian registration numbers are wrong (severity: critical, open)

Canada was the largest verification gap (28 charities, 0% verified), and all 28
already carried CRA-format business numbers. Testing whether those numbers are real
required finding an endpoint that returns *data*, not a status code. The CRA
Angular app calls one:

```
GET /ebci/hacc/ngcids/rest/api/cidsRequest/retrieveReportingPeriod/{BN}
→ 200 {"charityAccountDetails":{"bnView":{"organizationName": "...", …}}}
```

It discriminates correctly: a BN taken from CRA's own search returns the
organisation's legal name; a fabricated BN returns HTTP 417, as does an unknown one.

**Result across all 28 stored Canadian numbers:**

| Outcome | Count | Meaning |
|---|---:|---|
| Resolves, name matches the charity | **6** | Genuine (MSF, Heart & Stroke, Nature Conservancy, Plan International, WWF-Canada, Canadian Cancer Society) |
| Resolves, name is a **different organisation** | **2** | `boys-girls-clubs-canada` → "BLENHEIM UNITED CHURCH ENDOWMENT FUND"; `salvation-army-canada` → "THE SALVATION ARMY COMOX VALLEY COMMUNITY CHURCH" (a local church, not the national body) |
| Does not resolve | **20** | Same response as a fabricated control |

**22 of 28 (79%) display a government identifier that is wrong or unverifiable.**
None of them carried a "Verified" badge — the honest `listed` status was doing its
job — but the number itself was still printed on the page as fact.

The two wrong-entity matches are the important lesson: **a resolving identifier is
not evidence.** Verification must match the returned legal name against the charity,
exactly as the US pipeline does. Any check that stops at "the ID exists" will
happily attach a village church to a national charity.

**Caveat before acting:** HTTP 417 is being read as "not in the registry". That
inference is well-supported (a control fabrication returns it, and 8 real BNs return
data) but is not the registry saying "no such charity" in words. The 20 should be
re-derived from CRA's search by name rather than mass-deleted on this signal alone.

**Blocker for Canada regardless of the numbers:** CRA exposes no addressable
per-charity page. Result links are `javascript:void(0);` inside an Angular app, and
the legacy deep link returns HTTP 500. So even a correctly verified Canadian charity
currently has no public document to link to — which is TrustGive's whole promise.
Canada cannot reach "Verified" under the published methodology until that is solved.

---

## Finding 7 — Full US name-match audit: 4 wrong-entity badges (severity: high, fixed)

Canada showed that a *resolving* identifier proves nothing — the number can belong
to a different organisation entirely. That test had never been applied to the US
catalogue, where every EIN had been accepted simply because it resolved.

Audited all 296 US charities against ProPublica by comparing the registry's legal
name with the catalogue name (token overlap, corporate noise stripped). **244 had a
checkable record; 17 fell below the similarity threshold; 13 of those were benign**
— acronyms (ASPCA → *American Society for the Prevention of Cruelty to Animals*),
legal names (charity: water → *Charity Global Inc*), and genuine 2025 rebrands
(Leukemia & Lymphoma Society → *Blood Cancer United*; HSUS → *Humane World for
Animals*). That leaves **4 real failures, all carrying a "Verified" badge**:

| Charity | Stored EIN | Actually resolved to | Corrected EIN |
|---|---|---|---|
| possible-health | 562618866 | **Gates Foundation** (Seattle) | 203055055 — Nyaya Health |
| marine-conservation-institute | 943105570 | **Oceanic Society Expeditions** (Ross, CA) | 911725640 |
| earthwatch | 237162696 | *Unknown Organization*, 0 filings | 237168440 — Earthwatch Institute |
| wildlife-alliance | 411533188 | *Unknown Organization*, 0 filings | 521934148 — Wildlife Alliance Inc |

`earthwatch` is instructive: `237162696` vs the correct `237168440` differ by a
digit transposition — a plausible-looking EIN that resolved to nothing.

All four were re-sourced to their real records (each confirmed with 13–14 filings
and FY2023 revenue) and now carry real fiscal-period end dates rather than the
fabricated 1-January placeholder.

**Headline result: 240 of 244 checkable US records (98.4%) were correct.** The US
catalogue — the bulk of the site — is genuinely sound; the failures were isolated
and are now fixed.

---

## Finding 8 — 43 revenue figures the cited source did not support (severity: critical, fixed)

Found 2026-08-03 while preparing a research piece, not by a scheduled check —
which is itself the lesson: every existing control watches *identifiers and
links*, and none watched the money column.

The trail started at Compassion International, whose `last_filed_date` of
2019-06-30 looked like a stale-field bug. It wasn't: ProPublica's newest filing
with data for that EIN really is FY2019. The wrong thing was a `Financial` row
for **FY2023** carrying exactly **$1,100,000,000** and labelled
"IRS Form 990, FY 2023 (ProPublica)" — a period that source does not have.

Sweeping for the same shape found the scale. **43 of 385 financial rows had a
revenue that is an exact multiple of $10,000,000**, and every one sat on a
*published* charity; 35 of them were the figure rendered on the card and profile.
A genuine Form 990 or Charity Commission total landing on a round ten million is
vanishingly unlikely; 43 of them is the signature of seeded data.

| Cited as | Rows |
|---|---:|
| Annual report & accounts (Charity Commission UK) | 21 |
| Annual report (organisation's own publication) | 11 |
| IRS Form 990, FY 2023 (ProPublica) | 8 |
| IRS Form 990, FY 2022 (ProPublica direct PDF) | 3 |

Four were checked against the source they name; none held up:

| Charity | Displayed | Source says |
|---|---|---|
| catholic-relief-services | $1,100,000,000 | 0 filings with data for that EIN |
| catholic-charities-usa | $240,000,000 | 0 filings with data |
| compassion-international | FY2023 row | newest period is FY2019 |
| donorschoose | FY2023 row | newest period is FY2022 |

This is the §5 defect class moved into the money column: a figure that looks like
it came from a government filing, cited to that filing, where the filing does not
exist. It is the single worst thing this catalogue can publish.

**Resolution.** `strip_unsourced_financials` re-checked every flagged row against
ProPublica where an EIN existed, repaired the 6 it could, and deleted the 37 it
could not. UK and self-published figures are unrecoverable — the currency and
basis of the conversion were never stored, so there is nothing to check them
against. 35 charities now show no revenue at all.

Two of the repairs show what was at stake: ACLU Foundation was displaying
$400,000,000 against an actual $185,146,988, and CARE USA $700,000,000 against
$909,098,267 — wrong in both directions.

No charity was demoted. Their *registration* is still verified against a document
that opens; only the money was unsourced, which is exactly the line the profile's
"What we didn't check" block already draws.

The command distinguishes "the source says no" from "we could not reach the
source", and skips rather than deletes on the latter. That distinction was added
after two consecutive dry runs disagreed by one row: a timeout had silently
downgraded to "unsupported", which would have deleted a sound figure.

---

## Finding 9 — The ingest command would have re-created Findings 1, 3 and 7 (severity: high, fixed)

Found 2026-08-04, on opening `ingest_propublica` to start growing the catalogue —
which is the point. Every previous finding was repaired in the *repair* commands.
Nobody had re-read the command that **adds** rows, and it still carried the
original defects, so each new ingest would have reintroduced them at the same rate
they were being cleaned up.

| Defect | What it did | Matches |
|---|---|---|
| `charity.last_filed_date = date(year + 1, 1, 1)` | Stored a synthesised 1 January as a factual filing date | Finding 1, verbatim |
| `verification_status = VERIFIED`, set unconditionally *before* the filings were read | Any EIN that merely resolved earned the badge — no filing needed, no name check | Findings 3, 6, 7 |
| `fix_us_eins._fetch()` returned `None` for every failure | A dropped TCP connection printed "EIN does not resolve on ProPublica" | Finding 8's distinction, missing here |

The third one fired during this session's own batch: three rows whose EINs had
verified seconds earlier were skipped with a message stating their identifier was
wrong. Harmless in that direction — a skip is not a deletion — but the message was
false, and the same code shape is what silently downgraded a timeout to
"unsupported" in Finding 8.

**The fix.**
- `_period_end()` reads `tax_prd`, null when absent. Same function as
  `refresh_us_filings`, and now tested rather than duplicated on trust.
- Promotion requires **both** a filing carrying real revenue **and** a name match
  against what the registry returns.
- `_fetch()` distinguishes 404 ("the registry has no such EIN") from a transport
  failure ("we could not ask"), retries the latter, and reports it as retryable
  rather than as a verdict.

**On the name check.** It compares identifying-token *sets for equality*. A
substring test and a subset test were both measured against live ProPublica
search results on 2026-08-03 and both accepted wrong entities — "Chesapeake
Climate Action Network" for *Climate Action Network*, and "Sickle Cell Disease
Association Of America Michigan Chapter Inc" for the national body. An extra
identifying word is usually a different organisation.

It also accepts the IRS **trade name** (`sort_name`), not only the legal one:
EIN 03-0355315 is legally "Us Working Group Inc" and publicly Forest Stewardship
Council US; 52-1886511 is legally "Rape Abuse And Incest National Network Inc"
and publicly RAINN. Ignoring that field would mean refusing an answer the registry
itself publishes about its own entity.

**Its limit, stated rather than hidden.** Where two real organisations reduce to
the same identifying words — *Climate Action Network* vs *The US Climate Action
Network*, *NeighborWorks America* vs *National NeighborWorks Association* — no
comparison of the two strings can separate them. There is a test that asserts
this, so the limit lives in the suite instead of being discovered on a public
page. What contains it: the check guards rows ingested *from* the registry, where
the catalogue name is the registry name and the ambiguity cannot arise. Pointing
an existing curated row at a new identifier stays a reviewed step in
`fix_us_eins`.

---

## Finding 10 — The Australian check was the Canadian one, and it had already shipped (severity: high, fixed)

Found 2026-08-04, immediately after Finding 9 and by the same move: reading the
command instead of trusting its docstring.

`fix_au_abns` promoted a charity when
`https://abr.business.gov.au/ABN/View?abn={abn}` returned **HTTP 200**. Tested
against controls:

| ABN | Real? | ABR response |
|---|---|---|
| 28004778081 (World Vision Australia) | yes | 200, 21,147 bytes, entity named |
| 99668654249 (RSPCA Australia) | yes | 200, 19,161 bytes, entity named |
| **99999999999** | **fabricated** | 200, 8,777 bytes, no entity |
| **12345678901** | **fabricated** | 200, 8,777 bytes, no entity |
| **00000000000** | **fabricated** | 200, 8,777 bytes, no entity |

This is Finding 6 verbatim — a status code standing in for evidence — with one
difference that matters: the CRA command was caught before it ever ran, and this
one had already promoted **16 live rows**.

**Were any of them wrong?** No. All 16 were re-checked against the page body and
all 16 hold up. But that is a property of the input, not of the check: the ABNs
had been sourced by hand from the ACNC register, so the check was never asked a
question it could get wrong. A control that cannot fail is not evidence that the
data is right.

**What the check reads now**, all from the page body: that the register lists a
name for the ABN, that one of the names it lists is the charity, and that the
entity is *registered as a charity with the ACNC*. The last one is not redundant —
an ABN is issued to any business, and "this business exists" is not the claim a
verification badge makes.

**One real defect surfaced by the new check.** `rfds-australia` — presented as the
national Royal Flying Doctor Service — was verified against ABN 71004196230,
which the register names *Royal Flying Doctor Service of Australia (Victorian
Section)*. A live wrong-entity badge, the same shape as the Canadian
`salvation-army-canada` → local church case in Finding 7. Corrected to the
national body's ABN, 74438059643.

**The general rule, now applied twice in one day:** ask the registry for *data
about the entity* and compare it to the entity you are claiming. Every registry
whose front door is a web page will answer 200 to nonsense.

---

## Finding 11 — Five of seven New Zealand numbers belong to other organisations (severity: high, partly fixed)

Found 2026-08-04, applying the Finding 10 method to a third registry.

`register.charities.govt.nz/Charity/{cc}` answers **200 for CC99999999 and for
ZZ12345**, so the status code was never going to help here either. It is
server-rendered though, and carries the legal name, the registration number and
the current status. Checking the 7 stored numbers against those fields:

| Outcome | Count | Rows |
|---|---:|---|
| Correct | 2 | `forest-and-bird-nz`, `salvation-army-nz` |
| Registered to a **different organisation** | 4 | `canteen-nz` → *Ashburton Seniors Centre Trust*; `fred-hollows-foundation-nz` → *St Vincent de Paul, Hutt Valley*; `nz-cancer-society` → *The Fred Hollows Foundation (NZ)*; `world-vision-nz` → *St Vincent de Paul, Kaiapoi* (**deregistered**) |
| Not in the register at all | 1 | `nz-red-cross` |

**5 of 7 (71%)** stored a government identifier that is not theirs — the Canada
result from Finding 7 (79%) repeating in an unrelated country. Two countries
failing the same way says the fault is in how the seed data was assembled, not in
any one registry.

None of the seven was published, so nothing false reached a reader. That is the
verified-only filter working as designed, and it is the second time it has caught
this exact thing.

**`world-vision-nz` is the instructive one.** CC36358 is a genuine record for a
genuine organisation which is **deregistered** — New Zealand removes charities
that stop filing and keeps serving their page. A check that stopped at "the page
exists and names an organisation" would have passed it. `fix_nz_ccnumbers`
therefore requires the status to read *Registered*, on top of the name match.

**Partly fixed.** 3 rows published (including `fred-hollows-foundation-nz`, whose
correct number was the one `nz-cancer-society` had been holding). The remaining
wrong numbers cannot all be cleared yet: `registration_id` is a non-null
`CharField` under a `(country, registration_id)` unique constraint, so exactly one
row per country can hold the empty string. **Making that field nullable is the
prerequisite for removing a known-false identifier**, and it is now the blocker
for finishing this in NZ, Canada, and anywhere else the same shape turns up.

---

## Finding 12 — The nightly job removed badges when it could not reach the registry (severity: critical, fixed)

Found 2026-08-05, not by a scheduled check but by running the scheduled check
by hand and reading what it proposed.

`audit_source_links` classified each charity's links three ways: at least one
returns 200 (keep), none work and one answered 404/410 (clean), or none work and
none answered at all (timeouts, 5xx, rate limits). The third case **demoted the
charity**, with the reasoning that a demotion destroys nothing and is reversible.

A dry run said what that costs. ProPublica was throttling the calling host, 235
links came back unreachable, and the command proposed demoting **232 of 398
published charities** — a registry having a bad night would have emptied more
than half the catalogue, silently, at 02:00.

It had already happened at small scale. The published count moved 400 → 398
overnight while the Charity Commission was slow: `breast-cancer-now` and
`donkey-sanctuary` lost their badges to timeouts, not to dead links. Both
documents return 200 today.

This is the Finding 8 rule broken in a different command. That command was
explicitly built to *"distinguish the source says no from we could not reach the
source, and skip rather than delete on the latter"*. `audit_source_links` made
the distinction for **deletion** and ignored it for **demotion** — but a demoted
charity is hidden from the public API, so demotion is the user-visible act.

**The fix.** Unreachable now changes nothing; it prints `[REVIEW]` and moves on.
Demotion requires a registry actually answering 404/410, or no source document at
all. A timeout is not a regulator saying a filing does not exist, and the badge's
claim does not stop being true because a server did not answer in ten seconds.

The decision is now a pure function, `verdict_for(statuses)`, so the rule that
can remove a charity from the catalogue is testable without a database or a
network — `apps/charities/tests/test_source_link_verdicts.py` pins it, including
the shape of the 2026-08-05 sweep. The command also warns when unreachable links
outnumber reachable ones, so a run that measured the network cannot be read as a
finding about the catalogue.

**Also fixed here:** three `save(update_fields=[...])` calls changed
`verification_status` without naming `updated_at`. That is the Finding 2 trap
again — Django does not refresh an `auto_now` field unless it is listed — so a
row this command demoted tonight still told the reader it was last re-checked
months ago. The "freshness stamp is bumped per re-check" control was only ever
true of `refresh_us_filings`.

**Not restored.** The two demoted UK rows stay hidden. Re-promotion needs the
register to name the charity, and it will not: the Charity Commission page for
`1160558` carries no charity name in its server-rendered HTML, and the page for
`264818` names "THE DONKEY SANCTUARY — **1207593**", a different registration
number. Handing a badge back on a bare 200 is the defect this report opens with.

---

## What now prevents recurrence

| Control | Mechanism |
|---|---|
| Dates always sourced, never derived | `_period_end()` reads `tax_prd`; null when absent |
| Data currency | `refresh_us_filings` nightly via GitHub Actions → Railway |
| Evidence outliving its badge | `audit_source_links` nightly; demotes on a link the registry answers 404/410 for — never on one it merely failed to answer (Finding 12) |
| Freshness visible to the reader | `updated_at` bumped per re-check *and* per demotion, rendered on every profile |
| Search-engine currency | IndexNow submits all 1,085 URLs daily from the Cloudflare Worker |
| Unsourced money figures | `strip_unsourced_financials`; `check_financial_rows.py` re-runs the sweep |
| A fresh ingest re-creating repaired defects | `apps/ingestion/tests/test_propublica_evidence.py` pins the date and name-match rules |
| A status code standing in for evidence (AU) | `apps/charities/tests/test_au_registry_evidence.py` runs the parser over a real record, the 200-with-no-entity body, and a non-charity |
| Another organisation's registration, or a deregistered one (NZ) | `fix_nz_ccnumbers` requires legal name + the number asked for + status `Registered`; `apps/charities/tests/test_nz_registry_evidence.py` pins it against the five real mismatches |
| A registry outage emptying the catalogue | `verdict_for()` demotes only on a real 404/410; unreachable is reported, never acted on. Pinned by `test_source_link_verdicts.py` |
| A stale freshness stamp on a row the ETL just changed | every `save()` in `audit_source_links` now names `updated_at` alongside `verification_status` |

## Open items

1. Decide the treatment of the 6 registry-only "verified" charities.
2. ~~45 US EINs do not resolve on ProPublica — triage.~~ **Done 2026-08-04**:
   39 hidden US rows re-searched by name, 37 of their stored EINs were 404s,
   21 recovered and published, 18 documented with a reason in
   [`VERIFICATION_COVERAGE.md`](VERIFICATION_COVERAGE.md).
3. Non-US coverage: 141 charities remain `listed`; Canada (28) is still blocked —
   see [`VERIFICATION_COVERAGE.md`](VERIFICATION_COVERAGE.md). Australia is now
   23 of 25 and New Zealand 3 of 7.
4. 35 charities now display no revenue (Finding 8). For the 21 UK ones the figure
   is recoverable in principle — the Charity Commission publishes income on the
   register — but not from anything currently stored, and its API needs a key.
5. Nothing runs the Finding 8 sweep on a schedule. `check_financial_rows.py` is
   manual; it belongs in the nightly ETL alongside `audit_source_links`.
6. **Four duplicate catalogue rows** found while doing (2): `jdrf-breakthrough-t1d`
   / `jdrf`, `sea-shepherd-conservation-society` / `sea-shepherd`,
   `lcv-education-fund` / `league-conservation-voters`, and
   `whale-and-dolphin-conservation-usa` / `whale-dolphin-conservation-us`. Each
   pair is one organisation held twice, so the unique-registration constraint
   permanently keeps the second copy unverifiable. They need merging, not
   verifying, and until then they inflate the unverified count by four.
7. **`Charity.registration_id` cannot be emptied.** It is a non-null `CharField`
   inside a `(country, registration_id)` unique constraint, so at most one row per
   country can hold `""`. Removing a *known-false* identifier is therefore
   impossible beyond the first one — which is the blocker for finishing Finding 11
   in New Zealand and for acting on Finding 7 in Canada. Make it nullable.
8. **Two UK charities are hidden by a bug that no longer exists.**
   `breast-cancer-now` and `donkey-sanctuary` were demoted overnight by the
   Finding 12 defect, and nothing re-promotes automatically. Both documents
   return 200, but neither can be re-verified the way the US, AU and NZ rows
   were: the Charity Commission's page carries no charity name in its
   server-rendered HTML. They come back when the UK path has a real name check —
   which is what the Charity Commission API key is for.
9. **`donkey-sanctuary` may hold the wrong number.** Its stored registration is
   `264818`, and that register page prints "THE DONKEY SANCTUARY — 1207593".
   Whether `264818` is a superseded record or the wrong charity entirely has not
   been established; it is unpublished either way, so nothing false is on display.

## Method

Counts come from the production API and the production database directly. Every US
identifier was checked against
`https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json`
(free, no key); a claim was accepted only when the returned legal name matched the
catalogue entry and a filing with data existed. No identifier was written without
that read-back.

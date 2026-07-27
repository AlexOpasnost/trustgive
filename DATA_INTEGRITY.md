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

## What now prevents recurrence

| Control | Mechanism |
|---|---|
| Dates always sourced, never derived | `_period_end()` reads `tax_prd`; null when absent |
| Data currency | `refresh_us_filings` nightly via GitHub Actions → Railway |
| Evidence outliving its badge | `audit_source_links` nightly; demotes on a dead link |
| Freshness visible to the reader | `updated_at` bumped per re-check, rendered on every profile |
| Search-engine currency | IndexNow submits all 1,085 URLs daily from the Cloudflare Worker |

## Open items

1. Decide the treatment of the 6 registry-only "verified" charities.
2. 45 US EINs do not resolve on ProPublica — triage (most are `listed`, so they
   assert nothing, but they should not sit in the catalogue unexamined).
3. Non-US coverage: 175 charities remain `listed`; Canada (28) is tooled but
   unmapped — see [`VERIFICATION_COVERAGE.md`](VERIFICATION_COVERAGE.md).

## Method

Counts come from the production API and the production database directly. Every US
identifier was checked against
`https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json`
(free, no key); a claim was accepted only when the returned legal name matched the
catalogue entry and a filing with data existed. No identifier was written without
that read-back.

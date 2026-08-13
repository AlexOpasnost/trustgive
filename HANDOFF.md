# TrustGive — handoff

> Written 2026-08-11, updated 2026-08-13. Read this first, then
> `DATA_INTEGRITY.md` (the "Open items" list is the real backlog), then
> `STRATEGY.md` if you need the plan. Work in Russian with the owner.

---

## What this is

Charity discovery that links every claim to the regulator's own filing.
trustgive.org (Cloudflare Worker + static SPA), api.trustgive.org (Django on
Railway, Neon Postgres). Source lives at
`D:\gamesss\ProjectX\app_creater\projects\trustgive`.

**394 published charities across 11 countries.** 537 rows in the database; 143
are hidden by the `PUBLISHED` filter in `apps/charities/models.py` and return the
moment they can be verified.

Published by country: US 274 · GB 75 · AU 23 · ES 6 · IT 4 · NZ 3 · IN 3 ·
RU 2 · DE 2 · NL 1 · BR 1. **339 of the 394 show a revenue figure; 55 show none**
(was 290/104 before the UK money repair of 2026-08-13).

---

## The one rule everything else serves

**A record is published only when its document opens *and* the registry names
the same organisation.** An identifier that merely resolves is not evidence.
Never write a registration number, a date or a money figure that was not read
back from the source.

Its corollary, which this project has now learned five separate times:

> **"The source said no" and "we could not reach the source" are different
> facts, and code must not collapse them.**

Every incident below is a variation on one of those two sentences.

---

## Where the work stands

### Blocks A–F of STRATEGY: all done

F shipped 2026-08-10: six-step type scale, four spacing bands, green reserved
for verification only, dagger logo replaced, dark mode wired up. See `DESIGN.md`
v3.2.

### The UK task — done 2026-08-13

All six flagged rows were re-checked against sources the extract does not derive
from and acted on; `breast-cancer-now` and `donkey-sanctuary` are back; 65 of the
75 published GB rows now carry the register's own income with the exchange rate
stored beside it. Written up as **Findings 17 and 18** in `DATA_INTEGRITY.md`; the
paragraphs below are kept because they describe the data source and its traps,
which the next country will need.

Three things came out of it that are worth carrying forward:

1. **The screening pass's ten "false positives" were not false.** The register
   publishes working and previous names in a companion extract
   (`publicextract.charity_other_names.zip`). NSPCC, SIGHTSAVERS and SUSTRANS are
   all in it. The gate did not need to be loosened from equality to substring —
   it needed the register's own list of names. Do this before widening any rule.
2. **The live search is fuzzy *and* paginated.** Asking for 219099 returns a
   hundred RSPCA branches ahead of the RSPCA. At the default page of 20 the code
   concluded "no such registered charity", which is the project's oldest mistake
   in new clothes. Always go through `uk_register.lookup_number`, which answers
   `found` / `absent` / `unknown` and calls a full page without the number
   `unknown`.
3. **Outside the United States, every published revenue figure was seeded.** All
   16 of them, exact multiples of $100,000, sitting in the gap below Finding 15's
   $1M threshold. If another country's money is ever filled, check the shape at
   $100K first.

**The Charity Commission API key is not a blocker.** The regulator
publishes the entire register as an open daily download, no key:

```
https://ccewuksprdoneregsadata1.blob.core.windows.net/data/json/publicextract.charity.zip
```

397,878 rows, ~57 MB, refreshed daily. Fields: `charity_name`,
`registered_charity_number`, `charity_registration_status` (Registered/Removed),
`latest_income`, `latest_expenditure`, `linked_charity_number`. Companion files
(`publicextract.charity_annual_return_parta.zip` etc.) are listed on
<https://register-of-charities.charitycommission.gov.uk/en/register/full-register-download>.

**Trap in that file:** several rows share one `registered_charity_number`,
separated by `linked_charity_number`. Only `linked_charity_number == 0` is the
charity itself; the rest are subsidiary funds. Number 1089464 returns "GIBB
RESEARCH FELLOWSHIP ENDOWMENT FUND" on its linked row and Cancer Research UK on
row 0. Filter first or you will match the wrong entity.

**Fetch it with Python, not PowerShell** — `Invoke-WebRequest` fails the TLS
handshake against that blob host; `urllib` works.

**Get the companion names file too**, `publicextract.charity_other_names.zip`
(4 MB, same host). Without it the name gate rejects NSPCC, Sightsavers, Sustrans
and sixteen others; with it, they match on the register's own working or previous
name and the rule stays an equality test.

The commands that use all this:

```
python manage.py fix_gb_registrations --file=../gb_registration_fixes.json --dry-run
python manage.py fill_gb_revenue --extract=charity.zip --other-names=other_names.zip --dry-run
```

Both re-verify against the live register before writing, both refuse rather than
guess, and both report "could not read" separately from "the register said no".
`gb_registration_fixes.json` and `gb_false_regs.json` in the project root are the
record of what was decided and why; re-running them is a no-op, which is the
point.

**Currency is stored, not assumed.** `Financial` carries `original_currency`,
`original_amount`, `fx_rate`, `fx_rate_date` and `fx_source` since migration
0060, and `apps/charities/fx.py` reads the ECB reference rates. If another
country's money is ever filled, fill those five fields or the nightly audit will
fail the run — deliberately.

### Decisions the owner has already made

| Question | Answer |
|---|---|
| Bulk-ingest uncurated US orgs from ProPublica | **No** — the catalogue stays curated |
| Charities with no filing at all | **Demote** — done, 4 removed |
| Dark mode | **Ship it** — done |
| Catalogue licence | **CC0 1.0** — declared in the Dataset markup and on /api |
| IndexNow after a change | Wait for the 06:00 UTC cron |
| Annual report "State of Charity Transparency" | Not now |
| UK API key | Registered, confirmation email had not arrived. **Not needed** — the open extract plus the live register did the whole job |

### Search Console

The owner clicked **VALIDATE FIX** on the Soft 404 issue on 2026-08-11. Expect
Google to recrawl those 19 URLs over the following days.

Two numbers to watch, and they move independently:

- **Soft 404: 19 → 0.** Our side is already done; this is just revalidation.
- **Discovered — currently not indexed: 640 → 346 → ?** Crawl queue, moves on its
  own. 562 pages indexed as of 2026-08-10.

You can read Search Console yourself through **Claude in Chrome** (the owner's
own session — there is no separate account to grant you, and telling them to add
an email address is wrong; that mistake was made in this session). The console is
a heavy SPA and `get_page_text` sometimes times out waiting for `document_idle` —
retry, or take a screenshot instead.

---

## Findings closed in this session

All are written up in `DATA_INTEGRITY.md`; this is the index.

| # | What | Severity |
|---|---|---|
| 11 | Five of seven New Zealand numbers belonged to other organisations | high |
| 12 | The nightly link audit demoted on "could not reach the registry" — one throttled run proposed hiding **232 of 398** published charities | critical |
| 14 | Four organisations were in the catalogue twice | low |
| 15 | The money sweep looked for multiples of $10M while 70 published rows were multiples of $1M; **17 of 17 checkable ones were wrong** | critical |
| 16 | Four badges rested on registration alone, with no filing behind them | medium |
| 17 | Five published UK charities on another organisation's or a dead registration; confirmed against three independent sources each before anything moved | critical |
| 18 | **Every** published revenue figure outside the US — 16 of them — was an exact multiple of $100,000, sitting just below Finding 15's threshold | critical |

Plus, outside `DATA_INTEGRITY.md`:

- **Unpublished charity URLs answered HTTP 200** with the SPA shell. Google
  recorded 19 soft 404s. `lookupBySlug` in `worker/index.ts` now returns
  found/gone/unknown and answers 404, 200, 200 respectively.
- **`perf.yml` was red for eight straight weeks** against a healthy API, because
  `k6-load.js` hard-coded a slug that had been renamed. Slugs now come from the
  API at startup.
- **`cn()` was silently deleting classes** — tailwind-merge did not know the
  project's custom tokens, so the donate button's text colour was being merged
  away and rendered at ~3.4:1. `lib/utils.ts` now declares them; `utils.test.ts`
  pins it.
- **The Worker was never typechecked.** `tsconfig.app.json` covers only `src`,
  and wrangler bundles with esbuild. CI now runs `worker/tsconfig.json`.
- **Nothing validated the workflow files.** A line starting at column 1 inside a
  `run: |` block made `monitor.yml` unparseable; the run produced *no jobs* and
  `gh workflow run` misreported it as "no dispatch trigger". CI now runs
  `yaml.safe_load` + `bash -n` over every workflow.

---

## Traps — all of these cost real time

### Windows / shell

1. **Never rewrite files through PowerShell** (`Get-Content`/`-replace`/
   `WriteAllText`) — it mangles Cyrillic. Use the editing tools only.
2. **Multi-line PowerShell arguments break.** A here-string `@'…'@` does not
   assemble into one argument. Write commit messages to a file and use
   `git commit -F <path>`. This was violated once this session and failed exactly
   as documented.
3. **Local bash is `D:\msys64\usr\bin\bash.exe`.** Git Bash is not installed and
   WSL is broken (`execvpe(/bin/bash) failed`).
4. **Some hosts fail under PowerShell's TLS but work under Python** — the
   Charity Commission blob storage is one. If `Invoke-WebRequest` gives
   "connection closed", retry with `urllib` before concluding anything.

### Verification

5. **Check content, not status codes.** Every charity registry tested returns
   HTTP 200 for a fabricated identifier — CRA, ABR, NZ Charities Services. See
   the memory note `registry-status-codes-are-not-evidence`.
6. **Compare identifying-token *sets for equality*.** Substring and subset tests
   both matched wrong entities in live testing.
7. **Put known-good and known-bad controls in every registry sweep.** A Canadian
   re-check once returned the fabricated-number response for charities already
   confirmed genuine; only the controls failing too revealed it was a formatting
   bug, not a data finding.
8. **A green scheduled job proves nothing until you read what it asserts.** All
   four workflows in this repo had a defect. `perf.yml` was red for two months
   and everyone had learned to ignore the mail. The nightly money audit was the
   next one: green for four days over 16 fabricated figures, because its
   threshold was $1M and every survivor was a multiple of $100K (Finding 18).
9. **A search result page can be full.** The Charity Commission's search is
   fuzzy and paginated; asking it for the RSPCA's number returns a hundred RSPCA
   branches first. "The number was not on the page" is not "the register does
   not hold it". Any registry lookup you write needs three answers, not two —
   see `uk_register.lookup_number`.
10. **Before widening a name rule, look for the registry's own alias list.** Ten
   apparent mismatches in the UK screening were trading names the Charity
   Commission publishes in a companion file. The fix was to give the gate more
   *data*, not less *rule*.

### Deploy

11. **`wrangler deploy` does not always land.** Compare the bundle hash:
    `(Get-ChildItem frontend\web\dist\assets\index-*.js)[0].Name` against what
    trustgive.org actually serves. Wrangler lives in
    `frontend\web\node_modules\.bin\` — there is no root `package.json`.
12. **Bump `SITEMAP_VERSION` in `worker/index.ts`** whenever the sitemap's
    contents *or* a cached page's status code changes — it keys the edge cache.
    Currently `v3.28`.
13. **The CDN caches by URL before the Worker runs.** Only the TTL
    (`s-maxage=300`) helps. Bust with `?cb=…`, but remember any extra parameter
    on `/charities` triggers the noindex branch.

### Local limits

14. **pytest needs Postgres and only runs in CI** (Docker is dead). But
    **DB-free tests do run locally** — write verification logic as pure
    functions and you get a same-second loop. That caught three real bugs in the
    first session and the pagination bug in the second.
15. **`wrangler dev` cannot reach the API** (egress goes through a proxy workerd
    ignores). Verify the Worker on production after deploying.
16. **Django against prod:** `backend\.venv\Scripts\python.exe manage.py <cmd>`,
    always `--dry-run` first. Neon sometimes drops the first connection — retry.
    It did exactly that, once, on the first write of the UK run.
17. **Port 5173 may hold another worktree's dev server.** Start yours elsewhere;
    do not kill theirs.
18. **The Worker typecheck binary is `frontend/web/node_modules/.bin/tsc`.**
    `npx tsc` pulls a decoy package off npm that is not the TypeScript compiler.

---

## Automation

| Workflow | Schedule | What it does |
|---|---|---|
| `ci.yml` | push / PR | lint, types, pytest, vitest, **workflow YAML + shell validation**, **Worker typecheck** |
| `monitor.yml` | every 6 h | asserts page *content*, count agreement across three endpoints, 10 charities carry a document, a missing charity answers 404 |
| `etl.yml` | nightly 02:00 UTC | `refresh_us_filings`, `audit_source_links`, `audit_financial_sources --strict` |
| `perf.yml` | Sundays 03:00 UTC | k6 smoke, k6 load, Lighthouse |

`etl.yml` checks out the repo and runs it via `railway run`, so a fix on `main`
is live for that night's run — no deploy needed.

**All four were green as of 2026-08-11.** `audit_financial_sources --strict`
watches a wider net since 2026-08-13 (Finding 18): $100K instead of $1M, plus a
rule that a non-US figure must state the currency it was converted from. It ran
clean immediately after the repair — 362 rows, 0 flagged — but the next country
whose money gets filled will fail it unless the five FX fields are written.

---

## Access

Cloudflare authorised (`wrangler login` done, credentials on disk). Railway
deploys on `git push`. `gh` CLI works. Claude in Chrome connects to the owner's
browser — useful for Search Console, and the only way to reach it.

---

## How to know you are done, rather than feeling done

The catalogue's own measure: **the share of published rows whose regulator
document opens and names the right organisation.** Not the number of charities.
The 541-row catalogue with a third unverified was weaker than the 394-row one
that is fully sourced.

When you claim something is fixed, show the command output. When a check cannot
run, say so plainly instead of reasoning about what it would have said — that
distinction is the whole product.

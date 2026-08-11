# TrustGive — handoff

> Written 2026-08-11. Read this first, then `DATA_INTEGRITY.md` (the "Open
> items" list is the real backlog), then `STRATEGY.md` if you need the plan.
> Work in Russian with the owner.

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
RU 2 · DE 2 · NL 1 · BR 1. 290 of the 394 show a revenue figure; 104 show none,
which is the honest state after the money clean-up below.

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

### The immediate open task — UK, and it needs a decision

**The Charity Commission API key is no longer a blocker.** The regulator
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

Screening all 77 GB rows against it gave 59 clean matches and this:

| Row | Stored № | Register says | Reading |
|---|---|---|---|
| `cure-leukaemia` | 1100994 | PAG (PARENT ACTION GROUP) LIMITED, Removed, £6,435 | wrong entity |
| `leprosy-mission-uk` | 261249 | SIR GEORGE WEIDENFELD CHARITABLE TRUST, Removed | wrong entity |
| `maggies-cancer` | 1058460 | EURO CHARITY TRUST, Registered, £3.1M | wrong entity |
| `big-issue-foundation` | 1049077 | THE BIG ISSUE FOUNDATION, **Removed** | right name, dead registration |
| `joseph-rowntree-foundation` | 210169 | THE JOSEPH ROWNTREE FOUNDATION, **Removed** | right name, dead registration |
| `donkey-sanctuary` | 264818 | absent from the register entirely | wrong number (already hidden) |

**All five of the first are published right now.** This is the Finding 7/11
defect in a third country, and the first time it has been on rows the public can
see.

**Do not act on this from one source.** The same screening produced ten *false*
mismatches — NSPCC vs "National Society for the Prevention of Cruelty to
Children", Diabetes UK vs "British Diabetic Association", Sightsavers vs "Royal
Commonwealth Society for the Blind", Sustrans vs "Walk Wheel Cycle Trust" (a
genuine 2025 rename). A gate that produces ten false positives in one pass has
not earned the right to demote a famous charity unchecked. "Removed" on Joseph
Rowntree Foundation most likely means they re-registered as a CIO under a new
number — find the live number by name in the same extract before touching
anything.

**The owner was asked whether to proceed and had not answered when this was
written.** Roughly an hour of work: confirm each of the five by name, then either
correct the number or demote.

Two easy wins waiting behind the same extract:

- **`breast-cancer-now` is recoverable now.** Register says "BREAST CANCER NOW",
  status Registered, income £59,270,000. It is hidden only because the nightly
  audit demoted it on a timeout (Finding 12, since fixed) and nothing
  re-promotes automatically.
- **21 UK charities show no revenue** (a consequence of Finding 8). `latest_income`
  in the extract fills that — but it is GBP, and the field on the model is
  `total_revenue_usd`. Do not write a converted figure without storing the rate
  and date; that is how Finding 8 happened in the first place.

### Decisions the owner has already made

| Question | Answer |
|---|---|
| Bulk-ingest uncurated US orgs from ProPublica | **No** — the catalogue stays curated |
| Charities with no filing at all | **Demote** — done, 4 removed |
| Dark mode | **Ship it** — done |
| Catalogue licence | **CC0 1.0** — declared in the Dataset markup and on /api |
| IndexNow after a change | Wait for the 06:00 UTC cron |
| Annual report "State of Charity Transparency" | Not now |
| UK API key | Registered, confirmation email had not arrived. Now optional — see above |

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
   and everyone had learned to ignore the mail.

### Deploy

9. **`wrangler deploy` does not always land.** Compare the bundle hash:
   `(Get-ChildItem frontend\web\dist\assets\index-*.js)[0].Name` against what
   trustgive.org actually serves.
10. **Bump `SITEMAP_VERSION` in `worker/index.ts`** whenever the sitemap's
    contents *or* a cached page's status code changes — it keys the edge cache.
    Currently `v3.27`.
11. **The CDN caches by URL before the Worker runs.** Only the TTL
    (`s-maxage=300`) helps. Bust with `?cb=…`, but remember any extra parameter
    on `/charities` triggers the noindex branch.

### Local limits

12. **pytest needs Postgres and only runs in CI** (Docker is dead). But
    **DB-free tests do run locally** — write verification logic as pure
    functions and you get a same-second loop. That caught three real bugs this
    session.
13. **`wrangler dev` cannot reach the API** (egress goes through a proxy workerd
    ignores). Verify the Worker on production after deploying.
14. **Django against prod:** `backend\.venv\Scripts\python.exe manage.py <cmd>`,
    always `--dry-run` first. Neon sometimes drops the first connection — retry.
15. **Port 5173 may hold another worktree's dev server.** Start yours elsewhere;
    do not kill theirs.

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

**All four were green as of 2026-08-11.**

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

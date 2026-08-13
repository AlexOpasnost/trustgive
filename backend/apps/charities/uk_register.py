"""Reading the Charity Commission register for England and Wales.

Two sources, and the difference between them is the point.

* **The open daily extract.** The regulator publishes the whole register as a
  file, no key:
  `https://ccewuksprdoneregsadata1.blob.core.windows.net/data/json/publicextract.charity.zip`
  ~397,000 rows, refreshed daily. It is the only one of the two that carries
  `latest_income` together with the financial period it belongs to, so anything
  about money has to come from here.

* **The live register search.** The web application the public uses, answering
  now. It carries number, name, status and income, and it is a genuinely
  separate pipeline from the nightly blob, which is why it is worth asking
  twice.

Both are read here because a screening pass over the extract alone produced ten
false mismatches on trading names in August 2026 — NSPCC against "National
Society for the Prevention of Cruelty to Children", Sightsavers against "Royal
Commonwealth Society for the Blind". A gate with that error rate may not demote
a charity on its own say-so.

Three things bite when reading either source:

1. **Several rows share one charity number.** Only `linked_charity_number == 0`
   is the charity itself; the rest are subsidiary funds. Number 1089464 answers
   "GIBB RESEARCH FELLOWSHIP ENDOWMENT FUND" on a linked row and Cancer Research
   UK on row 0.
2. **The live search is fuzzy, and it paginates.** Asking for 1050327 returns
   that charity *and* an unrelated one; asking for 219099 returns a hundred
   RSPCA branches sorted ahead of the RSPCA itself. A row is evidence only when
   its number is the number asked for, and a full page with no such row means
   the question was not answered — not that the charity is absent.
   `lookup_number` is the only sanctioned way to ask.
3. **Its default scope is currently-registered charities.** "No match" therefore
   means "not a registered charity", not "no such number ever" — a removed
   charity needs `status="removed"` to be seen at all. Collapsing those two is
   the mistake this project has now made five times.

Nothing in this module writes to the database, so its rules are testable without
Postgres (which does not run locally here).
"""

from __future__ import annotations

import html
import http.cookiejar
import re
import time
import urllib.parse
import urllib.request

BASE = "https://register-of-charities.charitycommission.gov.uk"
PORTLET = "_uk_gov_ccew_portlet_CharitySearchPortlet_"
CHARITY_URL = BASE + "/charity-search/-/charity-details/{number}/accounts-and-annual-returns"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# The site's own page sizes are 20/50/100/200. 20 is not enough to ask about a
# number: 219099 is the RSPCA, and a search for it returns its branches first —
# the charity itself is the 40th row. At 20 the answer came back "no registered
# charity 219099", which is the project's oldest mistake wearing a new hat.
PAGE_SIZE = 200

# Words that carry no identifying signal in a charity's name. Deliberately short.
#
# "foundation", "trust" and "fund" are NOT noise in Britain and must never be
# added: Joseph Rowntree Foundation, Joseph Rowntree Charitable Trust and Joseph
# Rowntree Housing Trust are three different charities with three different
# numbers, and dropping those words merges them into one. The New Zealand list
# does drop them, which is safe there and would not be here.
_NAME_NOISE = frozenset(
    """the of and for a an in to at on ltd limited inc incorporated cio company
    co plc registered""".split()
)


def tokens(name: str) -> set[str]:
    name = (name or "").replace("'", "").replace("’", "").replace("&", " and ")
    name = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    return {t for t in name.split() if t and t not in _NAME_NOISE and len(t) > 1}


def name_forms(catalogue_name: str) -> list[set[str]]:
    """Token sets the catalogue entry may legitimately be known by.

    Catalogue names carry the legal name in brackets or after a dash — "Sands —
    Stillbirth and Neonatal Death Society". Both halves are this organisation and
    the register may hold either, so both are offered rather than one discarded.
    """
    raw = catalogue_name or ""
    forms = [raw, re.sub(r"\(.*?\)", " ", raw)]
    forms += re.findall(r"\((.*?)\)", raw)
    forms += [p for p in re.split(r"\s[—–-]\s", raw) if p.strip()]
    out: list[set[str]] = []
    for f in forms:
        t = tokens(f)
        if t and t not in out:
            out.append(t)
    return out


def names_match(catalogue_name: str, registry_names: list[str]) -> str | None:
    """Return the registry name that matches the catalogue entry, else None.

    Equality of identifying-token sets, the rule the US, AU and NZ gates use.
    Substring and subset tests both matched *wrong entities* in live testing, so
    neither is accepted here. `registry_names` may include the working and
    previous names the register itself records for that number, which is how
    "NSPCC" is allowed to equal its legal name without loosening the rule.
    """
    forms = name_forms(catalogue_name)
    for candidate in registry_names:
        reg = tokens(candidate)
        if reg and any(form == reg for form in forms):
            return candidate
    return None


def find_number(rows: list[dict], number: str) -> dict | None:
    """The row that is actually about `number`.

    The live search is fuzzy and returns neighbours. Everything else in the
    result set is about some other charity and must not be read as an answer.
    """
    want = str(number).strip()
    for row in rows:
        if str(row.get("number", "")).strip() == want:
            return row
    return None


def parse_income(text: str | None) -> int | None:
    """'£2,918,464' -> 2918464.

    Anything that is not a plain amount returns None rather than a number. The
    income cell also carries 'Removed' and 'Recently registered', and reading
    either of those as zero would put a false £0 on a charity's profile.
    """
    cleaned = re.sub(r"[^0-9.]", "", text or "")
    if not re.fullmatch(r"\d+(\.\d+)?", cleaned):
        return None
    return int(float(cleaned))


def _opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", UA),
        ("Accept", "text/html,application/xhtml+xml,*/*;q=0.8"),
        ("Accept-Language", "en-GB,en;q=0.9"),
    ]
    return opener


def parse_results(page: str) -> list[dict]:
    rows: list[dict] = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = [
            html.unescape(re.sub(r"<[^>]+>", " ", cell)).replace("\xa0", " ").strip()
            for cell in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)
        ]
        cells = [c for c in cells if c]
        if len(cells) >= 3 and re.fullmatch(r"\d{6,8}", cells[0]):
            rows.append(
                {
                    "number": cells[0],
                    "name": cells[1],
                    "status": cells[2],
                    "income": cells[3] if len(cells) > 3 else None,
                }
            )
    return rows


def live_search(
    keywords: str,
    status: str | None = None,
    timeout: int = 60,
    attempts: int = 3,
    delta: int = PAGE_SIZE,
) -> tuple[list[dict], str | None]:
    """Ask the live register. Returns (rows, error).

    `error` set means the register could not be read — never that the charity is
    absent. `status="removed"` is required to see a charity the Commission has
    taken off the register; without it the search covers registered charities
    only.
    """
    params = {
        "p_p_id": "uk_gov_ccew_portlet_CharitySearchPortlet",
        "p_p_lifecycle": "1",
        "p_p_state": "normal",
        "p_p_mode": "view",
        PORTLET + "cur": "1",
        PORTLET + "delta": str(delta),
        PORTLET + "keywords": keywords,
        PORTLET + "priv_r_p_useSession": "true",
        PORTLET + "priv_r_p_mvcRenderCommandName": "/search-results",
        PORTLET + "orderByCol": "charity-number",
        PORTLET + "orderByType": "asc",
    }
    if status:
        params[PORTLET + "filterCharityStatus"] = status
    url = f"{BASE}/en/charity-search?" + urllib.parse.urlencode(params)

    last: str | None = None
    for attempt in range(attempts):
        opener = _opener()
        try:
            # The results URL is a portlet action; it needs the session the
            # search page hands out, so that page is fetched first.
            opener.open(f"{BASE}/en/charity-search", timeout=timeout).read()
            with opener.open(url, timeout=timeout) as resp:
                page = resp.read().decode("utf-8", "replace")
        except Exception as exc:  # every failure here means "unreachable", nothing more
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2.0 * (attempt + 1))
            continue

        rows = parse_results(page)
        if rows:
            return rows, None
        if re.search(r"\b(no results|0 match|match(es)? found)", page, re.I):
            return [], None
        last = "results table not recognised in the response"
        time.sleep(2.0 * (attempt + 1))
    return [], last


def lookup_number(
    number: str, status: str | None = None, delta: int = PAGE_SIZE
) -> tuple[str, dict | None, str]:
    """Ask the live register about one charity number.

    Returns one of three verdicts, and the whole point of this function is that
    they are three and not two:

      ``("found", row, note)``   -- the register answered about this number
      ``("absent", None, note)`` -- the register answered, and this number is not
                                    in the scope searched
      ``("unknown", None, why)`` -- we did not get an answer: the site could not
                                    be read, or the results page was full and the
                                    number could have been on the next one

    "absent" is a fact about the register. "unknown" is a fact about us. Writing
    code that turns the second into the first is how one throttled run once
    proposed hiding 232 of 398 published charities.
    """
    rows, err = live_search(number, status=status, delta=delta)
    if err:
        return "unknown", None, err
    row = find_number(rows, number)
    if row is not None:
        return "found", row, f"{row['name']!r}, status {row['status']}"
    if len(rows) >= delta:
        return (
            "unknown",
            None,
            (
                f"the results page was full ({len(rows)} rows) and {number} was not on it; "
                f"the register may hold it further down"
            ),
        )
    scope = status or "registered"
    return "absent", None, f"the register returns no {scope} charity {number}"

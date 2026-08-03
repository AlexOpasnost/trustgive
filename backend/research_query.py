"""Measure what the catalogue can and cannot verify, and how stale filings are.

Read-only reporting script behind the /research articles. Run from backend/:

    .venv/Scripts/python.exe research_query.py

Kept in the repo rather than in a scratch directory so the figures published on
/research can be re-derived by anyone, which is the whole point of publishing
them. It touches whatever database DJANGO_SETTINGS_MODULE points at and writes
nothing.
"""

from __future__ import annotations

import datetime as dt
import os
from collections import Counter, defaultdict
from urllib.parse import urlparse

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trustgive.settings.development")
django.setup()

from apps.charities.models import Charity, SourceDocument  # noqa: E402

VERIFIED = "verified"


def main() -> None:
    print("=" * 70)
    print("PART 1 - what can and cannot be verified")
    print("=" * 70)

    total = Charity.objects.count()
    by_status = Counter(Charity.objects.values_list("verification_status", flat=True))
    print(f"rows in database    : {total}")
    for status, n in by_status.most_common():
        print(f"  {status:<12} {n:>5}  ({100 * n / total:.1f}%)")

    unver = Charity.objects.exclude(verification_status=VERIFIED)
    n_unver = unver.count()
    no_docs = unver.filter(source_documents__isnull=True).distinct().count()
    print(f"\nunverified          : {n_unver}")
    print(f"  with no document  : {no_docs}")
    print(f"  with a document   : {n_unver - no_docs}  (link did not resolve at audit)")

    print("\nunverified by country (top 15):")
    for code, n in Counter(unver.values_list("country", flat=True)).most_common(15):
        print(f"  {code:<4} {n:>5}")

    print("\nverification rate by country (>=5 rows):")
    all_by_country = Counter(Charity.objects.values_list("country", flat=True))
    ver_by_country = Counter(
        Charity.objects.filter(verification_status=VERIFIED).values_list("country", flat=True)
    )
    rows = [
        (code, n_all, ver_by_country.get(code, 0), 100 * ver_by_country.get(code, 0) / n_all)
        for code, n_all in all_by_country.items()
        if n_all >= 5
    ]
    for code, n_all, n_ver, pct in sorted(rows, key=lambda r: -r[1]):
        print(f"  {code:<4} {n_ver:>4}/{n_all:<4}  {pct:5.1f}% verified")

    print()
    print("=" * 70)
    print("PART 2 - how far behind the filings are")
    print("=" * 70)

    today = dt.date.today()
    pub = Charity.objects.filter(verification_status=VERIFIED)
    lag_by_country: dict[str, list[int]] = defaultdict(list)
    missing = Counter()
    for code, filed in pub.values_list("country", "last_filed_date"):
        if filed is None:
            missing[code] += 1
        else:
            lag_by_country[code].append((today - filed).days)

    with_date = sum(len(v) for v in lag_by_country.values())
    print(f"published charities     : {pub.count()}")
    print(f"  with a filing date    : {with_date}")
    print(f"  without a filing date : {sum(missing.values())}")
    print(f"  missing-date by country: {missing.most_common(10)}")

    print("\nmonths between fiscal-period end and today, by country (n>=3):")
    for code, lags in sorted(lag_by_country.items(), key=lambda kv: -len(kv[1])):
        if len(lags) < 3:
            continue
        lags.sort()
        median = lags[len(lags) // 2]
        print(
            f"  {code:<4} n={len(lags):<4} median {median / 30.44:5.1f}"
            f"   min {min(lags) / 30.44:4.1f}   max {max(lags) / 30.44:5.1f}"
        )

    all_lags = sorted(d for lags in lag_by_country.values() for d in lags)
    if all_lags:
        median_all = all_lags[len(all_lags) // 2]
        over_two_years = sum(1 for d in all_lags if d > 730)
        print(f"\noverall median lag      : {median_all / 30.44:.1f} months")
        print(
            f"  older than 24 months  : {over_two_years} of {len(all_lags)}"
            f"  ({100 * over_two_years / len(all_lags):.0f}%)"
        )

    print("\nregistry host -> published charities citing it:")
    per_host: dict[str, set[str]] = defaultdict(set)
    for slug, url in pub.values_list("slug", "source_documents__url"):
        if not url:
            continue
        host = urlparse(url).netloc.lower().removeprefix("www.")
        per_host[host].add(slug)
    for host, slugs in sorted(per_host.items(), key=lambda kv: -len(kv[1]))[:8]:
        print(f"  {host:<48} {len(slugs):>4}")

    print("\ndocument kinds among published charities:")
    kinds = Counter(
        SourceDocument.objects.filter(charity__verification_status=VERIFIED).values_list(
            "kind", flat=True
        )
    )
    for kind, n in kinds.most_common():
        print(f"  {kind:<28} {n:>5}")


if __name__ == "__main__":
    main()

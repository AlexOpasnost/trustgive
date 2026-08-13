"""Write UK revenue from the Charity Commission's own income figure.

Finding 8 deleted 43 unsourced revenue figures and could repair only the
American ones; the twenty-one British rows were left empty because the number
had been converted to dollars with no record of the rate. This command is the
repair, and it exists in this shape because of what the money column looked like
underneath: **every non-US revenue figure still published in August 2026 was an
exact multiple of $100,000**, which is not what a filing produces.

What it reads
-------------
The regulator's open daily extract, no key:

    https://ccewuksprdoneregsadata1.blob.core.windows.net/data/json/publicextract.charity.zip

That file is the only source that carries `latest_income` *together with the
financial period it covers*, and a figure without its period is not a fact about
a year. Fetch it with Python — the blob host fails PowerShell's TLS handshake.
Only `linked_charity_number == 0` is the charity itself.

What it checks before writing anything
--------------------------------------
1. the extract row's name must equal the catalogue name under the
   identifying-token rule (`uk_register.names_match`), and its status must be
   *Registered*;
2. the **live** register must return the same number with the same income. The
   extract is a nightly snapshot and the search is a live query; requiring both
   is what stops a screening pass from writing money on its own authority;
3. the income must have a financial period end date, which becomes the year the
   figure is filed under and the day its exchange rate is taken from.

Currency
--------
The register publishes pounds and the column is `total_revenue_usd`, so a
conversion is unavoidable. It is stored with the pounds it came from, the rate,
the date of the rate and who published it (`apps.charities.fx`, European Central
Bank reference rates). An unrecorded conversion is what made Finding 8's UK rows
unrepairable, and it will not be repeated silently.

    python manage.py fill_gb_revenue --extract=publicextract.charity.zip --dry-run
    python manage.py fill_gb_revenue --extract=publicextract.charity.zip
"""

from __future__ import annotations

import datetime as dt
import json
import time
import zipfile
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.charities import fx, uk_register
from apps.charities.models import Charity, Financial, VerificationStatus

CENTS = Decimal("0.01")


def read_extract(path: str) -> dict[int, dict]:
    """{charity number: the charity's own row} from publicextract.charity.zip.

    The file is a JSON array with one object per line. Streaming it line by line
    keeps half a gigabyte of JSON out of memory. Rows with a non-zero
    `linked_charity_number` are subsidiary funds sharing the number and are
    dropped here: 1089464 answers "GIBB RESEARCH FELLOWSHIP ENDOWMENT FUND" on
    one of them and Cancer Research UK on row 0.
    """
    out: dict[int, dict] = {}
    for record in _stream(path):
        if record.get("linked_charity_number") == 0:
            out[record["registered_charity_number"]] = record
    return out


def read_other_names(path: str) -> dict[int, list[str]]:
    """{charity number: working and previous names the register records for it}.

    From `publicextract.charity_other_names.zip`, the companion file. This is the
    register's own answer to the trading-name problem: it holds NSPCC under "The
    National Society for the Prevention of Cruelty to Children" and separately
    records "NSPCC", and Sustrans under "Walk Wheel Cycle Trust" with "Sustrans"
    as a previous name. Offering these to the name gate keeps it an equality test
    instead of forcing it down to a substring one — which is the change that
    would let another organisation's number through.
    """
    out: dict[int, list[str]] = {}
    for record in _stream(path):
        if record.get("linked_charity_number") == 0:
            out.setdefault(record["registered_charity_number"], []).append(record["charity_name"])
    return out


def _stream(path: str):
    archive = zipfile.ZipFile(path)
    name = archive.infolist()[0].filename
    with archive.open(name) as raw:
        for line in raw:
            text = line.decode("utf-8-sig").strip().lstrip("[,").rstrip("]")
            if text:
                yield json.loads(text)


class Command(BaseCommand):
    help = "Write GB revenue from the Charity Commission register, with the rate recorded."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--extract", required=True, help="publicextract.charity.zip")
        parser.add_argument(
            "--other-names",
            required=True,
            help="publicextract.charity_other_names.zip — the register's own working "
            "and previous names, without which the gate rejects NSPCC and Sustrans.",
        )
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
        parser.add_argument(
            "--slug", action="append", default=[], help="Limit to these slugs (repeatable)."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry: bool = options["dry_run"]
        only = set(options["slug"])

        self.stdout.write("reading the register extract…")
        register = read_extract(options["extract"])
        extract_date = next(iter(register.values()))["date_of_extract"][:10] if register else "?"
        self.stdout.write(f"  {len(register)} charities, extract of {extract_date}")
        aliases = read_other_names(options["other_names"])
        self.stdout.write(f"  {sum(len(v) for v in aliases.values())} working / previous names")

        self.stdout.write("reading ECB reference rates…")
        try:
            history = fx.load_history()
        except fx.RateUnavailableError as exc:
            raise CommandError(f"{exc}\nNo rate, no conversion, no write.") from exc
        self.stdout.write(f"  {len(history)} publication days")

        charities = Charity.objects.filter(
            country="GB", verification_status=VerificationStatus.VERIFIED
        ).order_by("slug")
        if only:
            charities = charities.filter(slug__in=only)

        written = skipped = unreachable = 0
        with transaction.atomic():
            for charity in charities:
                slug = charity.slug
                number = (charity.registration_id or "").strip()
                if not number.isdigit():
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- no numeric registration stored")
                    continue

                record = register.get(int(number))
                if record is None:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {number} is not in the extract")
                    continue

                catalogue_name = (charity.name or {}).get("en") or ""
                names = [record["charity_name"], *aliases.get(int(number), [])]
                matched = uk_register.names_match(catalogue_name, names)
                if not matched:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- {number} is {record['charity_name']!r}, "
                        f"not {catalogue_name!r}; money is not written on a disputed number"
                    )
                    continue
                if record["charity_registration_status"] != "Registered":
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- {number} has status "
                        f"{record['charity_registration_status']!r}"
                    )
                    continue

                income = record.get("latest_income")
                period_end = record.get("latest_acc_fin_period_end_date")
                if income is None or not period_end:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- the register holds no income with a financial "
                        f"period behind it"
                    )
                    continue
                gbp = Decimal(str(income)).quantize(CENTS)
                if gbp <= 0:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- register income is {gbp}")
                    continue
                period_end_date = dt.date.fromisoformat(period_end[:10])

                # Second source: the live register has to agree, to the pound.
                verdict, live, note = uk_register.lookup_number(number)
                if verdict == "unknown":
                    skipped += 1
                    unreachable += 1
                    self.stdout.write(f"[RETRY] {slug} -- {note}; left unchanged")
                    continue
                if verdict == "absent":
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {note}")
                    continue
                live_income = uk_register.parse_income(live["income"])
                if live_income is None:
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- the live register shows no income for {number} "
                        f"({live['income']!r})"
                    )
                    continue
                if Decimal(live_income) != gbp.to_integral_value():
                    skipped += 1
                    self.stdout.write(
                        f"[SKIP]  {slug} -- extract says £{gbp:,.0f}, live register says "
                        f"£{live_income:,}; two sources disagree, so neither is written"
                    )
                    continue

                try:
                    rate, rate_date = fx.cross_rate(history, "GBP", "USD", period_end_date)
                except fx.RateUnavailableError as exc:
                    skipped += 1
                    self.stdout.write(f"[SKIP]  {slug} -- {exc}")
                    continue

                usd = (gbp * rate).quantize(CENTS, rounding=ROUND_HALF_UP)
                year = period_end_date.year
                label = (
                    f"Charity Commission register: income £{gbp:,.0f} for the year ended "
                    f"{period_end_date:%d %b %Y}"
                )[:200]

                self.stdout.write(
                    f"[WRITE] {slug} -- {number} {matched!r}, FY{year} £{gbp:,.0f} "
                    f"x {rate:.5f} ({rate_date}) = ${usd:,.2f}"
                )
                written += 1
                if dry:
                    continue

                # One figure per charity-year, and the old rows are the seeded
                # ones this command replaces, so they go rather than accumulate.
                charity.financial_history.all().delete()
                Financial.objects.create(
                    charity=charity,
                    year=year,
                    total_revenue_usd=usd,
                    source_url=uk_register.CHARITY_URL.format(number=number),
                    source_label=label,
                    original_currency="GBP",
                    original_amount=gbp,
                    fx_rate=rate.quantize(Decimal("0.00000001")),
                    fx_rate_date=rate_date,
                    fx_source=fx.ECB_LABEL,
                )
                charity.total_revenue_usd = usd
                charity.last_filed_date = period_end_date
                charity.save(update_fields=["total_revenue_usd", "last_filed_date", "updated_at"])
                time.sleep(0.5)

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). written={written} "
                f"skipped={skipped} unreachable={unreachable}"
            )
        )
        if unreachable:
            self.stdout.write(
                self.style.WARNING(
                    f"{unreachable} row(s) were left unchanged because the live register could "
                    f"not be read, not because the figure failed. Re-run to finish them."
                )
            )

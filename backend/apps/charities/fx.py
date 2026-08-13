"""Currency conversion with the rate written down beside the figure.

Finding 8 deleted 43 revenue figures, and the reason the UK ones could not be
repaired instead was not that the money was unknown — the Charity Commission
publishes income for every registered charity. It was that the figures had been
converted into `total_revenue_usd` without anyone recording *what rate, on what
day, from which source*, so there was nothing to check them against. An
unlabelled conversion is indistinguishable from an invented number.

So this module never returns a converted amount on its own. It returns the rate
together with the date it applies to and the source that published it, and the
caller is expected to store all three next to the result.

The source is the European Central Bank's euro foreign-exchange reference rates,
published every TARGET working day at
`https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml` (no key, back to
1999). The ECB quotes against the euro, so GBP->USD is the cross rate
USD-per-EUR / GBP-per-EUR.

Rates are published only on working days. A financial period ending on a weekend
or a holiday has no rate of its own, so the most recent *earlier* publication is
used and `rate_date` says so — that is a different day from the one asked for,
and pretending otherwise would be the same class of error this module exists to
prevent.
"""

from __future__ import annotations

import datetime as dt
import re
import urllib.request
from decimal import Decimal

ECB_HIST = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
ECB_LABEL = "European Central Bank euro reference rates"
MAX_BACKFILL_DAYS = 10


class RateUnavailableError(Exception):
    """The rate could not be read. Never means the rate is zero or unknown-forever."""


def parse_hist(xml: str) -> dict[dt.date, dict[str, Decimal]]:
    """{date: {currency: units per EUR}} from the ECB history file."""
    out: dict[dt.date, dict[str, Decimal]] = {}
    for day_block in re.split(r'<Cube\s+time="', xml)[1:]:
        stamp, _, rest = day_block.partition('"')
        try:
            day = dt.date.fromisoformat(stamp)
        except ValueError:
            continue
        rates = {
            cur: Decimal(rate)
            for cur, rate in re.findall(
                r'<Cube\s+currency="([A-Z]{3})"\s+rate="([0-9.]+)"\s*/>', rest.split("</Cube>")[0]
            )
        }
        if rates:
            out[day] = rates
    return out


def cross_rate(
    history: dict[dt.date, dict[str, Decimal]],
    base: str,
    quote: str,
    on: dt.date,
    max_backfill_days: int = MAX_BACKFILL_DAYS,
) -> tuple[Decimal, dt.date]:
    """How many `quote` units one `base` unit bought, and the day that rate is from.

    Walks back at most `max_backfill_days` because the ECB does not publish on
    weekends or holidays. Raises rather than guessing if nothing is within reach.
    """
    for back in range(max_backfill_days + 1):
        day = on - dt.timedelta(days=back)
        rates = history.get(day)
        if not rates:
            continue
        base_per_eur = Decimal("1") if base == "EUR" else rates.get(base)
        quote_per_eur = Decimal("1") if quote == "EUR" else rates.get(quote)
        if base_per_eur and quote_per_eur:
            return (quote_per_eur / base_per_eur), day
    raise RateUnavailableError(
        f"no {base}->{quote} reference rate within {max_backfill_days} days before {on}"
    )


def load_history(timeout: int = 180) -> dict[dt.date, dict[str, Decimal]]:
    request = urllib.request.Request(ECB_HIST, headers={"User-Agent": "trustgive/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return parse_hist(response.read().decode("utf-8", "replace"))
    except Exception as exc:
        raise RateUnavailableError(
            f"could not read {ECB_HIST}: {type(exc).__name__}: {exc}"
        ) from exc

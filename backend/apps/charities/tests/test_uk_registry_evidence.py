"""What the UK gate must accept and must refuse.

Pinned against the real August 2026 screening of all 77 GB rows, which produced
six genuine problems and, on a looser rule, ten false ones. Both halves matter:
a gate that misses the wrong-entity rows is useless, and a gate that demotes
NSPCC because the register spells it out in full is worse than useless.

No database is touched here, which is deliberate — Postgres does not run on the
development machine, so the rules live in pure functions and can be checked in
the same second they are written.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import apps.charities.uk_register as uk_register
from apps.charities import fx
from apps.charities.uk_register import (
    find_number,
    lookup_number,
    name_forms,
    names_match,
    parse_income,
    parse_results,
    tokens,
)


class TestNameTokens:
    def test_legal_form_words_are_noise(self):
        assert tokens("Stonewall Equality Limited") == {"stonewall", "equality"}
        assert tokens("The Salvation Army") == {"salvation", "army"}

    def test_foundation_trust_and_fund_are_not_noise(self):
        """The trap that made the New Zealand noise list unusable here.

        Joseph Rowntree Foundation (1184957), Joseph Rowntree Charitable Trust
        (210037) and Joseph Rowntree Housing Trust (574577) are three charities.
        Dropping "foundation" and "trust" collapses them into one token set and
        the gate would then accept any of the three for any other.
        """
        jrf = tokens("Joseph Rowntree Foundation")
        jrct = tokens("Joseph Rowntree Charitable Trust")
        assert jrf != jrct
        assert not names_match("Joseph Rowntree Foundation", ["JOSEPH ROWNTREE CHARITABLE TRUST"])

    def test_bracketed_and_dashed_forms_are_both_offered(self):
        forms = name_forms("Sands — Stillbirth and Neonatal Death Society")
        assert {"sands"} in forms
        assert {"stillbirth", "neonatal", "death", "society"} in forms


class TestNamesMatch:
    def test_exact_name_matches_whatever_the_register_capitalises(self):
        assert names_match("Cure Leukaemia", ["CURE LEUKAEMIA"]) == "CURE LEUKAEMIA"
        assert names_match(
            "The Leprosy Mission Great Britain", ["The Leprosy Mission Great Britain"]
        )

    def test_a_working_name_the_register_records_is_accepted(self):
        """The ten false mismatches of the first pass, and how they are answered.

        The register holds these organisations under their legal names and their
        trading names in a companion table. Offering both is what lets the gate
        stay an equality test instead of being loosened into a substring one.
        """
        assert (
            names_match(
                "NSPCC", ["NATIONAL SOCIETY FOR THE PREVENTION OF CRUELTY TO CHILDREN", "NSPCC"]
            )
            == "NSPCC"
        )
        assert names_match(
            "Sightsavers", ["ROYAL COMMONWEALTH SOCIETY FOR THE BLIND", "SIGHTSAVERS"]
        )
        assert names_match("Diabetes UK", ["BRITISH DIABETIC ASSOCIATION", "DIABETES UK"])

    def test_the_five_wrong_entities_are_refused(self):
        """Exactly the rows that were published on another charity's number."""
        assert not names_match("Cure Leukaemia", ["PAG (PARENT ACTION GROUP) LIMITED"])
        assert not names_match(
            "The Leprosy Mission Great Britain", ["SIR GEORGE WEIDENFELD CHARITABLE TRUST"]
        )
        assert not names_match("Maggie's Centres", ["EURO CHARITY TRUST"])

    def test_a_subsidiary_fund_sharing_the_number_is_refused(self):
        """1089464 answers this on a linked row and Cancer Research UK on row 0."""
        assert not names_match("Cancer Research UK", ["GIBB RESEARCH FELLOWSHIP ENDOWMENT FUND"])

    def test_an_empty_registry_name_never_matches(self):
        assert not names_match("Cure Leukaemia", [""])
        assert not names_match("", ["CURE LEUKAEMIA"])


class TestFuzzySearchResults:
    """The live search returns neighbours; only the row asked for is an answer."""

    ROWS = [
        {"number": "1050327", "name": "The Leprosy Mission Great Britain", "status": "Registered"},
        {
            "number": "1189019",
            "name": "JANET AND BRYAN MOORE CHARITABLE TRUST",
            "status": "Registered",
        },
    ]

    def test_the_asked_for_number_is_selected(self):
        assert find_number(self.ROWS, "1050327")["name"] == "The Leprosy Mission Great Britain"

    def test_a_number_that_is_not_in_the_results_is_not_answered_by_a_neighbour(self):
        assert find_number(self.ROWS, "1100994") is None

    def test_results_are_read_out_of_the_table(self):
        html = (
            "<table><tr><th>Charity number</th><th>Charity name</th></tr>"
            "<tr><td>1100154</td><td>CURE LEUKAEMIA</td><td>Registered</td>"
            "<td>&pound;2,918,464</td></tr></table>"
        )
        rows = parse_results(html)
        assert rows == [
            {
                "number": "1100154",
                "name": "CURE LEUKAEMIA",
                "status": "Registered",
                "income": "£2,918,464",
            }
        ]

    def test_income_that_is_not_a_number_is_not_read_as_zero(self):
        assert parse_income("£2,918,464") == 2918464
        assert parse_income("Removed") is None
        assert parse_income(None) is None
        assert parse_income("") is None


class TestLookupNumberHasThreeAnswers:
    """ "Not in the register" and "we did not get an answer" must not be one branch.

    The pagination case is not hypothetical. Asking the live search for 219099
    returns RSPCA *branches* sorted ahead of the RSPCA, and at the site's default
    page size of 20 the charity itself is off the page. The first version of this
    module reported that as "the register returns no registered charity 219099",
    which is the sentence this project has been burned by five times.
    """

    def _stub(self, monkeypatch, rows, err=None):
        monkeypatch.setattr(uk_register, "live_search", lambda *a, **k: (rows, err))

    def test_found_returns_the_row_asked_for(self, monkeypatch):
        self._stub(monkeypatch, [{"number": "219099", "name": "RSPCA", "status": "Registered"}])
        verdict, row, _ = lookup_number("219099", delta=200)
        assert verdict == "found"
        assert row["name"] == "RSPCA"

    def test_a_short_page_without_the_number_is_absence(self, monkeypatch):
        self._stub(
            monkeypatch,
            [{"number": "111111", "name": "SOMEBODY ELSE", "status": "Registered"}],
        )
        verdict, row, note = lookup_number("9999999", delta=200)
        assert verdict == "absent"
        assert row is None
        assert "9999999" in note

    def test_a_full_page_without_the_number_is_not_absence(self, monkeypatch):
        rows = [
            {"number": str(200000 + i), "name": f"BRANCH {i}", "status": "Registered"}
            for i in range(200)
        ]
        self._stub(monkeypatch, rows)
        verdict, row, note = lookup_number("219099", delta=200)
        assert verdict == "unknown"
        assert row is None
        assert "full" in note

    def test_an_unreachable_register_is_not_absence(self, monkeypatch):
        self._stub(monkeypatch, [], err="TimeoutError: timed out")
        verdict, _, note = lookup_number("219099", delta=200)
        assert verdict == "unknown"
        assert "Timeout" in note

    def test_removed_scope_is_named_in_the_absence_note(self, monkeypatch):
        self._stub(monkeypatch, [])
        _, _, note = lookup_number("264818", status="removed", delta=200)
        assert "removed" in note


class TestExchangeRate:
    HIST = (
        '<Cube time="2025-03-31">'
        '<Cube currency="USD" rate="1.0815"/><Cube currency="GBP" rate="0.83536"/></Cube>'
        '<Cube time="2025-03-28">'
        '<Cube currency="USD" rate="1.0800"/><Cube currency="GBP" rate="0.83500"/></Cube>'
    )

    def test_cross_rate_is_derived_from_the_two_euro_legs(self):
        history = fx.parse_hist(self.HIST)
        rate, day = fx.cross_rate(history, "GBP", "USD", dt.date(2025, 3, 31))
        assert day == dt.date(2025, 3, 31)
        assert round(rate, 5) == round(Decimal("1.0815") / Decimal("0.83536"), 5)

    def test_a_weekend_period_end_uses_the_previous_publication_and_says_so(self):
        """30 March 2025 was a Sunday. The rate is Friday's, and rate_date shows it."""
        history = fx.parse_hist(self.HIST)
        rate, day = fx.cross_rate(history, "GBP", "USD", dt.date(2025, 3, 30))
        assert day == dt.date(2025, 3, 28)
        assert rate > 1

    def test_no_rate_within_reach_raises_rather_than_guessing(self):
        history = fx.parse_hist(self.HIST)
        try:
            fx.cross_rate(history, "GBP", "USD", dt.date(2024, 1, 15), max_backfill_days=3)
        except fx.RateUnavailableError:
            return
        raise AssertionError("a missing rate must be an error, not an assumed one")

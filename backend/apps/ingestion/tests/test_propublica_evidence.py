"""The two gates that decide whether a ProPublica ingest may say "Verified".

Both gates existed only as prose until 2026-08-03. `ingest_propublica` stamped
`VERIFIED` on every record it touched, before it had even read the filings, and
stored `date(tax_prd_yr + 1, 1, 1)` as the filing date. That is DATA_INTEGRITY.md
Finding 1 (fabricated dates) and Findings 3/6/7 (a resolving identifier treated as
evidence) reproduced on every fresh ingest, in the one command whose whole job is
to add new rows to the catalogue.

These tests are deliberately about the pure helpers rather than the command: they
are the parts that encode the rule, they need no database, and a wrong answer here
is what puts a false badge on a public page.
"""

from __future__ import annotations

from datetime import date

import pytest

from apps.ingestion.management.commands.ingest_propublica import _names_match, _period_end


class TestPeriodEnd:
    """`last_filed_date` must be read from the filing, never derived from it."""

    def test_reads_the_real_fiscal_period_end(self):
        assert _period_end({"tax_prd": "202312"}) == date(2023, 12, 31)

    def test_handles_a_non_december_year_end(self):
        assert _period_end({"tax_prd": "202406"}) == date(2024, 6, 30)

    def test_handles_a_leap_february(self):
        assert _period_end({"tax_prd": "202402"}) == date(2024, 2, 29)

    @pytest.mark.parametrize(
        "raw",
        [None, "", "2023", "20231", "2023123", "202313", "202300", "18991", "abcdef"],
    )
    def test_returns_none_rather_than_inventing_a_date(self, raw):
        # The old code answered 1 January of the following year here. A null is
        # an absent fact; 2024-01-01 was a fact that never happened.
        assert _period_end({"tax_prd": raw}) is None

    def test_never_returns_a_synthetic_first_of_january(self):
        for month in range(1, 13):
            got = _period_end({"tax_prd": f"2023{month:02d}"})
            assert got is not None
            assert not (got.month == 1 and got.day == 1)


class TestNamesMatch:
    """A resolving EIN is not evidence; the returned legal name has to agree."""

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            ("Sea Shepherd Conservation Society", "Sea Shepherd Conservation Society"),
            ("Sustainable Conservation", "Sustainable Conservation"),
            ("Equal Justice Initiative (EJI)", "Equal Justice Initiative"),
            ("Food Research & Action Center (FRAC)", "Food Research & Action Center Inc"),
            ("Older Adults Technology Services (OATS)", "Older Adults Technology Services Inc"),
        ],
    )
    def test_accepts_the_same_organisation(self, catalogue, registry):
        assert _names_match(catalogue, registry) is True

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            # Real wrong-entity candidates thrown up by a name search on
            # 2026-08-03. Every one of them would have earned a badge under a
            # substring or subset test.
            ("Climate Action Network (CAN International)", "Chesapeake Climate Action Network"),
            ("Pacific Environment", "Pacific Institute For Studies In Development Environment"),
            ("RAINN", "Carys Rainn Foundation"),
            ("The END Fund", "Development Fund Of The West End Inc"),
            ("Humane Society International", "Arizona Humane Society"),
            ("Forest Stewardship Council US", "Central Oregon Forest Stewardship Foundation"),
            ("Educate Girls Globally", "Educate The Girls Inc"),
            (
                "Sickle Cell Disease Association of America",
                "Sickle Cell Disease Association Of America Michigan Chapter Inc",
            ),
        ],
    )
    def test_rejects_a_different_organisation(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            ("Climate Action Network (CAN International)", "The Us Climate Action Network"),
            ("NeighborWorks America", "National Neighborworks Association"),
        ],
    )
    def test_records_the_limit_of_name_matching(self, catalogue, registry):
        """These pairs are different organisations that this gate calls equal.

        Not a bug to be patched with a longer stop-word list — the names really
        do reduce to the same identifying words, and no comparison of the two
        strings can separate them. The test exists so the limit is visible in the
        suite rather than discovered on a live page.

        What contains it: this gate only guards rows ingested straight from the
        registry, where the catalogue name *is* the registry name, so the
        ambiguity cannot arise. Pointing an existing curated row at a new
        identifier goes through `fix_us_eins` with a human-confirmed mapping.
        """
        assert _names_match(catalogue, registry) is True

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [("", "Sea Shepherd Conservation Society"), ("Sea Shepherd", ""), ("Inc", "The Fund")],
    )
    def test_an_unanswerable_comparison_is_not_a_yes(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False

    @pytest.mark.parametrize(
        ("catalogue", "legal", "trade"),
        [
            # The IRS holds two names, and for these the recognisable one is the
            # trade name. Checking only the legal name would throw away the
            # registry's own answer about its own entity.
            ("RAINN", "Rape Abuse And Incest National Network Inc", "Rainn"),
            (
                "Forest Stewardship Council US",
                "Us Working Group Inc",
                "Forest Stewardship Council Us",
            ),
            (
                # Also pins the apostrophe: registries write "Alzheimers" where
                # the charity writes "Alzheimer's".
                "Cure Alzheimer's Fund",
                "Alzheimers Disease Research Foundation",
                "Cure Alzheimers Fund",
            ),
        ],
    )
    def test_the_trade_name_counts_as_the_registry_answering(self, catalogue, legal, trade):
        assert _names_match(catalogue, legal) is False
        assert _names_match(catalogue, trade) is True

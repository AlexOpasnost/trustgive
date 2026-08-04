"""What the New Zealand register has to say before a badge is granted.

`register.charities.govt.nz/Charity/{cc}` returns HTTP 200 for CC99999999 and for
ZZ12345 exactly as it does for a real number — the third registry in a row where
the status code is not evidence (CRA in Finding 6, ABR in Finding 10). It is
server-rendered, so the checks read the record's own fields instead.

The stored numbers this replaced were mostly other people's: CC11146 is the
Ashburton Seniors Centre Trust, not CanTeen, and CC36358 is a *deregistered* St
Vincent de Paul branch, not World Vision New Zealand. The name gate and the
status gate each exist because one of those got past everything else.
"""

from __future__ import annotations

import pytest

from apps.charities.management.commands.fix_nz_ccnumbers import (
    _name_forms,
    _names_match,
    _tokens,
)


class TestNamesMatch:
    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            ("Salvation Army New Zealand", "The Salvation Army New Zealand"),
            ("Fred Hollows Foundation NZ", "The Fred Hollows Foundation (NZ)"),
            # The bracketed half is the legal name, and the register holds it.
            (
                "Forest & Bird (Royal Forest and Bird Protection Society of NZ)",
                "Royal Forest & Bird Protection Society Of New Zealand Incorporated",
            ),
        ],
    )
    def test_accepts_the_same_organisation(self, catalogue, registry):
        assert _names_match(catalogue, registry) is True

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            # Every one of these was a live stored number pointing somewhere else.
            ("CanTeen NZ", "Ashburton Seniors Centre Trust"),
            (
                "Fred Hollows Foundation NZ",
                "Society of St Vincent de Paul Hutt Valley and Wairarapa Area Council",
            ),
            ("Cancer Society of New Zealand", "The Fred Hollows Foundation (NZ)"),
            (
                "World Vision New Zealand",
                "Society of St Vincent De Paul St Patricks Vinnies Kaiapoi",
            ),
        ],
    )
    def test_rejects_another_organisations_registration(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False

    @pytest.mark.parametrize(
        ("catalogue", "registry"), [("", "Whatever Trust"), ("CanTeen NZ", "")]
    )
    def test_an_unanswerable_comparison_is_not_a_yes(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False


class TestNameForms:
    def test_offers_both_halves_of_a_bracketed_name(self):
        forms = _name_forms("Forest & Bird (Royal Forest and Bird Protection Society of NZ)")
        assert {"forest", "bird"} in forms
        assert {"royal", "forest", "bird", "protection"} in forms

    def test_a_plain_name_still_yields_itself(self):
        assert _tokens("Salvation Army New Zealand") in _name_forms("Salvation Army New Zealand")

    def test_country_words_are_not_identifying(self):
        # "New Zealand", "NZ" and "Aotearoa" appear in most entries on both sides
        # and separate nothing.
        assert _tokens("World Vision New Zealand") == {"world", "vision"}
        assert _tokens("Fred Hollows Foundation NZ") == {"fred", "hollows"}

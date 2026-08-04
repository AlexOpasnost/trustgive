"""What the Australian registry has to say before a badge is granted.

`fix_au_abns` accepted an ABN whenever the ABR page returned HTTP 200. Measured
2026-08-04, that page answers **200 for fabricated ABNs**: 99999999999,
12345678901 and 00000000000 each return the same 8,777-byte "not found" body with
a 200 status. It is the CRA trap from DATA_INTEGRITY.md Finding 6, in a registry
whose command had already promoted 16 live rows.

The page body does discriminate, so the checks moved onto it: the register has to
list a name, that name has to be the charity, and the entity has to be registered
as a charity with the ACNC. These tests run the parser over captured page shapes
rather than the live site, so they answer the same way in CI at midnight.
"""

from __future__ import annotations

import pytest

from apps.charities.management.commands.fix_au_abns import _names_match, _tokens

# Trimmed to the parts the parser reads. Left column intact so the label/value
# adjacency the extractor depends on is the real one.
REAL_RECORD = """
<span>ABN details</span>
<th>Entity name:</th><td>CARITAS AUSTRALIA LIMITED</td>
<th>ABN status:</th><td>Active from 05 Apr 2000</td>
<th>Entity type:</th><td>Australian Public Company</td>
<div>Australian Charities and Not-for-profits Commission (ACNC)</div>
<p>CARITAS AUSTRALIA LIMITED is registered with the ACNC as follows:</p>
<th>ACNC registration</th><td>Registered as a charity</td><td>03 Dec 2012</td>
"""

# The body an invented ABN gets back — a 200, and nothing about any entity.
NOT_FOUND_RECORD = """
<h1>Search</h1>
<p>The ABN you entered could not be found. Check the number and try again.</p>
"""

# An ABN that exists and is not a charity: the trap the ACNC line closes.
BUSINESS_ONLY_RECORD = """
<th>Entity name:</th><td>OZ PTY LTD</td>
<th>ABN status:</th><td>Active from 01 Jul 2001</td>
<th>Entity type:</th><td>Australian Private Company</td>
"""


def parse(html: str):
    """Exercise the command's own extraction, without going near the network."""
    import re

    text = re.sub(r"<[^>]+>", "\n", html)
    text = text.replace("&amp;", "&").replace("&#39;", "'").replace("&nbsp;", " ")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    labels = ("entity name", "business name", "trading name", "main name")
    names = []
    for i, line in enumerate(lines):
        if line.lower().rstrip(":").strip() in labels:
            for nxt in lines[i + 1 : i + 4]:
                if len(nxt) > 2 and not nxt.lower().startswith(("abn", "from", "to ")):
                    names.append(nxt)
                    break
    return names, "registered as a charity" in " ".join(lines).lower()


class TestRecordParsing:
    def test_a_real_record_yields_a_name_and_charity_status(self):
        names, acnc = parse(REAL_RECORD)
        assert names == ["CARITAS AUSTRALIA LIMITED"]
        assert acnc is True

    def test_the_not_found_body_yields_nothing(self):
        # This body arrives with HTTP 200. That is the whole point.
        names, acnc = parse(NOT_FOUND_RECORD)
        assert names == []
        assert acnc is False

    def test_an_ordinary_business_is_not_a_charity(self):
        names, acnc = parse(BUSINESS_ONLY_RECORD)
        assert names == ["OZ PTY LTD"]
        assert acnc is False


class TestNamesMatch:
    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            (
                "Australian Cancer Research Foundation (ACRF)",
                "AUSTRALIAN CANCER RESEARCH FOUNDATION",
            ),
            ("Asylum Seeker Resource Centre (ASRC)", "Asylum Seeker Resource Centre Inc."),
            # The legal entity routinely wraps the recognisable name in a trust
            # or holding company; that is not a different organisation.
            ("Mater Foundation (Australia)", "THE TRUSTEE FOR MATER FOUNDATION"),
            ("OzHarvest", "OzHarvest"),
            (
                "St Vincent de Paul Society Australia (Vinnies)",
                "St Vincent de Paul Society National Council of Australia Incorporated",
            ),
            (
                "Walter and Eliza Hall Institute of Medical Research (WEHI)",
                "THE WALTER AND ELIZA HALL INSTITUTE OF MEDICAL RESEARCH",
            ),
        ],
    )
    def test_accepts_the_same_organisation(self, catalogue, registry):
        assert _names_match(catalogue, registry) is True

    @pytest.mark.parametrize(
        ("catalogue", "registry"),
        [
            ("OzHarvest", "OZ PTY LTD"),
            ("Australian Cancer Research Foundation (ACRF)", "BOWEL CANCER AUSTRALIA"),
            (
                "Walter and Eliza Hall Institute of Medical Research (WEHI)",
                "THE WALTER & ELIZA HALL CHARITABLE FOUNDATION LIMITED",
            ),
            # An entity that holds a valid ABN and has nothing to do with us.
            ("OzHarvest", "ACT EMERGENCY SERVICES AGENCY"),
        ],
    )
    def test_rejects_an_unrelated_entity(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False

    def test_a_service_brand_is_not_the_registered_entity(self):
        """`kids-helpline-yourtown` stays hidden on purpose.

        The register knows the entity as "yourtown"; "Kids Helpline" is the
        service it runs. Confirming a name the registry does not carry would be
        inventing the link, so the row waits for a decision about its own name
        rather than being waved through.
        """
        assert _names_match("Kids Helpline (yourtown)", "YOURTOWN") is False

    @pytest.mark.parametrize(("catalogue", "registry"), [("", "OzHarvest"), ("OzHarvest", "")])
    def test_an_unanswerable_comparison_is_not_a_yes(self, catalogue, registry):
        assert _names_match(catalogue, registry) is False

    def test_apostrophes_do_not_split_a_word(self):
        assert _tokens("Alzheimer's Australia") == {"alzheimers"}

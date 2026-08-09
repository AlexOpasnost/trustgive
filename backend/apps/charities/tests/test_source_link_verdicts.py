"""What a set of probe results is allowed to do to a charity's badge.

`audit_source_links` runs nightly and can remove a charity from the public
catalogue. The rule it applies has to hold the line the project has drawn twice
already (Findings 8 and 11): **the source saying "no" is not the same event as
being unable to ask the source**, and only the first one may change anything.

The branch these tests pin used to demote on either. A dry run on 2026-08-05,
with ProPublica rate-limiting the calling host, proposed demoting 232 of 398
published charities — a registry having a bad night would have emptied more than
half the catalogue. It had already quietly taken the badge off two UK charities
overnight while the Charity Commission was slow to answer.
"""

from __future__ import annotations

import pytest

from apps.charities.management.commands.audit_source_links import verdict_for


class TestUnreachableIsNotDead:
    @pytest.mark.parametrize(
        "statuses",
        [
            ["ERR"],  # timeout / connection reset
            [500],
            [502, 503],
            ["ERR", 500],
            [429],  # rate-limited: the registry is refusing us, not denying the charity
            [403],  # blocked by a bot filter
        ],
    )
    def test_no_answer_changes_nothing(self, statuses):
        assert verdict_for(statuses) == "review"

    @pytest.mark.parametrize("statuses", [[404], [410], [404, "ERR"], [500, 410]])
    def test_an_actual_no_is_the_only_thing_that_demotes(self, statuses):
        assert verdict_for(statuses) == "clean"

    def test_a_rate_limited_sweep_never_demotes(self):
        # The shape of the 2026-08-05 run: every probe failed, none was a 404.
        sweep = [verdict_for(["ERR"]) for _ in range(232)]
        assert set(sweep) == {"review"}
        assert "clean" not in sweep


class TestOneWorkingLinkIsEnough:
    @pytest.mark.parametrize(
        "statuses",
        [[200], [200, 404], [200, "ERR"], [500, 200], [404, 410, 200]],
    )
    def test_a_charity_with_a_live_document_stands(self, statuses):
        assert verdict_for(statuses) == "keep"

    def test_keep_holds_even_when_every_other_link_is_proven_dead(self):
        # Dead links are pruned individually; the badge rests on the one that
        # opens, which is exactly what the badge claims.
        assert verdict_for([404, 404, 404, 200]) == "keep"


class TestNoDocuments:
    def test_no_links_at_all_is_its_own_case(self):
        # Nothing to probe, so nothing can be inferred from the network — but a
        # charity with no source document cannot support the badge either.
        assert verdict_for([]) == "empty"

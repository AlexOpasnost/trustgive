"""Charity catalog FilterSet."""

from __future__ import annotations

import re

import django_filters
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    TrigramWordSimilarity,
)
from django.db.models import (
    Case,
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    Q,
    Value,
    When,
)
from django.db.models.fields.json import KeyTextTransform

from apps.charities.hubs import registry_host
from apps.charities.models import Bucket, Charity, SizeBucket, VerificationStatus

# Trigram gate for a query that full-text search couldn't match — i.e. a typo.
#
# 0.5, measured against the live catalogue rather than guessed. At this value
# "givewel" → GiveWell (0.875), "red cros" → both Red Crosses (0.889), "oxfem" →
# the Oxfam entities (0.500), "save the childrne" → Save the Children (0.833),
# while "amnesty" (not in the catalogue) correctly returns nothing instead of
# American Cancer Society at 0.375. Lowering it to 0.4 admits that kind of noise;
# raising it to 0.6 loses "give well" (0.583).
#
# Returning nothing is the right failure here: the empty state explains that an
# absent organisation may be real but unconfirmed, which is true and useful. A
# plausible-looking wrong charity is neither.
WORD_SIMILARITY_THRESHOLD = 0.5

# Weight of an exact/prefix name or registration-number match relative to
# relevance. 4.0 puts any such row above every text match, which is the product's
# core promise: someone arriving with a name in hand gets that organisation
# first, not an organisation whose description happens to mention it.
EXACTNESS_WEIGHT = 4.0


class CharityFilter(django_filters.FilterSet):
    cause = django_filters.BaseInFilter(field_name="cause_tags", lookup_expr="overlap")
    # v3.7: country accepts comma-separated ISO codes so a single API call
    # can support regional filters like ?country=GB,DE,NL,CH,SE,FR (Europe).
    # Each value is still validated against Country.choices implicitly via
    # the model field; unknown codes simply match no rows. Was ChoiceFilter
    # (single-value) before v3.7 expanded the catalog to 14 countries.
    country = django_filters.BaseInFilter(field_name="country")
    size = django_filters.ChoiceFilter(field_name="size_bucket", choices=SizeBucket.choices)
    verification_status = django_filters.ChoiceFilter(choices=VerificationStatus.choices)
    badges = django_filters.CharFilter(method="filter_badges")
    q = django_filters.CharFilter(method="filter_search")
    # v3.0 (DESIGN.md §A) — primary user-facing taxonomy.
    bucket = django_filters.ChoiceFilter(choices=Bucket.choices)
    # v3.21 — backs the /charities/registry/{slug} hub pages (apps.charities.hubs).
    registry = django_filters.CharFilter(method="filter_registry")

    class Meta:
        model = Charity
        fields = [
            "cause",
            "country",
            "size",
            "verification_status",
            "badges",
            "q",
            "bucket",
            "registry",
        ]

    def filter_badges(self, queryset, name, value: str):
        slugs = [s for s in value.split(",") if s]
        if not slugs:
            return queryset
        return queryset.filter(charity_badges__badge__slug__in=slugs).distinct()

    def filter_registry(self, queryset, name, value: str):
        """Charities whose evidence was published by a known registry.

        Matched on the source document's URL host. `istartswith` on the full
        scheme+host prefix rather than `icontains` on the host alone: the latter
        would also match a registry name appearing inside a path or query string
        of some unrelated URL, which would put a charity on a registry page whose
        register never listed it.
        """
        host = registry_host((value or "").strip().lower())
        if not host:
            # Unknown registry slug → empty result, not the whole catalogue.
            # A silent no-op filter here would make /charities/registry/typo
            # render as "all 370 charities", which is a false claim about the
            # registry named in the URL.
            return queryset.none()
        prefixes = [
            f"https://{host}/",
            f"http://{host}/",
            f"https://www.{host}/",
            f"http://www.{host}/",
        ]
        condition = Q()
        for prefix in prefixes:
            condition |= Q(source_documents__url__istartswith=prefix)
        return queryset.filter(condition).distinct()

    def filter_search(self, queryset, name, value: str):
        """Rank a free-text query: exact identity first, then relevance.

        The dominant arrival is "someone named a charity at me — is it real?", so
        the organisation whose name or registration number *is* the query must be
        the first result. Everything else is secondary.

        Two defects fixed in v3.21, both found by measuring against production:

        1. `SearchRank("search_vector", …)` — passing the field as a **string**
           makes Django wrap it in `SearchVector("search_vector")`, i.e.
           `to_tsvector(search_vector::text)`. That re-parses the stored tsvector's
           text dump into a brand-new vector in which every lexeme carries the
           default weight D, discarding the A/B/C weights the trigger writes
           (name=A, registration_id=B, description=C). Effect: a query for
           "givewell" ranked Sightsavers and BRAC — whose descriptions say
           "GiveWell-recommended" twice — above GiveWell itself (0.076 vs 0.061).
           Passing `F("search_vector")` uses the stored vector and reverses that
           to 0.78 vs 0.15.

        2. `TrigramSimilarity` compares the query against the *whole* of
           `name_trgm`, which holds the EN and RU names concatenated. "givewell"
           against "givewell (the clear fund) givewell (the clear fund)" scores
           0.375 — below the 0.4 gate, so a misspelling like "givewel" matched
           nothing at all despite pg_trgm being installed. `TrigramWordSimilarity`
           scores the best-matching extent instead: 1.000 and 0.875 respectively.

        Ordering is a single combined score rather than
        `order_by("-rank", "-word_sim")`: with a lexicographic sort any row with a
        non-zero FTS rank outranks every typo-match, so "give well" would surface
        an incidental description hit ahead of GiveWell.
        """
        q = (value or "").strip()
        if not q:
            return queryset

        # Registration numbers get typed with their punctuation ("20-8625442",
        # "1234 5678"); the column stores them bare.
        registration = re.sub(r"[^0-9A-Za-z]", "", q)

        qs = queryset.annotate(
            name_en=KeyTextTransform("en", "name"),
            name_ru=KeyTextTransform("ru", "name"),
        )

        exact_match = Q(name_en__iexact=q) | Q(name_ru__iexact=q)
        if registration:
            exact_match |= Q(registration_id__iexact=registration)
        prefix_match = Q(name_en__istartswith=q) | Q(name_ru__istartswith=q)

        exactness = Case(
            When(exact_match, then=Value(2)),
            When(prefix_match, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )

        if len(q) < 3:
            # Two characters can't say much. Prefix matching is predictable;
            # trigram scores at this length are close to noise.
            short_match = prefix_match
            if registration:
                short_match |= Q(registration_id__istartswith=registration)
            return (
                qs.annotate(exactness=exactness)
                .filter(short_match)
                .order_by("-exactness", "name_en", "slug")
            )

        ts_q = SearchQuery(q, search_type="websearch", config="simple")
        return (
            qs.annotate(
                exactness=exactness,
                rank=SearchRank(F("search_vector"), ts_q),
                # word_similarity() can't use the GIN trgm index through a `>=`
                # comparison (that needs the `%>` operator), so this is a scan.
                # At 370 published rows it costs under a millisecond; revisit if
                # the catalogue reaches five figures.
                word_sim=TrigramWordSimilarity(q, "name_trgm"),
            )
            .filter(
                Q(search_vector=ts_q)
                | Q(word_sim__gte=WORD_SIMILARITY_THRESHOLD)
                | Q(exactness__gt=0)
            )
            .annotate(
                relevance=ExpressionWrapper(
                    F("exactness") * Value(EXACTNESS_WEIGHT) + F("rank") + F("word_sim"),
                    output_field=FloatField(),
                )
            )
            .order_by("-relevance", "slug")
        )

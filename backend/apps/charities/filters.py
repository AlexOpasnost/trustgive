"""Charity catalog FilterSet."""
from __future__ import annotations

import django_filters
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q

from apps.charities.models import Charity, Country, SizeBucket, VerificationStatus


class CharityFilter(django_filters.FilterSet):
    cause = django_filters.BaseInFilter(field_name="cause_tags", lookup_expr="overlap")
    country = django_filters.ChoiceFilter(choices=Country.choices)
    size = django_filters.ChoiceFilter(field_name="size_bucket", choices=SizeBucket.choices)
    verification_status = django_filters.ChoiceFilter(choices=VerificationStatus.choices)
    badges = django_filters.CharFilter(method="filter_badges")
    q = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Charity
        fields = ["cause", "country", "size", "verification_status", "badges", "q"]

    def filter_badges(self, queryset, name, value: str):
        slugs = [s for s in value.split(",") if s]
        if not slugs:
            return queryset
        return queryset.filter(charity_badges__badge__slug__in=slugs).distinct()

    def filter_search(self, queryset, name, value: str):
        q = (value or "").strip()
        if not q:
            return queryset

        if len(q) < 3:
            # Short query: trigram only
            return (
                queryset.annotate(sim=TrigramSimilarity("name_trgm", q))
                .filter(sim__gte=0.3)
                .order_by("-sim")
            )

        ts_q = SearchQuery(q, search_type="websearch", config="simple")
        return (
            queryset.annotate(
                rank=SearchRank("search_vector", ts_q),
                sim=TrigramSimilarity("name_trgm", q),
            )
            .filter(Q(search_vector=ts_q) | Q(sim__gte=0.4))
            .order_by("-rank", "-sim")
        )

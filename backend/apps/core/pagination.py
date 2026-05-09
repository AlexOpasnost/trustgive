"""Pagination class — PageNumberPagination with SPEC defaults.

Custom response shape includes `page` and `page_size` fields per
API_SPEC.md §2 (Pagination schema). DRF's default PageNumberPagination
omits them, which makes client-side "Showing X-Y of N" math impossible
without re-deriving from URL params.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    # Bumped 100 → 500 so the frontend catalog page can request the full
    # curated catalog in one shot without paginate-controls UI. As the
    # catalog scales past ~300 the frontend should switch to infinite
    # scroll / proper pagination.
    max_page_size = 500
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

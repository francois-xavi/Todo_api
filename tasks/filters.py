from django_filters import rest_framework as filters
from .models import *
from django.db.models import Q, Value, F


class TaskFilter(filters.FilterSet):
    """
    Filter class for to do tasks allowing filtering by date, completed
    and ordering by various fields.
    """
    start_date = filters.DateTimeFilter(
        field_name="updated_at",
        lookup_expr="gte",
        label="Updated on or after date (ISO 8601 date-time format, e.g.: 2021-01-01T00:00:00Z)",
    )
    end_date = filters.DateTimeFilter(
        field_name="updated_at",
        lookup_expr="lte",
        label="Updated on or before date (ISO 8601 date-time format, e.g.: 2021-01-01T23:59:59Z)",
    )
    search = filters.CharFilter(
        method="filter_by_search_param", label="Search (name or Description, case-insensitive)"
    )
    order_by = filters.OrderingFilter(
        fields=(
            ("updated_at", "updated_at"),
            ("created_at", "created_at")
        ),
        field_labels={
            "updated_at": "Sort by Updated Date",
            "created_at": "Sort by Created Date",
        },
        label="Sort by (Specify field for sorting results)",
    )

    class Meta:
        model = Task
        fields = ("start_date", "end_date", "search", "is_completed")
        order_by = ["updated_at"]

    def filter_by_search_param(self, queryset, name, value):
        """
        Search tasks by Title or description.
        """

        return (
            queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
            )
            .order_by("title")
        )

from rest_framework.filters import OrderingFilter


class CustomOrderingFilter(OrderingFilter):
    """Custom ordering renamed for convenience"""

    alias_map = {
        "latest": "created_at",
        "most_visited": "visit_count",
    }

    def remove_invalid_fields(
        self,
        queryset,
        ordering,
        view,
        request,
    ):
        new_ordering = []
        for field in ordering:
            desc = field.startswith("-")
            name = field.lstrip("-")
            if name in self.alias_map:
                name = self.alias_map[name]
            new_ordering.append(f"-{name}" if desc else name)
        return super().remove_invalid_fields(queryset, new_ordering, view, request)

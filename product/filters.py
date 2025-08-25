import django_filters
from django.db.models import Q

from product.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Product
        fields = ["min_price", "max_price"]

    def filter_search(
        self,
        queryset,
        name,
        value,
    ):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(slug__icontains=value)
            | Q(category__title__icontains=value)
        )

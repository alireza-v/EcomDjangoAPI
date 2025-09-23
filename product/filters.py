import django_filters
from django.db.models import Q
from django.utils import timezone

from product.models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Product filtering:
        - min_price: filter by min price
        - max_price: filter max price
        - in_stock: filter only available products in stock
        - brand: filter by the brand
    """

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    brand = django_filters.CharFilter(method="filter_brand")
    has_discount = django_filters.BooleanFilter(method="filter_discount")

    class Meta:
        model = Product
        fields = [
            "min_price",
            "max_price",
            "in_stock",
            "brand",
            "has_discount",
        ]

    def filter_in_stock(
        self,
        queryset,
        name,
        value,
    ):
        """The availble products in stock"""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock__lte=0)

    def filter_brand(self, queryset, name, value):
        return queryset.filter(Q(brand__icontains=value) | Q(title__icontains=value))

    def filter_discount(self, queryset, name, value):
        qs = queryset.filter(product_discount__end_date__gte=timezone.now())
        return qs

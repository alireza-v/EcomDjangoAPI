import django_filters
from django.db.models import Q
from django.utils import timezone

from product.models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Product filtering:
        - min_price
        - max_price
        - in_stock
        - brand
    """

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    has_discount = django_filters.BooleanFilter(method="filter_discount")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    brand = django_filters.CharFilter(method="filter_brand")

    class Meta:
        model = Product
        fields = [
            "min_price",
            "max_price",
            "has_discount",
            "in_stock",
            "brand",
        ]

    def filter_in_stock(
        self,
        queryset,
        name,
        value,
    ):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)

    def filter_brand(
        self,
        queryset,
        name,
        value,
    ):
        if not value:
            return queryset
        value = str(value).strip()
        qs = queryset.filter(Q(brand__icontains=value) | Q(title__icontains=value))
        return qs

    def filter_discount(
        self,
        queryset,
        name,
        value,
    ):
        qs = queryset.filter(product_discounts__end_date__gte=timezone.now())
        return qs

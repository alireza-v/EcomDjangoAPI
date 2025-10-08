from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers

from ..models import Category, Discount, Product
from .base import BaseSerializer
from .review import FeatureValueSerializer


class DiscountSerializer(BaseSerializer):
    class Meta:
        model = Discount
        fields = ["name", "percent", "end_date", "product", "category"]


class ProductSerializer(BaseSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="product-detail",
        lookup_field="slug",
    )
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    price_formatted = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    has_discount = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "in_stock",
            "stock",
            "title",
            "slug",
            "brand",
            "visit_count",
            "price",
            "price_formatted",
            "has_discount",
            "discount",
            "features",
            "main_image",
            "slug",
            "avg_rating",
            "created_at",
            "url",
        ]

    def get_price_formatted(self, obj):
        """price_formatter being called"""
        return f"{obj.price:,.0f}"

    def get_features(self, obj):
        """Product related features being called including name and value"""
        feature_qs = obj.product_features.all()
        return FeatureValueSerializer(
            feature_qs,
            many=True,
        ).data

    def get_avg_rating(self, obj):
        """
        avg_rating being called from the view
        """
        avg_rating = getattr(obj, "avg_rating", 0) or 0
        return f"{avg_rating:,.1f}"

    def get_in_stock(self, obj):
        """Boolean value of stock"""
        return obj.stock > 0

    def get_has_discount(self, obj):
        "bool value for product discounts"
        qs = obj.product_discounts.filter(end_date__gte=timezone.now())
        return qs.exists()

    def get_discount(self, obj):
        active_discount = obj.product_discounts.filter(
            end_date__gte=timezone.now()
        ).first()
        if active_discount:
            return [
                {
                    "name": active_discount.name,
                    "percent": active_discount.percent,
                    "end_date": f"{active_discount.end_date:%Y-%m-%d %H:%M:%S}",
                }
            ]


class CategorySerializer(BaseSerializer):
    products_preview = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    breadcrumb = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    discounts = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "title",
            "breadcrumb",
            "has_discount",
            "discounts",
            "products_preview",
            "subcategories",
        ]

    def get_breadcrumb(self, obj):
        return [
            {
                "id": cat.id,
                "title": cat.title,
                "slug": cat.slug,
            }
            for cat in obj.get_breadcrumbs()
        ]

    def get_products_preview(self, obj):
        """
        Returns the top 5 most visited products in the given category and each one annotated with the average rating from their related feedbacks
        """
        product_avg_rating = obj.products.annotate(
            avg_rating=Avg("product_feedbacks__rating")
        ).order_by("-visit_count")[:5]

        return ProductSerializer(
            product_avg_rating,
            many=True,
            context=self.context,
        ).data

    def get_subcategories(self, obj):
        """
        Returns a serialized list of subcategories for the given category
        """
        return CategorySerializer(
            obj.subcategories.all(),
            many=True,
            context=self.context,
        ).data

    def get_has_discount(self, obj):
        """
        Returns True if the category has any active discounts"
        """
        cat_discounts = obj.category_discounts.filter(end_date__gte=timezone.now())

        return cat_discounts.exists()

    def get_discounts(self, obj):
        """
        Returns list of active discounts
        """
        active_discounts = obj.category_discounts.filter(end_date__gte=timezone.now())

        return [
            {
                "name": discount.name,
                "percent": discount.percent,
                "end_date": f"{discount.end_date:%Y-%m-%d %H:%M:%S}",
            }
            for discount in active_discounts
        ]


class ProductDetailSerializer(BaseSerializer):
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    formatted_price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "brand",
            "stock",
            "in_stock",
            "price",
            "formatted_price",
            "description",
            "main_image",
            "images",
            "features",
        ]

    def get_formatted_price(self, obj):
        return f"{obj.price:,.0f}"

    def get_features(self, obj):
        """Return product related features"""
        qs = obj.product_features.all()
        return FeatureValueSerializer(
            qs,
            many=True,
            context=self.context,
        ).data

    def get_in_stock(self, obj):
        """Boolean stock value"""
        return obj.stock > 0

    def get_images(self, obj):
        """
        Fetch product related images
        """
        images = obj.images.all()
        urls = []
        for img in images:
            if img.image and hasattr(img.image, "url"):
                urls.append(img.image.url)
        return urls

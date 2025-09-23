from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from product.models import (
    Category,
    Discount,
    FeatureValue,
    Feedback,
    Like,
    Product,
    ProductImage,
)


class BaseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Remove null values
    """

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {k: v for k, v in rep.items() if v not in (None, "", [], {})}


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
        qs = obj.product_discount.filter(end_date__gte=timezone.now())
        return qs.exists()

    def get_discount(self, obj):
        active_discount = obj.product_discount.filter(
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
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "title",
            "breadcrumb",
            "has_discount",
            "discount",
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
        Return sets of products for preview
        e.g. top 5 most visited products in the category
        """
        qs = obj.products.annotate(
            avg_rating=Avg("product_feedbacks__rating")
        ).order_by("-visit_count")[:5]
        return ProductSerializer(
            qs,
            many=True,
            context=self.context,
        ).data

    def get_subcategories(self, obj):
        """Return subcategories of each category"""
        return CategorySerializer(
            obj.subcategories.all(),
            many=True,
            context=self.context,
        ).data

    def get_has_discount(self, obj):
        "bool value for category discounts"
        qs = obj.category_discount.filter(end_date__gte=timezone.now())
        return qs.exists()

    def get_discount(self, obj):
        active_discount = obj.category_discount.filter(
            end_date__gte=timezone.now()
        ).first()
        if active_discount:
            return [
                {
                    "name": active_discount.name,
                    "percent": active_discount.percent,
                    "end_date": f"{active_discount.end_date:%Y-%m-%d %H:%M:%S}",
                },
            ]


class FeatureValueSerializer(BaseSerializer):
    feature = serializers.StringRelatedField()

    class Meta:
        model = FeatureValue
        fields = [
            "feature",
            "value",
        ]


class ProductImageSerializer(BaseSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductFeatureSerializer(BaseSerializer):
    class Meta:
        model = FeatureValue
        fields = [
            "product",
            "feature",
            "value",
        ]


class FeedbackSerializer(BaseSerializer):
    user = serializers.StringRelatedField()
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
        required=False,
    )
    product = serializers.SerializerMethodField()
    score = serializers.IntegerField(
        help_text="Rating from 1 to 5 stars",
        min_value=1,
        max_value=5,
        source="rating",
    )
    comment = serializers.CharField(source="description")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "user",
            "score",
            "comment",
            "product_id",
            "created_at",
            "product",
        ]

    def get_product(self, obj):
        """Fetch product related comments"""
        if obj.product:
            qs = obj.product.product_features.all()
            return {
                "title": obj.product.title,
                "price": obj.product.price,
                "formatted_price": obj.product.price_formatter,
                "features": [
                    {
                        "name": item.feature.name,
                        "value": item.value,
                    }
                    for item in qs
                ],
            }
        return None

    def validate(self, data):
        user = self.context["request"].user
        view = self.context["view"]

        product_id = view.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        # Unique constraint on user and product
        if Feedback.objects.filter(
            user=user,
            product_id=product_id,
        ).exists():
            raise serializers.ValidationError(
                "You already submitted a comment on this product"
            )

        data["product"] = product
        return data


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


class LikeSerializer(BaseSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    associated_product = serializers.SerializerMethodField(source="product")

    class Meta:
        model = Like
        fields = [
            "product",
            "associated_product",
        ]

    def get_associated_product(self, obj):
        qs = obj.product
        return {
            "id": qs.id,
            "title": qs.title,
            "price": qs.price,
            "price_formatted": qs.price_formatter,
        }

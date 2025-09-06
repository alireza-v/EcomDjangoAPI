from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from product.models import (
    Category,
    FeatureValue,
    Feedback,
    Like,
    Product,
    ProductImage,
)


class BaseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Remove null values from response
    """

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {k: v for k, v in rep.items() if v not in (None, "", [], {})}


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
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "stock",
            "in_stock",
            "title",
            "slug",
            "brand",
            "visit_count",
            "price",
            "price_formatted",
            "features",
            "url",
            "main_image",
            "description",
            "slug",
            "avg_rating",
            "created_at",
        ]

    def get_price_formatted(self, obj):
        return f"{obj.price:,.0f}"

    def get_features(self, obj):
        feature_qs = obj.product_features.all()
        return FeatureValueSerializer(
            feature_qs,
            many=True,
        ).data

    def get_avg_rating(self, obj):
        return getattr(obj, "avg_rating", 0) or 0

    def get_in_stock(self, obj):
        return obj.stock > 0

    def get_created_at(self, obj):
        return f"{obj.created_at:%Y-%m-%d %H:%M:%S}"


class CategorySerializer(BaseSerializer):
    products_preview = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "title",
            "products_preview",
            "subcategories",
        ]

    def get_products_preview(self, obj):
        """
        Return sets of products for preview
        Example: top 5 most visited products in the category
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
        return CategorySerializer(
            obj.subcategories.all(),
            many=True,
            context=self.context,
        ).data


class FeatureValueSerializer(ModelSerializer):
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


class ProductFeatureSerializer(ModelSerializer):
    class Meta:
        model = FeatureValue
        fields = [
            "product",
            "feature",
            "value",
        ]


class CategoryBreadcrumbSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "slug",
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
    rate = serializers.IntegerField(
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
            "rate",
            "comment",
            "product_id",
            "created_at",
            "product",
        ]

    def get_product(self, obj):
        if obj.product:
            qs = obj.product.product_features.all()
            return {
                "title": obj.product.title,
                "price": obj.product.price_formatter,
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
    price_formatted = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

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
            "price_formatted",
            "main_image",
            "description",
            "features",
        ]

    def get_price_formatted(self, obj):
        return f"{obj.price:,.0f}"

    def get_features(self, obj):
        qs = obj.product_features.all()
        return FeatureValueSerializer(
            qs,
            many=True,
            context=self.context,
        ).data

    def get_in_stock(self, obj):
        return obj.stock > 0


class LikeSerializer(ModelSerializer):
    user = serializers.StringRelatedField()
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    product_related = serializers.StringRelatedField(source="product")

    class Meta:
        model = Like
        fields = [
            "user",
            "product",
            "product_related",
        ]

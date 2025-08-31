from django.db.models import Avg
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
        view_name="product-detail-api",
        lookup_field="slug",
    )
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "stock",
            "title",
            "slug",
            "visit_count",
            "price",
            "features",
            "url",
            "main_image",
            "description",
            "slug",
            "avg_rating",
            "created_at",
        ]

    def get_price(self, obj):
        if obj:
            return f"{obj.price:,.0f}"
        return obj

    def get_features(self, obj):
        from product.serializers import FeatureValueSerializer

        feature_qs = obj.feature_values.all()
        return FeatureValueSerializer(
            feature_qs,
            many=True,
        ).data

    def get_avg_rating(self, obj):
        return getattr(obj, "avg_rating", 0) or 0


class CategorySerializer(BaseSerializer):
    products_preview = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "title",
            "slug",
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


class FeedbackSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    product_value = serializers.SerializerMethodField()
    rating = serializers.IntegerField(
        help_text="Rating from 1 to 5 stars",
        min_value=1,
        max_value=5,
    )

    class Meta:
        model = Feedback
        fields = [
            "description",
            "rating",
            "user",
            "product",
            "product_value",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }

    def get_product_value(self, obj):
        if obj.product:
            return {
                "id": obj.product.id,
                "title": obj.product.title,
                "price": f"{obj.product.price:,.0f}",
            }
        return None

    def validate(self, data):
        user = self.context["request"].user
        product = data.get("product")

        if Feedback.objects.filter(
            user=user,
            product=product,
        ).exists():
            raise serializers.ValidationError("You already made a review.")
        return data


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

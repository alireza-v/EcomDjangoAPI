from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..models import (
    FeatureValue,
    Feedback,
    Like,
    Product,
    ProductImage,
)
from .base import BaseSerializer


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

from django.db import transaction
from rest_framework import serializers

from cart.models import (
    CartItem,
)
from product.models import Product
from product.serializers import BaseSerializer


class CartSerializer(BaseSerializer):
    action = serializers.ChoiceField(
        choices=[
            "add",
            "remove",
        ],
        write_only=True,
        default="add",
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    product = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=5,
        default=1,
        error_messages={
            "min_value": "min value is 1",
            "max_value": "max value is 5",
            "invalid": "Please enter a valid integer value",
        },
    )
    created_at = serializers.DateTimeField(format="%Y:%m:%d %H:%M:%S", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "quantity",
            "subtotal",
            "action",
            "product_id",
            "created_at",
            "product",
        ]

    def get_product(self, obj):
        """Return user cart info"""
        product = obj.product
        features = product.product_features.all()
        discount = product.product_discount.all()

        return {
            "id": product.id,
            "in_stock": product.stock >= 1,
            "title": product.title,
            "price": product.price,
            "formatted_price": f"{product.price:,.0f}",
            "main_image": product.main_image or None,
            "discount": [
                {
                    "name": d.name,
                    "percent": f"{d.percent:,.1f}",
                    "end_date": f"{d.end_date:%Y-%m-%d %H:%M:%S}",
                }
                for d in discount
            ],
            "features": [
                {
                    "name": f.feature.name,
                    "value": f.value,
                }
                for f in features
            ],
        }

    def validate(self, attrs):
        product = attrs.get("product_id")
        buy_quantity = attrs.get("quantity", 1)

        action = attrs.get("action", "add")
        user = self.context["request"].user
        cart_max_limit = 5  # cart limitation

        cart = CartItem.objects.filter(
            user=user,
            product=product,
        ).first()
        cart_quantity = cart.quantity if cart else 0
        total_quantity = cart_quantity + buy_quantity

        if action == "add":
            if total_quantity > cart_max_limit:
                raise serializers.ValidationError(
                    {"detail": f"You have reached the cart limit ({cart_max_limit})"}
                )
            if total_quantity > product.stock:
                raise serializers.ValidationError(
                    {"detail": f"Quantity exceeds available stock({product.stock})"}
                )

        return attrs

    def create(self, validated_data):
        data = validated_data

        user = self.context["request"].user
        product = data.get("product_id")
        quantity = data.get("quantity", 1)
        action = data.get("action", "add")

        with transaction.atomic():
            if action == "remove":
                try:
                    user_cart = CartItem.objects.get(user=user, product=product)
                except CartItem.DoesNotExist:
                    raise serializers.ValidationError({"detail": "Cart is empty"})

                if quantity > user_cart.quantity:
                    raise serializers.ValidationError(
                        {"detail": "Cannot remove more than available"}
                    )
                user_cart.quantity -= quantity

                if user_cart.quantity <= 0:
                    user_cart.delete()
                else:
                    user_cart.save()

            elif action == "add":
                user_cart, created = CartItem.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={
                        "quantity": quantity,
                    },
                )

                if not created:
                    user_cart.quantity += quantity
                    user_cart.save()

            return user_cart

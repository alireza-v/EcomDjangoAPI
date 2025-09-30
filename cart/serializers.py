from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from cart.models import (
    CartItem,
)
from product.models import Product
from product.serializers import BaseSerializer


class CartSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
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
            "user_info",
        ]

    def get_user_info(self, obj):
        return {
            "id": obj.user.id,
            "email": obj.user.email,
        }

    def get_product(self, obj):
        """Return cart related products"""
        product = obj.product
        features = product.product_features.all()
        discounts = product.product_discounts.all()

        return {
            "id": product.id,
            "in_stock": product.stock >= 1,
            "title": product.title,
            "price": product.price,
            "main_image": product.main_image or None,
            "discounts": [
                {
                    "name": value.name,
                    "percent": f"{value.percent:,.1f}",
                    "end_date": f"{value.end_date:%Y-%m-%d %H:%M:%S}",
                }
                for value in discounts
            ],
            "features": [
                {
                    "name": feature.feature.name,
                    "value": feature.value,
                }
                for feature in features
            ],
        }

    def validate(self, attrs):
        """
        Validate total number againts cart max limit
        Validate total number against stock
        """
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
            elif total_quantity > product.stock:
                raise serializers.ValidationError(
                    {"detail": f"Quantity exceeds available stock ({product.stock})"}
                )
        elif action == "remove":
            if not cart:
                raise serializers.ValidationError({"detail": "Cart is empty"})

            if buy_quantity > cart.quantity:
                raise serializers.ValidationError(
                    {"detail": "Cannot remove more than available"}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        data = validated_data
        user = self.context["request"].user
        product = data.get("product_id")
        buy_quantity = data.get("quantity", 1)
        action = data.get("action", "add")

        cart_qs = CartItem.objects.filter(
            user=user,
            product=product,
        ).select_for_update()
        cart = cart_qs.first()

        if action == "remove":
            if buy_quantity > cart.quantity:
                raise serializers.ValidationError(
                    {"detail": "Cannot remove more than available"}
                )

            cart.quantity = F("quantity") - buy_quantity
            cart.save(update_fields=["quantity"])
            cart.refresh_from_db()
            if cart.quantity == 0:
                cart.delete()
                cart = CartItem(user=user, product=product, quantity=0)
            return cart

        elif action == "add":
            if not cart:
                cart = CartItem.objects.create(
                    user=user,
                    product=product,
                    quantity=buy_quantity,
                )
            else:
                cart.quantity = F("quantity") + buy_quantity
                cart.save(update_fields=["quantity"])
                cart.refresh_from_db()

            return cart

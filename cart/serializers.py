from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)
from product.models import Product
from product.serializers import BaseSerializer


class CartSerializer(BaseSerializer):
    subtotal = serializers.SerializerMethodField()
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

    class Meta:
        model = CartItem
        fields = [
            "quantity",
            "subtotal",
            "action",
            "product_id",
            "product",
        ]

    def get_subtotal(self, obj):
        return f"{obj.subtotal:,.0f}"

    def get_product(self, obj):
        data = {
            "stock": obj.product.stock,
            "id": obj.product.id,
            "title": obj.product.title,
            "price": f"{obj.product.price:,.0f}",
            "main_image": obj.product.main_image,
        }

        return {k: v for k, v in data.items() if v not in (None, "", [], {})}

    def validate(self, attrs):
        product = attrs.get("product_id")
        buy_quantity = attrs.get("quantity", 1)
        action = attrs.get("action", "add")
        user = self.context["request"].user

        cart_item = CartItem.objects.filter(
            user=user,
            product=product,
        ).first()

        if action == "add":
            current_quantity = cart_item.quantity if cart_item else 0
            total_quantity = current_quantity + buy_quantity

            if total_quantity > product.stock:
                raise serializers.ValidationError(
                    {"detail": f"Quantity exceeds available stock"}
                )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product_id"]
        quantity = validated_data.get("quantity", 1)
        action = validated_data.get("action", "add")  # choices=["add", "remove"]

        if action == "remove":
            try:
                cart_item = CartItem.objects.get(user=user, product=product)
            except CartItem.DoesNotExist:
                raise serializers.ValidationError({"detail": "Cart is empty"})

            with transaction.atomic():
                if quantity > cart_item.quantity:
                    raise serializers.ValidationError(
                        {"detail": "Cannot remove more than available"}
                    )
                cart_item.quantity -= quantity

                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()

        elif action == "add":
            with transaction.atomic():
                cart_item, created = CartItem.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={
                        "quantity": quantity,
                    },
                )

                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()

        return cart_item


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Delivery address",
    )


class OrderItemSerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    price_at_purchase = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "price_at_purchase",
            "subtotal",
        ]

    def get_product(self, obj):
        product = obj.product
        return {
            "id": product.id,
            "title": product.title,
            "price": f"{product.price:,.0f}",
            "stock": product.stock,
            "main_image": product.main_image.url if product.main_image else None,
        }

    def get_subtotal(self, obj):
        return f"{obj.quantity * obj.price_at_purchase:,.0f}"

    def get_price_at_purchase(self, obj):
        return f"{obj.price_at_purchase:,.0f}"


class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(
        many=True,
        read_only=True,
    )
    total = serializers.SerializerMethodField()
    total_prices = serializers.SerializerMethodField(source="total_amount")

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "shipping_address",
            "total_prices",
            "total",
            "created_at",
            "order_items",
        ]

    def get_total_prices(self, obj):
        return f"{obj.total_amount:,.0f}"

    def get_total(self, obj):
        return f"{obj.total:,.0f}"

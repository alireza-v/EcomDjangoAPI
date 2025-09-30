from rest_framework import serializers

from orders.models import Order, OrderItem
from product.serializers import BaseSerializer


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(
        max_length=255,
        help_text="Delivery address",
    )


class OrderItemSerializer(BaseSerializer):
    product = serializers.SerializerMethodField()
    price_at_purchase = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "quantity",
            "price_at_purchase",
            "product",
        ]

    def get_product(self, obj):
        """OrderItem related products"""
        product = obj.product
        return {
            "product_id": product.id,
            "product_title": product.title,
            "product_price": f"{product.price:,.0f}",
            "stock": product.stock,
            "product_main_image": product.main_image.url
            if product.main_image
            else None,
        }

    def get_price_at_purchase(self, obj):
        return f"{obj.price_at_purchase:,.0f}"


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    subtotal = serializers.ReadOnlyField(source="total_amount")

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "shipping_address",
            "subtotal",
            "order_items",
            "created_at",
        ]

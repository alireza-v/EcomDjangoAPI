from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from product.models import Product

from .models import CartItem


class CartItemSerializer(ModelSerializer):
    action = serializers.ChoiceField(
        choices=[
            "add",
            "remove",
        ],
        write_only=True,
        default="add",
    )
    user = serializers.StringRelatedField()
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=5,
        default=1,
        error_messages={
            "min_value": "min value is 1",
            "max_value": "max value is 5",
            "invalid": "Please enter a valid integer value.",
        },
    )
    product_info = serializers.StringRelatedField(source="product")

    class Meta:
        model = CartItem
        fields = [
            "action",
            "user",
            "product",
            "quantity",
            "product_info",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        product = validated_data.get("product")
        specified_quantity = validated_data.get("quantity", 1)
        action = validated_data.get("action")

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={
                "quantity": specified_quantity,
            },
        )

        if created:
            return cart_item

        if action == "add":
            cart_item.quantity += specified_quantity

        elif action == "remove":
            if cart_item.quantity < specified_quantity:
                raise serializers.ValidationError(
                    {
                        "detail": "Cannot remove more than the available.",
                    },
                    400,
                )
            cart_item.quantity -= specified_quantity

        cart_item.save()
        return cart_item

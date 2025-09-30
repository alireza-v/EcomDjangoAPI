from decimal import Decimal

from django.db.models import F
from rest_framework import serializers

from cart.models import CartItem
from orders.models import Order, OrderItem


def create_order(
    user,
    shipping_address,
    cart_items,
):
    """
    - Create order and order items
    - Stock value deducted
    - User cart deleted
    """

    # Calculate discount
    subtotal = sum(cart.product.discounted_price * cart.quantity for cart in cart_items)
    pending_order = Order.objects.filter(
        user=user,
        status=Order.Status.PENDING,
    )

    if pending_order.exists():
        raise serializers.ValidationError(
            {
                "detail": "Pending order already exists",
            }
        )

    order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        total_amount=subtotal,
    )

    order_items = [
        OrderItem(
            order=order,
            product=cart.product,
            quantity=cart.quantity,
            price_at_purchase=cart.product.discounted_price,
        )
        for cart in cart_items
    ]
    OrderItem.objects.bulk_create(order_items)

    # Deduct stock & clear user cart
    for cart in cart_items:
        product = cart.product
        product.stock = F("stock") - cart.quantity
        product.save(update_fields=["stock"])

    CartItem.objects.filter(
        user=user,
        product__in=[c.product for c in cart_items],
    ).delete()

    return order, order_items

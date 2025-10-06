from collections import defaultdict
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from cart.models import CartItem
from product.models import Product

from .models import Order, OrderItem


@transaction.atomic
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
    ).select_for_update()

    # One pending order per user
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
        Product.objects.filter(id=cart.product_id).update(
            stock=F("stock") - cart.quantity
        )
    CartItem.objects.filter(
        user=user, product__in=[c.product for c in cart_items]
    ).delete()

    return (
        order,
        order_items,
    )


@transaction.atomic
def mark_pending_orders():
    """
    Mark pending orders older than 30 minutes as expired and restore product stock safely
    """

    expired_orders = Order.objects.filter(
        status=Order.Status.PENDING,
        created_at__lt=timezone.now() - timedelta(minutes=30),
    ).prefetch_related("order_items__product")

    if not expired_orders.exists():
        return

    expired_orders.update(status=Order.Status.EXPIRED)

    stock_changes = defaultdict(int)
    for order in expired_orders:
        for item in order.order_items.all():
            stock_changes[item.product_id] += item.quantity

    for product_id, qty in stock_changes.items():
        Product.objects.filter(id=product_id).update(stock=F("stock") + qty)

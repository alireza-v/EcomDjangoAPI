import random

import pytest
from django.db import IntegrityError

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)


@pytest.mark.parametrize("quantity", [1, 5, 10])
def test_user_cart_setup(
    cart_item_factory,
    sample_active_user,
    sample_products,
    quantity,
):
    user = sample_active_user
    product = sample_products["products"][0]
    cart_item = cart_item_factory(
        product=product,
        quantity=quantity,
    )

    assert cart_item.subtotal == f"{product.price * quantity:,.0f}"
    assert cart_item.user == user
    assert CartItem.objects.filter(
        user=user,
        product=product,
    ).exists()
    assert (
        str(cart_item)
        == f"{user.email} - {cart_item.product.title} (x{cart_item.quantity})"
    )

    with pytest.raises(IntegrityError):
        cart_item_factory(
            product=product,
            quantity=quantity,
        )


@pytest.mark.parametrize(
    "status",
    [
        "pending",
        "paid",
        "failed",
        "shipped",
    ],
)
def test_order_creation(
    sample_active_user,
    order_factory,
    status,
):
    user = sample_active_user
    order = order_factory(status)

    assert order.user == user
    assert Order.objects.filter(pk=order.pk).exists()
    assert order.status == status
    assert str(order) == f"Order by {user} - Status: {order.status.capitalize()}"


@pytest.mark.parametrize("quantity, price", [(1, 10.5), (5, 50.0), (10, 99.99)])
def test_order_item_creation(
    sample_products,
    sample_order,
    order_item_factory,
    quantity,
    price,
):
    product = sample_products["products"][0]

    order = sample_order

    order_item = order_item_factory(
        order=order,
        product=product,
        quantity=quantity,
        price=price,
    )

    assert OrderItem.objects.filter(
        order=order,
        product=product,
    ).exists()

    assert isinstance(order_item.quantity, int)
    assert order_item.quantity > 0
    assert isinstance(order_item.price_at_purchase, float)
    assert order_item.price_at_purchase > 0
    assert str(
        f"{order_item.product.title} x{order_item.quantity} (Order status: {order_item.order.status})"
    )

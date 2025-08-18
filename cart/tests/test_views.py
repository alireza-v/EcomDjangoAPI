from random import randint

import pytest
from django.urls import reverse

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)
from conftest import User


@pytest.mark.parametrize(
    "action,quantity,expected_status",
    [
        ("add", 5, 201),
        ("remove", 5, 201),
        ("remove", randint(6, 19), 400),
    ],
)
def test_cart_create(
    api_client,
    sample_products,
    sample_active_user,
    sample_carts,
    action,
    quantity,
    expected_status,
):
    _, _, product = sample_products
    user = sample_active_user
    cart = sample_carts

    api_client.force_authenticate(user)

    url = reverse("cart-create")
    response = api_client.post(
        url,
        {
            "product": product.id,
            "action": action,
            "quantity": quantity,
        },
    )

    assert response.status_code == expected_status

    if expected_status == 201 or expected_status == 200:
        data = response.json()
        print(response.status_code)
        print(data)
        assert all(
            key
            for key in [
                "user",
                "quantity",
                "product_info",
            ]
        )
        prev_quantity = cart.quantity if cart else 0  # current cart quantity

        if action == "add":
            expected_quantity = prev_quantity + quantity
        elif action == "remove":
            expected_quantity = (
                prev_quantity - quantity if prev_quantity >= quantity else prev_quantity
            )

        assert data["quantity"] == expected_quantity
    else:
        data = response.json()
        assert expected_status == 400


@pytest.mark.parametrize(
    "setup_cart,expected_status",
    [
        (True, 204),
        (False, 400),
    ],
)
def test_cart_drop(
    api_client,
    sample_active_user,
    sample_carts,
    setup_cart,
    expected_status,
):
    user = sample_active_user

    api_client.force_authenticate(user=user)
    url = reverse("cart-drop")

    if not setup_cart:
        sample_carts.delete()

    response = api_client.post(url)
    assert response.status_code == expected_status


def test_cart_list(
    api_client,
    sample_products,
    sample_active_user,
    sample_carts,
):
    user = sample_active_user

    api_client.force_authenticate(user)

    url = reverse("cart-list")
    response = api_client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert all(key for key in ["user", "quantity", "product_info"])


def test_failed_order(api_client, sample_active_user):
    user = sample_active_user

    url = reverse("checkout")
    api_client.force_authenticate(user)

    response = api_client.post(url)

    assert User.objects.filter(email=user.email)
    assert response.status_code == 400
    assert "Cart is empty" in response.data["detail"]


def test_success_order(
    api_client,
    sample_active_user,
    sample_products,
    sample_carts,
):
    user = sample_active_user
    _, _, product = sample_products
    cart = sample_carts

    api_client.force_authenticate(user=user)
    url = reverse("checkout")

    stock = product.stock
    cart_quantity = cart.quantity
    expected_stock = stock - cart_quantity

    response = api_client.post(url)

    # empty cart check
    if stock < cart_quantity:
        assert response.status_code == 400
        assert f"Not enough stock for {product.title}"
        return
    else:
        assert response.status_code == 201
        assert "Order created with success" in response.data["detail"]
        assert all(key in response.data for key in ["detail", "order_id", "status"])

        order = Order.objects.filter(
            user=user,
            status="pending",
        ).first()
        assert order is not None

        # refresh Product table
        product.refresh_from_db()
        assert product.stock == expected_stock

        order_item = OrderItem.objects.filter(
            order=order,
            product=product,
            quantity=cart_quantity,
            price_at_purchase=product.price,
        )
        assert order_item.exists()

        assert not CartItem.objects.filter(
            user=user,
        ).exists()

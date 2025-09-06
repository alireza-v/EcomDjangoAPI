import pytest
from django.urls import reverse

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)


def test_cart_list(auth_client):
    client, _ = auth_client

    response = client.get(
        reverse("cart-list-create"),
    )
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)

    expected_keys = [
        "user",
        "quantity",
        "product",
    ]
    assert all(expected_keys.issubset(item.keys()) for item in data)


@pytest.mark.parametrize(
    "action,quantity",
    [
        ("add", 3),
        ("add", 11),
        ("remove", 5),
        ("remove", 11),
    ],
)
def test_cart_create(
    auth_client,
    sample_products,
    sample_carts,
    action,
    quantity,
):
    product = sample_products["products"][0]
    client, _ = auth_client
    cart = sample_carts
    initial_cart_quantity = cart.quantity if cart else 0
    stock = product.stock

    url = reverse("cart-list-create")
    response = client.post(
        url,
        {
            "product_id": product.id,
            "quantity": quantity,
            "action": action,
        },
    )

    if action == "add" and quantity > stock:
        expected_status = 400
    elif action == "remove" and quantity > initial_cart_quantity:
        expected_status = 400
    else:
        expected_status = 201

    assert response.status_code == expected_status

    if response.status_code in (200, 201):
        data = response.json()

        if action == "add":
            expected_quantity = initial_cart_quantity + quantity
        elif action == "remove":
            expected_quantity = initial_cart_quantity - quantity

        assert data["quantity"] == expected_quantity


@pytest.mark.parametrize(
    "setup_cart,expected_status",
    [
        (True, 204),
        (False, 200),
    ],
)
def test_cart_clear(
    auth_client,
    sample_carts,
    setup_cart,
    expected_status,
):
    client, _ = auth_client
    url = reverse("cart-clear")

    if not setup_cart:
        sample_carts.delete()

    response = client.delete(url)
    assert response.status_code == expected_status


def test_order_success(
    auth_client,
    sample_products,
    sample_carts,
):
    product = sample_products["products"][0]
    cart = sample_carts
    client, user = auth_client

    url = reverse("checkout")

    stock = product.stock
    cart_quantity = cart.quantity
    expected_stock = stock - cart_quantity

    response = client.post(
        url,
        {
            "address": "some-address",
        },
    )

    if stock < cart_quantity:
        assert response.status_code == 400
        return
    else:
        assert response.status_code == 201
        assert all(
            key in response.data
            for key in [
                "detail",
                "status",
                "items",
            ]
        )

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


def test_order_list(auth_client):
    client, _ = auth_client
    url = reverse("order-list")
    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)

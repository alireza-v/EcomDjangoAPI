import pytest
from django.urls import reverse

from cart.models import CartItem
from orders.models import Order, OrderItem


@pytest.mark.parametrize(
    "setup_cart,status_code",
    [
        (True, 201),
        (False, 400),
    ],
)
def test_checkout(
    auth_client,
    sample_products,
    cart_item_factory,
    setup_cart,
    status_code,
):
    client, user = auth_client
    product = sample_products["products"][0]
    url = reverse("checkout")

    if setup_cart:
        cart = cart_item_factory(
            user=user,
            product=product,
        )
        response = client.post(
            path=url,
            data={
                "address": "random-address",
            },
        )
        print(response.data)

        assert response.status_code == status_code

        order = Order.objects.filter(
            user=user,
            status=Order.Status.PENDING,
        ).first()
        assert order is not None
        expected_stock = product.stock - cart.quantity
        product.refresh_from_db()
        assert product.stock == expected_stock
        order_item = OrderItem.objects.filter(
            order=order,
            product=product,
            quantity=cart.quantity,
            price_at_purchase=product.price,
        )
        assert order_item.exists()
        assert not CartItem.objects.filter(
            user=user,
        ).exists()
    else:
        response = client.post(
            path=url,
            data={
                "address": "some-address",
            },
        )

        assert response.status_code == status_code
        assert "out of stock" in response.data


def test_invoice(auth_client, sample_order_item):
    client, _ = auth_client
    url = reverse("invoice-list")

    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)

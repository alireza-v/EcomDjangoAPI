from decimal import Decimal

import pytest
from django.db import IntegrityError

from cart.models import CartItem


@pytest.mark.parametrize("quantity", [1, 5, 10])
def test_user_cart_setup(
    cart_item_factory,
    auth_client,
    sample_products,
    quantity,
):
    """
    User related cart tested with multiple values
    """
    _, user = auth_client
    product = sample_products["products"][0]

    cart_item = cart_item_factory(
        user=user,
        product=product,
        quantity=quantity,
    )

    cart_sub = f"{cart_item.subtotal:,.0f}"
    expected_sub = f"{Decimal(product.price * quantity):,.0f}"

    assert cart_sub == expected_sub
    assert isinstance(cart_item.subtotal, Decimal)
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
            user=user,
            product=product,
            quantity=quantity,
        )

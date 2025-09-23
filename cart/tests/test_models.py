import pytest
from django.db import IntegrityError

from cart.models import CartItem


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
        user=user,
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
            user=user,
            product=product,
            quantity=quantity,
        )

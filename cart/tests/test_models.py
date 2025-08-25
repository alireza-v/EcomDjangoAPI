from cart.models import *


def test_cart_creation(
    sample_carts,
    sample_active_user,
    sample_products,
):
    cart = sample_carts
    user = sample_active_user
    _, _, product = sample_products

    assert cart.user == user
    assert CartItem.objects.filter(user=user, product=product).exists()


def test_order_creation(
    sample_active_user,
    sample_order,
):
    user = sample_active_user
    order = sample_order

    assert order.user == user
    assert Order.objects.filter(pk=order.pk).exists()
    assert order.status == "pending"
    assert str(order) == f"Order by {user} - Status: {order.status.capitalize()}"


def test_order_item_creation(
    sample_products,
    sample_order_item,
    sample_active_user,
):
    _, _, product = sample_products
    order_item = sample_order_item
    user = sample_active_user

    assert order_item.order.user == user
    assert order_item.product == product
    assert isinstance(order_item.quantity, int)
    assert order_item.quantity > 0
    assert isinstance(order_item.price_at_purchase, float)
    assert order_item.price_at_purchase > 0
    assert str(
        f"{order_item.product.title} x{order_item.quantity} (Order status: {order_item.order.status})"
    )

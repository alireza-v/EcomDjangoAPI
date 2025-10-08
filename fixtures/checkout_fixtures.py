import random

import pytest
from faker import Faker

from cart.models import CartItem
from orders.models import Order, OrderItem
from payments.models import Payment

faker = Faker()


@pytest.fixture
def sample_cart_item(
    db,
    sample_active_user,
    sample_products,
):
    """Ready-made simple instance"""
    product = sample_products["products"][0]
    return CartItem.objects.create(
        user=sample_active_user,
        product=product,
        quantity=random.randint(1, 10),
    )


@pytest.fixture
def cart_item_factory(
    db,
):
    """
    Factory fixture to create CartItem instances using custom values
    """

    def create_cart_item(
        user,
        product,
        quantity: int = 1,
    ):
        return CartItem.objects.create(
            user=user,
            product=product,
            quantity=quantity,
        )

    return create_cart_item


@pytest.fixture
def sample_order(db, sample_active_user):
    """Create order instance"""

    return Order.objects.create(
        user=sample_active_user,
        shipping_address=faker.address(),
        total_amount=faker.pyfloat(
            left_digits=10,
            right_digits=2,
            positive=True,
        ),
    )


@pytest.fixture
def order_factory(db, sample_active_user):
    """Order model factory"""

    def _create_order(status: str = "pending"):
        return Order.objects.create(
            user=sample_active_user,
            status=status,
        )

    return _create_order


@pytest.fixture
def sample_order_item(
    db,
    sample_order,
    sample_products,
):
    order = sample_order
    product = sample_products["products"][0]

    return OrderItem.objects.create(
        order=order,
        product=product,
        quantity=random.randint(1, 10),
        price_at_purchase=faker.pyfloat(left_digits=10, right_digits=2, positive=True),
    )


@pytest.fixture
def order_item_factory(db):
    def _create_order_items(
        order,
        product=None,
        quantity=1,
        price=None,
    ):
        return OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=price,
        )

    return _create_order_items


@pytest.fixture
def sample_payment(
    db,
    sample_order,
    sample_active_user,
):
    return Payment.objects.create(
        order=sample_order,
        user=sample_active_user,
        track_id=str(faker.random_number(digits=10, fix_len=True)),
        amount=faker.pyfloat(left_digits=10, right_digits=2, positive=True),
    )

"""
The centralized configuration file which is to define fixtures, hooks, and shared test setup that can be reused across multiple test modules in the project.
"""

import random

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from rest_framework.test import APIClient

from cart.models import CartItem, Order, OrderItem
from product.models import (
    Category,
    FeatureName,
    FeatureValue,
    Feedback,
    Like,
    Product,
    ProductImage,
)

User = get_user_model()
RAW_PASSWORD = "edrQWE451"
faker = Faker()
client = APIClient()


@pytest.fixture
def auth_client(sample_active_user):
    """
    Return an authenticated API client & User
    """
    api_client = client

    api_client.force_authenticate(user=sample_active_user)

    return (
        api_client,
        sample_active_user,
    )


@pytest.fixture(autouse=True, scope="session")
def disable_throttling():
    """
    Disable throttling during tests
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []


@pytest.fixture
def sample_active_user(db):
    return User.objects.create_user(
        username="active_user",
        email="active_user@email.com",
        password=RAW_PASSWORD,
        is_active=True,
    )


@pytest.fixture
def sample_inactive_user(db):
    return User.objects.create_user(
        username="inactive_user",
        email="inactive_user@email.com",
        password=RAW_PASSWORD,
        is_active=False,
    )


@pytest.fixture
def sample_products(db):
    # Parent category
    parent = Category.objects.create(
        title="Electronics",
        visit_count=random.randint(0, 50),
    )
    # Child category
    child_categories = []
    for i in range(3):
        child = Category.objects.create(
            title=f"Mobile Phones {i + 1}",
            parent=parent,
            visit_count=random.randint(0, 10),
        )
        child_categories.append(child)

    # Products
    products = []
    for i, child in enumerate(child_categories):
        for j in range(5):
            product = Product.objects.create(
                title=f"Samsung {i + 1}-{j + 1}",
                category=child,
                price=round(random.uniform(10000, 3000), 2),
                description="Product description!",
                stock=random.randint(1, 10),
                visit_count=random.randint(0, 10),
            )
            products.append(product)
    return {
        "parent": parent,
        "child": child_categories,
        "products": products,
    }


@pytest.fixture
def sample_feature_name(db):
    return FeatureName.objects.create(
        name="color",
    )


@pytest.fixture
def sample_features(
    db,
    sample_products,
    sample_feature_name,
):
    product = sample_products["products"][0]
    feature_name = sample_feature_name

    feature = FeatureValue.objects.create(
        product=product,
        feature=feature_name,
        value="red",
    )
    return feature


@pytest.fixture
def sample_images(db, sample_products):
    product = sample_products["products"][0]

    image_file = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"\x47\x49\x46\x38\x39\x61",
        content_type="image/jpeg",
    )
    return ProductImage.objects.create(
        product=product,
        image=image_file,
    )


@pytest.fixture
def sample_feedbacks(
    db,
    sample_active_user,
    sample_products,
):
    def create_feedback(
        user=None,
        product=None,
        **kwargs,
    ):
        user = sample_active_user
        product = sample_products["products"][0]

        return Feedback.objects.create(
            user=user,
            product=product,
            description=kwargs.get("description", faker.text(max_nb_chars=100)),
            rating=kwargs.get("rating", random.randint(1, 5)),
        )

    return create_feedback


@pytest.fixture
def sample_likes(
    db,
    sample_active_user,
    sample_products,
):
    user = sample_active_user
    product = sample_products["products"][0]

    return Like.objects.create(
        user=user,
        product=product,
    )


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
    sample_active_user,
    sample_products,
):
    """
    Factory fixture to create CartItem instances using custom values
    """
    user = sample_active_user

    def _create_cart_item(
        product=None,
        quantity: int = 1,
    ):
        if product is None:
            product = sample_products["products"][0]
        return CartItem.objects.create(
            user=user,
            product=product,
            quantity=quantity,
        )

    return _create_cart_item


@pytest.fixture
def sample_order(
    db,
    sample_active_user,
):
    user = sample_active_user

    return Order.objects.create(
        user=user,
    )


@pytest.fixture
def order_factory(db, sample_active_user):
    """Order model factory"""

    user = sample_active_user

    def _create_order(status: str = "pending"):
        return Order.objects.create(
            user=user,
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
def order_item_factory(db, sample_products):
    def _create_order_items(
        order,
        product=None,
        quantity=1,
        price=None,
    ):
        if product:
            product = sample_products["products"][0]
        if price:
            price = product.price
        return OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=price,
        )

    return _create_order_items

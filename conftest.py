import random

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from rest_framework.test import APIClient

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)
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


@pytest.fixture
def api_client(db):
    return APIClient()


@pytest.fixture(autouse=True, scope="session")
def disable_throttling():
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
def sample_auth_token(
    db,
    sample_active_user,
    api_client,
):
    """Return token as auth_token"""
    user = sample_active_user

    response = api_client.post(
        "/auth/token/login/",
        {
            "email": user.email,
            "password": "123!@#QWE",
        },
    )
    return response.data


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
    parent = Category.objects.create(
        title="Electronics",
        visit_count=random.randint(0, 50),
    )
    child = Category.objects.create(
        title="Mobile Phones",
        parent=parent,
        visit_count=random.randint(0, 50),
    )
    product = Product.objects.create(
        title="Samsung",
        category=child,
        price=round(random.uniform(1000.0, 3000.0), 2),
        description="Product description!",
        stock=random.randint(1, 10),
        visit_count=random.randint(0, 50),
    )
    return parent, child, product


@pytest.fixture
def sample_feature_name(db):
    return FeatureName.objects.create(
        name="color",
    )


@pytest.fixture
def sample_features(db, sample_products, sample_feature_name):
    _, _, product = sample_products
    feature_name = sample_feature_name

    feature = FeatureValue.objects.create(
        product=product,
        feature=feature_name,
        value="red",
    )
    return feature


@pytest.fixture
def sample_images(db, sample_products):
    _, _, product = sample_products
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
def sample_feedbacks(db, sample_active_user, sample_products):
    _, _, product = sample_products

    feedback = Feedback.objects.create(
        user=sample_active_user,
        product=product,
        description="Product feedback!",
        rating=random.randint(1, 5),
    )
    return feedback


@pytest.fixture
def sample_likes(db, sample_active_user, sample_products):
    user = sample_active_user
    _, _, product = sample_products

    return Like.objects.create(
        user=user,
        product=product,
    )


@pytest.fixture
def sample_carts(db, sample_active_user, sample_products):
    _, _, product = sample_products
    user = sample_active_user

    return CartItem.objects.create(
        user=user,
        product=product,
        quantity=5,
    )


@pytest.fixture
def sample_order(db, sample_active_user):
    user = sample_active_user

    return Order.objects.create(
        user=user,
    )


@pytest.fixture
def sample_order_item(db, sample_order, sample_products):
    order = sample_order
    _, _, product = sample_products

    return OrderItem.objects.create(
        order=order,
        product=product,
        quantity=random.randint(1, 10),
        price_at_purchase=faker.pyfloat(left_digits=10, right_digits=2, positive=True),
    )

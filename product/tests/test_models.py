import random

import pytest
from django.db import IntegrityError, transaction
from django.utils.text import slugify

from product.models import (
    FeatureValue,
    Feedback,
    Like,
)


def test_category_slug_auto_generated(sample_products):
    category = sample_products["parent"]

    assert category.slug == slugify(category.title, allow_unicode=True)


def test_category_get_breadcrumb(sample_products):
    child = sample_products["child"][0]
    breadcrumbs = child.get_breadcrumbs()

    assert breadcrumbs == [sample_products["parent"], child]


def test_product_category_hierarchy(sample_products):
    parent = sample_products["parent"]
    child = sample_products["child"][0]
    product = sample_products["products"][0]

    assert parent.title == "Electronics"
    assert parent.subcategories.count() >= 1
    assert parent.slug == "electronics"

    assert child.parent == parent

    assert product.category == child


def test_product_price_formatting(sample_products):
    product = sample_products["products"][0]
    price = product.price_formatter

    assert price == f"{product.price:,.0f}"


def test_product_slug_auto_generated(sample_products):
    product = sample_products["products"][0]

    assert product.slug == slugify(product.title, allow_unicode=True)


def test_product_image(sample_images, sample_products):
    product = sample_products["products"][0]
    image = sample_images

    assert image.product == product

    assert str(image) == f"{product.title} - {image.id}"


def test_product_features(
    sample_features,
    sample_products,
    sample_feature_name,
):
    product = sample_products["products"][0]
    feature_name = sample_feature_name

    assert sample_features.product == product
    assert sample_features.feature == feature_name
    assert sample_features.value == "red"


def test_product_feature_str(sample_features):
    features = sample_features

    assert (
        str(features)
        == f"{features.product.title} - {features.feature.name}: {features.value}"
    )


def test_product_feature_unique_constraint(
    sample_products,
    sample_features,
    sample_feature_name,
):
    product = sample_products["products"][0]
    feature_name = sample_feature_name
    feature = sample_features

    # Avoid being failed and left as broken state in database
    with transaction.atomic():
        # Prevent duplicate values being inserted
        with pytest.raises(IntegrityError):
            FeatureValue.objects.create(
                product=product,
                feature=feature_name,
                value=feature.value,
            )

    new_feature = FeatureValue.objects.create(
        product=product,
        feature=feature_name,
        value="new-value",
    )
    assert new_feature.value == "new-value"


def test_product_likes(
    sample_active_user,
    sample_likes,
    sample_products,
):
    user = sample_active_user
    product = sample_products["products"][0]

    assert sample_likes.user == user
    assert sample_likes.product == product
    assert str(sample_likes) == f"{product.title}"


def test_likes_unique_constraint(
    sample_likes,
    sample_products,
    sample_active_user,
):
    user = sample_active_user
    product = sample_products["products"][0]

    with pytest.raises(IntegrityError):
        Like.objects.create(
            user=user,
            product=product,
        )


def test_feedback(
    sample_active_user,
    sample_feedbacks,
    sample_products,
):
    product = sample_products["products"][0]
    user = sample_active_user
    feedback = sample_feedbacks(user=user, produc=product)

    assert feedback.user.email == user.email
    assert feedback.product == product
    assert str(feedback) == f"{user.email}- {feedback.description[:10]}"

    with pytest.raises(IntegrityError):
        Feedback.objects.create(
            user=user,
            product=product,
            rating=random.randint(1, 5),
        )

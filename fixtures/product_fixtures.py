import random

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from product.models import (
    Category,
    FeatureName,
    FeatureValue,
    Product,
    ProductImage,
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
                stock=5,
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

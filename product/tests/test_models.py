def test_product_category_hierarchy(sample_products):
    parent, child, product = sample_products

    assert parent.title == "Electronics"
    assert parent.subcategories.count() == 1
    assert parent.slug == "electronics"

    assert child.title == "Mobile Phones"
    assert child.parent == parent
    assert str(child) == "Mobile Phones"
    assert child.slug == "mobile-phones"

    assert product.title == "Samsung"
    assert product.category == child
    assert "mobile-phones" in [parent.slug, child.slug]
    assert product.slug == "samsung"


def test_product_image(sample_images, sample_products):
    _, _, product = sample_products
    image = sample_images

    assert image.product == product
    assert image.product.title == "Samsung"
    assert str(image) == f"{product.title} - {image.id}"


def test_product_features(
    sample_features,
    sample_products,
    sample_feature_name,
):
    _, _, product = sample_products
    feature_name = sample_feature_name

    assert sample_features.product == product
    assert sample_features.feature == feature_name
    assert sample_features.value == "red"


def test_product_likes(
    sample_active_user,
    sample_likes,
    sample_products,
):
    user = sample_active_user
    _, _, product = sample_products

    assert sample_likes.user == user
    assert sample_likes.product == product


def test_feedback(
    sample_active_user,
    sample_feedbacks,
    sample_products,
):
    _, _, product = sample_products
    user = sample_active_user
    feedback = sample_feedbacks

    assert sample_feedbacks.user.email == user.email
    assert feedback.product == product

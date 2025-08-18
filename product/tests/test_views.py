import pytest
from django.urls import reverse
from django.utils.text import slugify

from product.models import Feedback, Like


def test_products(api_client, sample_products, sample_features):
    _, _, product = sample_products
    features = [sample_features]

    url = reverse("product-list-api")
    response = api_client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, list)

    product_found = False

    for category in response.data:
        for subcategory in category.get("subcategories", []):
            for prod in subcategory.get("products", []):
                if prod["title"] == product.title:
                    product_found = True

                    assert prod["id"] == product.id
                    assert prod["price"] == f"{product.price:,.0f}"
                    assert prod["slug"] == slugify(product.title)
                    assert prod["features"] == [
                        {"feature": f.feature.name, "value": f.value} for f in features
                    ]
                    break
    assert product_found, f"Product '{product.title}' not found in response"


def test_product_with_params(api_client, sample_products):
    category, child, product = sample_products

    url = reverse("product-list-api")
    response = api_client.get(
        url,
        {
            "selected": child.slug,
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    returned_category = data[0]
    assert (
        returned_category["title"] == child.title
        or returned_category["title"] == category.title
    )

    found = False
    for prod in returned_category.get("products", []):
        if prod["id"] == product.id:
            found = True
            assert prod["title"] == product.title
            assert prod["price"] == f"{product.price:,.0f}"
            break

    for sub in returned_category.get("subcategories", []):
        for prod in sub.get("products", []):
            if prod["id"] == product.id:
                found = True
                assert prod["title"] == product.title
                assert prod["price"] == f"{product.price:,.0f}"
                break
    assert found, f"Product '{product.title}' not found in response"


def extract_products(category):
    products = category.get("products", [])
    for sub in category.get("subcategories", []):
        products += extract_products(sub)
    return products


def test_search_products(api_client, sample_products):
    _, _, product = sample_products

    url = reverse("product-list-api")
    response = api_client.get(
        url,
        {
            "search": product.title,
        },
    )

    all_products = []
    for category in response.json():
        all_products += extract_products(category)

    assert response.status_code == 200
    assert any(p["title"] == product.title for p in all_products)


def test_filter_products(api_client, sample_products):
    _, child, _ = sample_products
    url = reverse("product-list-api")

    filter_response = api_client.get(
        url,
        {
            "selected": child.slug,
            "min_price": 500,
            "max_price": 1000,
        },
    )
    assert filter_response.status_code == 200

    data = filter_response.json()
    filtered_products = data[0].get("products", [])

    price = [float(p["price"].replace(",", "")) for p in filtered_products]

    assert sorted(price) == price


@pytest.mark.parametrize(
    "sort_order,is_desc",
    [
        ("price_asc", False),
        ("price_desc", True),
        ("most_visited", True),
    ],
)
def test_sort_products(api_client, sample_products, sort_order, is_desc):
    _, child, _ = sample_products
    url = reverse("product-list-api")

    sort_response = api_client.get(
        url,
        {
            "selected": child.slug,
            "sorted": sort_order,
        },
    )

    assert sort_response.status_code == 200

    data = sort_response.json()
    products = data[0].get("products", [])
    prices = [float(p["price"].replace(",", "")) for p in products]

    assert prices == sorted(prices, reverse=is_desc)


def test_sort_products_failed(api_client, sample_products):
    url = reverse("product-list-api")

    response = api_client.get(
        url,
        {
            "sorted": "invalid_sorted",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert "products" in data[0]

    products = data[0].get("products", [])
    product_ids = [p["id"] for p in products]

    assert product_ids == sorted(product_ids, reverse=True)


def test_product_detail(api_client, sample_products):
    _, _, product = sample_products

    url = reverse(
        "product-detail-api",
        kwargs={
            "slug": product.slug,
        },
    )
    response = api_client.get(url)
    data = response.data

    assert response.status_code == 200
    assert data["title"] == product.title
    assert data["description"] == product.description


def test_create_feedback(api_client, sample_active_user, sample_products):
    user = sample_active_user
    _, _, product = sample_products

    url = reverse(
        "create-feedback",
    )
    api_client.force_authenticate(user)
    response = api_client.post(
        url,
        {
            "product": product.id,
            "description": "Excellet product!",
            "rating": 3,
        },
    )

    assert response.status_code == 201
    assert Feedback.objects.filter(user=user, product=product).exists()


def test_create_feedback_invalid(
    api_client, sample_products, sample_active_user, sample_feedbacks
):
    user = sample_active_user
    _, _, product = sample_products

    url = reverse("create-feedback")

    api_client.force_authenticate(user)
    feedback = sample_feedbacks

    assert Feedback.objects.filter(user=user).exists()

    response = api_client.post(
        url,
        {
            "product": product.id,
            "description": "Excellet product!",
            "rating": 3,
        },
    )
    data = response.json()

    assert response.status_code == 400
    assert data["non_field_errors"][0] == "You already made a review."


@pytest.mark.parametrize(
    "like_exists_before, expected_status",
    [
        (True, 200),
        (False, 201),
    ],
)
def test_like_toggle(
    api_client,
    sample_active_user,
    sample_products,
    sample_likes,
    like_exists_before,
    expected_status,
):
    user = sample_active_user
    _, _, product = sample_products

    api_client.force_authenticate(user)
    url = reverse("like-toggle")

    if like_exists_before:
        sample_likes
    else:
        Like.objects.filter(
            user=user,
            product=product,
        ).delete()

    response = api_client.post(
        url,
        {
            "product": product.id,
        },
    )

    assert response.status_code == expected_status

    if like_exists_before:
        assert not Like.objects.filter(
            user=user,
            product=product,
        ).exists()
    else:
        assert Like.objects.filter(
            user=user,
            product=product,
        ).exists()
        assert "user" in response.data and "product_related" in response.data

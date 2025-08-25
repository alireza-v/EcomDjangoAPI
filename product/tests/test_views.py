import random

import pytest
from django.urls import reverse

from product.models import Feedback, Like


def test_products(
    api_client,
    sample_products,
    sample_features,
):
    _, _, product = sample_products
    features = [sample_features]

    url = reverse("product-list-api")
    response = api_client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, dict)

    expected = ["count", "next", "previous", "results"]
    for key in expected:
        assert key in response.data


def test_select_product_with_slug(api_client, sample_products):
    _, _, product = sample_products

    url = reverse("product-list-api")
    response = api_client.get(
        url,
        {
            "category": product.slug,
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "param,value",
    [
        ("min_price", lambda _: random.randint(10_000_000, 50_000_000)),
        ("max_price", lambda _: random.randint(10_000_000, 50_000_000)),
        ("wrong_param", "wrong-value"),
    ],
)
def test_products_filtering(
    api_client,
    sample_products,
    sample_features,
    param,
    value,
):
    if callable(value):
        value = value(sample_products)

    url = reverse("product-list-api")
    response = api_client.get(url, {param: value})

    assert response.status_code == 200

    data = response.data
    results = data["results"]

    if results:
        expected_fields = [
            "title",
            "slug",
            "visit_count",
            "price",
            "features",
        ]
        assert isinstance(results, list)

        for res in results:
            for exp in expected_fields:
                assert exp in res


@pytest.mark.parametrize(
    "sort_order,is_desc",
    [
        ("price", False),
        ("-price", True),
        ("visit_count", False),
        ("-visit_count", True),
        ("created_at", False),
        ("-created_at", True),
    ],
)
def test_products_sorted(
    api_client,
    sample_products,
    sort_order,
    is_desc,
):
    _, _, _ = sample_products
    url = reverse("product-list-api")

    response = api_client.get(url, {"ordering": sort_order})

    assert response.status_code == 200

    results = response.json()["results"]
    field = sort_order.lstrip("-")
    values = [item[field] for item in results]

    if is_desc:
        assert values == sorted(values, reverse=True)
    else:
        assert values == sorted(values)


def test_search_products(
    api_client,
    sample_products,
):
    _, _, product = sample_products

    url = reverse("product-list-api")
    response = api_client.get(url, {"search": product.title})

    assert response.status_code == 200
    results = response.json()["results"]

    assert len(results) == 1
    assert results[0]["slug"] == product.slug


def test_categories(api_client, sample_products):
    url = reverse("category-list-api")
    response = api_client.get(url)
    data = response.data

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1

    expected = [
        "title",
        "slug",
        "products_preview",
        "subcategories",
    ]
    for exp in expected:
        assert exp in data[0]


def test_product_detail(
    api_client,
    sample_products,
):
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


def test_feedback_create(
    api_client,
    sample_active_user,
    sample_products,
):
    user = sample_active_user
    _, _, product = sample_products

    api_client.force_authenticate(user=user)

    url = reverse(
        "create-feedback",
    )
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


def test_invalid_feedback_create(
    api_client,
    sample_products,
    sample_active_user,
    sample_feedbacks,
):
    user = sample_active_user
    _, _, product = sample_products

    url = reverse("create-feedback")

    api_client.force_authenticate(user)

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
def test_toggle_likes(
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

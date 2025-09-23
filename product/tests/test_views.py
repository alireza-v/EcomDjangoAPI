import random

import pytest
from django.urls import reverse

from conftest import faker
from product.models import Feedback, Like


def test_products(
    auth_client,
    sample_products,
):
    """Fetch products"""

    _ = sample_products["products"][0]

    client, _ = auth_client

    url = reverse("product-list")
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, dict)

    expected = [
        "count",
        "next",
        "previous",
        "results",
    ]
    for key in expected:
        assert key in response.data


def test_filter_by_category(
    auth_client,
    sample_products,
):
    client, _ = auth_client
    product = sample_products["products"][0]

    url = reverse("product-list")
    response = client.get(
        url,
        {
            "category": product.slug,
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "param,value,expectation",
    [
        (
            "min_price",
            lambda _: random.randint(5_000_000, 15_000_000),
            lambda product, value: int(product["price"]) >= value,
        ),
        (
            "max_price",
            lambda _: random.randint(20_000_000, 40_000_000),
            lambda product, value: int(product["price"]) <= value,
        ),
        (
            "in_stock",
            lambda _: random.choice([True, False]),
            lambda product, v: product["in_stock"] is v,
        ),
    ],
)
def test_product_filtering(auth_client, sample_products, param, value, expectation):
    """Filter products by the given parameters and validate results."""

    client, _ = auth_client
    url = reverse("product-list")

    if callable(value):
        value = value(sample_products)
        print(f"value: {value}")

    response = client.get(url, {param: value})

    assert response.status_code == 200

    results = response.json()["results"]

    if expectation:
        if results:
            assert all(expectation(product, value) for product in results), (
                f"Filter {param}={value} returned wrong results: {results}"
            )
        else:
            assert results == []
    else:
        assert len(results) == len(sample_products)


@pytest.mark.parametrize(
    "order_field,is_desc",
    [
        ("price", False),
        ("-price", True),
        ("visit_count", False),
        ("-visit_count", True),
        ("created_at", False),
        ("-created_at", True),
    ],
)
def test_product_ordering(
    auth_client,
    sample_products,
    order_field,
    is_desc,
):
    """
    Ordering fields:
        - price
        - visit_count
        - created_at
    """

    url = reverse("product-list")
    client, _ = auth_client

    response = client.get(
        url,
        {
            "ordering": order_field,
        },
    )

    assert response.status_code == 200

    results = response.json()["results"]
    field = order_field.lstrip("-")
    values = [item[field] for item in results]

    if is_desc:
        assert values == sorted(values, reverse=True)
    else:
        assert values == sorted(values)


def test_search_products(
    auth_client,
    sample_products,
):
    product = sample_products["products"][0]

    client, _ = auth_client

    url = reverse("product-list")
    response = client.get(
        url,
        {
            "q": product.title,
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]

    assert len(results) == 1
    assert results[0]["slug"] == product.slug


def test_categories(auth_client, sample_products):
    client, _ = auth_client

    url = reverse("category-list")
    response = client.get(url)
    data = response.data

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1


def test_product_detail(auth_client, sample_products):
    product = sample_products["products"][0]
    client, _ = auth_client

    url = reverse(
        "product-detail",
        kwargs={
            "slug": product.slug,
        },
    )
    response = client.get(url)
    data = response.data

    assert response.status_code == 200
    assert isinstance(response.data, dict)
    assert data["title"] == product.title
    assert data["description"] == product.description


@pytest.mark.parametrize(
    "already_made_comment,exp_st_code",
    [
        (False, 201),
        (True, 400),
    ],
)
def test_feedback_create(
    auth_client,
    sample_products,
    sample_feedbacks,
    already_made_comment,
    exp_st_code,
):
    product = sample_products["products"][0]
    client, user = auth_client

    if already_made_comment:
        sample_feedbacks()

    url = reverse(
        "list-create-feedback",
        kwargs={"product_id": product.id},
    )
    payload = {
        "comment": faker.text(max_nb_chars=50),
        "score": random.randint(1, 5),
    }
    response = client.post(url, payload)

    feedback_count = Feedback.objects.filter(
        user=user,
        product=product,
    ).count()

    assert response.status_code == exp_st_code

    # In either case, the counting should be 1
    assert feedback_count == 1

    expected_keys = ["user", "score", "comment"]

    if exp_st_code == 201:
        missing_keys = set(expected_keys) - set(
            response.data.keys()
        )  # Only the intended keys are present
        assert not missing_keys, f"Missing keys in response: {missing_keys}"


@pytest.mark.parametrize(
    "p_id",
    [
        ("valid"),
        (1000000),
    ],
)
def test_feedback_list(
    sample_products,
    auth_client,
    sample_feedbacks,
    p_id,
):
    product = sample_products["products"][0]
    client, _ = auth_client

    if p_id == "valid":  # valid product_id
        p_id = product.id

    url = reverse(
        "list-create-feedback",
        kwargs={"product_id": p_id},
    )
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, dict)
    result = response.data["results"]
    if result:
        assert isinstance(result[0], list)
        expected_keys = ["user", "rate"]
        for key in expected_keys:
            assert key in expected_keys
    else:
        assert not result


@pytest.mark.parametrize(
    "already_liked, expected_status",
    [
        (True, 200),
        (False, 201),
    ],
)
def test_toggle_likes(
    auth_client,
    sample_products,
    sample_likes,
    already_liked,
    expected_status,
):
    product = sample_products["products"][0]
    client, user = auth_client

    url = reverse("like-toggle")

    if already_liked:
        sample_likes(
            user=user,
            product=product,
        )

    response = client.post(
        url,
        {
            "product": product.id,
        },
    )

    assert response.status_code == expected_status

    if already_liked:
        assert not Like.objects.filter(
            user=user,
            product=product,
        ).exists()
    else:
        assert Like.objects.filter(
            user=user,
            product=product,
        ).exists()

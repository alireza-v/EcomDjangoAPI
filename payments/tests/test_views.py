from unittest.mock import patch

import requests
from django.urls import reverse

from orders.models import Order
from payments.models import Payment


def test_no_pending_order(auth_client):
    client, _ = auth_client
    url = reverse("create-payment")
    response = client.post(url)

    assert response.status_code == 400


@patch("payments.views.requests.post")
def test_create_new_payment(
    mock_post,
    auth_client,
    sample_order,
):
    client, _ = auth_client
    url = reverse("create-payment")
    mock_post.return_value.json.return_value = {
        "result": 100,
        "trackId": "FAKE_TRACK_ID",
        "message": "Success",
    }
    response = client.post(url)

    assert response.status_code == 200
    assert response.data["trackId"] == "FAKE_TRACK_ID"
    assert Payment.objects.filter(order=sample_order, track_id="FAKE_TRACK_ID").exists()


@patch("payments.views.requests.post")
def test_existing_payment_returned(
    mock_post,
    auth_client,
    sample_order,
    sample_payment,
):
    client, _ = auth_client
    url = reverse("create-payment")
    response = client.post(url)

    assert response.status_code == 200
    assert "Already initiated payment" in response.data["message"]
    assert Payment.objects.filter(order=sample_order).count() == 1


def test_callback_without_track_id(auth_client):
    client, _ = auth_client
    url = reverse("payment-callback")
    response = client.get(url)
    assert response.status_code == 400
    assert response.data["detail"] == "track_id not provided"


def test_callback_payment_not_found(auth_client):
    client, _ = auth_client
    url = reverse("payment-callback")
    response = client.get(
        url,
        {
            "trackId": "not-exist",
        },
    )
    assert response.status_code == 404
    assert "No payment record found" in response.data["detail"]


@patch("payments.views.requests.post")
def test_callback_success(
    mock_post,
    auth_client,
    sample_order,
    sample_payment,
):
    payment = sample_payment
    order = sample_order
    client, _ = auth_client
    url = reverse("payment-callback")
    mock_post.return_value.json.return_value = {"result": 100}
    response = client.get(
        url,
        {
            "trackId": payment.track_id,
        },
    )
    assert response.status_code == 200
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.SUCCESS
    assert sample_order.status == Order.Status.PAID
    assert "Payment was successful" in response.data["detail"]


@patch("payments.views.requests.post")
def test_callback_previously_verified(
    mock_post, auth_client, sample_payment, sample_order
):
    order = sample_order
    payment = sample_payment
    client, _ = auth_client
    url = reverse("payment-callback")
    mock_post.return_value.json.return_value = {"result": 201}
    response = client.get(
        url,
        {
            "trackId": payment.track_id,
        },
    )
    assert response.status_code == 200
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.Status.SUCCESS
    assert order.status == Order.Status.PAID
    assert "success" in response.data["detail"]


@patch("payments.views.requests.post")
def test_callback_failed_payment(mock_post, auth_client, sample_order, sample_payment):
    order = sample_order
    payment = sample_payment
    client, _ = auth_client
    url = reverse("payment-callback")
    mock_post.return_value.json.return_value = {
        "result": -1,
        "message": "Insufficient funds",
    }
    response = client.get(
        url,
        {
            "trackId": payment.track_id,
        },
    )
    assert response.status_code == 400
    payment.refresh_from_db()
    assert payment.status == Payment.Status.FAILED


@patch(
    "payments.views.requests.post",
    side_effect=requests.RequestException("Gateway down"),
)
def test_callback_gateway_error(
    mock_post,
    auth_client,
    sample_order,
    sample_payment,
):
    client, _ = auth_client
    url = reverse("payment-callback")
    response = client.get(
        url,
        {
            "trackId": sample_payment.track_id,
        },
    )
    assert response.status_code == 502


def test_payment_history(auth_client):
    client, _ = auth_client
    url = reverse("payment-history")
    response = client.get(url)
    assert response.status_code == 200

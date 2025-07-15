import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@pytest.mark.django_db
def test_user_registration(api_client):
    payload = {
        "email": "test_user@email.com",
        "password": "123!@#QWE",
    }
    response = api_client.post("/auth/users/", payload)

    assert response.status_code == 201
    assert all(key in response.data for key in ("email", "id"))


@pytest.mark.django_db
def test_user_already_registered(api_client, create_active_user):
    user = create_active_user
    payload = {
        "email": user.email,
        "password": user.password,
    }
    response = api_client.post("/auth/users/", payload)

    assert response.status_code == 400
    assert (
        "custom user with this email already exists."
        in response.data.get("email")[0].lower()
    )


def test_user_activation(create_inactive_user, api_client):
    user = create_inactive_user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = reverse(
        "activation",
        kwargs={
            "uid": uid,
            "token": token,
        },
    )
    response = api_client.get(url)

    user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["result"] == "Account activated"
    assert user.is_active is True

def test_user_invalid_activation_token(create_inactive_user,api_client):
        user=create_inactive_user

        uid=urlsafe_base64_encode(force_bytes(user.pk))
        token="invalid token"

        url=reverse("activation",kwargs={
                "uid":uid,
                "token":token,
        })
        response=api_client.get(url)

        assert response.status_code==400
        assert response.data["error"]=="Invalid activation link"

        user.refresh_from_db()

        assert user.is_active is False



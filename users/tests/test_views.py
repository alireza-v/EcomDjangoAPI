import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from conftest import *

User = get_user_model()
faker = Faker()


@pytest.mark.parametrize(
    "email,username,password",
    [
        (faker.email(), faker.user_name(), faker.password(length=8)),
        (faker.email(), "", faker.password(length=8)),
    ],
)
def test_user_registration(
    db,
    api_client,
    email,
    username,
    password,
):
    payload = {
        "email": email,
        "username": username,
        "password": password,
    }
    response = api_client.post(
        "/auth/users/",
        payload,
    )

    assert response.status_code == 201
    assert all(key in response.data for key in ("email", "username"))

    # check password hashing
    user = User.objects.get(email=email)
    assert user.check_password(password)


def test_user_already_registered(
    api_client,
    sample_active_user,
):
    user = sample_active_user

    payload = {
        "email": user.email,
        "username": user.username,
        "password": RAW_PASSWORD,
    }
    response = api_client.post(
        "/auth/users/",
        payload,
    )

    assert response.status_code == 400
    assert (
        "custom user with this email already exists."
        in response.data.get("email")[0].lower()
    )


@pytest.mark.parametrize(
    "email,username",
    [
        ("bademail", "fake-user"),
        ("test@email", ""),
        ("", "some-user"),
        ("example@email.com", "123"),
    ],
)
def test_user_register_invalid_credentials(
    db,
    api_client,
    email,
    username,
):
    short_password = "123"
    response = api_client.post(
        "/auth/users/",
        {
            "email": email,
            "username": username,
            "password": short_password,
        },
    )

    assert response.status_code == 400
    assert any(key in response.data for key in ("email", "password"))


def test_user_activation(
    api_client,
    sample_inactive_user,
):
    user = sample_inactive_user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = api_client.get(f"/api/users/activate/{uid}/{token}/")

    user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["result"] == "Account activated"
    assert user.is_active is True
    assert User.objects.filter(email=user.email).exists()


def test_user_invalid_activation_token(api_client, sample_inactive_user):
    user = sample_inactive_user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = "invalid-token"

    url = reverse(
        "activation",
        kwargs={
            "uid": uid,
            "token": token,
        },
    )
    response = api_client.get(url)

    assert response.status_code == 400
    assert response.data["error"] == "Invalid activation link"

    user.refresh_from_db()

    assert user.is_active is False


def test_user_login(
    api_client,
    sample_active_user,
):
    user = sample_active_user

    response = api_client.post(
        "/auth/jwt/create/",
        {
            "email": user.email,
            "password": RAW_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert all(
        key in response.data
        for key in (
            "access",
            "refresh",
        )
    )


@pytest.mark.parametrize(
    "email,password,code",
    [
        ("email", "123", 401),
        ("example@email", "123", 401),
        ("example@email.com", "123", 401),
        ("example@email.com", "", 400),
    ],
)
def test_user_login_failed(
    db,
    api_client,
    email,
    password,
    code,
):
    response = api_client.post(
        "/auth/jwt/create/",
        {
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == code
    if code == 401:
        assert (
            "No active account found with the given credentials"
            in response.data["detail"]
        )
    if code == 400:
        assert "This field may not be blank." in response.data["password"]


def test_user_logout(
    api_client,
    sample_active_user,
):
    user = sample_active_user

    login_response = api_client.post(
        "/auth/jwt/create/",
        {
            "email": user.email,
            "password": RAW_PASSWORD,
        },
    )

    access = login_response.data.get("access")
    refresh = login_response.data.get("refresh")

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )

    logout_response = api_client.post(
        "/auth/jwt/logout/",
        {
            "refresh": refresh,
        },
    )

    assert logout_response.status_code == 200
    assert isinstance(logout_response.data, dict)

    refresh_attempt = api_client.post(
        "/auth/jwt/refresh/",
        {
            "refresh": refresh,
        },
    )
    assert refresh_attempt.status_code == 401
    assert "token_not_valid" in str(refresh_attempt.data).lower()

    with pytest.raises(TokenError):
        RefreshToken(refresh).check_blacklist()


@pytest.mark.parametrize(
    "email,code",
    [
        ("example@email.com", 204),
        ("", 400),
    ],
)
def test_reset_password_request(
    api_client,
    email,
    code,
):
    response = api_client.post(
        "/auth/users/reset_password/",
        {
            "email": email,
        },
    )

    assert response.status_code == code


@pytest.mark.parametrize(
    "valid_token,expected_code",
    [
        (True, 204),
        (False, 400),
    ],
)
def test_reset_password_confirm(
    api_client,
    sample_active_user,
    valid_token,
    expected_code,
):
    user = sample_active_user

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    if valid_token:
        token = default_token_generator.make_token(user)
    else:
        token = "invalid-token"

    response = api_client.post(
        "/auth/users/reset_password_confirm/",
        {
            "uid": uid,
            "token": token,
            "new_password": RAW_PASSWORD,
        },
    )
    print(response)
    print(response.data)

    assert response.status_code == expected_code

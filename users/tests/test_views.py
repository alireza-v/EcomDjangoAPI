import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from fixtures.auth_fixtures import RAW_PASSWORD

User = get_user_model()
faker = Faker()


@pytest.mark.parametrize(
    "email,username,password,code",
    [
        (
            faker.email(),
            faker.user_name(),
            faker.password(length=8),
            201,
        ),
        (
            faker.email(),
            "",
            faker.password(length=8),
            201,
        ),
        (
            "active_user@email.com",
            "active_user",
            faker.password(length=8),
            400,
        ),
        (
            "active_user@email.com",
            "active_user",
            "123",
            400,
        ),
        (
            "active_user@email.com",
            "active_user",
            "",
            400,
        ),
    ],
)
def test_user_registration(
    client,
    sample_active_user,
    email,
    username,
    password,
    code,
):
    """
    Test user registration with valid & invalid input and expected output including:
        - status code
        - database state
        - password hashing
    """
    payload = {
        "email": email,
        "username": username,
        "password": password,
    }
    response = client.post(
        "/auth/users/",
        payload,
    )

    assert response.status_code == code
    if code == 201:
        assert all(key in response.data for key in ["email", "username"])

        user_created = User.objects.filter(email=email)
        assert user_created.exists()

        user_qs = user_created.first()
        assert user_qs.check_password(password)

    elif code == 400:
        assert any(key in response.data for key in ["email", "username", "password"])


@pytest.mark.parametrize(
    "token_generator_function,code,result,is_active",
    [
        (
            lambda user: default_token_generator.make_token(user),
            200,
            "Account activated",
            True,
        ),
        (lambda user: "Invalid token", 400, "Invalid credentials", False),
    ],
)
def test_user_activation(
    client,
    sample_inactive_user,
    token_generator_function,
    code,
    result,
    is_active,
):
    user = sample_inactive_user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator_function(user)

    url = reverse(
        "activation",
        kwargs={
            "uid": uid,
            "token": token,
        },
    )
    response = client.get(url)

    assert response.status_code == code
    if code == 200:
        assert response.data["detail"] == result
    else:
        assert response.data["error"] == result

    user.refresh_from_db()

    assert user.is_active is is_active
    assert User.objects.filter(email=user.email).exists()


@pytest.mark.parametrize(
    "email,password,code,keys,error",
    [
        ("active_user@email.com", RAW_PASSWORD, 200, ["access", "refresh"], None),
        (
            "email",
            "123",
            401,
            None,
            "Email or password is incorrect",
        ),
        (
            "example@email",
            "123",
            401,
            None,
            "Email or password is incorrect",
        ),
        (
            "example@email.com",
            "123",
            401,
            None,
            "Email or password is incorrect",
        ),
        ("example@email.com", "", 400, None, "This field may not be blank."),
    ],
)
def test_user_login(
    auth_client,
    email,
    password,
    code,
    keys,
    error,
):
    client, _ = auth_client

    response = client.post(
        "/auth/jwt/create/",
        {
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == code

    if code == 200:
        assert all(key in response.data for key in keys)
    else:
        if code == 401:
            assert error in response.data["detail"]
        elif code == 400:
            assert error in response.data["password"]


def test_user_logout(auth_client):
    client, user = auth_client

    login_response = client.post(
        "/auth/jwt/create/",
        {
            "email": user.email,
            "password": RAW_PASSWORD,
        },
    )

    access = login_response.data.get("access")
    refresh = login_response.data.get("refresh")

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )

    logout_response = client.post(
        "/auth/jwt/logout/",
        {
            "refresh": refresh,
        },
    )

    assert logout_response.status_code == 200
    assert isinstance(logout_response.data, dict)

    refresh_attempt = client.post(
        "/auth/jwt/refresh/",
        {
            "refresh": refresh,
        },
    )
    assert refresh_attempt.status_code == 401
    assert "token_not_valid" in str(refresh_attempt.data).lower()

    with pytest.raises(TokenError):
        RefreshToken(refresh).check_blacklist()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email,code",
    [
        ("example@email.com", 204),
        ("", 400),
    ],
)
def test_reset_password_request(
    client,
    email,
    code,
):
    response = client.post(
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
    auth_client,
    valid_token,
    expected_code,
):
    client, user = auth_client

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    if valid_token:
        token = default_token_generator.make_token(user)
    else:
        token = "invalid-token"

    response = client.post(
        "/auth/users/reset_password_confirm/",
        {
            "uid": uid,
            "token": token,
            "new_password": RAW_PASSWORD,
        },
    )

    assert response.status_code == expected_code

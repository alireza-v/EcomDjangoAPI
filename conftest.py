import pytest
from rest_framework.test import APIClient


@pytest.fixture
def user_model():
    from django.contrib.auth import get_user_model

    return get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_active_user(db, user_model):
    return user_model.objects.create_user(
        email="active_user@email.com",
        password="123!@#QWE",
        is_active=True,
    )


@pytest.fixture
def create_inactive_user(db, user_model):
    return user_model.objects.create_user(
        email="inactive_user@email.com",
        password="123!@#QWE",
        is_active=False,
    )

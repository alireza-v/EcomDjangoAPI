import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

RAW_PASSWORD = "qrzWISK2819*#^!"


@pytest.fixture(autouse=True, scope="session")
def disable_throttling():
    """Disable DRF throttling during all tests"""
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []


@pytest.fixture
def sample_active_user(db):
    """Return an active Django user"""
    User = get_user_model()
    return User.objects.create_user(
        username="active_user",
        email="active_user@email.com",
        password=RAW_PASSWORD,
        is_active=True,
    )


@pytest.fixture
def sample_inactive_user(db):
    """Return an inactive Django user"""
    User = get_user_model()
    return User.objects.create_user(
        username="inactive_user",
        email="inactive_user@email.com",
        password=RAW_PASSWORD,
        is_active=False,
    )


@pytest.fixture
def auth_client(sample_active_user):
    """Return authenticated DRF API client and the user"""
    client = APIClient()
    client.force_authenticate(user=sample_active_user)
    return client, sample_active_user

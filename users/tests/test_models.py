from conftest import RAW_PASSWORD


def test_active_user(sample_active_user):
    user = sample_active_user

    assert user.username == "active_user"
    assert user.email == "active_user@email.com"
    # Passwords being hashed
    assert user.check_password(RAW_PASSWORD) is True
    assert user.is_active is True
    assert str(user) == user.email or user.username or f"User- {user.pk}"


def test_inactive_user(sample_inactive_user):
    user = sample_inactive_user

    assert user.email == "inactive_user@email.com"
    assert not user.is_active

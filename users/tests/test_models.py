from conftest import RAW_PASSWORD


def test_user_active(sample_active_user):
    user = sample_active_user

    assert user.email == "active_user@email.com"
    assert user.check_password(RAW_PASSWORD) is True
    assert user.is_active is True


def test_user_inactive(sample_inactive_user):
    user = sample_inactive_user

    assert user.email == "inactive_user@email.com"
    assert user.check_password(RAW_PASSWORD) is True
    assert not user.is_active

def test_user_active(create_active_user):
    user = create_active_user

    assert user.email == "active_user@email.com"
    assert user.check_password("123!@#QWE") is True
    assert user.is_active is True


def test_user_inactive(create_inactive_user):
    user = create_inactive_user

    assert user.email == "inactive_user@email.com"
    assert user.check_password("123!@#QWE") is True
    assert not user.is_active

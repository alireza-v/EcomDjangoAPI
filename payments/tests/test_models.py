def test_payment_model(
    sample_payment,
    sample_active_user,
    sample_order,
):
    assert sample_payment.user == sample_active_user
    assert str(sample_payment) == f"Payment for {sample_order}"

from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/",
        views.PaymentRequestAPIView.as_view(),
        name="create-payment",
    ),
    path(
        "callback/",
        views.PaymentVerifyAPIView.as_view(),
        name="payment-callback",
    ),
    path(
        "list/",
        views.PaymentHistoryAPIView.as_view(),
        name="payment-history",
    ),
]

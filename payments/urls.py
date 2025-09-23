from django.urls import path

from payments import views

urlpatterns = [
    path(
        "create/",
        views.PaymentRequest.as_view(),
        name="create-payment",
    ),
    path(
        "callback/",
        views.PaymentCallback.as_view(),
        name="payment-callback",
    ),
    path("list/", views.PaymentHistoryAPIView.as_view(), name="payment-history"),
]

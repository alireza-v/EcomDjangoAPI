from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.CheckoutAPIView.as_view(),
        name="checkout",
    ),
    path(
        "invoice/",
        views.InvoiceAPIView.as_view(),
        name="invoice-list",
    ),
]

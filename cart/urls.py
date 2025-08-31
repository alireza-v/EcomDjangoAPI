from django.urls import path

from cart import views

urlpatterns = [
    path(
        "cart/",
        views.CartListCreateAPIView.as_view(),
        name="cart-list-create",
    ),
    path(
        "cart/clear/",
        views.ClearCartAPIView.as_view(),
        name="cart-clear",
    ),
    path(
        "",
        views.CheckoutAPIView.as_view(),
        name="checkout",
    ),
    path(
        "orders/",
        views.OrderListAPIView.as_view(),
        name="order-list",
    ),
]

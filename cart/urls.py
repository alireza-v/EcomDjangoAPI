from django.urls import path

from . import views

urlpatterns = [
    path(
        "cart/",
        views.CartCreateAPIView.as_view(),
        name="cart-create",
    ),
    path(
        "cart/drop/",
        views.CartDropAPIView.as_view(),
        name="cart-drop",
    ),
    path(
        "carts/",
        views.CartListAPIView.as_view(),
        name="cart-list",
    ),
    path(
        "",
        views.CheckoutAPIView.as_view(),
        name="checkout",
    ),
]

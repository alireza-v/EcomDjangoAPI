from django.urls import path

from cart import views

urlpatterns = [
    path(
        "cart/",
        views.CartCreateAPIView.as_view(),
        name="cart-create",
    ),
    path(
        "cart/drop/",
        views.ClearCartAPIView.as_view(),
        name="cart-drop",
    ),
    path(
        "carts/",
        views.ShoppingCartListAPIView.as_view(),
        name="cart-list",
    ),
    path(
        "",
        views.CheckoutAPIView.as_view(),
        name="checkout",
    ),
]

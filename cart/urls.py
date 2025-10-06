from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.CartListCreateAPIView.as_view(),
        name="cart-list-create",
    ),
    path(
        "cart/clear/",
        views.ClearCartAPIView.as_view(),
        name="cart-clear",
    ),
]

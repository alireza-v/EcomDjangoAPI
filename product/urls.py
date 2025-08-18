from django.urls import path

from product import views

urlpatterns = [
    # products
    path(
        "",
        views.ProductListAPIView.as_view(),
        name="product-list-api",
    ),
    path(
        "detail/<str:slug>/",
        views.ProductDetailAPIView.as_view(),
        name="product-detail-api",
    ),
    # feedbacks
    path(
        "feedbacks/",
        views.FeedbackCreateAPIView.as_view(),
        name="create-feedback",
    ),
    # likes
    path("likes/", views.LikeToggleCreateAPIView.as_view(), name="like-toggle"),
]

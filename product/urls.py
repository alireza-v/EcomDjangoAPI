from django.urls import path

from . import views

urlpatterns = [
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
    path(
        "feedbacks/",
        views.FeedbackCreateAPIView.as_view(),
        name="create-feedback",
    ),
    path(
        "likes/",
        views.LikeToggleCreateAPIView.as_view(),
        name="like-toggle",
    ),
]

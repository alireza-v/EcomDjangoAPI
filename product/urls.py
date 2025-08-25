from django.urls import path

from product import views

urlpatterns = [
    path(
        "",
        views.ProductListAPIView.as_view(),
        name="product-list-api",
    ),
    path(
        "categories/",
        views.CategoryListAPIView.as_view(),
        name="category-list-api",
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
    path(
        "<str:slug>/",
        views.ProductDetailAPIView.as_view(),
        name="product-detail-api",
    ),
]

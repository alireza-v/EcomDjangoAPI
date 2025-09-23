from django.urls import path

from product import views

urlpatterns = [
    path(
        "",
        views.ProductListAPIView.as_view(),
        name="product-list",
    ),
    path(
        "categories/",
        views.CategoryListAPIView.as_view(),
        name="category-list",
    ),
    path(
        "<int:product_id>/feedbacks/",
        views.FeedbackListCreateAPIView.as_view(),
        name="list-create-feedback",
    ),
    path(
        "likes/",
        views.LikeToggleCreateAPIView.as_view(),
        name="like-toggle",
    ),
    path(
        "info/<str:slug>/",
        views.ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
]

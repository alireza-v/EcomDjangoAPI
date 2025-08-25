from django.contrib import admin

from product.models import (
    Category,
    FeatureValue,
    Feedback,
    Like,
    Product,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "parent",
        "visit_count",
        "slug",
    ]
    readonly_fields = ["visit_count", "slug"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "main_image",
        "category",
        "visit_count",
        "slug",
    ]
    readonly_fields = ["visit_count", "slug"]


@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "feature",
        "value",
    ]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "product",
        "description",
        "rating",
    ]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "product"]

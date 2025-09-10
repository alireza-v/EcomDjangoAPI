from django.contrib import admin

from product.models import (
    Category,
    FeatureName,
    FeatureValue,
    Feedback,
    Like,
    Product,
    ProductImage,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "parent",
        "visit_count",
        "slug",
    ]
    fields = ["title", "parent"]
    readonly_fields = ["visit_count", "slug"]


class FeatureInline(admin.TabularInline):
    model = FeatureValue
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    can_delete = False
    readonly_fields = [
        "user",
        "product",
        "description",
        "rating",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        FeatureInline,
        ProductImageInline,
        FeedbackInline,
    ]
    search_fields = ["title", "brand"]
    list_filter = ["created_at", "price"]
    ordering = ["-created_at"]

    list_display = [
        "title",
        "price_formatter",
        "category",
        "main_image",
        "brand",
        "feature_list",
        "short_description",
        "visit_count",
        "stock",
    ]
    fields = [
        "title",
        "category",
        "main_image",
        "price",
        "description",
        "stock",
        "brand",
    ]
    readonly_fields = ["visit_count", "slug"]

    class Media:
        js = ["admin/js/price_format.js"]

    @admin.display(description="ویژگی ها")
    def feature_list(self, obj):
        return ", ".join(
            [f"{fv.feature.name}: {fv.value}" for fv in obj.product_features.all()]
        )

    @admin.display(description="قیمت")
    def price_formatter(self, obj):
        return obj.price_formatter

    @admin.display(description="توضیحات")
    def short_description(self, obj):
        return obj.description[:20]


@admin.register(FeatureName)
class FeatureNameAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    list_filter = ["created_at", "name"]


@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "feature",
        "value",
    ]
    autocomplete_fields = ["feature"]

from django.db.models import Q
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer

from product.models import *


class BaseSerializer(ModelSerializer):
    """
    Base serializer that removes fields with null values from the API response
    """

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {k: v for k, v in rep.items() if v is not None}


class FeatureValueSerializer(ModelSerializer):
    feature = serializers.StringRelatedField()

    class Meta:
        model = FeatureValue
        fields = [
            "feature",
            "value",
        ]


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductSerializer(BaseSerializer):
    price = serializers.ReadOnlyField(source="price_formatter")
    parent = serializers.StringRelatedField(source="category")
    features = FeatureValueSerializer(
        source="feature_values",
        many=True,
        read_only=True,
    )
    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "parent",
            "price",
            "main_image",
            "images",
            "description",
            "visit_count",
            "features",
        ]


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "products_per_page"
    max_page_size = 20


class CategorySerializer(ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "slug",
            "subcategories",
            "products",
        ]

    def get_subcategories(self, obj):
        if hasattr(obj, "subcategories"):
            return CategorySerializer(
                obj.subcategories.all(),
                many=True,
                context=self.context,
            ).data
        return []

    def get_products(self, obj):
        if obj.subcategories.exists():
            return []

        context = self.context

        # query params
        search_param = context.get("search")
        sort_params = context.get("sorted")
        max_price = context.get("max_price")
        min_price = context.get("min_price")

        product_qs = obj.products.all()

        try:
            min_price = float(min_price.replace(",", "")) if min_price else None
            max_price = float(max_price.replace(",", "")) if max_price else None
        except ValueError:
            min_price, max_price = None, None

        # search
        if search_param:
            product_qs = product_qs.filter(
                Q(title__icontains=search_param)
                | Q(description__icontains=search_param),
            )
            if not product_qs.exists():
                return product_qs.none()

        # price filtering
        if min_price:
            product_qs = product_qs.filter(price__gte=min_price)

        if max_price:
            product_qs = product_qs.filter(price__lte=max_price)

        # return empty list if no results found
        if (min_price or max_price) and not product_qs.exists():
            return []

        # sorting
        if sort_params == "price_asc":
            product_qs = product_qs.order_by("price")
        elif sort_params == "price_desc":
            product_qs = product_qs.order_by("-price")
        elif sort_params == "most_visited":
            product_qs = product_qs.order_by("-visit_count")

        else:
            # sorting fallback
            product_qs = product_qs.order_by("-visit_count")

        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(
            product_qs, self.context["request"]
        )
        serialized_products = ProductSerializer(
            paginated_products,
            many=True,
            context=self.context,
        )

        return {
            "count": product_qs.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serialized_products.data,
        }


class ProductFeatureSerializer(ModelSerializer):
    class Meta:
        model = FeatureValue
        fields = [
            "product",
            "feature",
            "value",
        ]


class CategoryBreadcrumbSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "slug",
        ]


class FeedbackSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    product_value = serializers.SerializerMethodField()
    rating = serializers.IntegerField(
        help_text="Rating from 1 to 5 stars",
        min_value=1,
        max_value=5,
    )

    class Meta:
        model = Feedback
        fields = [
            "description",
            "rating",
            "user",
            "product",
            "product_value",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }

    def get_product_value(self, obj):
        if obj.product:
            return {
                "id": obj.product.id,
                "title": obj.product.title,
                "price": f"{obj.product.price:,.0f}",
            }
        return None

    def validate(self, data):
        user = self.context["request"].user
        product = data.get("product")

        if Feedback.objects.filter(
            user=user,
            product=product,
        ).exists():
            raise serializers.ValidationError("You already made a review.")
        return data


class LikeSerializer(ModelSerializer):
    user = serializers.StringRelatedField()
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
    )
    product_related = serializers.StringRelatedField(source="product")

    class Meta:
        model = Like
        fields = [
            "user",
            "product",
            "product_related",
        ]

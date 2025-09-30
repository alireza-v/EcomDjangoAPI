from django.db import IntegrityError, transaction
from django.db.models import Avg, F, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    filters,
    generics,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from product.filters import ProductFilter
from product.models import (
    Category,
    Feedback,
    Like,
    Product,
)
from product.ordering import CustomOrderingFilter
from product.pagination import FeedbackPagination, ProductPagination
from product.serializers import (
    CategorySerializer,
    FeedbackSerializer,
    LikeSerializer,
    ProductDetailSerializer,
    ProductSerializer,
)


class ProductListAPIView(generics.ListAPIView):
    """
    Fetch categories by slug
    Products filtering:
        - min_price
        - max_price
        - in_stock
        - brand
        - has_discount
    Paginated lists of products
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [
        DjangoFilterBackend,
        CustomOrderingFilter,
    ]
    filterset_class = ProductFilter
    ordering_fields = [
        "price",
        "visit_count",
        "created_at",
    ]
    ordering = ["-visit_count"]

    def get_queryset(self):
        """
        Return products under the given  category by the given slug
        Example: ?category = <str:slug>
        """

        qs = Product.objects.annotate(avg_rating=Avg("product_feedbacks__rating"))

        query = self.request.query_params.get("q", "")
        category_slug = self.request.query_params.get("category", "")

        # search products using title, slug, category title
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(slug__icontains=query)
                | Q(category__title__icontains=query)
            )

        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        return qs

    @swagger_auto_schema(
        operation_summary="Product list",
        manual_parameters=[
            openapi.Parameter(
                name="q",
                in_=openapi.IN_QUERY,
                description="Seach products",
                type=openapi.TYPE_STRING,
                example="laptop",
            ),
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Category info by given slug",
                required=False,
                example="electronics",
            ),
            openapi.Parameter(
                name="max_price",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Filter products by max_price",
                required=False,
            ),
            openapi.Parameter(
                name="min_price",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Filter products by min_price",
                required=False,
            ),
            openapi.Parameter(
                name="ordering",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Sorted by price | visit_count | created_at",
                required=False,
                example="-created_at",
            ),
            openapi.Parameter(
                "in_stock",
                openapi.IN_QUERY,
                description="Filter by stock availability",
                type=openapi.TYPE_BOOLEAN,
                example=True,
            ),
            openapi.Parameter(
                "brand",
                openapi.IN_QUERY,
                description="Filter by brand",
                type=openapi.TYPE_STRING,
                example="samsung",
            ),
            openapi.Parameter(
                "has_discount",
                openapi.IN_QUERY,
                description="Only show discounted products",
                type=openapi.TYPE_BOOLEAN,
                example=True,
            ),
        ],
        tags=["Product"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryListAPIView(generics.ListAPIView):
    """
    Return list of top-level categories (parent=null) with prefetching of subcategories and products
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).prefetch_related(
            "subcategories__products",
        )

    @swagger_auto_schema(
        operation_summary="Category list",
        operation_description="Retrieve top-level categories along with subcategories and products",
        responses={
            200: CategorySerializer(many=True),
        },
        tags=["Product"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    - Retrieve product details using product slug
    - Increment visit counts if called atomically
    """

    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @swagger_auto_schema(
        operation_summary="Product Detail",
        operation_description="Fetch product details using the slug. Visit count incremented atomically",
        manual_parameters=[
            openapi.Parameter(
                name="slug",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Product slug",
                required=True,
            ),
        ],
        responses={
            200: ProductSerializer,
            404: openapi.Response(description="Product not found"),
            400: openapi.Response(
                description="Transaction rolled back due to an error"
            ),
        },
        tags=["Product"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get("slug")
        try:
            with transaction.atomic():
                instance = (
                    self.get_queryset()
                    .select_for_update()
                    .get(
                        slug=slug,
                    )
                )
                instance.visit_count = F("visit_count") + 1
                instance.save(update_fields=["visit_count"])
                instance.refresh_from_db()

            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except IntegrityError:
            return Response(
                {"detail": "Transaction rolled back due to an error"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeedbackListCreateAPIView(generics.ListCreateAPIView):
    """
    List & Create feedbacks using product_id
    """

    serializer_class = FeedbackSerializer
    pagination_class = FeedbackPagination
    filter_backends = [
        filters.OrderingFilter,
    ]
    ordering_fields = [
        "created_at",
        "rating",
    ]
    ordering = ["-rating"]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")

        return Feedback.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        serializer.save(
            user=self.request.user,
            product=product,
        )

    def get_permissions(self):
        """
        Authentication required only for POST requests
        """
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List feedbacks",
        operation_description="List feedbacks using product_id",
        manual_parameters=[
            openapi.Parameter(
                name="product_id",
                in_=openapi.IN_PATH,
                description="Fetch product instance using its id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: FeedbackSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Feedback"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Feedback",
        operation_description="Submit feedback for a product using its ID.",
        request_body=FeedbackSerializer,
        responses={
            201: FeedbackSerializer,
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Feedback"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LikeToggleCreateAPIView(APIView):
    """
    Like & Unlike a product
    """

    serializer_class = LikeSerializer

    @swagger_auto_schema(
        operation_summary="Like toggler",
        operation_description="Toggle like/unlike for a product",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product"],
            properties={
                "product": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the product to like/unlike",
                ),
            },
        ),
        responses={
            200: openapi.Response("Like removed"),
            201: openapi.Response("Like created", LikeSerializer),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Product not found"),
        },
        tags=["Product Likes"],
    )
    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        user = request.user

        if not product_id:
            return Response(
                {"detail": "Product ID required"}, status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(
            Product,
            pk=product_id,
        )
        like, created = Like.objects.get_or_create(
            user=user,
            product=product,
        )
        if not created:
            like.delete()
            return Response(
                {
                    "detail": "Like removed",
                },
                status=status.HTTP_200_OK,
            )
        serializer = LikeSerializer(like)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_summary="List user likes",
        operation_description="Retrieve list of all products liked by authenticated user",
        responses={
            200: openapi.Response(
                description="List of likes",
                schema=LikeSerializer(many=True),
            ),
            401: openapi.Response(
                description="Unauthorized",
            ),
        },
        tags=["Product Likes"],
    )
    def get(self, request, *args, **kwargs):
        qs = Like.objects.filter(user=request.user)
        serializer = self.serializer_class(qs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

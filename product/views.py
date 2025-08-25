from django.db import IntegrityError, transaction
from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from product.filters import ProductFilter
from product.models import Category, Like, Product
from product.pagination import ProductPagination
from product.serializers import (
    CategorySerializer,
    FeedbackSerializer,
    LikeSerializer,
    ProductSerializer,
)


class ProductListAPIView(generics.ListAPIView):
    """
    Fetched categories using slug
    Products filtered by max_price | min_price
    Paginated lists of products
    Products sorted by price | visit_count | created_at
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    ordering_fields = [
        "price",
        "visit_count",
        "created_at",
    ]

    def get_queryset(self):
        """
        Return products by category slug passed as query param:
        ?category=<str:slug>
        """
        qs = Product.objects.annotate(avg_rating=Avg("feedbacks__rating"))
        category_slug = self.request.query_params.get("category")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Category info by given slug",
                required=False,
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
    Retrieve product details by slug and increment visit counts
    """

    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @swagger_auto_schema(
        operation_summary="Product Detail",
        operation_description="Retrieve product details using the slug. Visit count incremented atomically",
        manual_parameters=[
            openapi.Parameter(
                name="slug",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Slug of the product",
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


class FeedbackCreateAPIView(generics.CreateAPIView):
    """
    Create feedbacks on selected product using product id
    """

    serializer_class = FeedbackSerializer

    @swagger_auto_schema(
        operation_summary="Create Feedback",
        operation_description="Submit feedback for a product using its ID.",
        request_body=FeedbackSerializer,
        responses={
            201: FeedbackSerializer,
            400: "Bad request",
        },
        tags=["Feedback"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeToggleCreateAPIView(APIView):
    """
    Like & Unlike a product
    """

    @swagger_auto_schema(
        operation_id="Toggle likes",
        operation_summary="Like toggler",
        operation_description="Toggle like/unlike for a product.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product"],
            properties={
                "product": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the product to like/unline",
                ),
            },
        ),
        responses={
            200: openapi.Response("Like removed"),
            201: openapi.Response("Like created", LikeSerializer),
            400: "Bad request",
            404: "Product not found",
        },
        tags=["Likes"],
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

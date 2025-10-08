from django.db import IntegrityError, transaction
from django.db.models import Avg, F, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..filters import ProductFilter
from ..models import Category, Product
from ..ordering import CustomOrderingFilter
from ..pagination import ProductPagination
from ..serializers import CategorySerializer, ProductDetailSerializer, ProductSerializer


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
    Return list of top-level categories (null parents) with prefetching of subcategories
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).prefetch_related(
            "subcategories__products",
        )

    @swagger_auto_schema(
        operation_summary="List categories",
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

    @transaction.atomic
    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get("slug")
        try:
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

from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from product import serializers

from .models import Category, Like, Product
from .serializers import LikeSerializer


def custom_404_view(request, exception):
    return JsonResponse(
        {"detail": "صفحه مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND
    )


class ProductListAPIView(generics.ListAPIView):
    """
    Retrieve a list of products.

    - If a product slug is provided, returns products under that category.
    - Supports filtering and sorting via query parameters.
    """

    serializer_class = serializers.CategorySerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search products",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "selected",
                openapi.IN_QUERY,
                description="Slug of the selected category",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "sorted",
                openapi.IN_QUERY,
                description="Sort order: 'price_asc', 'price_desc', or default (visit count desc)",
                type=openapi.TYPE_STRING,
                enum=["price_asc", "price_desc"],
            ),
            openapi.Parameter(
                "min_price",
                openapi.IN_QUERY,
                description="Minimum price filter",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "max_price",
                openapi.IN_QUERY,
                description="Maximum price filter",
                type=openapi.TYPE_NUMBER,
            ),
        ],
        tags=["Product"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Fetch subcategories/products using the prefetched PK.
        """

        selected_slug = self.request.query_params.get("selected")
        if selected_slug:
            category = get_object_or_404(
                Category,
                slug=selected_slug,
            )
            return Category.objects.filter(
                pk=category.pk,
            ).prefetch_related(
                "subcategories__products",
                "products",
            )

        # return most popular ones
        return (
            Category.objects.filter(
                parent__isnull=True,
            )
            .prefetch_related(
                "subcategories__products",
            )
            .order_by("-visit_count")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()

        params = self.request.query_params

        context["search"] = params.get("search")
        context["sorted"] = params.get("sorted")
        context["min_price"] = params.get("min_price")
        context["max_price"] = params.get("max_price")

        return context


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @swagger_auto_schema(
        operation_summary="Product detail",
        operation_description="Product details using the slug",
        manual_parameters=[
            openapi.Parameter(
                name="slug",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Slug of the product",
                required=True,
            ),
        ],
        tags=["Product"],
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Lock the row until transaction ends
                instance = (
                    self.get_queryset()
                    .select_for_update()
                    .get(
                        slug=kwargs["slug"],
                    )
                )
                instance.visit_count = F("visit_count") + 1
                instance.save(
                    update_fields=["visit_count"],
                )
                instance.refresh_from_db()

            serializer = self.get_serializer(instance)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except IntegrityError:
            return Response(
                {
                    "detail": "Transaction rolled back due to error.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeedbackCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FeedbackSerializer

    @swagger_auto_schema(
        operation_summary="Create feedback",
        operation_description="Authenticated users can submit feedback using the product ID.",
        request_body=serializers.FeedbackSerializer,
        responses={
            201: serializers.FeedbackSerializer(many=True),
            400: "Bad Request",
            401: "Authentication credentials were not provided.",
        },
        tags=["Feedback"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeToggleCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
                {"detail": "Product ID required."}, status=status.HTTP_400_BAD_REQUEST
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

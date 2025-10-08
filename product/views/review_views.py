from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Feedback, Like, Product
from ..pagination import FeedbackPagination
from ..serializers import (
    FeedbackSerializer,
    LikeSerializer,
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
        Authentication required only for POST method
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

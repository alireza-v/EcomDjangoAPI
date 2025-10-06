from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CartItem
from .serializers import CartSerializer


class CartListCreateAPIView(generics.ListCreateAPIView):
    """
    List & Create user cart items using the given product ID
    """

    serializer_class = CartSerializer

    def get_queryset(self):
        """
        Return user specific cart associated with related products sorted by latest ones
        """
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__product_features__feature")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Fetch cart items",
        operation_description="Return list of user cart items",
        responses={
            401: openapi.Response(description="Unauthorized"),
            200: CartSerializer(many=True),
        },
        tags=["Cart"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add products to cart",
        operation_description="Add & remove products from cart",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["add", "remove"]
                ),
                "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, min=1, max=5),
            },
            required=["product_id"],
            example={
                "action": "add",
                "product_id": 42,
            },
        ),
        responses={
            201: CartSerializer(),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ClearCartAPIView(APIView):
    """
    Clear user cart items
    """

    @swagger_auto_schema(
        operation_summary="Clear user cart",
        operation_description="Remove cart items",
        responses={
            204: openapi.Response(description="Cart dropped successfully"),
            200: openapi.Response(description="Cart already empty"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Cart"],
    )
    def delete(self, request, *args, **kwargs):
        deleted, _ = CartItem.objects.filter(user=request.user).delete()

        if deleted:
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {
                "detail": "Cart already empty",
            },
            status=status.HTTP_200_OK,
        )

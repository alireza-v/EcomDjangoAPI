from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CartItem,
    Order,
    OrderItem,
)
from .serializers import CartItemSerializer


class CartCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    @swagger_auto_schema(
        operation_summary="Create cart items",
        operation_description="Create cart items using product ID",
        request_body=CartItemSerializer,
        responses={
            201: CartItemSerializer(),
            401: "Unauthorized",
            400: "Bad request",
        },
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartDropAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Clear user cart",
        operation_description="Deletes all cart items for the authenticated user.",
        responses={
            204: openapi.Response(
                description="Cart dropped successfully — no content returned",
            ),
            400: openapi.Response(
                description="Cart already empty.",
            ),
        },
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        carts = CartItem.objects.filter(user=user)

        if carts.exists():
            carts.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {
                "detail": "Cart already empty.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CartListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()

    @swagger_auto_schema(
        operation_summary="Cart list",
        operation_description="Display user cart items",
        responses={
            200: CartItemSerializer(many=True),
            401: "Unauthorized",
        },
        tags=["Cart"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CheckoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Checkout and create an order",
        operation_description=(
            "Takes all items from the authenticated user's cart, "
            "checks stock availability, creates an order and order items, "
            "updates product stock, and clears the cart. "
            "If stock is insufficient or cart is empty, returns an error."
        ),
        responses={
            201: openapi.Response(
                description="Order successfully created",
                examples={
                    "application/json": {
                        "detail": "Order created with success!",
                        "order_id": 1,
                        "status": "pending",
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request - cart empty or insufficient stock",
                examples={
                    "application/json": {"detail": "Not enough stock for Product A"}
                },
            ),
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.select_related("product").filter(user=user)

        if not cart_items.exists():
            return Response(
                {
                    "detail": "Cart is empty",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=user,
        )
        for cart in cart_items:
            product = cart.product

            if product.stock < cart.quantity:
                return Response(
                    {"detail": f"Not enough stock for {product.title}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product.stock -= cart.quantity
            product.save()

            # create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart.quantity,
                price_at_purchase=product.price,
            )

        # clear cart
        cart_items.delete()

        return Response(
            {
                "detail": "Order created with success!",
                "order_id": order.id,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )

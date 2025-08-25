from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import CartItem, Order, OrderItem
from cart.serializers import CartItemSerializer


class CartCreateAPIView(generics.CreateAPIView):
    """Create cart items"""

    permission_classes = [IsAuthenticated]
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


class ClearCartAPIView(APIView):
    """
    Allow authenticated users to clear all items from their cart
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Clear user cart",
        operation_description="Deletes all cart items for the authenticated user.",
        responses={
            204: openapi.Response(
                description="Cart dropped successfully — no content returned",
            ),
            200: openapi.Response(
                description="Cart already empty",
            ),
        },
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        user_cart_contents = CartItem.objects.filter(user=request.user)

        if user_cart_contents.exists():
            user_cart_contents.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {
                "detail": "Cart already empty",
            },
            status=status.HTTP_200_OK,
        )


class ShoppingCartListAPIView(generics.ListAPIView):
    """
    Retrieves list of cart items associated with the authenticated user
    """

    serializer_class = CartItemSerializer

    @swagger_auto_schema(
        operation_summary="Car list",
        operation_description="Display user cart items",
        responses={
            200: CartItemSerializer(many=True),
            401: "Unauthorized",
        },
        tags=["Cart"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CheckoutAPIView(APIView):
    """Start checkout process"""

    @swagger_auto_schema(
        operation_summary="Checkout and create an order",
        operation_description=(
            "Takes all items from the authenticated user's cart, ",
            "checks stock availability, creates an order and order items, ",
            "updates product stock, and clears the cart. ",
            "If stock is insufficient or cart is empty, returns an error.",
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
        user_shopping_cart = CartItem.objects.select_related("product").filter(
            user=request.user
        )

        if not user_shopping_cart.exists():
            return Response(
                {
                    "detail": "Cart is empty",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=request.user,
        )
        for cart in user_shopping_cart:
            product = cart.product

            if product.stock < cart.quantity:
                return Response(
                    {
                        "detail": f"Not enough stock for {product.title}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product.stock -= cart.quantity
            product.save()

            # create order-item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart.quantity,
                price_at_purchase=product.price,
            )

        # reset cart
        user_shopping_cart.delete()

        return Response(
            {
                "detail": "Order created with success!",
                "order_id": order.id,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )

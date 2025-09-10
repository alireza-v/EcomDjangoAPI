from django.db import transaction
from django.db.models import F, Prefetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import (
    CartItem,
    Order,
    OrderItem,
)
from cart.serializers import (
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
)


class CartListCreateAPIView(generics.ListCreateAPIView):
    """
    List & Create user cart items using the given product ID
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        """
        Return user specific cart associated with the related products sorted by the latest ones
        """
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__product_features__feature")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Get user cart items",
        operation_description="Returns list of current user's cart items with product info",
        responses={
            200: CartSerializer(many=True),
        },
        tags=["Cart"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add or remove items in cart",
        operation_description="Add a product to the cart or remove the products quantity ",
        request_body=CartSerializer,
        responses={
            201: CartSerializer(),
            400: "Validation error",
        },
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ClearCartAPIView(APIView):
    """
    Clear user cart items
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Clear user cart",
        operation_description="Deletes cart items for at once.",
        responses={
            204: openapi.Response(description="Cart dropped successfully"),
            200: openapi.Response(
                description="Cart already empty",
            ),
        },
        tags=["Cart"],
    )
    def delete(self, request, *args, **kwargs):
        deleted, _ = CartItem.objects.filter(user=request.user).delete()

        # Number of objects being deleted
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


class CheckoutAPIView(APIView):
    """
    Start the checkout process with partial fulfillment support
    Functionality:
        1. Fetch user cart items
        2. Compare cart item quantities to available product stock
        3. Create an order instance for the user
        4. Create order item instance from the cart items that have sufficient stock
        5. Deduct stock for processed items and remove related cart items and product stock value
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    @swagger_auto_schema(
        operation_summary="Start checkout process",
        operation_description=(
            "User cart info turned into order"
            "Only items with sufficient stock are included"
            "Stock is reduced for processed items, and they are removed from the cart"
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["address"],
            properties={
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Shipping address for the order",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Order created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Order status"
                        ),
                        "items": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "product": openapi.Schema(type=openapi.TYPE_STRING),
                                    "quantity": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "price": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                            description="Processed items in the order",
                        ),
                        "skipped_items": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Items skipped due to insufficient stock (optional)",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Cart empty or out of stock",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING),
                        "items": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Items that could not be processed",
                        ),
                    },
                ),
            ),
        },
        tags=["Cart"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipping_address = serializer.validated_data["address"]

        # Access user cart related products
        active_cart_items = (
            CartItem.objects.select_related("product")
            .select_for_update()
            .filter(user=request.user)
        )

        if not active_cart_items.exists():
            return Response(
                {"detail": "No user cart found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_total = 0
        insufficient_stock = []  # products with no stock
        valid_items = []

        for cart in active_cart_items:
            product = cart.product

            # collect cart items with insufficient stock and skip them
            if cart.quantity > product.stock:
                insufficient_stock.append(f"{product.title} out of stock")
                continue

            # total products amount
            order_total += product.price * cart.quantity
            valid_items.append(cart)

        if not valid_items:
            return Response(
                {
                    "detail": insufficient_stock,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=order_total,
        )

        order_items = []
        processed_products = []

        for cart in valid_items:
            product = cart.product
            quantity = cart.quantity

            product.stock = F("stock") - quantity
            product.save(update_fields=["stock"])
            product.refresh_from_db()

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price,
                )
            )
            processed_products.append(product)
        OrderItem.objects.bulk_create(order_items)

        CartItem.objects.filter(
            user=request.user, product__in=processed_products
        ).delete()

        response_data = {
            "detail": "Order created!",
            "status": order.status,
            "items": [
                {
                    "product": item.product.title,
                    "quantity": item.quantity,
                    "price": f"{item.price_at_purchase:,.0f}",
                }
                for item in order_items
            ],
        }

        if insufficient_stock:
            response_data["skipped_items"] = insufficient_stock

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class OrderListAPIView(generics.ListAPIView):
    """
    List user related orders and order items
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Fetch OrderItem nested info relation including orders and products filtered by current authenticated user
        """
        return Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "order_items", queryset=OrderItem.objects.select_related("product")
            )
        )

    @swagger_auto_schema(
        operation_summary="List user orders",
        operation_description="Returns user orders with detailed info",
        responses={
            200: OrderSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Orders"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

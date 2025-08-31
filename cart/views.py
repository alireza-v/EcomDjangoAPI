from django.db import transaction
from django.db.models import F, Prefetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import CartItem, Order, OrderItem
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
        Return last created cart item
        """
        cart = CartItem.objects.filter(user=self.request.user).select_related("product")
        return cart.order_by("-created_at")

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
    Clear user cart
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


class CheckoutAPIView(APIView):
    """
    Start the checkout process with partial fulfillment support

    Function:

    1. Fetch active cart items for the authenticated user
    2. Compare cart item quantities to available product stock
    3. Create an Order instance for the user
    4. Create OrderItem instances from the cart items that have sufficient stock
    5. Deduct stock for processed items and remove them from the cart
    6. Return a response indicating processed and skipped items
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    @swagger_auto_schema(
        operation_summary="Start checkout process",
        operation_description=(
            "Processes the authenticated user's cart items into an Order and OrderItems "
            "Only items with sufficient stock are included "
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
                description="Order created ",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "order_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="ID of the created order",
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
                description="Cart empty or all items have insufficient stock",
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

        # user cart items
        active_cart_items = (
            CartItem.objects.select_related("product")
            .select_for_update()
            .filter(user=request.user)
        )

        # raise error if no related cart found
        if not active_cart_items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        insufficient_stock = []
        order_total = 0
        valid_order_items = []

        for cart in active_cart_items:
            product = cart.product

            # collect cart items with insufficient stock and skip them
            if product.stock < cart.quantity:
                insufficient_stock.append(
                    f"{product.title} (available: {product.stock}, requested: {cart.quantity})"
                )
                continue

            # total products amount
            order_total += product.price * cart.quantity
            valid_order_items.append(
                {
                    "product": product,
                    "quantity": cart.quantity,
                    "price_at_purchase": product.price,
                }
            )

        if not valid_order_items:
            return Response(
                {
                    "detail": "Insufficient amount in stock",
                    "items": insufficient_stock,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=order_total,  # total prices
        )

        order_items = []
        for item in valid_order_items:
            product = item["product"]
            quantity = item["quantity"]

            product.stock = F("stock") - quantity
            product.save(update_fields=["stock"])
            product.refresh_from_db()

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=item["price_at_purchase"],
                )
            )
        OrderItem.objects.bulk_create(order_items)

        processed_products = [item["product"] for item in valid_order_items]

        CartItem.objects.filter(
            user=request.user,
            product__in=processed_products,
        ).delete()

        response_data = {
            "detail": "Order created!",
            "order_id": order.id,
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
    List all orders of the authenticated user along with associated order items.
    Each order includes its items and product details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "order_items", queryset=OrderItem.objects.select_related("product")
            )
        )

    @swagger_auto_schema(
        operation_summary="List user orders",
        operation_description="Returns all orders for the authenticated user with detailed order items",
        responses={
            200: OrderSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Orders"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

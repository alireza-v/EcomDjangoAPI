from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.utils import get_cart_items
from orders.models import Order
from orders.serializers import CheckoutSerializer, OrderSerializer
from orders.utils import create_order


class CheckoutAPIView(APIView):
    """
    Start the checkout process with partial fulfillment support

    Functionality:
        1. Fetch user cart items
        2. Compare cart item quantities against the stock
        3. Create both order and order_item instances if validated
        5. Deduct stock and clear user cart
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    @swagger_auto_schema(
        operation_summary="Start checkout process",
        operation_description="Fetch cart information and create an invoice",
        request_body=CheckoutSerializer(),
        responses={
            400: openapi.Response("Cart empty or out of stock"),
            401: openapi.Response("Unauthorized"),
            201: openapi.Response(
                description="Order created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "result": openapi.Schema(
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
        },
        tags=["Order"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipping_address = serializer.validated_data["address"]

        cart_items, errors = get_cart_items(user=request.user)

        if not cart_items:
            return Response(
                {
                    "out of stock": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order, order_items = create_order(
            user=request.user,
            shipping_address=shipping_address,
            cart_items=cart_items,
        )
        response_data = {
            "result": "Order created",
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
        if errors:
            response_data["skipped_items"] = errors

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class InvoiceAPIView(generics.ListAPIView):
    """
    List user related orders and order items
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Fetch OrderItem nested info relation including orders and products filtered by current authenticated user
        """
        order = Order.objects.filter(user=self.request.user)
        qs = order.prefetch_related("order_items__product")
        return qs

    @swagger_auto_schema(
        operation_summary="List order invoice",
        operation_description="Returns order invoice with detailed info",
        responses={
            200: OrderSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Order"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

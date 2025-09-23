import os

import requests
from django.db import transaction
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from payments.models import Payment
from payments.serializers import PaymentSerializer

load_dotenv()


class PaymentRequest(APIView):
    permission_classes = [permissions.IsAuthenticated]
    payment_url = "https://gateway.zibal.ir/v1/request"

    @swagger_auto_schema(
        operation_summary="Request payment for pending order",
        operation_description="Return payment url and track id for pending order",
        responses={
            200: openapi.Response(
                description="Payment request successfully created",
            ),
            400: openapi.Response(
                description="No pending order or payment gateway error",
            ),
            401: openapi.Response(description="Unauthorized"),
            502: openapi.Response(
                description="Payment gateway connection error",
            ),
        },
        tags=["Payment"],
    )
    def post(self, request, *args, **kwargs):
        """
        Return payment on pending order
        """
        pending_order = (
            Order.objects.filter(
                user=request.user,
                status=Order.Status.PENDING,
            )
            .prefetch_related("order_items")
            .order_by("-created_at")
            .first()
        )

        if not pending_order:
            return Response(
                {"detail": "No pending order found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_payment = Payment.objects.filter(
            order=pending_order,
            status=Payment.Status.PENDING,
        ).last()

        if existing_payment:
            return Response(
                {
                    "track_id": existing_payment.track_id,
                    "payment_url": f"https://gateway.zibal.ir/start/{existing_payment.track_id}",
                    "message": "Already initiated payment",
                },
                status=status.HTTP_200_OK,
            )

        try:
            response = requests.post(
                url=self.payment_url,
                json={
                    "merchant": os.getenv("ZIBAL_MERCHANT", "zibal"),
                    "amount": int(pending_order.total_amount),
                    "callbackUrl": os.getenv("DOMAIN") + "/api/v1/payments/callback/",
                },
                timeout=10,
            ).json()
        except requests.RequestException as e:
            return Response(
                {
                    "detail": f"Payment gateway error: {str(e)}",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if response["result"] == 100:
            Payment.objects.create(
                order=pending_order,
                user=request.user,
                track_id=response["trackId"],
                amount=pending_order.total_amount,
                raw_response=response,
            )
            return Response(
                {
                    "trackId": response["trackId"],
                    "result": response["result"],
                    "message": response["message"],
                    "payment_url": f"https://gateway.zibal.ir/start/{response['trackId']}",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Payment gateway error",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentCallback(APIView):
    """
    Verify the payment using zibal gateway and update both payment and order status
    """

    verify_url = "https://gateway.zibal.ir/v1/verify"

    @swagger_auto_schema(
        operation_summary="Verify payment callback",
        operation_description="Verify payment with Zibal gateway using the given trackId",
        manual_parameters=[
            openapi.Parameter(
                "trackId",
                openapi.IN_QUERY,
                description="Unique transaction ID returned from Zibal",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Payment verification success",
            ),
            400: openapi.Response(
                description="Payment failed or invalid trackId",
            ),
            502: openapi.Response(
                description="Payment gateway connection error",
            ),
        },
        tags=["Payment"],
    )
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        track_id = request.GET.get("trackId")
        if not track_id:
            return Response(
                {
                    "detail": "trackId required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(
                track_id=track_id,
                status=Payment.Status.PENDING,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "No payment found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify zibal payment
        try:
            response = requests.post(
                self.verify_url,
                json={
                    "merchant": os.getenv("ZIBAL_MERCHANT", "zibal"),
                    "trackId": track_id,
                },
                timeout=10,
            ).json()
        except requests.RequestException as e:
            return Response(
                {
                    "detail": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Success payment
        if response["result"] == 100:
            order = payment.order

            payment.status = "success"
            payment.raw_response = response
            payment.save(update_fields=["status", "raw_response"])

            order.status = Order.Status.PAID
            order.save(update_fields=["status"])

            return Response(
                {
                    "result": "Payment was success",
                },
                status=status.HTTP_200_OK,
            )

        # Already verified
        elif response["result"] == 201:
            order = payment.order
            payment.status = "success"
            payment.raw_response = response
            payment.save(update_fields=["status", "raw_response"])

            order.status = Order.Status.PAID
            order.save(update_fields=["status"])
            return Response(
                {
                    "detail": "Payment success",
                },
                status=status.HTTP_200_OK,
            )
        # Payment failed
        else:
            payment.status = "failed"
            payment.raw_response = response
            payment.save(update_fields=["status", "raw_response"])

            return Response(
                response,
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentHistoryAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related("order")

    @swagger_auto_schema(
        operation_summary="List user payment history",
        operation_description="Returns list of payments associated with authenticated user",
        responses={
            200: PaymentSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Payment"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

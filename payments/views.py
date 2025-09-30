import os
from logging import getLogger

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

logger = getLogger()


class PaymentRequestAPIView(APIView):
    payment_url = os.getenv("ZIBAL_PAYMENT_URL")
    request_payment = os.getenv("ZIBAL_REQUEST_PAYMENT")

    @swagger_auto_schema(
        operation_summary="Request payment for pending order",
        operation_description="Return payment url and track id for pending order",
        request_body=None,
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
            .first()
        )

        if not pending_order:
            return Response(
                {
                    "detail": "No pending order found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_payment = Payment.objects.filter(
            order=pending_order, status=Payment.Status.PENDING
        ).last()

        if existing_payment:
            return Response(
                {
                    "track_id": existing_payment.track_id,
                    "payment_url": self.request_payment
                    + f"/{existing_payment.track_id}",
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
                    "callbackUrl": os.getenv("DOMAIN") + os.getenv("PAYMENT_CALLBACK"),
                },
                timeout=5,
            ).json()
        except requests.RequestException as e:
            return Response(
                {
                    "detail": f"Payment gateway error: {str(e)}",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Success response
        if response["result"] == 100:
            try:
                with transaction.atomic():
                    Payment.objects.create(
                        order=pending_order,
                        user=request.user,
                        track_id=response["trackId"],
                        amount=pending_order.total_amount,
                        raw_response=response,
                    )
            except Exception as e:
                logger.error(
                    f"Failed to persist payment info {response['trackId']}: {str(e)}"
                )
                return Response(
                    {
                        "detail": "Internal error happened while creating payment credentials",
                        "track_id": response["trackId"],
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "trackId": response["trackId"],
                    "result": response["result"],
                    "message": response["message"],
                    "payment_url": f"{self.request_payment}/{response['trackId']}",
                },
                status=status.HTTP_200_OK,
            )
        # Failure response
        else:
            return Response(
                {
                    "detail": "Payment gateway error",
                    "result": response["result"],
                    "message": response["message"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentVerifyAPIView(APIView):
    """
    Verify the payment and update both payment and order status
    """

    permission_classes = [permissions.AllowAny]
    verify_url = os.getenv("ZIBAL_VERIFY_PAYMENT")

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
                    "detail": "trackId not provided",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.select_for_update().get(
                track_id=track_id,
                status=Payment.Status.PENDING,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "No payment record found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify payment
        try:
            response = requests.post(
                self.verify_url,
                json={
                    "merchant": os.getenv("ZIBAL_MERCHANT", "zibal"),
                    "trackId": track_id,
                },
                timeout=5,
            ).json()
        except requests.RequestException as e:
            return Response(
                {
                    "detail": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Success payment
        if response["result"] in [100, 201]:
            payment.status = Payment.Status.SUCCESS
            payment.raw_response = response
            payment.save(update_fields=["status", "raw_response"])

            order = payment.order
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])

            return Response(
                {
                    "result": "Payment was successful",
                    "track_id": track_id,
                },
                status=status.HTTP_200_OK,
            )

        # Payment failed
        else:
            payment.status = Payment.Status.FAILED
            payment.raw_response = response
            payment.save(update_fields=["status", "raw_response"])

            return Response(
                response,
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentHistoryAPIView(generics.ListAPIView):
    """User payment history"""

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

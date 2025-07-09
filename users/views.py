import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from product.models import Category

from .serializers import CategorySerializer

User = get_user_model()


@api_view(["GET"])
def activate_user_view(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response(
            {
                "result": "Account activated",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "error": "Invalid activation link",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related(
        "products", "subcategories", "subcategories__products"
    )
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Get the list of top-level categories with their children",
        responses={
            200: CategorySerializer(many=True),
            401: "Unauthorized - authentication credentials not provided",
            403: "Forbidden - you do not have permission to access this resource.",
        },
        security=[{"Token": []}],
        tags=["Categories"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@api_view(["POST"])
def password_change_confirm(request, uid, token):
    new_password = request.data.get("new_password")

    if not new_password:
        return Response({"error": "New password is required."}, status=400)

    response = requests.post(
        "http://localhost:9000/auth/users/reset_password_confirm/",
        json={
            "uid": uid,
            "token": token,
            "new_password": new_password,
        },
    )

    if response.status_code == 204:
        return Response({"result": "Password reset confirmed."})
    else:
        return Response(response.json(), status=response.status_code)


# del

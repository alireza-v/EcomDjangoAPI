from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

User = get_user_model()


@swagger_auto_schema(
    method="get",
    operation_summary="Activate user account",
    operation_description="Activate user account using the UID and token",
    responses={
        200: openapi.Response(description="Account activated"),
        400: openapi.Response(description="Invalid activation link"),
    },
    tags=["Custom Auth"],
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def activate_user_view(
    request,
    uid,
    token,
):
    """
    Activate user account by the given uid | token
    """
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

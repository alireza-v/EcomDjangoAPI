import logging

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Custom user registeration
    """

    username = serializers.CharField(required=False)
    email = serializers.EmailField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            "email",
            "username",
            "password",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("This email address already registered")
            )
        return value


class CustomTokenSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _(
            "Email or password is incorrect",
        )
    }

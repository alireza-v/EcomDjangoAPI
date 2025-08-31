from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Cutom user-register serializer
    """

    username = serializers.CharField(required=False)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            "email",
            "username",
            "password",
        ]

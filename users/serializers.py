from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    cutoms user registration serializer
    """

    username = serializers.CharField(required=False)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            "email",
            "username",
            "password",
        ]

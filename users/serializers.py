from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import *


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(required=False)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            "email",
            "username",
            "password",
        ]

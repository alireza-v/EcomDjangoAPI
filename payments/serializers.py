from rest_framework import serializers

from orders.serializers import OrderSerializer

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=True)

    class Meta:
        model = Payment
        fields = [
            "order",
            "track_id",
            "amount",
            "status",
        ]

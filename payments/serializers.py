from rest_framework import serializers

from orders.serializers import OrderSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    formatted_amount = serializers.SerializerMethodField()
    order = OrderSerializer(many=True)

    class Meta:
        model = Payment
        fields = [
            "order",
            "track_id",
            "amount",
            "formatted_amount",
            "status",
        ]

    def get_formatted_amount(self, obj):
        return f"{obj.amount:,.0f}"

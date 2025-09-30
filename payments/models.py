from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from users.models import TimestampModel


class Payment(TimestampModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_payments",
    )
    gateway = models.CharField(max_length=100, default="zibal")
    track_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )
    raw_response = models.JSONField(
        null=True,
        blank=True,
    )
    paid_at = models.DateTimeField(
        verbose_name=_("زمان پرداخت"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Payment for {self.order}"

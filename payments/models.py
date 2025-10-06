from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from users.models import BaseModel


class Payment(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        EXPIRED = "expired", _("Expired")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
        related_name="order_payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="user_payments",
    )
    gateway = models.CharField(
        verbose_name=_("Payment gateway"),
        max_length=100,
        default="zibal",
    )
    track_id = models.CharField(
        verbose_name=_("TrackId"),
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=15,
        decimal_places=2,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
    )
    raw_response = models.JSONField(
        verbose_name=_("Raw response"),
        null=True,
        blank=True,
    )
    paid_at = models.DateTimeField(
        verbose_name=_("Paid at"),
        blank=True,
        null=True,
    )

    def mark_success(self, response_data):
        """Mark payment as successful"""
        self.status = self.Status.SUCCESS
        self.raw_response = response_data
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "raw_response", "paid_at"])

        self.order.status = Order.Status.PAID
        self.order.save(update_fields=["status"])

    def mark_failure(self, response_data):
        """Mark payment as failure"""
        self.status = self.Status.FAILED
        self.raw_response = response_data
        self.save(update_fields=["status", "raw_response"])

        self.order.status = Order.Status.FAILED
        self.order.save(update_fields=["status"])

    def __str__(self):
        return f"Payment for {self.order}"

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from users.models import BaseModel


class Order(BaseModel):
    """
    Store user order info
    """

    class Status(models.TextChoices):
        """
        Order status being updated at checkout
        """

        PENDING = "pending", _("Pending")
        EXPIRED = "expired", _("Expired")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="user_orders",
    )
    status = models.CharField(
        verbose_name=_("Status"),
        choices=Status.choices,
        max_length=20,
        default=Status.PENDING,
        db_index=True,
    )
    shipping_address = models.TextField(
        verbose_name=_("Shipping address"),
    )
    total_amount = models.DecimalField(
        verbose_name=_("Total amount"),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Snapshot of the total price at checkout time",
    )
    paid_at = models.DateTimeField(
        verbose_name=_("Paid at"),
        blank=True,
        null=True,
    )

    @property
    def total(self):
        """
        Return computed total amount
        """
        return sum(
            Decimal(item.price_at_purchase) * item.quantity
            for item in self.order_items.all()
        )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش ها"

    def __str__(self):
        return f"Order by {self.user} - Status: {self.status.capitalize()}"


class OrderItem(BaseModel):
    """
    Store detailed info about each order
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
        related_name="order_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_("Product"),
        related_name="product_order_items",
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    price_at_purchase = models.DecimalField(
        verbose_name=_("Price at purchase"),
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "مقدار سفارش"
        verbose_name_plural = "مقادیر سفارش"

    def __str__(self):
        return (
            f"{self.product.title} x{self.quantity} (Order status: {self.order.status})"
        )

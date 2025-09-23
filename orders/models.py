from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from users.models import TimestampModel


class Order(TimestampModel):
    """
    Store user order info
    """

    class Status(models.TextChoices):
        """
        Order status being updated at payment time
        """

        PENDING = "pending", _("PENDING")
        PAID = "paid", _("PAID")
        FAILED = "failed", _("FAILED")
        SHIPPED = "shipped", _("SHIPPED")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("کاربر"),
        on_delete=models.CASCADE,
        related_name="user_orders",
    )
    status = models.CharField(
        verbose_name=_("وضعیت"),
        choices=Status.choices,
        max_length=20,
        default=Status.PENDING,
        db_index=True,
    )
    shipping_address = models.TextField(
        verbose_name=_("آدرس تحویل"),
    )
    total_amount = models.DecimalField(
        verbose_name=_("مبلغ کل"),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Snapshot of the total price at checkout time",
    )

    @property
    def total(self):
        """
        Returns computed total amount
        i.e. sum of all OrderItem prices * quantities
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


class OrderItem(TimestampModel):
    """
    Store detailed info about each product in Order, i.e. quantity | price
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("سفارش"),
        related_name="order_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # Prevent deletion if order existed
        verbose_name=_("محصول"),
        related_name="product_order_items",
    )
    quantity = models.PositiveIntegerField(verbose_name="مقدار")
    price_at_purchase = models.DecimalField(
        verbose_name=_("قیمت خرید"),
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

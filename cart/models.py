from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from users.models import TimestampModel

User = get_user_model()


class CartItem(TimestampModel):
    user = models.ForeignKey(
        User,
        verbose_name=_("کاربر"),
        on_delete=models.CASCADE,
        related_name="cart_users",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("محصول"),
        related_name="cart_products",
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("مقدار"),
        default=1,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_cart_item",
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.title} (x{self.quantity})"


class Order(TimestampModel):
    STATUS = [
        ("pending", "PENDING"),
        ("paid", "PAID"),
        ("completed", "COMPLETED"),
        ("canceled", "CANCELED"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("کاربر"),
        related_name="orders",
    )
    status = models.CharField(
        verbose_name=_("وضعیت"),
        choices=STATUS,
        max_length=20,
        default="pending",
    )

    def __str__(self):
        return f"Order by {self.user} - Status: {self.status.capitalize()}"


class OrderItem(TimestampModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("سفارش"),
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_("محصول"),
        related_name="item_products",
    )
    quantity = models.PositiveIntegerField(verbose_name="مقدار")
    price_at_purchase = models.DecimalField(
        verbose_name=_("قیمت خرید"),
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"{self.product.title} x{self.quantity} (Order status: {self.order.status})"
        )

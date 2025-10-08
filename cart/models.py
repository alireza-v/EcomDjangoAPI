from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from users.models import BaseModel


class CartItem(BaseModel):
    """
    User cart model to store items
        - user: User
        - product: Product
        - quantity: product quantity
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="user_carts",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        related_name="product_carts",
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Cart list")
        verbose_name_plural = _("Cart lists")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_product_per_user",
            )
        ]

    @property
    def subtotal(self):
        """
        Return the subtotal after the discount is applied
        """
        return Decimal(self.quantity) * self.product.discounted_price

    def __str__(self):
        return f"{self.user.email} - {self.product.title} (x{self.quantity})"

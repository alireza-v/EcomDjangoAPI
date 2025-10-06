from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import BaseModel

from .product import Product


class Feedback(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="user_feedbacks",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="product_feedbacks",
    )
    description = models.TextField(verbose_name=_("Description"))
    rating = models.PositiveSmallIntegerField(
        verbose_name=_("Rating"),
    )

    class Meta:
        """
        Constraint (uniqueness):
            - User may comment on product once
        """

        verbose_name = "بازخورد"
        verbose_name_plural = "بازخورد ها"
        ordering = ["-rating"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product"
            ),
        ]

    def __str__(self):
        return f"{self.user.email}- {self.description[:10]}"


class Like(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="user_likes",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="product_likes",
    )

    class Meta:
        """
        constraint (uniqueness):
            - Product likes by each user
        """

        verbose_name = "مورد علاقه"
        verbose_name_plural = "مورد علاقه ها"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_product_likes"
            ),
        ]

    def __str__(self):
        return self.product.title

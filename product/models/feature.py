from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import BaseModel

from .product import Product


class FeatureName(BaseModel):
    name = models.CharField(
        verbose_name=_("Feature name"),
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "عنوان ویژگی"
        verbose_name_plural = "ویژگی ها"

    def __str__(self):
        return self.name


class FeatureValue(BaseModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="product_features",
    )
    feature = models.ForeignKey(
        FeatureName,
        verbose_name=_("Feature"),
        on_delete=models.CASCADE,
        related_name="feature_values",
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=100,
    )

    class Meta:
        """
        Constraint (uniqueness):
            - product
            - feature
            - value
        """

        ordering = ["-id"]
        verbose_name = "مقدار ویژگی "
        verbose_name_plural = "مقادیر ویژگی ها"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "feature",
                    "value",
                ],
                name="unique_product_feature_value",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}: {self.value}"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to="products/gallery/",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عکس ها"
        verbose_name_plural = "عکس ها"

    def __str__(self):
        return f"{self.product.title} - {self.id}"

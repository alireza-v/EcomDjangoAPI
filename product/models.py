from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image
from slugify import slugify as py_slugify

User = get_user_model()
from users.models import TimestampModel


def custom_slugify(value):
    return py_slugify(value, lowercase=True)


class Category(TimestampModel):
    title = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = py_slugify(self.title)
        super().save(*args, **kwargs)


class Product(TimestampModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    main_image = models.ImageField(upload_to="products/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = py_slugify(self.title)
        super().save(*args, **kwargs)


class ProductFeature(TimestampModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="features", null=True
    )
    name = models.CharField(max_length=100, null=True)
    value = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.product.title} - {self.name}: {self.value}"


class ProductImage(TimestampModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/", null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} - {self.id}"


class Feedback(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="feedbacks"
    )
    description = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.email}- {self.description[:10]}"


"""del"""

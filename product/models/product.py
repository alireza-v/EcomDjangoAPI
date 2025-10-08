from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from users.models import BaseModel


class Category(BaseModel):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    visit_count = models.PositiveIntegerField(
        verbose_name=_("Visit counts"),
        default=0,
        null=True,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        allow_unicode=True,
    )

    class Meta:
        """Unique title per category"""

        ordering = ["-visit_count"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        constraints = [
            models.UniqueConstraint(
                fields=["title", "parent"],
                name="unique_category_per_parent",
            ),
        ]

    def get_breadcrumbs(self):
        """
        Return the breadcrumb path of the category from the top-level parent down to itself
        """
        breadcrumbs = []
        category = self
        while category:
            breadcrumbs.insert(0, category)
            category = category.parent
        return breadcrumbs

    def validate_unique(self, exclude=None):
        """Respect uniqueness in admin"""
        super().validate_unique(exclude=exclude)
        if (
            Category.objects.filter(
                title=self.title,
                parent=self.parent,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {
                    "title": "Category with this title already exists",
                }
            )

    def save(self, *args, **kwargs):
        """slug field populated from the title"""
        if not self.slug:
            self.slug = slugify(
                self.title,
                allow_unicode=True,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(BaseModel):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        related_name="products",
    )

    price = models.DecimalField(
        verbose_name=_("Price"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    main_image = models.ImageField(
        verbose_name=_("Main image"),
        upload_to="products/",
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(
        verbose_name=_("Stock"),
        default=0,
    )
    visit_count = models.PositiveIntegerField(
        _("Visit counts"),
        default=0,
        null=True,
    )
    brand = models.CharField(
        verbose_name=_("Brand"),
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        allow_unicode=True,
    )

    class Meta:
        """
        Constraint (uniqueness):
            - title
            - brand
        """

        ordering = ["-visit_count", "-created_at"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        constraints = [
            models.UniqueConstraint(
                fields=["title", "brand"],
                name="unique_title",
            )
        ]

    def get_discount(self):
        """
        Find max discount for products and  categories
        """
        discounts = list(self.product_discounts.filter(end_date__gte=timezone.now()))
        if self.category:
            discounts += list(
                self.category.category_discounts.filter(end_date__gte=timezone.now())
            )
        return max([d.percent for d in discounts], default=0)

    @property
    def discounted_price(self):
        discount = Decimal(self.get_discount())
        price = Decimal(self.price)
        return price * (Decimal("100") - discount) / Decimal("100")

    @property
    def price_formatter(self):
        if self.price is not None:
            return f"{self.price:,.0f}"
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Discount(BaseModel):
    "Discounts on parents and subcategories"

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
    )
    percent = models.PositiveIntegerField(
        verbose_name=_("Percent"),
        validators=[
            MaxValueValidator(
                limit_value=70,
                message=_("Max percent value 70"),
            )
        ],
    )
    end_date = models.DateTimeField(
        verbose_name=_("End date"),
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="product_discounts",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="category_discounts",
    )

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

    def clean(self):
        super().clean()
        if self.end_date <= timezone.now():
            raise ValidationError(
                {"end_date": "End date must be in the future"},
            )

    def __str__(self):
        return self.name

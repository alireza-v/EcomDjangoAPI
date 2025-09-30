from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from users.models import TimestampModel


class Category(TimestampModel):
    title = models.CharField(
        verbose_name=_("گروه"),
        max_length=255,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("زیر مجموعه"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    visit_count = models.PositiveIntegerField(
        verbose_name=_("بازدید ها"),
        default=0,
        null=True,
    )
    slug = models.SlugField(
        verbose_name=_("شناسه"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        allow_unicode=True,
    )

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

    class Meta:
        ordering = ["-visit_count"]
        verbose_name = _("گروه")
        verbose_name_plural = _("گروه ها")
        constraints = [
            models.UniqueConstraint(
                fields=["title", "parent"],
                name="unique_category_per_parent",
            ),
        ]

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
            raise ValidationError({"title": "Category with this title already exist"})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """slug field populated from the title"""
        if not self.slug:
            self.slug = slugify(
                self.title,
                allow_unicode=True,
            )
        super().save(*args, **kwargs)


class FeatureName(TimestampModel):
    name = models.CharField(
        verbose_name=_("نام ویژگی"),
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "عنوان ویژگی"
        verbose_name_plural = "ویژگی ها"

    def __str__(self):
        return self.name


class Product(TimestampModel):
    title = models.CharField(
        verbose_name=_("نام"),
        max_length=255,
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("گروه"),
        on_delete=models.CASCADE,
        related_name="products",
    )

    price = models.DecimalField(
        verbose_name=_("قیمت"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    main_image = models.ImageField(
        verbose_name=_("عکس رسمی"),
        upload_to="products/",
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("توضیحات"),
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(
        verbose_name=_("موجودی"),
        default=0,
    )
    visit_count = models.PositiveIntegerField(
        _("بازدید ها"),
        default=0,
        null=True,
    )
    brand = models.CharField(
        verbose_name=_("برند"),
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        _("شناسه"),
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
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")
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


class Discount(TimestampModel):
    "Discount model for products and categories"

    name = models.CharField(
        verbose_name=_("نام"),
        max_length=100,
    )
    percent = models.PositiveIntegerField(
        verbose_name=_("درصد"),
        validators=[MaxValueValidator(100)],
    )
    end_date = models.DateTimeField(verbose_name=_("تایخ انقضا"))
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصولات"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="product_discounts",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("گروه ها"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="category_discounts",
    )

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.end_date <= timezone.now():
            raise ValidationError({"end_date": "End date must be in the future"})

    class Meta:
        verbose_name = "تخفیف"
        verbose_name_plural = "تخفیف ها"


class FeatureValue(TimestampModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصولات"),
        on_delete=models.CASCADE,
        related_name="product_features",
    )
    feature = models.ForeignKey(
        FeatureName,
        verbose_name=_("عنوان ویژگی"),
        on_delete=models.CASCADE,
        related_name="feature_values",
    )
    value = models.CharField(
        verbose_name=_("مقدار"),
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


class ProductImage(TimestampModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        verbose_name=_("عکس"),
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


class Feedback(TimestampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("کاربر"),
        on_delete=models.CASCADE,
        related_name="user_feedbacks",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
        on_delete=models.CASCADE,
        related_name="product_feedbacks",
    )
    description = models.TextField(_("توضیحات"))
    rating = models.PositiveSmallIntegerField(
        _("امتیاز"),
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


class Like(TimestampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_likes",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
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

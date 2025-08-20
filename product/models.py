from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()
from users.models import TimestampModel


class Category(TimestampModel):
    title = models.CharField(
        verbose_name=_("عنوان"),
        max_length=255,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("عنوان گروه"),
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
        breadcrumbs = []
        category = self
        while category:
            breadcrumbs.insert(0, category)
            category = category.parent
        return breadcrumbs

    class Meta:
        verbose_name = _("گروه")
        verbose_name_plural = _("گروه ها")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.title,
                allow_unicode=True,
            )
        super().save(*args, **kwargs)


class FeatureName(TimestampModel):
    name = models.CharField(
        verbose_name=_("نام"),
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "عنوان ویژگی"
        verbose_name_plural = " عنوان ویژگی ها"

    def __str__(self):
        return self.name


class Product(TimestampModel):
    title = models.CharField(
        verbose_name=_("عنوان"),
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
        verbose_name=_("عکس اصلی"),
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
    slug = models.SlugField(
        _("شناسه"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        allow_unicode=True,
    )

    class Meta:
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")

    @property
    def price_formatter(self):
        if self.price is not None:
            return f"{self.price:,.0f}"
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.title,
                allow_unicode=True,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class FeatureValue(TimestampModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
        on_delete=models.CASCADE,
        related_name="feature_values",
    )
    feature = models.ForeignKey(
        FeatureName,
        verbose_name=_("عنوان ویژگی"),
        on_delete=models.CASCADE,
        related_name="product_values",
    )
    value = models.CharField(
        verbose_name=_("مقدار"),
        max_length=100,
    )

    class Meta:
        verbose_name = "مقدار ویژگی محصول"
        verbose_name_plural = "مقادیر ویژگی های محصول"
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
        verbose_name=_("عکس رسمی"),
        upload_to="products/gallery/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.product.title} - {self.id}"


class Feedback(TimestampModel):
    user = models.ForeignKey(
        User,
        verbose_name=_("کاربر"),
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    description = models.TextField(_("توضیحات"))
    rating = models.PositiveSmallIntegerField(
        _("امتیاز"),
        null=True,
    )

    class Meta:
        verbose_name = "بازخورد"
        verbose_name_plural = "بازخورد ها"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product"
            ),
        ]

    def __str__(self):
        return f"{self.user.email}- {self.description[:10]}"


class Like(TimestampModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_likes",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_likes",
    )

    class Meta:
        verbose_name = "مورد علاقه"
        verbose_name_plural = "مورد علاقه ها"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_like"
            ),
        ]

    def __str__(self):
        return self.product.title

import os
import random

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker

from product.models import (
    Category,
    FeatureName,
    FeatureValue,
    Feedback,
    Product,
    ProductImage,
)

User = get_user_model()
fake = Faker("fa_IR")


class Command(BaseCommand):
    help = "پر کردن پایگاه داده با دسته‌بندی‌ها، محصولات، ویژگی‌ها و بازخوردها."

    features_list = [
        ("برند", ["اپل", "سامسونگ", "دل", "اچ‌پی", "لنوو"]),
        ("حافظه", ["128 گیگابایت", "256 گیگابایت", "512 گیگابایت", "1 ترابایت"]),
        ("رم", ["4 گیگابایت", "8 گیگابایت", "16 گیگابایت", "32 گیگابایت"]),
        ("رنگ", ["مشکی", "نقره‌ای", "آبی", "قرمز"]),
        ("اندازه صفحه", ["13 اینچ", "15 اینچ", "17 اینچ"]),
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("در حال وارد کردن داده‌ها..."))

        Category.objects.all().delete()

        parent = Category.objects.create(title="محصولات دیجیتال")

        subcategories = [
            Category.objects.create(
                title="لپ‌تاپ",
                parent=parent,
                visit_count=random.randint(1, 100),
            ),
            Category.objects.create(
                title="گوشی هوشمند",
                parent=parent,
                visit_count=random.randint(1, 100),
            ),
        ]

        user, created = User.objects.get_or_create(email="admin@email.com")
        if created:
            user.set_password("123")
            user.is_superuser = True
            user.is_staff = True
            user.save()

        # اضافه کردن ویژگی‌ها
        for name, _ in self.features_list:
            FeatureName.objects.get_or_create(name=name)

        features_dict = {feature.name: feature for feature in FeatureName.objects.all()}

        # ایجاد محصولات
        for subcat in subcategories:
            for i in range(5):
                product = Product.objects.create(
                    title=f"{subcat.title} مدل {i + 1}",
                    category=subcat,
                    price=random.randint(200, 3000)
                    * 100,  # به تومان یا دلار قابل تغییر است
                    description=fake.text(max_nb_chars=200),
                    stock=random.randint(0, 10),
                    visit_count=random.randint(1, 100),
                )

                # انتخاب ویژگی‌های تصادفی
                selected_features = random.sample(
                    self.features_list,
                    random.randint(2, 4),
                )
                for feature_name, values in selected_features:
                    value = random.choice(values)
                    FeatureValue.objects.get_or_create(
                        product=product,
                        feature=features_dict[feature_name],
                        value=value,
                    )

                # تصویر اصلی
                main_image_path = os.path.join(
                    "static", f"product/images/{subcat.title}/image_{i + 1}.jpg"
                )
                if os.path.exists(main_image_path):
                    with open(main_image_path, "rb") as image_file:
                        product.main_image.save(
                            f"{product.slug}_image_{i}.jpg",
                            File(image_file),
                            save=False,
                        )

                product.save()

                # تصاویر گالری
                for j in range(1, 4):
                    alt_image_filename = f"alt_image_{j}.jpg"
                    alt_image_path = os.path.join(
                        "static",
                        f"product/images/{subcat.title}/{alt_image_filename}",
                    )
                    if os.path.exists(alt_image_path):
                        with open(alt_image_path, "rb") as alt_file:
                            ProductImage.objects.create(
                                product=product,
                                image=File(
                                    alt_file, name=f"{product.slug}_alt_{j}.jpg"
                                ),
                            )

                # بازخوردها
                Feedback.objects.create(
                    user=user,
                    product=product,
                    description=random.choice(
                        [
                            "خیلی عالی بود!",
                            "از خریدم راضی هستم.",
                            "میتوانست بهتر باشد.",
                            "عملکرد فوق‌العاده!",
                            "ارزش خرید ندارد.",
                        ]
                    ),
                    rating=random.randint(1, 5),
                )

        self.stdout.write(self.style.SUCCESS("✅ داده‌ها با موفقیت وارد شدند!"))

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from ...models import (
    Category,
    Discount,
    FeatureName,
    FeatureValue,
    Feedback,
    Like,
    Product,
)

User = get_user_model()
fake = Faker("fa_IR")
USER_PASSWORD = "123!@#QWE"


class Command(BaseCommand):
    help = "Seed the database with random data for necessary models"

    brand_list = [
        "سامسونگ",
        "شیائومی",
        "نوکیا",
        "آنر",
        "هواوی",
    ]
    memory_list = [
        "128 گیگابایت",
        "256 گیگابایت",
        "512 گیگابایت",
    ]
    features_list = [
        (
            "حافظه",
            [
                "128 گیگابایت",
                "256 گیگابایت",
                "512 گیگابایت",
            ],
        ),
        (
            "رم",
            [
                "4 گیگابایت",
                "8 گیگابایت",
                "16 گیگابایت",
                "32 گیگابایت",
            ],
        ),
        (
            "رنگ",
            [
                "مشکی",
                "نقره‌ای",
                "آبی",
                "قرمز",
            ],
        ),
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("seed data..."))

        Category.objects.all().delete()

        parent = Category.objects.create(title="محصولات دیجیتال")

        subcategories = [
            Category.objects.create(
                title="گوشی موبایل",
                parent=parent,
                visit_count=random.randint(1, 50),
            ),
        ]

        for i in range(1, 50):
            user, created = User.objects.get_or_create(
                email=f"active_user_{i}@example.com"
            )
            if created:
                user.set_password(USER_PASSWORD)
                user.is_active = True
                user.save()

        for name, _ in self.features_list:
            FeatureName.objects.get_or_create(name=name)

        for subcat in subcategories:
            for i in range(1, 6):
                index = i
                brand = random.choice(self.brand_list)

                product = Product.objects.create(
                    title=f"{subcat} {brand} شماره {index}",
                    brand=brand,
                    category=subcat,
                    price=random.randint(10_000_000, 50_000_000),
                    description=fake.text(max_nb_chars=100),
                    stock=random.randint(0, 10),
                    visit_count=random.randint(1, 100),
                )
                discounts = Discount.objects.create(
                    name=f"تخفیف شماره {index}",
                    percent=random.randint(1, 50),
                    end_date=timezone.now() + timedelta(days=random.randint(1, 10)),
                    product=product,
                )

                # Liked products by users
                likes = Like.objects.create(user=user, product=product)

                # Features
                features_dict = {f.name: f for f in FeatureName.objects.all()}
                k = random.randint(2, min(4, len(self.features_list)))
                selected_features = random.sample(
                    self.features_list,
                    k,
                )
                for feature_name, values in selected_features:
                    feature_obj = features_dict.get(feature_name)
                    if not feature_obj:
                        feature_obj, _ = FeatureName.objects.get_or_create(
                            name=feature_name
                        )
                    FeatureValue.objects.get_or_create(
                        product=product,
                        feature=feature_obj,
                        value=random.choice(values),
                    )

                # Feedbacks
                users = list(User.objects.all())
                k = random.randint(5, min(15, len(users)))
                user_comments = random.sample(users, k)
                for user in user_comments:
                    Feedback.objects.create(
                        user=user,
                        product=product,
                        description=fake.text(max_nb_chars=50),
                        rating=random.randint(1, 5),
                    )

        self.stdout.write(self.style.SUCCESS("seed data success!"))

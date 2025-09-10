import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from product.models import (
    Category,
    FeatureName,
    FeatureValue,
    Feedback,
    Product,
)

User = get_user_model()
fake = Faker("fa_IR")
USER_PASSWORD = "123!@#QWE"


class Command(BaseCommand):
    help = "Seed the database with random data by necessary models"

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
        "1 ترابایت",
    ]
    features_list = [
        (
            "حافظه",
            [
                "128 گیگابایت",
                "256 گیگابایت",
                "512 گیگابایت",
                "1 ترابایت",
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
        (
            "اندازه صفحه",
            [
                "13 اینچ",
                "15 اینچ",
                "17 اینچ",
            ],
        ),
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("seed data..."))

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

        for i in range(1, 101):
            user, created = User.objects.get_or_create(
                email=f"active_user_{i}@example.com"
            )
            if created:
                user.set_password(USER_PASSWORD)
                user.is_active = True
                user.save()

        for name, _ in self.features_list:
            FeatureName.objects.get_or_create(name=name)

        features_dict = {feature.name: feature for feature in FeatureName.objects.all()}

        for subcat in subcategories:
            for i in range(5):
                brand = random.choice(self.brand_list)
                memory = random.choice(self.memory_list)

                product = Product.objects.create(
                    title=f"گوشی {brand} ظرفیت {memory}",
                    brand=brand,
                    category=subcat,
                    price=random.randint(10_000_000, 50_000_000),
                    description=fake.text(max_nb_chars=100),
                    stock=random.randint(0, 10),
                    visit_count=random.randint(1, 100),
                )

                # Assign random features
                selected_features = random.sample(
                    self.features_list,
                    random.randint(2, 4),
                )
                for feature_name, values in selected_features:
                    FeatureValue.objects.create(
                        product=product,
                        feature=features_dict[feature_name],
                        value=random.choice(values),
                    )

                # Random feedbacks from random users
                users = list(User.objects.all())
                feedback_users = random.sample(users, random.randint(5, 15))
                for user in feedback_users:
                    Feedback.objects.create(
                        user=user,
                        product=product,
                        description=fake.text(max_nb_chars=50),
                        rating=random.randint(1, 5),
                    )

        self.stdout.write(self.style.SUCCESS("seed data success!"))

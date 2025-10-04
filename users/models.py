from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        email,
        username=None,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault(
            "is_active",
            False,
        )
        user = self.model(
            email=email,
            username=username,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class TimestampModel(models.Model):
    """
    Timestamp tracking for all models
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
    )

    class Meta:
        abstract = True


class CustomUser(TimestampModel, AbstractUser):
    """
    Custom user model where email is used as the primary identifier
    """

    email = models.EmailField(unique=True, verbose_name=_("آدرس ایمیل"))
    username = models.CharField(
        verbose_name=_("نام کاربری"),
        max_length=50,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or self.username or f"User- {self.pk}"

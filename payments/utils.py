from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Payment


@transaction.atomic
def expired_payments():
    pending_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        created_at__lt=timezone.now() - timedelta(minutes=30),
    )

    if not pending_payments.exists():
        return

    pending_payments.update(status=Payment.Status.EXPIRED)

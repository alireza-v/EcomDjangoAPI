from celery import shared_task

from .utils import expired_payments


@shared_task
def expired_payments_task():
    expired_payments()

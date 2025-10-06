from celery import shared_task

from .utils import mark_pending_orders


@shared_task
def expired_orders_task():
    mark_pending_orders()

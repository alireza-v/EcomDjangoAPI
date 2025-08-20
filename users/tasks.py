import time

from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def long_task():
    time.sleep(10)
    return "Executed after 10 seconds"

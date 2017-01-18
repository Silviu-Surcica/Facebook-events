from __future__ import absolute_import, unicode_literals
from celery import task, shared_task
import time


@task
def add(x, y):
    time.sleep(5)
    return x+y

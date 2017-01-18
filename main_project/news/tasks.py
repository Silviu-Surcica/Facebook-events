from celery import task
import time


@task
def add(x, y):
    time.sleep(1)
    return x+y

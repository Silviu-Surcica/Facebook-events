from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from django.db import models

# Create your models here.


class Event(models.Model):
    author = models.ForeignKey('auth.User')
    fb_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    cover_picture = models.URLField(max_length=255, blank=True, null=True, default=None)
    profile_picture = models.URLField(max_length=255, blank=True, null=True, default=None)
    description = models.CharField(null=True, default=None, blank=True, max_length=1500)
    distance = models.CharField(max_length=50)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    category = models.CharField(null=True, default=None, blank=True, max_length=50)
    stats = models.TextField(default=None, blank=True, null=True)

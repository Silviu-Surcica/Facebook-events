from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from django.db import models


class Event(models.Model):

    fb_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    cover_picture = models.URLField(max_length=255, blank=True, null=True, default=None)
    profile_picture = models.URLField(max_length=255, blank=True, null=True, default=None)
    description = models.TextField(null=True, default=None, blank=True)
    distance = models.CharField(max_length=50, null=True, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    category = models.CharField(null=True, default=None, blank=True, max_length=50)
    stats = JSONField(default=None)

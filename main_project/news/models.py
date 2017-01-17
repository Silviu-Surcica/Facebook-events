from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    description = models.CharField(max)
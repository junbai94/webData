# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class FutDaily(models.Model):
    instID = models.CharField(primary_key=True, max_length=100)
    date = models.DateTimeField(primary_key=True)
    exch = models.CharField(max_length=100, primary_key=True)
    open = models.FloatField(blank=True)
    close = models.FloatField(blank=True)
    high = models.FloatField(blank=True)
    low = models.FloatField(blank=True)
    volume = models.BigIntegerField(blank=True)
    openInterest = models.BigIntegerField(blank=True)

    class Meta:
        db_table = 'fut_daily'
        unique_together = ('instID', 'date', 'exch')


class Log(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=100, default="Julian")
    article = models.TextField()
    pair = models.CharField(max_length=200, default=None)

    class Meta:
        db_table = 'log'
# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-22 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plotting', '0010_auto_20180222_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

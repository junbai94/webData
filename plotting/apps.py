# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PlottingConfig(AppConfig):
    name = 'plotting'
    techicals_default = {
        'BBANDS': {
            'col': 'spread',
            'period': 9,
        },
    }

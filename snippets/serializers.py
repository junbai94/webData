# -*- coding: utf-8 -*-
"""
Created on 1/27/2018 2:55 PM

@author: Jimmy

Serializer class for Models
"""

from rest_framework import serializers
from .models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'linenos', 'language', 'style')
from rest_framework import serializers
from .models import FutDaily, Log


class FutDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = FutDaily
        fields = ('instID', 'date', 'exch', 'open', 'close', 'high', 'low', 'volume', 'openInterest')


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields= ('datetime', 'author', 'article', 'pair')
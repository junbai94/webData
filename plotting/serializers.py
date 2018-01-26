from rest_framework import serializers
from .models import FutDaily


class FutDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = FutDaily
        fields = ('instID', 'date', 'exch', 'open', 'close', 'high', 'low', 'volume', 'OpenInterest')
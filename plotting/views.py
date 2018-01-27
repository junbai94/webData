# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from .models import FutDaily
from .serializers import FutDailySerializer


from rest_framework import generics


class FutList(generics.ListAPIView):
    serializer_class = FutDailySerializer

    def get_queryset(self):
        queryset = FutDaily.objects.filter(date__gte=datetime(2017, 12, 12))
        instID = self.request.query_params.get('instid', None)
        start = self.request.query_params.get('start', None)
        if instID:
            queryset = queryset.filter(instID=instID)
        if start:
            queryset = queryset.filter(date__gte=datetime.strptime(start, "%Y%m%d"))
        return queryset


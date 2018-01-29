# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from .models import FutDaily
from .serializers import FutDailySerializer

# REST framework class views
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

# filters
# from url_filter.integrations.drf import DjangoFilterBackend


class FutList(generics.ListAPIView):
    serializer_class = FutDailySerializer

    def get_queryset(self):
        queryset = FutDaily.objects.all()
        instID = self.request.query_params.get('instid', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        exch = self.request.query_params.get('exch', None)
        if instID:
            instID = [x for x in instID.split(',')]
            queryset = queryset.filter(instID__in=instID)
        if exch:
            queryset = queryset.filter(exch=exch.upper())
        if start:
            queryset = queryset.filter(date__gte=datetime.strptime(start, "%Y%m%d"))
        if end:
            queryset = queryset.filter(date__lte=datetime.strptime(end, "%Y%m%d"))
        return queryset


class Charter(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/index.html'

    def get(self, request):
        return Response({})
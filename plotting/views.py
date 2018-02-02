# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .apps import PlottingConfig
import sys
sys.path.append(PlottingConfig.datapy)
import datapy as dy
from datetime import datetime
import pandas as pd
import json

# include classes we need
from .models import FutDaily
from .serializers import FutDailySerializer
from .forms import FutDailyForm

# REST framework class views
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

#############################################################################################
# APIs
#############################################################################################
class FutList(generics.ListAPIView):
    """
    Return multiple price lists of futures
    """
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


class FutSpread(APIView):
    """
    Return the spread of close prices between two futures
    """
    def get(self, request, format=None):
        ids = self.request.query_params.get('instid', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        technicals = self.request.query_params.get('technical', None)
        if not ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            id1, id2 = ids.split(',')
            fut1 = FutDaily.objects.filter(instID=id1)
            fut2 = FutDaily.objects.filter(instID=id2)
        if start:
            fut1 = fut1.filter(date__gte=datetime.strptime(start, "%Y%m%d"))
            fut2 = fut2.filter(date__gte=datetime.strptime(start, "%Y%m%d"))
        if end:
            fut1 = fut1.filter(date__gte=datetime.strptime(end, "%Y%m%d"))
            fut2 = fut2.filter(date__gte=datetime.strptime(end, "%Y%m%d"))


        df1 = pd.DataFrame.from_records(fut1.values())
        df2 = pd.DataFrame.from_records(fut2.values())
        df1 = df1[['date', 'close']]
        df2 = df2[['date', 'close']]
        df = df1.merge(df2, on='date')
        df['spread'] = df['close_x'] - df['close_y']
        df = df[['date', 'spread']]

        if technicals:
            technicals = technicals.split(',')
            for technical in technicals:
                if technical in dir(dy.techie):
                    f = getattr(dy.techie, technical)
                    df = f(df, 9, 'spread')

        df = df.dropna()
        data = df.to_dict(orient='records')
        return Response(data)


#############################################################################################
# Views
#############################################################################################
class Charter(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/index.html'

    def get(self, request):
        pairs = json.dumps(['hc1805,rb1805', 'rb1805,i1805'])
        return Response({'pairs': pairs})


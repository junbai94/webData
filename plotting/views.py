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
class APIBase(APIView):
    """
    Base class for all API classes
    """
    def get(self, request, format=None):
        return Response()


    def post(self, request, format=None):
        return Response()


    def _get_ids(self):
        """
        Get a list of ids from query parameters
        """
        ID = self.request.query_params.get('id', None)
        ID = ID.split(',')
        result = list()
        for id_ in ID:
            if '$' in id_:
                result.append(id_.replace('$', ''))
            else:
                result.append(id_)
        return result


    def _get_time(self, param):
        """
        parse start or end
        """
        result = self.request.query_params.get(param, None)
        if result:
            result = datetime.strptime(result, "%Y%m%d").strftime("%Y-%m-%d")
        return result


    def parse(self, param):
        """
        return a list of results
        """
        # special handling for id
        if param == 'id':
            return self._get_ids()

        # special handling for time
        if param in ['start', 'end']:
            return self._get_time(param)

        result = self.request.query_params.get(param, None)
        if result:
            result = result.split(',')
        return result


    def _handle_techincal(self, technicals, df, config=None):
        SUPPORTS = ['BBANDS']
        config = PlottingConfig.techicals_default if not config else config

        for tech in technicals:
            if tech in SUPPORTS:
                f = getattr(dy.techie, tech)
                df = f(df, config[tech].get('period'), config[tech].get('col'))
        return df.dropna()


    def parse_query(self):
        """
        Filter out queryset based on URL queries
        :return: a merged dataframe of all
        """
        ID = self.request.query_params.get('id', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)

        if ID:
            ID = ID.split(',')

        if start:
            start =datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")

        if end:
            end = datetime.strptime(end, "%Y%m%d").strftime("%Y-%m-%d")

        output = list()
        for id_ in ID:
            if '$' in id_:
                id_ = id_.replace('$', '')
                df = dy.get_data(id_, id_, 'fut_daily', frm=start, to=end)
            else:
                df = dy.get_data(id_, id_, frm=start, to=end)
            output.append(df)

        return dy.merge_data(*output)


class DataList(APIBase):
    """
    Standard retrival API for data
    """
    def get(self, request, format=None):
        df = self.parse_query()
        data = df.to_dict(orient='records')
        return Response(data)


class FutSpread(APIBase):
    """
    Return the spread of close prices between two futures
    """
    def get(self, request, format=None):
        technicals = self.parse('technical')

        df = self.parse_query()
        id0, id1 = self._get_ids()
        df['spread'] = df[id0] - df[id1]
        df = self._handle_techincal(technicals, df)
        data = df.to_dict(orient='records')
        return Response(data)


class FutRegression(APIBase):
    """
    Return whole regression data package
    """
    def get(self, request, format=None):
        df = self.parse_query()
        dep, indep = self._get_ids()
        reg = dy.Regression(df, dep, indep)
        df = reg.df.copy()
        df['resid'] = reg.result.resid
        data = {
            'package': {
                'k': reg.result.params[1],
                'b': reg.result.params[0],
                'rsqr': reg.result.rsquared,
                'std': reg.result.resid.std(),
            },
            'data': df.to_dict(orient='records')
        }
        return Response(data)

#############################################################################################
# Views
#############################################################################################
class Charter(APIBase):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/index.html'

    def get(self, request):
        target = ['$hc1805,$rb1805', '$hc1805,$hc1810', '$rb1805,$rb1810', '$i1805,$i1810',
                  'bs_billet,tr_scrap', ]
        pairs = json.dumps(target)
        return Response({'pairs': pairs})


class Detail(APIBase):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/detail.html'

    def get(self, request):
        pair = self.request.query_params.get('id', '')
        start = self.request.query_params.get('start', '')
        end = self.request.query_params.get('end', '')
        return Response({'pair': pair,
                         'start':start,
                         'end': end,})


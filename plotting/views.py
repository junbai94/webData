# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .apps import PlottingConfig
from utils import datapy as dy
from datetime import datetime
import pandas as pd
import json
from django.shortcuts import render, HttpResponseRedirect

# include classes we need
from .models import FutDaily, Log
from .serializers import FutDailySerializer, LogSerializer
from .forms import FutDailyForm

# REST framework class views
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
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

        if technicals:
            for tech in technicals:
                if tech in SUPPORTS:
                    f = getattr(dy.techie, tech)
                    df = f(df, config[tech].get('period'), config[tech].get('col'))
            return df.dropna()

        return df


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
            # elif '!' in id_:
            #     id_ = id_.replace('!', '')
            #     df = dy.get_cont_contract(id_, 1, '2000-01-01', '2100-01-01', name=id_)
            elif id_ in ['hrc_china_fob']:
                df = dy.get_data(id_, id_, frm=start, to=end, conversion=('USD', 'CNY'))
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
        weight = self.parse('weight')
        name = list()
        config = dict()
        if technicals:
            for tech in technicals:
                tech_name, period = tech.split('_')
                name.append(tech_name)
                config[tech_name] = {'period': int(period), 'col': 'spread'}

        df = self.parse_query()
        id0, id1 = self._get_ids()
        if weight:
            df[id0] = df[id0] * float(weight[0])
            df[id1] = df[id1] * float(weight[1])
        df['spread'] = df[id0] - df[id1]
        if technicals:
            df = self._handle_techincal(name, df, config=config)
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
        cadf = dy.adfuller(reg.result.resid)
        if cadf[0] <= cadf[4]['5%']:
            boolean = 'likely'
        else:
            boolean = 'unlikely'
        if boolean == 'likely':
            period = dy.half_life(reg.result.resid)
        else:
            period = 'N.A.'
        data = {
            'package': {
                'k': reg.result.params[1],
                'b': reg.result.params[0],
                'rsqr': reg.result.rsquared,
                'std': reg.result.resid.std(),
                'reversion': boolean,
                'period': period,
            },
            'data': df.to_dict(orient='records')
        }
        return Response(data)


class LogAPI(APIView):
    def get(self, request, format=None):
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect('/plotting/logs/')
        return Response(status=status.HTTP_400_BAD_REQUEST)


#############################################################################################
# Views
#############################################################################################
class Charter(APIBase):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/index.html'

    def get(self, request):
        with open('config.json', 'r') as f:
            pairs = json.load(f)
        pairs = json.dumps(pairs)
        return Response({'pairs': pairs})


class Detail(APIBase):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/detail.html'

    def get(self, request):
        pair = self.request.query_params.get('id', '')
        start = self.request.query_params.get('start', '')
        end = self.request.query_params.get('end', '')
        logs = Log.objects.filter(pair=pair)
        serializer = LogSerializer(logs, many=True)
        content = JSONRenderer().render(serializer.data)
        return Response({
            'pair': pair,
            'start':start,
            'end': end,
            'logs': content,
        })


##############################################################################################
# Dev
##############################################################################################
class Dev(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'plotting/dev.html'

    def get(self, request, format=None):
        with open('C:/Users/j291414/Desktop/test.json', 'r') as f:
            test = json.load(f)
        test = json.dumps(test)
        return Response({'context': test})


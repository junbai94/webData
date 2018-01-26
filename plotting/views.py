# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404
from .models import FutDaily
from .serializers import FutDailySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class FutDetail(APIView):
    def get_contract(self, instID):
        try:
            return FutDaily.objects.filter(instID=instID)
        except FutDaily.DoesNotExist:
            return Http404


    def get(self, request, instID, format=None):
        fut = self.get_contract(instID)
        serializer = FutDailySerializer(fut, many=True)
        return Response(serializer.data)


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Snippet
from .serializers import SnippetSerializer
from rest_framework import generics


class SnippetList(generics.ListAPIView):
    serializer_class = SnippetSerializer

    def get_queryset(self):
        queryset = Snippet.objects.all()
        pk = self.request.query_params.get('pk', None)
        if pk:
            queryset = queryset.filter(pk=pk)
        return queryset


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer


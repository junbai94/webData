# -*- coding: utf-8 -*-
"""
Created on 1/27/2018 3:14 PM

@author: Jimmy

Script description
"""


from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^snippets/$', views.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
    url(r'^index/$', views.Index.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
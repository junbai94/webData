from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.DataList.as_view()),
    url(r'^index/$', views.Charter.as_view(), name='index'),
    url(r'^spread/$', views.FutSpread.as_view()),
    url(r'^detail/$', views.Detail.as_view()),
    url(r'^regression/$', views.FutRegression.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^futdaily/(?P<instID>[0-9]+)/$', views.FutDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^compounds/$', CompoundList.as_view()),
    url(r'^compounds/(?P<pk>[0-9]+)/$', CompoundDetails.as_view(), name='compound-detail'),
)

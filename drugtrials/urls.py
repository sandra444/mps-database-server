from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # User can view their studies
    url(r'^drugtrials/$', DrugTrialList.as_view(), name='drugtrial_list'),
)

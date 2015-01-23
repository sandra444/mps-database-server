from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # User can view their studies
    url(r'^drugtrials/$', DrugTrialList.as_view(), name='drugtrial_list'),
    url(r'^drugtrials/(?P<pk>[0-9]+)/$', drug_trial_detail, name='drugtrial_detail'),
)

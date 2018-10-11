from django.conf.urls import url
from .views import (
    DrugTrialList,
    DrugTrialDetail,
    AdverseEventsList,
    AdverseEventDetail,
    CompareAdverseEvents
)
import drugtrials.ajax

urlpatterns = [
    # Proposed URLS:
    # User can view drugtrials
    url(r'^drugtrials/$', DrugTrialList.as_view(), name='drugtrial_list'),
    url(r'^drugtrials/(?P<pk>[0-9]+)/$', DrugTrialDetail.as_view(), name='drugtrial_detail'),
    # User can view adverse events
    url(r'^adverse_events/$', AdverseEventsList.as_view(), name='adverse_events_list'),
    url(r'^adverse_events/(?P<pk>[0-9]+)/$', AdverseEventDetail.as_view(), name='adverse_events_details'),
    url(r'^compare_adverse_events/$', CompareAdverseEvents.as_view(), name='compare_adverse_events'),

    # Revise URL
    url(r'^drugtrials_ajax/$', drugtrials.ajax.ajax)
]

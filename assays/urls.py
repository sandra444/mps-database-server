from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # User can view their studies
    url(r'^assays/user_index/$', UserIndex.as_view(), name='user_index'),
    # User can view all group studies
    url(r'^assays/group_index/$', GroupIndex.as_view(), name='group_index'),
    # # The main page for a study
    # url(r'^assays/(?P<study_id>d+)/$', XXX),
    # # Change pages for respective models
    # url(r'^assays/(?P<study_id>d+)/assaychipsetup/?P<setup_id>d+/$', XXX),
    # url(r'^assays/(?P<study_id>d+)/assaychipreadout/?P<readout_id>d+/$', XXX),
    # url(r'^assays/(?P<study_id>d+)/assaytestresult/?P<result_id>d+/$', XXX),
    # # Add pages for respective models
    # url(r'^assays/(?P<study_id>d+)/assaychipsetup/add/$', XXX),
    # url(r'^assays/(?P<study_id>d+)/assaychipreadout/add/$', XXX),
    # url(r'^assays/(?P<study_id>d+)/assaytestresult/add/$', XXX),

    # Original URLS: Add views to be replaced by new interface
    # TODO limit list and detail views to unrestricted models
    url(r'^assays/organchipstudy/$', AssayRunList.as_view()),
    #url(r'^assays/organchipstudy/add$', AssayRunAdd.as_view()),
    url(r'^assays/organchipstudy/(?P<pk>[0-9]+)/$', AssayRunDetail.as_view(), name='study-detail'),

    url(r'^assays/assaychipsetup/$', AssayChipSetupList.as_view()),
    #url(r'^assays/assaychipsetup/add$', AssayChipSetupAdd.as_view()),
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/$', AssayChipSetupDetail.as_view(), name='setup-detail'),

    url(r'^assays/assaychipreadout/$', AssayChipReadoutList.as_view()),
    #url(r'^assays/assaychipreadout/add$', AssayChipReadoutAdd.as_view()),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/$', AssayChipReadoutDetail.as_view(), name='readout-detail'),

    url(r'^assays/assaytestresult/$', AssayTestResultList.as_view()),
    #url(r'^assays/assaytestresult/add$', AssayTestResultAdd.as_view()),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/$', AssayTestResultDetail.as_view(), name='result-detail'),
)

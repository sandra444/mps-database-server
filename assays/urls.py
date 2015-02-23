from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # User can view their studies
    url(r'^assays/user_index/$', UserIndex.as_view(), name='user_index'),
    # User can view all group studies
    url(r'^assays/group_index/$', GroupIndex.as_view(), name='group_index'),
    # The main page for a study
    url(r'^assays/(?P<study_id>[0-9]+)/$', StudyIndex.as_view(), name='study_index'),
    # Update page for studies
    url(r'^assays/(?P<pk>[0-9]+)/update/$', AssayRunUpdate.as_view(), name='study-update'),
    # Delete view for studies
    url(r'^assays/(?P<pk>[0-9]+)/delete/$', AssayRunDelete.as_view(), name='study-delete'),
    # # Change pages for respective models
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/update/$', AssayChipSetupUpdate.as_view(), name='setup_update'),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/update/$', AssayChipReadoutUpdate.as_view(), name='readout_update'),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/update/$', AssayTestResultUpdate.as_view(), name='result_update'),
    # # Add pages for respective models
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipsetup/add/$', AssayChipSetupAdd.as_view(), name='setup_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipreadout/add/$', AssayChipReadoutAdd.as_view(), name='readout_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaytestresult/add/$', AssayTestResultAdd.as_view(), name='result_add'),

    # Original URLS: Add views to be replaced by new interface
    # TODO limit list and detail views to unrestricted models
    url(r'^assays/organchipstudy/$', AssayRunList.as_view(), name='study_list'),
    url(r'^assays/organchipstudy/add/$', AssayRunAdd.as_view(), name='study_add'),
    url(r'^assays/organchipstudy/(?P<pk>[0-9]+)/$', AssayRunDetail.as_view(), name='study_detail'),

    url(r'^assays/assaychipsetup/$', AssayChipSetupList.as_view(), name='setup_list'),
    #url(r'^assays/assaychipsetup/add$', AssayChipSetupAdd.as_view()),
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/$', AssayChipSetupDetail.as_view(), name='setup_detail'),

    url(r'^assays/assaychipreadout/$', AssayChipReadoutList.as_view(), name='readout_list'),
    #url(r'^assays/assaychipreadout/add$', AssayChipReadoutAdd.as_view()),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/$', AssayChipReadoutDetail.as_view(), name='readout_detail'),

    url(r'^assays/assaytestresult/$', AssayTestResultList.as_view(), name='result_list'),
    #url(r'^assays/assaytestresult/add$', AssayTestResultAdd.as_view()),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/$', AssayTestResultDetail.as_view(), name='result_detail'),
)

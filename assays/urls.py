from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    # User can view their studies
    url(r'^assays/user_index/$', UserIndex.as_view(), name='user_index'),
    # User can view all group studies
    url(r'^assays/group_index/$', GroupIndex.as_view(), name='group_index'),
    # The main page for a study
    url(r'^assays/(?P<pk>[0-9]+)/$', StudyIndex.as_view(), name='study_index'),
    # Update page for studies
    url(r'^assays/(?P<pk>[0-9]+)/update/$', AssayRunUpdate.as_view(), name='study-update'),
    # Delete view for studies
    url(r'^assays/(?P<pk>[0-9]+)/delete/$', AssayRunDelete.as_view(), name='study-delete'),
    # # Change pages for respective models
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/update/$', AssayChipSetupUpdate.as_view(), name='setup_update'),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/update/$', AssayChipReadoutUpdate.as_view(), name='readout_update'),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/update/$', AssayTestResultUpdate.as_view(), name='result_update'),

    url(r'^assays/assaydevicesetup/(?P<pk>[0-9]+)/update/$', AssayDeviceSetupUpdate.as_view(), name='plate_setup_update'),
    url(r'^assays/assaydevicereadout/(?P<pk>[0-9]+)/update/$', AssayDeviceReadoutUpdate.as_view(), name='plate_readout_update'),

    # # Add pages for respective models
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipsetup/add/$', AssayChipSetupAdd.as_view(), name='setup_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipreadout/add/$', AssayChipReadoutAdd.as_view(), name='readout_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaytestresult/add/$', AssayTestResultAdd.as_view(), name='result_add'),

    url(r'^assays/(?P<study_id>[0-9]+)/assaydevicesetup/add/$', AssayDeviceSetupAdd.as_view(), name='plate_setup_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaydevicereadout/add/$', AssayDeviceReadoutAdd.as_view(), name='plate_readout_add'),

    # # Delete pages for respective models
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/delete/$', AssayChipSetupDelete.as_view(), name='setup_delete'),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/delete/$', AssayChipReadoutDelete.as_view(), name='readout_delete'),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/delete/$', AssayTestResultDelete.as_view(), name='result_delete'),

    url(r'^assays/assaydevicesetup/(?P<pk>[0-9]+)/delete/$', AssayDeviceSetupDelete.as_view(), name='plate_setup_delete'),
    url(r'^assays/assaydevicereadout/(?P<pk>[0-9]+)/delete/$', AssayDeviceReadoutDelete.as_view(), name='plate_readout_delete'),

    url(r'^assays/studyconfiguration/$', StudyConfigurationList.as_view(), name='studyconfiguration_list'),
    url(r'^assays/studyconfiguration/add/$', StudyConfigurationAdd.as_view(), name='studyconfiguration_add'),
    url(r'^assays/studyconfiguration/(?P<pk>[0-9]+)/$', StudyConfigurationUpdate.as_view(), name='studyconfiguration_update'),

    url(r'^assays/assaylayout/$', AssayLayoutList.as_view(), name='assaylayout_list'),
    url(r'^assays/assaylayout/add/$', AssayLayoutAdd.as_view(), name='assaylayout_add'),
    url(r'^assays/assaylayout/(?P<pk>[0-9]+)/$', AssayLayoutUpdate.as_view(), name='assaylayout_update'),
    url(r'^assays/assaylayout/(?P<pk>[0-9]+)/delete/$', AssayLayoutDelete.as_view(), name='assaylayout_delete'),

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

    url(r'^assays/assaydevicesetup/$', AssayDeviceSetupList.as_view(), name='plate_setup_list'),
    url(r'^assays/assaydevicesetup/(?P<pk>[0-9]+)/$', AssayDeviceSetupDetail.as_view(), name='plate_setup_detail'),

    url(r'^assays/assaydevicereadout/$', AssayDeviceReadoutList.as_view(), name='plate_readout_list'),
    url(r'^assays/assaydevicereadout/(?P<pk>[0-9]+)/$', AssayDeviceReadoutDetail.as_view(), name='plate_readout_detail'),
)

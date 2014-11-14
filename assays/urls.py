from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    url(r'^assays/organchipstudy/$', AssayRunList.as_view()),
    url(r'^assays/organchipstudy/add$', AssayRunAdd.as_view()),
    url(r'^assays/organchipstudy/(?P<pk>[0-9]+)/$', AssayRunDetail.as_view(), name='study-detail'),

    url(r'^assays/assaychipsetup/$', AssayChipSetupList.as_view()),
    url(r'^assays/assaychipsetup/add$', AssayChipSetupAdd.as_view()),
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/$', AssayChipSetupDetail.as_view(), name='setup-detail'),

    url(r'^assays/assaychipreadout/$', AssayChipReadoutList.as_view()),
    url(r'^assays/assaychipreadout/add$', AssayChipReadoutAdd.as_view()),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/$', AssayChipReadoutDetail.as_view(), name='readout-detail'),

    url(r'^assays/assaytestresult/$', AssayTestResultList.as_view()),
    url(r'^assays/assaytestresult/add$', AssayTestResultAdd.as_view()),
    url(r'^assays/assaytestresult/(?P<pk>[0-9]+)/$', AssayTestResultDetail.as_view(), name='result-detail'),
)

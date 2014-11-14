from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    url(r'^assays/assaychipreadout/$', AssayChipReadoutList.as_view()),
    url(r'^assays/assaychipreadout/add$', AssayChipReadoutAdd.as_view()),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/$', AssayChipReadoutDetail.as_view(), name='readout-detail'),
    url(r'^assays/organchipstudy/$', AssayRunList.as_view()),
    url(r'^assays/organchipstudy/add$', AssayRunAdd.as_view()),
    url(r'^assays/organchipstudy/(?P<pk>[0-9]+)/$', AssayRunDetail.as_view(), name='study-detail'),
)

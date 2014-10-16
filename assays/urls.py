from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    url(r'^assays/runs/$', RunList.as_view()),
    url(r'^assays/new_read/$', manage_readouts),
    url(r'^assays/reads/$', AssayChipReadoutList.as_view()),
)

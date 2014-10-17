from django.conf.urls import patterns, url
from assays.views import *

urlpatterns = patterns('',
    url(r'^assays/runs/$', AssayRunList.as_view()),
    url(r'^assays/new_read/$', add_readout),
    url(r'^assays/reads/$', AssayChipReadoutList.as_view()),
)

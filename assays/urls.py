from django.conf.urls import patterns, url
from assays.views import RunList, manage_readouts

urlpatterns = patterns('',
    url(r'^assays/runs/$', RunList.as_view()),
    url(r'^assays/read/$', manage_readouts),
)

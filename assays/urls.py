from django.conf.urls import patterns, url
from assays.views import RunList

urlpatterns = patterns('',
    url(r'^assays/runs/$', RunList.as_view()),
)

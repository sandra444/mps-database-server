from django.conf.urls import url
from .views import (
    CompoundsList,
    CompoundsAdd,
    CompoundsReport,
    CompoundsDetail,
    CompoundsUpdate
)
import compounds.ajax

urlpatterns = [
    url(r'^compounds/$', CompoundsList.as_view(), name='compound-list'),
    url(r'^compounds/add/$', CompoundsAdd.as_view(), name='compound-add'),
    url(r'^compounds/report/$', CompoundsReport.as_view(), name='compound-report'),
    url(r'^compounds/(?P<pk>[0-9]+)/$', CompoundsDetail.as_view(), name='compound-detail'),
    url(r'^compounds/(?P<pk>[0-9]+)/update/$', CompoundsUpdate.as_view(), name='compound-update'),
    url(r'^compounds_ajax/$', compounds.ajax.ajax),
]

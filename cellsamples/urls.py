from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # specify cellsample if we decide to also let users add cell type etc.
    url(r'^cellsamples/cellsample/add/$', CellSampleAdd.as_view(), name='cellsample_add'),
    url(r'^cellsamples/cellsample/$', CellSampleList.as_view(), name='cellsample_list'),
    url(r'^cellsamples/cellsample/(?P<pk>[0-9]+)/$', CellSampleUpdate.as_view(), name='cellsample_update'),
)

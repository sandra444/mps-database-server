from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    # Proposed URLS:
    # specify cellsample if we decide to also let users add cell type etc.
    url(r'^cellsamples/cellsample/add/$', CellSampleAdd.as_view(), name='cellsample_add'),
    url(r'^cellsamples/cellsample/$', CellSampleList.as_view(), name='cellsample_list'),
    url(r'^cellsamples/cellsample/(?P<pk>[0-9]+)/$', CellSampleUpdate.as_view(), name='cellsample_update'),
    url(r'^cellsamples/celltype/add/$', CellTypeAdd.as_view(), name='celltype_add'),
    url(r'^cellsamples/celltype/$', CellTypeList.as_view(), name='celltype_list'),
    url(r'^cellsamples/celltype/(?P<pk>[0-9]+)/$', CellTypeUpdate.as_view(), name='celltype_update'),
    url(r'^cellsamples/cellsubtype/add/$', CellSubtypeAdd.as_view(), name='cellsubtype_add'),
    url(r'^cellsamples/cellsubtype/$', CellSubtypeList.as_view(), name='cellsubtype_list'),
    url(r'^cellsamples/cellsubtype/(?P<pk>[0-9]+)/$', CellSubtypeUpdate.as_view(), name='cellsubtype_update'),
)

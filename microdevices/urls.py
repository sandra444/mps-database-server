from django.conf.urls import patterns, url
from microdevices.views import *

urlpatterns = patterns('',
    # User can view their studies
    url(r'^microdevices/$', microdevice_list, name='microdevice-list'),
    url(r'^microdevices/device/(?P<pk>[0-9]+)/$', MicrodeviceDetail.as_view(), name='microdevice-detail'),
    url(r'^microdevices/model/(?P<pk>[0-9]+)/$', organ_model_detail, name='model-detail'),
    url(r'^microdevices/device/add/$', MicrodeviceAdd.as_view(), name='microdevice-add'),
    url(r'^microdevices/model/add/$', OrganModelAdd.as_view(), name='model-add'),
    url(r'^microdevices/device/(?P<pk>[0-9]+)/update/$', MicrodeviceUpdate.as_view(), name='microdevice-update'),
    url(r'^microdevices/model/(?P<pk>[0-9]+)/update/$', OrganModelUpdate.as_view(), name='model-update'),
)

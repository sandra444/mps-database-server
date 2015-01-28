from django.conf.urls import patterns, url
from microdevices.views import *

urlpatterns = patterns('',
    # User can view their studies
    url(r'^microdevices/$', microdevice_list, name='microdevice-list'),
    url(r'^microdevices/(?P<pk>[0-9]+)/$', MicrodeviceDetail.as_view(), name='microdevice-detail'),
)

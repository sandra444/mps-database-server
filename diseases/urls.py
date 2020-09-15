from django.conf.urls import url
from .views import (
    DiseaseList,
    DiseaseOverview,
    DiseaseClinicalData,
    DiseaseBiology,
    DiseaseModel
)

urlpatterns = [
    url(r'^diseases/$', DiseaseList.as_view()),
    url(r'^diseases/(?P<pk>[0-9]+)/$', DiseaseOverview.as_view()),
    url(r'^diseases/(?P<pk>[0-9]+)/clinicaldata/$', DiseaseClinicalData.as_view()),
    url(r'^diseases/(?P<pk>[0-9]+)/biology/$', DiseaseBiology.as_view()),
    url(r'^diseases/(?P<pk>[0-9]+)/model/$', DiseaseModel.as_view())
]

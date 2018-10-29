from django.conf.urls import url
from assays.views import (
    AssayStudyEditableList,
    AssayStudyIndex,
    AssayStudyUpdate,
    AssayStudyDelete,
    AssayStudySummary,
    AssayStudyData,
    AssayStudyDataUpload,
    AssayStudyList,
    AssayStudyAdd,
    AssayMatrixItemDetail,
    AssayMatrixItemUpdate,
    AssayMatrixItemDelete,
    AssayStudyConfigurationList,
    AssayStudyConfigurationAdd,
    AssayStudyConfigurationUpdate,
    AssayMatrixAdd,
    AssayMatrixDetail,
    AssayMatrixUpdate,
    AssayMatrixDelete,
    AssayStudySignOff,
    AssayStudyReproducibility,
    AssayStudyImages,
    AssayTargetList,
    AssayTargetDetail,
    AssayMethodList,
    AssayMethodDetail,
    AssayPhysicalUnitsList,
    AssaySampleLocationList,
    GraphingReproducibilityFilterView,
    AssayInterStudyReproducibility,
    AssayStudyDataPlots,
    AssayDataFromFilters,
    AssayStudySetAdd,
    AssayStudySetUpdate,
    AssayStudySetDataPlots,
    AssayStudySetReproducibility,
    AssayStudySetList,
)
import assays.ajax

urlpatterns = [
    # User can view their studies
    # url(r'^assays/user_index/$', UserIndex.as_view(), name='user_index'),
    # User can view all Editable Studies
    # url(r'^assays/editable_studies/$', GroupIndex.as_view(), name='editable_studies'),
    url(r'^assays/assaystudy/editable_studies/$', AssayStudyEditableList.as_view(), name='editable_study_list'),
    # The main page for a study
    # url(r'^assays/(?P<pk>[0-9]+)/$', StudyIndex.as_view(), name='study_index'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/$', AssayStudyIndex.as_view(), name='assay_study_index'),
    # Update page for studies
    # url(r'^assays/(?P<pk>[0-9]+)/update/$', AssayRunUpdate.as_view(), name='study-update'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/update/$', AssayStudyUpdate.as_view(), name='assay_study_update'),
    # Delete view for studies
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/delete/$', AssayStudyDelete.as_view(), name='study-delete'),
    # Summary view for studies
    # url(r'^assays/(?P<pk>[0-9]+)/summary/$', AssayRunSummary.as_view(), name='study-summary'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/summary/$', AssayStudySummary.as_view(), name='assay_study_summary'),
    # # All data for a study
    # url(r'^assays/(?P<pk>[0-9]+)/data/$', ReturnStudyData.as_view(), name='study-data'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/data/$', AssayStudyData.as_view(), name='assay_study_data'),
    # # Bulk Readout Upload for Studies
    # url(r'^assays/(?P<pk>[0-9]+)/bulk/$', ReadoutBulkUpload.as_view(), name='readout-bulk-upload'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/upload/$', AssayStudyDataUpload.as_view(), name='assay_study_upload'),

    # NEW_TO_BE_REVISED
    url(r'^assays/assaystudy/$', AssayStudyList.as_view(), name='assay_study_list'),
    url(r'^assays/assaystudy/add/$', AssayStudyAdd.as_view(), name='assay_study_add'),

    url(r'^assays/assaymatrixitem/(?P<pk>[0-9]+)/$', AssayMatrixItemDetail.as_view(), name='assay_matrix_item_detail'),
    url(r'^assays/assaymatrixitem/(?P<pk>[0-9]+)/update/$', AssayMatrixItemUpdate.as_view(), name='assay_matrix_item_update'),
    url(r'^assays/assaymatrixitem/(?P<pk>[0-9]+)/delete/$', AssayMatrixItemDelete.as_view(), name='assay_matrix_item_delete'),

    url(r'^assays/studyconfiguration/$', AssayStudyConfigurationList.as_view(), name='studyconfiguration_list'),
    url(r'^assays/studyconfiguration/add/$', AssayStudyConfigurationAdd.as_view(), name='studyconfiguration_add'),
    url(r'^assays/studyconfiguration/(?P<pk>[0-9]+)/$', AssayStudyConfigurationUpdate.as_view(), name='studyconfiguration_update'),

    # Add a matrix
    url(r'^assays/assaystudy/(?P<study_id>[0-9]+)/assaymatrix/add/$', AssayMatrixAdd.as_view(), name='assay_matrix_add'),
    url(r'^assays/assaymatrix/(?P<pk>[0-9]+)/$', AssayMatrixDetail.as_view(), name='assay_matrix_detail'),
    url(r'^assays/assaymatrix/(?P<pk>[0-9]+)/update/$', AssayMatrixUpdate.as_view(), name='assay_matrix_update'),
    url(r'^assays/assaymatrix/(?P<pk>[0-9]+)/delete/$', AssayMatrixDelete.as_view(), name='assay_matrix_delete'),

    url(r'^assays/studyconfiguration/$', AssayStudyConfigurationList.as_view(), name='studyconfiguration_list'),
    url(r'^assays/studyconfiguration/add/$', AssayStudyConfigurationAdd.as_view(), name='studyconfiguration_add'),
    url(r'^assays/studyconfiguration/(?P<pk>[0-9]+)/$', AssayStudyConfigurationUpdate.as_view(), name='studyconfiguration_update'),

    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/reproducibility/$', AssayStudyReproducibility.as_view(), name='assay_study_reproducibility'),

    # Images
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/images/$', AssayStudyImages.as_view(), name='study-images'),

    # Targets and Methods
    url(r'^assays/targets/$', AssayTargetList.as_view(), name='assay-targets-list'),
    url(r'^assays/targets/(?P<pk>[0-9]+)/$', AssayTargetDetail.as_view(), name='assay-targets-detail'),
    url(r'^assays/methods/$', AssayMethodList.as_view(), name='assay-methods-list'),
    url(r'^assays/methods/(?P<pk>[0-9]+)/$', AssayMethodDetail.as_view(), name='assay-methods-detail'),

    # Units
    url(r'^assays/units/$', AssayPhysicalUnitsList.as_view(), name='assay-units-list'),

    # Sample Locations
    url(r'^assays/locations/$', AssaySampleLocationList.as_view(), name='assay-locations-list'),

    # Location for assay filter
    url(r'^assays/graphing_reproducibility/$', GraphingReproducibilityFilterView.as_view(), name='graphing-reproducibility'),
    url(r'^assays/assay_interstudy_reproducibility/$', AssayInterStudyReproducibility.as_view(), name='interstudy-reproducibility'),
    url(r'^assays/assaystudy_data_plots/$', AssayStudyDataPlots.as_view(), name='assaystudy-data-plots'),

    # Study Set urls
    url(
        r'^assays/assaystudyset/add/$',
        AssayStudySetAdd.as_view(),
        name='assaystudyset-add'
    ),
    url(
        r'^assays/assaystudyset/(?P<pk>[0-9]+)/update/$',
        AssayStudySetUpdate.as_view(),
        name='assaystudyset-add'
    ),
    url(
        r'^assays/assaystudyset/(?P<pk>[0-9]+)/$',
        AssayStudySetDataPlots.as_view(),
        name='assaystudyset-data-plots'
    ),
    url(
        r'^assays/assaystudyset/(?P<pk>[0-9]+)/reproducibility/$',
        AssayStudySetReproducibility.as_view(),
        name='assaystudyset-reproducibility'
    ),
    url(
        r'^assays/assaystudyset/$',
        AssayStudySetList.as_view(),
        name='assaystudyset-list'
    ),

    # Data from filters
    url(r'^assays/data_from_filters/$', AssayDataFromFilters.as_view(), name='data-from-filters'),

    # Ajax
    url(r'^assays_ajax/$', assays.ajax.ajax),
]

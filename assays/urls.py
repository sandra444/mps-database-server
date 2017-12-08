from django.conf.urls import patterns, url
# TODO NO WILDCARDS PLEASE
from assays.views import *

urlpatterns = patterns('',
    # User can view their studies
    # url(r'^assays/user_index/$', UserIndex.as_view(), name='user_index'),
    # User can view all Editable Studies
    url(r'^assays/editable_studies/$', GroupIndex.as_view(), name='editable_studies'),
    url(r'^assays/assaystudy/editable_assay_studies/$', AssayStudyEditableList.as_view(), name='editable_study_list'),
    # The main page for a study
    url(r'^assays/(?P<pk>[0-9]+)/$', StudyIndex.as_view(), name='study_index'),
    url(r'^assays/assaystudy/(?P<pk>[0-9]+)/$', AssayStudyIndex.as_view(), name='assay_study_index'),
    # Update page for studies
    url(r'^assays/(?P<pk>[0-9]+)/update/$', AssayStudyUpdate.as_view(), name='study-update'),
    # Delete view for studies
    # url(r'^assays/(?P<pk>[0-9]+)/delete/$', AssayStudyDelete.as_view(), name='study-delete'),
    # Summary view for studies
    url(r'^assays/(?P<pk>[0-9]+)/summary/$', AssayRunSummary.as_view(), name='study-summary'),
    # # All data for a study
    url(r'^assays/(?P<pk>[0-9]+)/data/$', ReturnStudyData.as_view(), name='study-data'),
    # # Bulk Readout Upload for Studies
    url(r'^assays/(?P<pk>[0-9]+)/bulk/$', ReadoutBulkUpload.as_view(), name='readout-bulk-upload'),

    # NEW_TO_BE_REVISED
    url(r'^assays/assaystudy/$', AssayStudyList.as_view(), name='assay_study_list'),
    url(r'^assays/assaystudy/add/$', AssayStudyAdd.as_view(), name='assay_study_add'),

    url(r'^assays/assaymatrixitem/(?P<pk>[0-9]+)/update/$', AssayMatrixItemUpdate.as_view(), name='assay_study_list'),

    url(r'^assays/studyconfiguration/$', StudyConfigurationList.as_view(), name='studyconfiguration_list'),
    url(r'^assays/studyconfiguration/add/$', StudyConfigurationAdd.as_view(), name='studyconfiguration_add'),
    url(r'^assays/studyconfiguration/(?P<pk>[0-9]+)/$', StudyConfigurationUpdate.as_view(), name='studyconfiguration_update'),

    # Add a matrix
    url(r'^assays/(?P<study_id>[0-9]+)/assaymatrix/add/$', AssayMatrixAdd.as_view(), name='assay_matrix_add'),
    url(r'^assays/assaymatrix/(?P<pk>[0-9]+)/$', AssayMatrixUpdate.as_view(), name='assay_matrix_update'),

    # DEPRECATED >>
    # Change pages for respective models
    # Change access for a study DEPRECATED
    # url(r'^assays/(?P<pk>[0-9]+)/access/$', AssayRunUpdateAccess.as_view(), name='study-access'),
    # Sign off
    url(r'^assays/(?P<pk>[0-9]+)/sign_off/$', AssayRunSignOff.as_view(), name='study-sign_off'),
    # # Change pages for respective models
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/update/$', AssayChipSetupUpdate.as_view(), name='setup_update'),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/update/$', AssayChipReadoutUpdate.as_view(), name='readout_update'),
    url(r'^assays/assaychiptestresult/(?P<pk>[0-9]+)/update/$', AssayChipTestResultUpdate.as_view(), name='result_update'),

    # Deprecated
    # url(r'^assays/assayplatesetup/(?P<pk>[0-9]+)/update/$', AssayPlateSetupUpdate.as_view(), name='plate_setup_update'),
    # url(r'^assays/assayplatereadout/(?P<pk>[0-9]+)/update/$', AssayPlateReadoutUpdate.as_view(), name='plate_readout_update'),
    # url(r'^assays/assayplatetestresult/(?P<pk>[0-9]+)/update/$', AssayPlateTestResultUpdate.as_view(), name='plate_result_update'),

    # # Add pages for respective models
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipsetup/add/$', AssayChipSetupAdd.as_view(), name='setup_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaychipreadout/add/$', AssayChipReadoutAdd.as_view(), name='readout_add'),
    url(r'^assays/(?P<study_id>[0-9]+)/assaychiptestresult/add/$', AssayChipTestResultAdd.as_view(), name='result_add'),

    # Deprecated
    # url(r'^assays/(?P<study_id>[0-9]+)/assayplatesetup/add/$', AssayPlateSetupAdd.as_view(), name='plate_setup_add'),
    # url(r'^assays/(?P<study_id>[0-9]+)/assayplatereadout/add/$', AssayPlateReadoutAdd.as_view(), name='plate_readout_add'),
    # url(r'^assays/(?P<study_id>[0-9]+)/assayplatetestresult/add/$', AssayPlateTestResultAdd.as_view(), name='plate_result_add'),

    # # Delete pages for respective models
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/delete/$', AssayChipSetupDelete.as_view(), name='setup_delete'),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/delete/$', AssayChipReadoutDelete.as_view(), name='readout_delete'),
    url(r'^assays/assaychiptestresult/(?P<pk>[0-9]+)/delete/$', AssayChipTestResultDelete.as_view(), name='result_delete'),

    # DEPRECATED <<
    # Deprecated
    # url(r'^assays/assayplatesetup/(?P<pk>[0-9]+)/delete/$', AssayPlateSetupDelete.as_view(), name='plate_setup_delete'),
    # url(r'^assays/assayplatereadout/(?P<pk>[0-9]+)/delete/$', AssayPlateReadoutDelete.as_view(), name='plate_readout_delete'),
    # url(r'^assays/assayplatetestresult/(?P<pk>[0-9]+)/delete/$', AssayPlateTestResultDelete.as_view(), name='plate_result_delete'),

    url(r'^assays/studyconfiguration/$', StudyConfigurationList.as_view(), name='studyconfiguration_list'),
    url(r'^assays/studyconfiguration/add/$', StudyConfigurationAdd.as_view(), name='studyconfiguration_add'),
    url(r'^assays/studyconfiguration/(?P<pk>[0-9]+)/$', StudyConfigurationUpdate.as_view(), name='studyconfiguration_update'),

    # Deprecated
    # url(r'^assays/assaylayout/$', AssayLayoutList.as_view(), name='assaylayout_list'),
    # url(r'^assays/assaylayout/add/$', AssayLayoutAdd.as_view(), name='assaylayout_add'),
    # url(r'^assays/assaylayout/(?P<pk>[0-9]+)/$', AssayLayoutUpdate.as_view(), name='assaylayout_update'),
    # url(r'^assays/assaylayout/(?P<pk>[0-9]+)/delete/$', AssayLayoutDelete.as_view(), name='assaylayout_delete'),

    # DEPRECATED
    url(r'^assays/study/$', AssayRunList.as_view(), name='study_list'),
    url(r'^assays/study/add/$', AssayRunAdd.as_view(), name='study_add'),
    # url(r'^assays/study/(?P<pk>[0-9]+)/$', AssayRunDetail.as_view(), name='study_detail'),

    # DEPRECATED >>
    url(r'^assays/assaychipsetup/$', AssayChipSetupList.as_view(), name='setup_list'),
    #url(r'^assays/assaychipsetup/add$', AssayChipSetupAdd.as_view()),
    url(r'^assays/assaychipsetup/(?P<pk>[0-9]+)/$', AssayChipSetupDetail.as_view(), name='setup_detail'),

    url(r'^assays/assaychipreadout/$', AssayChipReadoutList.as_view(), name='readout_list'),
    #url(r'^assays/assaychipreadout/add$', AssayChipReadoutAdd.as_view()),
    url(r'^assays/assaychipreadout/(?P<pk>[0-9]+)/$', AssayChipReadoutDetail.as_view(), name='readout_detail'),

    url(r'^assays/assaychiptestresult/$', AssayChipTestResultList.as_view(), name='result_list'),
    #url(r'^assays/assaychiptestresult/add$', AssayChipTestResultAdd.as_view()),
    url(r'^assays/assaychiptestresult/(?P<pk>[0-9]+)/$', AssayChipTestResultDetail.as_view(), name='result_detail'),

    # Deprecated
    # url(r'^assays/assayplatesetup/$', AssayPlateSetupList.as_view(), name='plate_setup_list'),
    # url(r'^assays/assayplatesetup/(?P<pk>[0-9]+)/$', AssayPlateSetupDetail.as_view(), name='plate_setup_detail'),
    #
    # url(r'^assays/assayplatereadout/$', AssayPlateReadoutList.as_view(), name='plate_readout_list'),
    # url(r'^assays/assayplatereadout/(?P<pk>[0-9]+)/$', AssayPlateReadoutDetail.as_view(), name='plate_readout_detail'),
    #
    # url(r'^assays/assayplatetestresult/$', AssayPlateTestResultList.as_view(), name='plate_result_list'),
    # url(r'^assays/assayplatetestresult/(?P<pk>[0-9]+)/$', AssayPlateTestResultDetail.as_view(), name='plate_result_detail'),
)

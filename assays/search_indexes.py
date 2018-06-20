#import datetime
from haystack import indexes
from .models import *


# class AssayRunIndex(indexes.SearchIndex, indexes.Indexable):
#     # Substring search is made possible by using EdgeNgramField/NgramField in lieu of CharField
#     # EdgeNgramfields are more efficient, but only can search based off of starts with
#     # NgramFields are less efficient, but are better at seeing if the index contains it at all
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     # However, is it in poor taste to apply it to the document?
#
#     # created_by = indexes.CharField(model_attr='created_by')
#     # created_on = indexes.DateTimeField(model_attr='created_on')
#
#     def get_model(self):
#         return AssayRun
#
#     # This is just to hide items posted "in the future"
#     # It was part of the Haystack "Getting Started" but is of little use to us
#     # However, filtering results with this function by some other means may be helpful
#     # def index_queryset(self, using=None):
#     #     """Used when the entire index for model is updated."""
#     #     return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
#
#
# class AssayChipSetupIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayChipSetup
#
#
# class AssayChipReadoutIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayChipReadout
#
#
# class AssayChipTestResultIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayChipTestResult
#
#
# class AssayStudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayStudyConfiguration
#
#
# class AssayPlateSetupIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayPlateSetup
#
#
# class AssayPlateReadoutIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayPlateReadout
#
#
# class AssayPlateTestResultIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayPlateTestResult
#
#
# class AssayLayoutIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     group = indexes.CharField(model_attr='group')
#     restricted = indexes.CharField(model_attr='restricted')
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayLayout


class AssayStudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayStudyConfiguration


class AssayStudyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    permissions = indexes.NgramField(use_template=True, indexed=False)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayStudy

    def index_queryset(self, using=None):
        queryset = self.get_model().objects.all().prefetch_related(
            'assaystudystakeholder_set__group',
            'assaystudyassay_set__target',
            'assaystudyassay_set__method',
            'assaystudyassay_set__unit',
            'assaystudyassay_set__unit',
            'assaymatrixitem_set__assaysetupsetting_set__setting',
            'assaymatrixitem_set__assaysetupcell_set__cell_sample',
            'assaymatrixitem_set__assaysetupcell_set__density_unit',
            'assaymatrixitem_set__assaysetupcell_set__cell_sample__cell_type__organ',
            'assaymatrixitem_set__assaysetupcompound_set__compound_instance__compound',
            'assaymatrixitem_set__assaysetupcompound_set__concentration_unit',
            'assaymatrixitem_set__device',
            'assaymatrixitem_set__organ_model',
        )

        stakeholders = AssayStudyStakeholder.objects.filter(
            sign_off_required=False,
            signed_off_by_id=None
        )

        stakeholder_map = {}

        for stakeholder in stakeholders:
            stakeholder_map.update({
                stakeholder.study_id: True
            })

        for object in queryset:
            if object.id in stakeholder_map:
                object.stakeholder_approval = False
            else:
                object.stakeholder_approval = True

        return queryset


# Not sure if we want matrices anyway
# class AssayMatrixIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     permissions = indexes.NgramField(use_template=True, indexed=False)
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayMatrix
#
#     def index_queryset(self, using=None):
#         queryset = self.get_model().objects.all().prefetch_related(
#             # TODO
#         )
#
#         stakeholders = AssayStudyStakeholder.objects.filter(
#             sign_off_required=False,
#             signed_off_by_id=None
#         )
#
#         stakeholder_map = {}
#
#         for stakeholder in stakeholders:
#             stakeholder_map.update({
#                 stakeholder.study_id: True
#             })
#
#         for object in queryset:
#             if object.study_id in stakeholder_map:
#                 object.stakeholder_approval = False
#             else:
#                 object.stakeholder_approval = True
#
#         return queryset


# class AssayMatrixItemIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     permissions = indexes.NgramField(use_template=True, indexed=False)
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayMatrixItem
#
#     def index_queryset(self, using=None):
#         queryset = self.get_model().objects.all().prefetch_related(
#             'assaysetupsetting_set__setting',
#             'assaysetupcell_set__cell_sample',
#             'assaysetupcell_set__density_unit',
#             'assaysetupcell_set__cell_sample__cell_type__organ',
#             'assaysetupcompound_set__compound_instance__compound',
#             'assaysetupcompound_set__concentration_unit',
#             'device',
#             'organ_model',
#         )
#
#         stakeholders = AssayStudyStakeholder.objects.filter(
#             sign_off_required=False,
#             signed_off_by_id=None
#         )
#
#         stakeholder_map = {}
#
#         for stakeholder in stakeholders:
#             stakeholder_map.update({
#                 stakeholder.study_id: True
#             })
#
#         for object in queryset:
#             if object.study_id in stakeholder_map:
#                 object.stakeholder_approval = False
#             else:
#                 object.stakeholder_approval = True
#
#         return queryset

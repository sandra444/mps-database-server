#import datetime
from haystack import indexes
from .models import *
import os.path
from mps.settings import WHOOSH_INDEX


class AssayStudyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    permissions = indexes.NgramField(use_template=True, indexed=False)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayStudy

    def index_queryset(self, using=None):
        # NOTE: FOR THIS CHECK TO WORK PROPERLY, THE STUDIES MODEL MUST BE INDEXED FIRST
        # Somewhat evil way to discern whether this is to build an index
        if os.path.isfile(os.path.join(WHOOSH_INDEX, '_MAIN_0.toc')):
            queryset = self.get_model().objects.all().prefetch_related(
                'assaystudystakeholder_set__group',
                'assaystudyassay_set__target',
                'assaystudyassay_set__method',
                'assaystudyassay_set__unit',
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
        else:
            return super(AssayStudyIndex, self).index_queryset(using)


# Remove the study configuration index for now
# class AssayStudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayStudyConfiguration

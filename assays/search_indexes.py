#import datetime
from haystack import indexes
from .models import AssayStudy
# import os.path
# from mps.settings import WHOOSH_INDEX


class AssayStudyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    permissions = indexes.NgramField(use_template=True, indexed=False)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayStudy


# Remove the study configuration index for now
# class AssayStudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.NgramField(document=True, use_template=True)
#
#     rendered = indexes.CharField(use_template=True, indexed=False)
#
#     def get_model(self):
#         return AssayStudyConfiguration

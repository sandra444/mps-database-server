#import datetime
from haystack import indexes
from .models import *


class AssayRunIndex(indexes.SearchIndex, indexes.Indexable):
    # Substring search is made possible by using EdgeNgramField/NgramField in lieu of CharField
    # EdgeNgramfields are more efficient, but only can search based off of starts with
    # NgramFields are less efficient, but are better at seeing if the index contains it at all
    text = indexes.NgramField(document=True, use_template=True)

    group = indexes.CharField(model_attr='group')
    restricted = indexes.CharField(model_attr='restricted')

    rendered = indexes.CharField(use_template=True, indexed=False)

    # However, is it in poor taste to apply it to the document?

    # created_by = indexes.CharField(model_attr='created_by')
    # created_on = indexes.DateTimeField(model_attr='created_on')

    def get_model(self):
        return AssayRun

    # This is just to hide items posted "in the future"
    # It was part of the Haystack "Getting Started" but is of little use to us
    # However, filtering results with this function by some other means may be helpful
    # def index_queryset(self, using=None):
    #     """Used when the entire index for model is updated."""
    #     return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())


class AssayChipSetupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    group = indexes.CharField(model_attr='group')
    restricted = indexes.CharField(model_attr='restricted')

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayChipSetup


class AssayChipReadoutIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    group = indexes.CharField(model_attr='group')
    restricted = indexes.CharField(model_attr='restricted')

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayChipReadout


class AssayChipTestResultIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    group = indexes.CharField(model_attr='group')
    restricted = indexes.CharField(model_attr='restricted')

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return AssayChipTestResult


class StudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return StudyConfiguration


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

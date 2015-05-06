#import datetime
from haystack import indexes
from .models import *


class AssayRunIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    # Substring search is made possible by using EdgeNgramField in lieu of CharField
    # text = indexes.CharField(document=True, use_template=True)

    created_by = indexes.CharField(model_attr='created_by')
    group = indexes.CharField(model_attr='group')
    #created_on = indexes.DateTimeField(model_attr='created_on')

    def get_model(self):
        return AssayRun

    # This is just to hide items posted "in the future"
    # It was part of the Haystack "Getting Started" but is of little use to us
    # However, filtering results with this function by some other means may be helpful
    # def index_queryset(self, using=None):
    #     """Used when the entire index for model is updated."""
    #     return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())


class AssayChipSetupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    created_by = indexes.CharField(model_attr='created_by')
    group = indexes.CharField(model_attr='group')

    def get_model(self):
        return AssayChipSetup


class AssayChipReadoutIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    created_by = indexes.CharField(model_attr='created_by')
    group = indexes.CharField(model_attr='group')

    def get_model(self):
        return AssayChipReadout


class AssayTestResultIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    created_by = indexes.CharField(model_attr='created_by')
    group = indexes.CharField(model_attr='group')

    def get_model(self):
        return AssayTestResult


class StudyConfigurationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return StudyConfiguration

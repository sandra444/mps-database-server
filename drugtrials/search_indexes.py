from haystack import indexes
from .models import *


class OpenFDACompoundIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return OpenFDACompound

class DrugTrialIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return DrugTrial

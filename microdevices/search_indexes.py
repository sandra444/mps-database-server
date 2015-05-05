from haystack import indexes
from .models import *


class OrganModelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return OrganModel


class MicrodeviceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return Microdevice

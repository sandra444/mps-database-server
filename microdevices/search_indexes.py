from haystack import indexes
from .models import OrganModel, Microdevice


class OrganModelIndex(indexes.SearchIndex, indexes.Indexable):
    """Search index for Organ Models"""
    text = indexes.NgramField(document=True, use_template=True)
    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return OrganModel


class MicrodeviceIndex(indexes.SearchIndex, indexes.Indexable):
    """Search index for Microdevices"""
    text = indexes.NgramField(document=True, use_template=True)
    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return Microdevice

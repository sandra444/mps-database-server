from haystack import indexes
from .models import Compound


class CompoundIndex(indexes.SearchIndex, indexes.Indexable):
    """Search Index for Compounds"""
    text = indexes.NgramField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return Compound

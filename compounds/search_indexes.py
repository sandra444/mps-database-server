from haystack import indexes
from .models import *


class CompoundIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return Compound

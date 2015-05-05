from haystack import indexes
from .models import *

class CellSampleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return CellSample


class CellTypeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return CellType

from import_export import resources
from cellsamples.models import CellSample


class CellSampleResource(resources.ModelResource):

    class Meta(object):
        model = CellSample


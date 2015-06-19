from import_export import resources
from assays.models import AssayPlateReadout


class AssayPlateReadoutResource(resources.ModelResource):

    class Meta(object):
        model = AssayPlateReadout

from import_export import resources
from assays.models import AssayDeviceReadout


class AssayDeviceReadoutResource(resources.ModelResource):

    class Meta(object):
        model = AssayDeviceReadout

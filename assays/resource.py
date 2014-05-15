from import_export import resources
from assays.models import AssayDeviceReadout, AssayTest


class AssayDeviceReadoutResource(resources.ModelResource):

    class Meta(object):
        model = AssayDeviceReadout


class AssayTestResource(resources.ModelResource):

    class Meta(object):
        model = AssayTest


from import_export import resources
from bioactivities.models import BioactivityType


class BioactivityTypeTableResource(resources.ModelResource):

    class Meta(object):
        model = BioactivityTypeTable




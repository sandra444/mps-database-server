from import_export import resources
from bioactivities.models import BioactivityType


class BioactivityTypeResource(resources.ModelResource):

    class Meta(object):
        model = BioactivityType




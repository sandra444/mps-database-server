from import_export import resources
from compounds.models import Compound


class CompoundResource(resources.ModelResource):

    class Meta(object):
        model = Compound


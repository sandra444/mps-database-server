from import_export import resources
from compounds.models import Compound


class CompoundResource(resources.ModelResource):
    """Import-Export Resource for Compounds"""
    class Meta(object):
        model = Compound

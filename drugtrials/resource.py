from import_export import resources
from drugtrials.models import DrugTrial


class DrugTrialResource(resources.ModelResource):
    """Drug Trial Resource"""
    class Meta(object):
        model = DrugTrial

from import_export import resources
from drugtrials.models import DrugTrial


class DrugTrialResource(resources.ModelResource):

    class Meta(object):
        model = DrugTrial

from .models import FindingResult
from django.views.generic import ListView

class DrugTrialList(ListView):
    #model = FindingResult
    template_name = 'drugtrials/drugtrial_list.html'

    def get_queryset(self):
        queryset = FindingResult.objects.prefetch_related('drug_trial','finding_name', 'value_units').select_related('drug_trial__compound', 'drug_trial__species', 'finding_name__organ', 'finding_name__finding_type').all()
        return queryset

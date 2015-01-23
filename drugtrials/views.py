from .models import FindingResult,  DrugTrial
from django.views.generic import ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

class DrugTrialList(ListView):
    #model = FindingResult
    template_name = 'drugtrials/drugtrial_list.html'

    def get_queryset(self):
        queryset = FindingResult.objects.prefetch_related('drug_trial','finding_name', 'value_units').select_related('drug_trial__compound', 'drug_trial__species', 'finding_name__organ', 'finding_name__finding_type').all()
        return queryset

def drug_trial_detail(request, *args, **kwargs):
    c = RequestContext(request)

    trial = get_object_or_404(DrugTrial, pk=kwargs.get('pk'))
    results = FindingResult.objects.filter(drug_trial=trial).prefetch_related('drug_trial','finding_name', 'value_units').select_related('drug_trial__compound', 'drug_trial__species', 'finding_name__organ', 'finding_name__finding_type')

    c.update({
        'trial': trial,
        'results': results,
    })

    return render_to_response('drugtrials/drugtrial_detail.html', c)

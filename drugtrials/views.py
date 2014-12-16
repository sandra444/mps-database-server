from .models import FindingResult
from django.views.generic import ListView

class DrugTrialList(ListView):
    model = FindingResult
    template_name = 'drugtrials/drugtrial_list.html'

from .models import DrugTrial
from django.views.generic import ListView

class DrugTrialList(ListView):
    model = DrugTrial
    template_name = 'drugtrials/drugtrial_list.html'

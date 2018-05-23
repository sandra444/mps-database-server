from django.views.generic import ListView, DetailView, CreateView
from mps.mixins import SpecificGroupRequiredMixin
# from forms import DiseaseForm
from django.shortcuts import render
from models import Disease, DiseaseBiologyOtherResources, DiseaseClinicalTrial
from assays.models import AssayStudy, AssayMatrixItem
from microdevices.models import OrganModel
from drugtrials.models import FindingResult

# Should this functionality be replicated in the diseases app? I figure not, the models already preclude modularity.
from assays.utils import get_user_accessible_studies
from assays.views import get_queryset_with_organ_model_map, get_queryset_with_number_of_data_points, get_queryset_with_stakeholder_sign_off

# Create your views here.
class DiseaseList(ListView):
    model = Disease
    template_name = 'diseases/disease_list.html'


class DiseaseOverview(DetailView):
    model = Disease
    template_name = 'diseases/disease_overview.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context


class DiseaseBiology(DetailView):
    model = Disease
    template_name = 'diseases/disease_biology.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        disease = context['disease']
        context['biology_other_resources'] = DiseaseBiologyOtherResources.objects.filter(disease=disease)
        return context


class DiseaseClinicalData(DetailView):
    model = Disease
    template_name = 'diseases/disease_clinicaldata.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        disease = context['disease']
        # context['clinicaltrials'] = DiseaseClinicalTrial.objects.filter(disease=disease)
        # context['trial_findings'] = FindingResult.objects.filter(drugtrial__disease_id__contains=context['disease'])
        context['trial_findings'] = FindingResult.objects.filter(drug_trial__disease__name=context['disease'])
        return context


class DiseaseModel(DetailView):
    model = Disease
    template_name = 'diseases/disease_model.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        context['disease_models'] = OrganModel.objects.filter(disease__name=context['disease'])
        # studies = AssayStudy.objects.filter(disease=True, assaymatrixitem__organ_model_id__in=context['disease_models']).distinct()

        combined = get_user_accessible_studies(self.request.user).filter(assaymatrixitem__organ_model_id__in=context['disease_models']).distinct()

        get_queryset_with_organ_model_map(combined)
        get_queryset_with_number_of_data_points(combined)
        get_queryset_with_stakeholder_sign_off(combined)

        context['studies'] = combined
        return context


# class DiseaseAdd(SpecificGroupRequiredMixin, CreateView):
#     """Allows the addition of Diseases"""
#     model = Disease
#     template_name = 'diseases/disease_add.html'
#     form_class = DiseaseForm

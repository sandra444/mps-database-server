from django.views.generic import ListView, DetailView, CreateView
from mps.mixins import SpecificGroupRequiredMixin
# from forms import DiseaseForm
from django.shortcuts import render
from models import Disease, DiseaseBiologyOtherResources, DiseaseClinicalTrial


# Create your views here.
class DiseaseList(ListView):
    model = Disease
    template_name = 'diseases/disease_list.html'


class DiseaseOverview(DetailView):
    model = Disease

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context
    template_name = 'diseases/disease_overview.html'


class DiseaseBiology(DetailView):
    model = Disease

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        disease = context['disease']
        context['biology_other_resources'] = DiseaseBiologyOtherResources.objects.filter(disease=disease)
        return context
    template_name = 'diseases/disease_biology.html'


class DiseaseClinicalData(DetailView):
    model = Disease

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        disease = context['disease']
        context['clinicaltrials'] = DiseaseClinicalTrial.objects.filter(disease=disease)
        return context
    template_name = 'diseases/disease_clinicaldata.html'


class DiseaseModel(DetailView):
    model = Disease

    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context
    template_name = 'diseases/disease_model.html'


# class DiseaseAdd(SpecificGroupRequiredMixin, CreateView):
#     """Allows the addition of Diseases"""
#     model = Disease
#     template_name = 'diseases/disease_add.html'
#     form_class = DiseaseForm

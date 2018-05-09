from django.views.generic import ListView, DetailView
from django.shortcuts import render
from models import Disease

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


class DiseaseClinicalData(DetailView):
    model = Disease
    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context
    template_name = 'diseases/disease_clinicaldata.html'


class DiseaseBiology(DetailView):
    model = Disease
    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context
    template_name = 'diseases/disease_biology.html'


class DiseaseModel(DetailView):
    model = Disease
    def get_context_data(self, **kwargs):
        context = {}
        context['disease'] = Disease.objects.get(pk=self.kwargs['pk'])
        return context
    template_name = 'diseases/disease_model.html'

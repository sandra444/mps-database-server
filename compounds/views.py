# coding=utf-8

from .models import Compound

from django.views.generic import ListView, DetailView
from django.utils import timezone


class CompoundList(ListView):
    model = Compound
    template_name = 'compounds/compounds.html'
    paginate_by = 50

class CompoundDetails(DetailView):
    model = Compound
    template_name = 'compounds/compound.html'

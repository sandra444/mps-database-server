# coding=utf-8

from .models import Compound

from django.views.generic import ListView, DetailView
from django.utils import timezone


class CompoundList(ListView):
    model = Compound
    template_name = 'compounds/compounds.html'
    paginate_by = 50

    def get_queryset(self):
        try:
            name = self.request.GET['name']
        except:
            name = ''
        if (name != ''):
            object_list = self.model.objects.filter(name__icontains = name)
        else:
            object_list = self.model.objects.all()
        return object_list

class CompoundDetails(DetailView):
    model = Compound
    template_name = 'compounds/compound.html'

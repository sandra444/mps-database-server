from django.views.generic import ListView
from assays.models import AssayRun, AssayChipReadout

class AssayRunList(ListView):
    model = AssayRun

class AssayChipReadoutList(ListView):
    model = AssayChipReadout

from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from assays.models import AssayChipReadout
from assays.forms import AssayChipReadoutForm
from django.core.context_processors import csrf

def add_readout(request):
    ReadoutFormSet = AssayChipReadoutForm
    if request.method == 'POST':
        formset = ReadoutFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = ReadoutFormSet()

    args = {}
    args.update(csrf(request))
    args['form'] = formset

    return render_to_response("assays/add_readout.html", args)

from django.views.generic.edit import CreateView

class AssayChipReadoutAdd(CreateView):
    model = AssayChipReadout
    #fields = ['name']

from django.views.generic.detail import DetailView
from django.utils import timezone

class AssayChipReadoutDetail(DetailView):

    model = AssayChipReadout

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

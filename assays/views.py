from django.views.generic import ListView
from assays.models import AssayRun

class RunList(ListView):
    model = AssayRun

from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from assays.models import AssayChipReadout

def manage_readouts(request):
    ReadoutFormSet = modelformset_factory(AssayChipReadout)
    if request.method == 'POST':
        formset = ReadoutFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = ReadoutFormSet()
    return render_to_response("assays/manage_readouts.html", {
        "formset": formset,
    })

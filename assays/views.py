from django.views.generic import ListView
from assays.models import AssayRun

class RunList(ListView):
    model = AssayRun

from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from assays.models import AssayChipReadout
from assays.forms import AssayChipReadoutForm
from django.core.context_processors import csrf

def manage_readouts(request):
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

    return render_to_response("assays/manage_readouts.html", args)

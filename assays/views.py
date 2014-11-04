# coding=utf-8

from django.views.generic import ListView, CreateView, DetailView
from assays.models import AssayChipReadout

class AssayChipReadoutList(ListView):
    model = AssayChipReadout

from assays.forms import AssayChipReadoutForm

from django.forms.models import inlineformset_factory
from django.views.generic.edit import CreateView
from assays.models import AssayChipReadoutAssay
from assays.admin import AssayChipReadoutInlineFormset, parseChipCSV
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

ACRAFormSet = inlineformset_factory(AssayChipReadout,AssayChipReadoutAssay, formset=AssayChipReadoutInlineFormset)

class AssayChipReadoutAdd(CreateView):
    template_name = 'assays/create_readout.html'
    form_class = AssayChipReadoutForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssayChipReadoutAdd, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ACRAFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ACRAFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            if formset.__dict__['files']:
                file = formset.__dict__['files']['file']
                parseChipCSV(self.object,file)
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))

from django.views.generic.detail import DetailView
from django.utils import timezone

class AssayChipReadoutDetail(DetailView):

    model = AssayChipReadout

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

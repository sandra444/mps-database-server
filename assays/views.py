# coding=utf-8

from django.views.generic import ListView, CreateView, DetailView
from assays.models import *
from assays.admin import *
from assays.forms import *
from django import forms

from django.forms.models import inlineformset_factory
from django.views.generic.edit import CreateView
from assays.models import *
from django.shortcuts import redirect
# May be useful later
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from django.views.generic.detail import DetailView
from django.utils import timezone

from mps.filters import *

#TODO Refactor imports

# Class-based views for studies
class AssayRunList(ListView):
    model = AssayRun


class AssayRunAdd(CreateView):
    template_name = 'assays/assayrun_add.html'
    form_class = AssayRunForm

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Study
            self.object.save()
            if form.__dict__['files']:
                file = form.__dict__['files']['file']
                # TODO test bulk import
                parseRunCSV(self.object,file)
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayRunDetail(DetailView):
    model = AssayRun


# Class based view for chip setups
class AssayChipSetupList(ListView):
    model = AssayChipSetup


AssayChipCellsFormset = inlineformset_factory(AssayChipSetup,AssayChipCells, formset=forms.models.BaseInlineFormSet, extra=1)


class AssayChipSetupAdd(CreateView):
    template_name = 'assays/assaychipsetup_add.html'
    form_class = AssayChipSetupForm

    def get_context_data(self, **kwargs):
        context = super(AssayChipSetupAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AssayChipCellsFormset(self.request.POST)
        else:
            context['formset'] = AssayChipCellsFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        # get user via self.request.user
        if formset.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Readout
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipSetupDetail(DetailView):
    model = AssayChipSetup


# Class based views for readouts
class AssayChipReadoutList(ListView):
    model = AssayChipReadout

ACRAFormSet = inlineformset_factory(AssayChipReadout,AssayChipReadoutAssay, formset=AssayChipReadoutInlineFormset, extra=1)


class AssayChipReadoutAdd(CreateView):
    template_name = 'assays/assaychipreadout_add.html'
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
        # get user via self.request.user
        if formset.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Readout
            self.object.save()
            formset.instance = self.object
            formset.save()
            if formset.__dict__['files']:
                file = formset.__dict__['files']['file']
                parseChipCSV(self.object,file)
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipReadoutDetail(DetailView):

    model = AssayChipReadout

    # Using get is a good way to circumvent tedious calls in a decorator
    # It may be useful to define a modified base detail view with this preexisting
    # Obviously the desired group is currently hardcoded, but it could be placed in a base model ("only viewable by:")
    def get(self, request, **kwargs):
        self.object = self.get_object()
        if not has_group(request.user, 'UPitt'):
            return self.render_to_response({'now':timezone.now()}) # Just date for now
        context = super(AssayChipReadoutDetail, self).get_context_data(**kwargs)
        return self.render_to_response(context)


# Class-based views for studies
class AssayTestResultList(ListView):
    model = AssayTestResult


TestResultFormSet = inlineformset_factory(AssayTestResult,AssayResult, formset=forms.models.BaseInlineFormSet, extra=1)

class AssayTestResultAdd(CreateView):
    template_name = 'assays/assaytestresult_add.html'
    form_class = AssayResultForm

    def get_context_data(self, **kwargs):
        context = super(AssayTestResultAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TestResultFormSet(self.request.POST)
        else:
            context['formset'] = TestResultFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        # get user via self.request.user
        if formset.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Readout
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayTestResultDetail(DetailView):
    model = AssayTestResult

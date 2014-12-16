# coding=utf-8

from django.views.generic import ListView, CreateView, DetailView
from assays.models import *
from assays.admin import *
from assays.forms import *
from django import forms

from django.forms.models import inlineformset_factory
from django.views.generic.edit import CreateView
from assays.models import *
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
#from django.http import Http404
# May be useful later
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mps.filters import *

#TODO Refactor imports

# NOTE THAT YOU NEED TO MODIFY INLINES HERE, NOT IN FORMS


# Add this mixin via multiple-inheritance and you need not change the dispatch every time
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class StudyAccessMixin(object):
    def get(self, request, **kwargs):
        self.object = None
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        if not has_group(request.user, study.group):
            raise PermissionDenied()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

# Class-based views for indexes
class UserIndex(LoginRequiredMixin,ListView):
    context_object_name = 'user_index'
    template_name = 'assays/index.html'

    def get_context_data(self, request, **kwargs):
        self.object_list = AssayRun.objects.filter(created_by=request.user)
        return super(UserIndex, self).get_context_data(**kwargs)

    def get(self, request, **kwargs):
        if len(request.user.groups.values_list('pk',flat=True)) == 0:
            raise PermissionDenied()
        context = self.get_context_data(request, **kwargs)
        self.queryset = self.object_list
        context['title'] = 'User Study Index'
        return self.render_to_response(context)


class GroupIndex(LoginRequiredMixin,ListView):
    context_object_name = 'group_index'
    template_name = 'assays/index.html'

    def get_context_data(self, request, **kwargs):
        # Alternative method using users
        # groups = request.user.groups.values_list('name',flat=True)
        # users = Group.objects.get(name=groups[0]).user_set.all()
        # if len(groups) > 1:
        #     for group in groups[1:]:
        #         current_users = Group.objects.get(name=group).user_set.all()
        #         users = current_users | users
        # self.object_list = AssayRun.objects.filter(created_by=users)
        groups = request.user.groups.values_list('pk',flat=True)
        groups = Group.objects.filter(pk__in=groups)
        self.object_list = AssayRun.objects.filter(group__in=groups)
        return super(GroupIndex, self).get_context_data(**kwargs)

    def get(self, request, **kwargs):
        if len(request.user.groups.values_list('pk',flat=True)) == 0:
            raise PermissionDenied()
        context = self.get_context_data(request, **kwargs)
        self.queryset = self.object_list
        context['title'] = 'Group Study Index'
        return self.render_to_response(context)


class StudyIndex(LoginRequiredMixin,ListView):
    context_object_name = 'study_index'
    template_name = 'assays/study_index.html'

    def get_context_data(self, request, **kwargs):
        # Use kwargs to grab info from the URL
        self.object_list = AssayRun.objects.filter(pk=self.kwargs['study_id'])
        return super(StudyIndex, self).get_context_data(**kwargs)

    def get(self, request, **kwargs):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        if not has_group(request.user, study.group):
            raise PermissionDenied()
        context = self.get_context_data(request, **kwargs)
        self.queryset = self.object_list
        context['setups'] = AssayChipSetup.objects.filter(assay_run_id=self.queryset)
        context['readouts'] = AssayChipReadout.objects.filter(chip_setup=context['setups'])
        context['results'] = AssayTestResult.objects.filter(chip_setup=context['setups'])
        return self.render_to_response(context)


# Class-based views for studies
class AssayRunList(LoginRequiredMixin, ListView):
    model = AssayRun

    def get_queryset(self):
        return AssayRun.objects.filter(restricted=False) | AssayRun.objects.filter(group__in=self.request.user.groups.all())


class AssayRunAdd(LoginRequiredMixin, CreateView):
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
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            # In order to display errors properly, make sure they are added to POST
            #form['errors'] = form.errors
            return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, **kwargs):
        self.object = None
        if len(request.user.groups.values_list('pk',flat=True)) == 0:
            raise PermissionDenied()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))


class AssayRunDetail(LoginRequiredMixin, DetailView):
    model = AssayRun

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.restricted and not has_group(request.user, self.object.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# Class based view for chip setups
class AssayChipSetupList(LoginRequiredMixin, ListView):
    model = AssayChipSetup

    def get_queryset(self):
        return AssayChipSetup.objects.filter(assay_run_id__restricted=False) | AssayChipSetup.objects.filter(assay_run_id__group__in=self.request.user.groups.all())


AssayChipCellsFormset = inlineformset_factory(AssayChipSetup,AssayChipCells, formset=AssayChipCellsInlineFormset, extra=1,
                                              widgets = {'cellsample_density': forms.TextInput(attrs={'size': 5}),
                                                         'cell_passage': forms.TextInput(attrs={'size': 5}),})


class AssayChipSetupAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_add.html'
    # May want to define form with initial here
    form_class = AssayChipSetupForm

    def get_context_data(self, **kwargs):
        context = super(AssayChipSetupAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AssayChipCellsFormset(self.request.POST)
            context['study'] = self.kwargs.get('study_id')
        else:
            context['formset'] = AssayChipCellsFormset()
            context['study'] = self.kwargs.get('study_id')
        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.assay_run_id = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted
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


class AssayChipSetupDetail(LoginRequiredMixin, DetailView):
    model = AssayChipSetup

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.assay_run_id.restricted and not has_group(request.user, self.object.assay_run_id.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# Class based views for readouts
class AssayChipReadoutList(LoginRequiredMixin, ListView):
    model = AssayChipReadout

    def get_queryset(self):
        return AssayChipReadout.objects.filter(chip_setup__assay_run_id__restricted=False) | AssayChipReadout.objects.filter(chip_setup__assay_run_id__group__in=self.request.user.groups.all())

ACRAFormSet = inlineformset_factory(AssayChipReadout,AssayChipReadoutAssay, formset=AssayChipReadoutInlineFormset, extra=1)


class AssayChipReadoutAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    template_name = 'assays/assaychipreadout_add.html'
    form_class = AssayChipReadoutForm

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ACRAFormSet(self.request.POST, self.request.FILES)
            context['study'] = self.kwargs.get('study_id')
        else:
            context['formset'] = ACRAFormSet()
            context['study'] = self.kwargs.get('study_id')
        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.group = study.group
        form.instance.restricted = study.restricted
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


class AssayChipReadoutDetail(LoginRequiredMixin, DetailView):
    model = AssayChipReadout

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.chip_setup.assay_run_id.restricted and not has_group(request.user, self.object.chip_setup.assay_run_id.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# Class-based views for studies
class AssayTestResultList(LoginRequiredMixin, ListView):
    model = AssayTestResult

    def get_queryset(self):
        return AssayTestResult.objects.filter(assay_device_readout__restricted=False) | AssayTestResult.objects.filter(assay_device_readout__group__in=self.request.user.groups.all())


TestResultFormSet = inlineformset_factory(AssayTestResult,AssayResult, formset=TestResultInlineFormset, extra=1,
                                              widgets = {'value': forms.TextInput(attrs={'size': 10}),})

class AssayTestResultAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    template_name = 'assays/assaytestresult_add.html'
    form_class = AssayResultForm

    def get_context_data(self, **kwargs):
        context = super(AssayTestResultAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TestResultFormSet(self.request.POST)
            context['study'] = self.kwargs.get('study_id')
        else:
            context['formset'] = TestResultFormSet()
            context['study'] = self.kwargs.get('study_id')
        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.assay_device_readout = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted
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


class AssayTestResultDetail(LoginRequiredMixin, DetailView):
    model = AssayTestResult

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.assay_device_readout.restricted and not has_group(request.user, self.object.assay_device_readout.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

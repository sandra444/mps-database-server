# coding=utf-8

from django.views.generic import ListView, CreateView, DetailView, UpdateView
from assays.models import *
from cellsamples.models import CellSample
from assays.admin import *
from assays.forms import *
from django import forms

from django.forms.models import inlineformset_factory
from django.views.generic.edit import CreateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
# from django.http import Http404
# May be useful later
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mps.filters import *
from django.db.models import Q

# TODO Refactor imports

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
class UserIndex(LoginRequiredMixin, ListView):
    context_object_name = 'user_index'
    template_name = 'assays/index.html'

    def get_context_data(self, request, **kwargs):
        self.object_list = AssayRun.objects.filter(created_by=request.user).prefetch_related('created_by')
        return super(UserIndex, self).get_context_data(**kwargs)

    def get(self, request, **kwargs):
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
            raise PermissionDenied()
        context = self.get_context_data(request, **kwargs)
        self.queryset = self.object_list
        context['title'] = 'User Study Index'
        # Check if this is setup only; if so add to add respective URLS
        if request.GET.get('setup', ''):
            context['setup'] = '/?setup=1'
        else:
            context['setup'] = ''
        return self.render_to_response(context)


class GroupIndex(LoginRequiredMixin, ListView):
    context_object_name = 'group_index'
    template_name = 'assays/index.html'

    def get_context_data(self, request, **kwargs):
        # Alternative method using users
        # groups = request.user.groups.values_list('name',flat=True)
        # users = Group.objects.get(name=groups[0]).user_set.all()
        # if len(groups) > 1:
        # for group in groups[1:]:
        # current_users = Group.objects.get(name=group).user_set.all()
        # users = current_users | users
        # self.object_list = AssayRun.objects.filter(created_by=users)
        groups = request.user.groups.values_list('pk', flat=True)
        groups = Group.objects.filter(pk__in=groups)
        self.object_list = AssayRun.objects.filter(group__in=groups).prefetch_related('created_by')
        return super(GroupIndex, self).get_context_data(**kwargs)

    def get(self, request, **kwargs):
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
            raise PermissionDenied()
        context = self.get_context_data(request, **kwargs)
        self.queryset = self.object_list
        context['title'] = 'Group Study Index'
        # Check if this is setup only; if so add to add respective URLS
        if request.GET.get('setup', ''):
            context['setup'] = '/?setup=1'
        else:
            context['setup'] = ''
        return self.render_to_response(context)


class StudyIndex(LoginRequiredMixin, ListView):
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
        context['setups'] = AssayChipSetup.objects.filter(assay_run_id=self.queryset).prefetch_related('assay_run_id',
                                                                                                       'device',
                                                                                                       'compound',
                                                                                                       'unit',
                                                                                                       'created_by')
        context['readouts'] = AssayChipReadout.objects.filter(chip_setup=context['setups']).prefetch_related(
            'chip_setup', 'timeunit', 'created_by').select_related('chip_setup__compound',
                                                                   'chip_setup__unit')
        context['results'] = AssayResult.objects.prefetch_related('assay_name', 'assay_result', 'result_function', 'result_type',
                                                    'test_unit').select_related('assay_result__assay_device_readout',
                                                                                'assay_result__chip_setup',
                                                                                'assay_result__chip_setup__compound',
                                                                                'assay_result__chip_setup__unit',
                                                                                'assay_name__readout_id',
                                                                                'assay_name__assay_id',
                                                                                'assay_name__reader_id',
                                                                                'assay_name__readout_unit',
                                                                                'assay_result__created_by').filter(assay_result__chip_setup=context['setups'])

        # Check if this is setup only; if so add to add respective URLS
        if request.GET.get('setup', ''):
            context['setup'] = '/?setup=1'
        else:
            context['setup'] = ''
        return self.render_to_response(context)


# Class-based views for studies
class AssayRunList(LoginRequiredMixin, ListView):
    model = AssayRun

    def get_queryset(self):
        return AssayRun.objects.filter(restricted=False).prefetch_related('center_id',
                                                                          'created_by') | AssayRun.objects.filter(
            group__in=self.request.user.groups.all()).prefetch_related('center_id', 'created_by')


class AssayRunAdd(LoginRequiredMixin, CreateView):
    template_name = 'assays/assayrun_add.html'
    form_class = AssayRunForm

    def get_context_data(self, **kwargs):
        # Get group selection possibilities
        groups = self.request.user.groups.filter(
            ~Q(name__contains="Add ") & ~Q(name__contains="Change ") & ~Q(name__contains="Delete "))
        context = super(AssayRunAdd, self).get_context_data(**kwargs)
        context['groups'] = groups
        # Check if this is setup only; if so add to add respective URLS
        # if self.request.GET.get('setup', ''):
        # context['setup'] = '/?setup=1'
        # else:
        #     context['setup'] = ''
        return context

    # Test form validity
    def form_valid(self, form):
        url_add = ''
        if self.request.GET.get('setup', ''):
            url_add = '?setup=1'
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Study
            self.object.save()
            return redirect(
                self.object.get_absolute_url() + url_add)  # assuming your model has ``get_absolute_url`` defined.
        else:
            # In order to display errors properly, make sure they are added to POST
            # form['errors'] = form.errors
            return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, **kwargs):
        self.object = None
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
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
        context['setups'] = AssayChipSetup.objects.filter(assay_run_id=self.object).prefetch_related('assay_run_id',
                                                                                                     'device',
                                                                                                     'compound',
                                                                                                     'unit',
                                                                                                     'created_by')
        context['readouts'] = AssayChipReadout.objects.filter(chip_setup=context['setups']).prefetch_related(
            'chip_setup', 'timeunit', 'created_by').select_related('chip_setup__compound',
                                                                   'chip_setup__unit')
        context['results'] = AssayResult.objects.prefetch_related('assay_name', 'assay_result', 'result_function', 'result_type',
                                                    'test_unit').select_related('assay_result__assay_device_readout',
                                                                                'assay_result__chip_setup',
                                                                                'assay_result__chip_setup__compound',
                                                                                'assay_result__chip_setup__unit',
                                                                                'assay_name__readout_id',
                                                                                'assay_name__assay_id',
                                                                                'assay_name__reader_id',
                                                                                'assay_name__readout_unit',
                                                                                'assay_result__created_by').filter(assay_result__chip_setup=context['setups'])
        return self.render_to_response(context)


# Class based view for chip setups
class AssayChipSetupList(LoginRequiredMixin, ListView):
    model = AssayChipSetup

    def get_queryset(self):
        return AssayChipSetup.objects.filter(assay_run_id__restricted=False).prefetch_related('assay_run_id', 'device',
                                                                                              'compound', 'unit',
                                                                                              'created_by') | AssayChipSetup.objects.filter(
            assay_run_id__group__in=self.request.user.groups.all()).prefetch_related('assay_run_id', 'device',
                                                                                     'compound', 'unit', 'created_by')


AssayChipCellsFormset = inlineformset_factory(AssayChipSetup, AssayChipCells, formset=AssayChipCellsInlineFormset,
                                              extra=1,
                                              widgets={
                                              'cellsample_density': forms.NumberInput(attrs={'style': 'width:75px;', }),
                                              'cell_passage': forms.TextInput(attrs={'size': 5}), })


class AssayChipSetupAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_add.html'
    # May want to define form with initial here
    form_class = AssayChipSetupForm

    def get_context_data(self, **kwargs):
        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(group__in=groups).order_by('-receipt_date').prefetch_related(
            'cell_type',
            'supplier',
        ).select_related('cell_type__cell_subtype')
        context = super(AssayChipSetupAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AssayChipCellsFormset(self.request.POST)
            # context['study'] = self.kwargs.get('study_id')
            context['cellsamples'] = cellsamples
        else:
            context['formset'] = AssayChipCellsFormset()
            # context['study'] = self.kwargs.get('study_id')
            context['cellsamples'] = cellsamples
        return context

    def form_valid(self, form):
        url_add = ''
        if self.request.GET.get('setup', ''):
            url_add = '?setup=1'
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.assay_run_id = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted
        context = self.get_context_data()
        formset = context['formset']
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Readout
            self.object.save()
            formset.instance = self.object
            formset.save()
            if data['another']:
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(
                    self.object.get_absolute_url() + url_add)  # assuming your model has ``get_absolute_url`` defined.
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


class AssayChipSetupUpdate(LoginRequiredMixin,StudyAccessMixin, UpdateView):
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_add.html'
    form_class = AssayChipSetupForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(group__in=groups).order_by('-receipt_date').prefetch_related(
            'cell_type',
            'supplier',
        ).select_related('cell_type__cell_subtype')

        # Render form
        formset = AssayChipCellsFormset(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                cellsamples = cellsamples))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(self.request.POST, instance=self.object)
        formset = AssayChipCellsFormset(self.request.POST, instance=form.instance)

        # TODO refactor redundant code here; testing for now

        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(group__in=groups).order_by('-receipt_date').prefetch_related(
            'cell_type',
            'supplier',
        ).select_related('cell_type__cell_subtype')

        form.instance.assay_device_readout = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            # TODO maintain original created by
            # Just change created by as well for now
            self.object.modified_by = self.object.created_by = self.request.user
            # Save overall test result
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                cellsamples = cellsamples))


# Class based views for readouts
class AssayChipReadoutList(LoginRequiredMixin, ListView):
    model = AssayChipReadout

    def get_queryset(self):
        return AssayChipReadout.objects.filter(chip_setup__assay_run_id__restricted=False).prefetch_related(
            'chip_setup', 'timeunit', 'created_by').select_related('chip_setup__compound',
                                                                   'chip_setup__unit') | AssayChipReadout.objects.filter(
            chip_setup__assay_run_id__group__in=self.request.user.groups.all()).prefetch_related('chip_setup',
                                                                                                 'timeunit',
                                                                                                 'created_by').select_related(
            'chip_setup__compound', 'chip_setup__unit')


ACRAFormSet = inlineformset_factory(AssayChipReadout, AssayChipReadoutAssay, formset=AssayChipReadoutInlineFormset,
                                    extra=1)


class AssayChipReadoutAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    template_name = 'assays/assaychipreadout_add.html'
    form_class = AssayChipReadoutForm

    def get_context_data(self, **kwargs):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list)))

        context = super(AssayChipReadoutAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ACRAFormSet(self.request.POST, self.request.FILES)
            context['setups'] = setups
            # context['study'] = self.kwargs.get('study_id')
        else:
            context['formset'] = ACRAFormSet()
            context['setups'] = setups
            # context['study'] = self.kwargs.get('study_id')
        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.group = study.group
        form.instance.restricted = study.restricted
        context = self.get_context_data()
        formset = context['formset']
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Chip Readout
            self.object.save()
            formset.instance = self.object
            formset.save()
            if formset.__dict__['files']:
                file = formset.__dict__['files']['file']
                parseChipCSV(self.object, file)
            if data['another']:
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    def render_to_response(self, context):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        if not context.get('setups',''):
            return redirect('/assays/'+str(study.id))

        return super(AssayChipReadoutAdd, self).render_to_response(context)


class AssayChipReadoutDetail(LoginRequiredMixin, DetailView):
    model = AssayChipReadout

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.chip_setup.assay_run_id.restricted and not has_group(request.user,
                                                                            self.object.chip_setup.assay_run_id.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class AssayChipReadoutUpdate(LoginRequiredMixin,StudyAccessMixin, UpdateView):
    model = AssayChipReadout
    template_name = 'assays/assaychipreadout_add.html'
    form_class = AssayChipReadoutForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)

        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list))) | AssayChipSetup.objects.filter(pk=self.object.chip_setup.id)

        # Render form
        formset = ACRAFormSet(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                setups = setups))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(self.request.POST, instance=self.object)
        formset = ACRAFormSet(self.request.POST, instance=form.instance)

        # TODO refactor redundant code here; testing for now

        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)

        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list))) | AssayChipSetup.objects.filter(pk=self.object.chip_setup.id)

        form.instance.assay_device_readout = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            # TODO maintain original created by
            # Just change created by as well for now
            self.object.modified_by = self.object.created_by = self.request.user
            # Save overall test result
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                setups = setups))


# Class-based views for studies
class AssayTestResultList(LoginRequiredMixin, ListView):
    # model = AssayTestResult
    template_name = 'assays/assaytestresult_list.html'

    def get_queryset(self):
        initial_query = AssayResult.objects.prefetch_related('assay_name', 'assay_result', 'result_function', 'result_type',
                                                    'test_unit').select_related('assay_result__assay_device_readout',
                                                                                'assay_result__chip_setup',
                                                                                'assay_result__chip_setup__compound',
                                                                                'assay_result__chip_setup__unit',
                                                                                'assay_name__readout_id',
                                                                                'assay_name__assay_id',
                                                                                'assay_name__reader_id',
                                                                                'assay_name__readout_unit',
                                                                                'assay_result__created_by')

        return initial_query.filter(assay_result__assay_device_readout__restricted=False) | \
               initial_query.filter(assay_result__assay_device_readout__group__in=self.request.user.groups.all())


TestResultFormSet = inlineformset_factory(AssayTestResult, AssayResult, formset=TestResultInlineFormset, extra=1,
                                          widgets={'value': forms.NumberInput(attrs={'style': 'width:100px;', }), })


class AssayTestResultAdd(LoginRequiredMixin, StudyAccessMixin, CreateView):
    template_name = 'assays/assaytestresult_add.html'
    form_class = AssayResultForm

    def get_context_data(self, **kwargs):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayTestResult.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list)))

        context = super(AssayTestResultAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TestResultFormSet(self.request.POST)
            context['setups'] = setups
            # context['study'] = self.kwargs.get('study_id')
        else:
            context['formset'] = TestResultFormSet()
            context['setups'] = setups
            # context['study'] = self.kwargs.get('study_id')
        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        form.instance.assay_device_readout = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted
        context = self.get_context_data()
        formset = context['formset']
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save overall test result
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    def render_to_response(self, context):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        if not context.get('setups',''):
            return redirect('/assays/'+str(study.id))

        return super(AssayTestResultAdd, self).render_to_response(context)


class AssayTestResultDetail(LoginRequiredMixin, DetailView):
    model = AssayTestResult

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.assay_device_readout.restricted and not has_group(request.user,
                                                                         self.object.assay_device_readout.group):
            raise PermissionDenied
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class AssayTestResultUpdate(LoginRequiredMixin,StudyAccessMixin, UpdateView):
    model = AssayTestResult
    template_name = 'assays/assaytestresult_add.html'
    form_class = AssayResultForm

    # Alternative (cleaner?) method

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayTestResult.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)

        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list))) | AssayChipSetup.objects.filter(pk=self.object.chip_setup.id)

        # Render form
        formset = TestResultFormSet(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                setups = setups))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(self.request.POST, instance=self.object)
        formset = TestResultFormSet(self.request.POST, instance=form.instance)

        # TODO refactor redundant code here; testing for now

        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayTestResult.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)

        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list))) | AssayChipSetup.objects.filter(pk=self.object.chip_setup.id)

        form.instance.assay_device_readout = study
        form.instance.group = study.group
        form.instance.restricted = study.restricted

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            # TODO maintain original created by
            # Just change created by as well for now
            self.object.modified_by = self.object.created_by = self.request.user
            # Save overall test result
            self.object.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(
            self.get_context_data(form=form,
                                formset = formset,
                                setups = setups))

# coding=utf-8

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from assays.models import *
from cellsamples.models import CellSample
# TODO TRIM THIS IMPORT
from assays.admin import *
from assays.forms import *
from django import forms

from django.forms.models import inlineformset_factory
# from django.shortcuts import redirect, get_object_or_404, render_to_response
# from django.contrib.auth.models import Group
# from django.core.exceptions import PermissionDenied
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

# from mps.templatetags.custom_filters import *

from mps.mixins import *
from mps.base.models import save_forms_with_tracking

# import ujson as json
import xlrd

from django.conf import settings
# Convert to valid file name
import string
import re
import os
import codecs
import cStringIO

from mps.settings import MEDIA_ROOT, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX

# TODO Refactor imports
# TODO REFACTOR CERTAIN WHITTLING TO BE IN FORM AS OPPOSED TO VIEW
# TODO Rename get_absolute_url when the function does not actually return the model's URL
# TODO It is probably more semantic to overwrite get_context_data and form_valid in lieu of post and get for updates
# TODO ^ Update Views should be refactored soon
# NOTE THAT YOU NEED TO MODIFY INLINES HERE, NOT IN FORMS


class UnicodeWriter:
    """Used to write UTF-8 CSV files"""
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        """Init the UnicodeWriter

        Params:
        f -- the file stream to write to
        dialect -- the "dialect" of csv to use (default excel)
        encoding -- the text encoding set to use (default utf-8)
        """
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        """This function takes a Unicode string and encodes it to the output"""
        self.writer.writerow([s.encode('utf-8') for s in row])
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        """This function writes out all rows given"""
        for row in rows:
            self.writerow(row)


def add_study_fields_to_form(self, form, add_study=False):
    """Adds study, group, and restricted to a form

    Params:
    self -- the object in question
    form -- the form to be added to
    add_study -- boolean indicating whether to add the study to the model
    """
    study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

    if add_study:
        form.instance.assay_run_id = study

    form.instance.group = study.group
    form.instance.restricted = study.restricted


# Removed User Index as it caused confusion
# Class-based views for indexes
# class UserIndex(OneGroupRequiredMixin, ListView):
#     """Displays all of the user's studies"""
#     context_object_name = 'user_index'
#     template_name = 'assays/index.html'
#
#     def get_context_data(self, request, **kwargs):
#         self.object_list = AssayRun.objects.filter(created_by=request.user).prefetch_related('created_by', 'group')
#
#         return super(UserIndex, self).get_context_data(**kwargs)
#
#     def get(self, request, **kwargs):
#         context = self.get_context_data(request, **kwargs)
#         self.queryset = self.object_list
#         context['title'] = request.user.first_name + "'s Studies"
#
#         return self.render_to_response(context)


# May want to merge with UserIndex?
class GroupIndex(OneGroupRequiredMixin, ListView):
    """Displays all of the studies linked to groups that the user is part of"""
    template_name = 'assays/index.html'

    def get_queryset(self):
        return AssayRun.objects.filter(
            group__in=self.request.user.groups.all()
        ).prefetch_related('created_by', 'group', 'signed_off_by')

    # def get_context_data(self, request, **kwargs):
    #     groups = request.user.groups.values_list('pk', flat=True)
    #     groups = Group.objects.filter(pk__in=groups)
    #     self.object_list = AssayRun.objects.filter(group__in=groups).prefetch_related('created_by', 'group')
    #
    #     return super(GroupIndex, self).get_context_data(**kwargs)
    #
    #     return self.render_to_response(context)


class StudyIndex(ViewershipMixin, DetailView):
    """Show all chip and plate models associated with the given study"""
    model = AssayRun
    context_object_name = 'study_index'
    template_name = 'assays/study_index.html'

    # TODO OPTIMIZE DATABASE HITS
    def get(self, request, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['setups'] = AssayChipSetup.objects.filter(
            assay_run_id=self.object
        ).prefetch_related(
            'organ_model',
            'device',
            'compound',
            'unit',
            'created_by',
        )
        readouts = AssayChipReadout.objects.filter(
            chip_setup=context['setups']
        ).prefetch_related(
            'created_by',
            'chip_setup__compound',
            'chip_setup__unit'
        )

        related_assays = AssayChipReadoutAssay.objects.filter(
            readout_id__in=readouts
        ).prefetch_related(
            'readout_id',
            'assay_id'
        ).order_by(
            'assay_id__assay_short_name'
        )
        related_assays_map = {}

        for assay in related_assays:
            # start appending to a list keyed by the readout ID for all related images
            related_assays_map.setdefault(assay.readout_id_id, []).append(assay)

        for readout in readouts:
            # set an attribute on the readout that is the list created above
            readout.related_assays = related_assays_map.get(readout.id)

        context['readouts'] = readouts

        context['results'] = AssayChipResult.objects.prefetch_related(
            'result_function',
            'result_type',
            'test_unit',
            'assay_result__chip_readout__chip_setup__unit',
            'assay_result__chip_readout__chip_setup__compound',
            'assay_name__assay_id',
            'assay_result__created_by'
        ).filter(
            assay_result__chip_readout=context['readouts']
        )

        context['number_of_results'] = AssayChipTestResult.objects.filter(chip_readout=context['readouts']).count()

        # PLATES
        context['plate_setups'] = AssayPlateSetup.objects.filter(
            assay_run_id=self.object
        ).prefetch_related(
            'assay_layout',
            'created_by'
        )
        readouts = AssayPlateReadout.objects.filter(
            setup=context['plate_setups']
        ).prefetch_related(
            'setup',
            'created_by'
        )

        related_assays = AssayPlateReadoutAssay.objects.filter(
            readout_id__in=readouts
        ).prefetch_related(
            'readout_id',
            'assay_id'
        ).order_by(
            'assay_id__assay_short_name'
        )
        related_assays_map = {}

        for assay in related_assays:
            # start appending to a list keyed by the readout ID for all related images
            related_assays_map.setdefault(assay.readout_id_id, []).append(assay)

        for readout in readouts:
            # set an attribute on the readout that is the list created above
            readout.related_assays = related_assays_map.get(readout.id)

        context['plate_readouts'] = readouts

        context['plate_results'] = AssayPlateResult.objects.prefetch_related(
            'result_function',
            'result_type',
            'test_unit',
            'assay_result__readout__setup',
            'assay_name__assay_id',
            'assay_result__created_by'
        ).filter(
            assay_result__readout=context['plate_readouts']
        )

        context['number_of_plate_results'] = AssayPlateTestResult.objects.filter(
            readout=context['plate_readouts']
        ).count()

        return self.render_to_response(context)


# Class-based views for studies
class AssayRunList(LoginRequiredMixin, ListView):
    """A list of all studies"""
    model = AssayRun

    def get_queryset(self):
        queryset = AssayRun.objects.prefetch_related(
            'created_by',
            'group',
            'signed_off_by'
        )
        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        return queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )

StudySupportingDataFormset = inlineformset_factory(
    AssayRun,
    StudySupportingData,
    formset=StudySupportingDataInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'description': forms.Textarea(attrs={'rows': 3}),
    }
)


class AssayRunAdd(OneGroupRequiredMixin, CreateView):
    """Add a study"""
    template_name = 'assays/assayrun_add.html'
    form_class = AssayRunForm

    def get_context_data(self, **kwargs):
        context = super(AssayRunAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = StudySupportingDataFormset(self.request.POST, self.request.FILES)
            else:
                context['formset'] = StudySupportingDataFormset()

        return context

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(groups, self.request.POST, self.request.FILES)
        # If GET
        else:
            return form_class(groups)

    # Test form validity
    def form_valid(self, form):
        formset = StudySupportingDataFormset(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(
                self.object.get_absolute_url()
            )
        else:
            return self.render_to_response(self.get_context_data(form=form))


# class AssayRunDetail(DetailRedirectMixin, DetailView):
#     """Details for a Study"""
#     model = AssayRun
#
#     update_redirect_url = '/assays/{}'
#
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data(object=self.object)
#         context['setups'] = AssayChipSetup.objects.filter(
#             assay_run_id=self.object
#         ).prefetch_related(
#             'assay_run_id',
#             'device',
#             'compound',
#             'unit',
#             'created_by'
#         )
#         readouts = AssayChipReadout.objects.filter(
#             chip_setup=context['setups']
#         ).prefetch_related(
#             'chip_setup',
#             'created_by'
#         ).select_related(
#             'chip_setup__compound',
#             'chip_setup__unit'
#         )
#
#         related_assays = AssayChipReadoutAssay.objects.filter(
#             readout_id__in=readouts
#         ).prefetch_related(
#             'readout_id',
#             'assay_id'
#         ).order_by(
#             'assay_id__assay_short_name'
#         )
#         related_assays_map = {}
#
#         for assay in related_assays:
#             # start appending to a list keyed by the readout ID for all related images
#             related_assays_map.setdefault(assay.readout_id_id, []).append(assay)
#
#         for readout in readouts:
#             # set an attribute on the readout that is the list created above
#             readout.related_assays = related_assays_map.get(readout.id)
#
#         context['readouts'] = readouts
#
#         context['results'] = AssayChipResult.objects.prefetch_related(
#             'assay_name',
#             'assay_result',
#             'result_function',
#             'result_type',
#             'test_unit'
#         ).select_related(
#             'assay_result__chip_readout__chip_setup',
#             'assay_result__chip_readout__chip_setup__unit',
#             'assay_name__assay_id',
#             'assay_result__created_by'
#         ).filter(
#             assay_result__chip_readout=context['readouts']
#         )
#
#         return self.render_to_response(context)


class AssayRunUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update the fields of a Study"""
    model = AssayRun
    template_name = 'assays/assayrun_add.html'
    form_class = AssayRunForm

    def get_context_data(self, **kwargs):
        context = super(AssayRunUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = StudySupportingDataFormset(
                    self.request.POST,
                    self.request.FILES,
                    instance=self.object
                )
            else:
                context['formset'] = StudySupportingDataFormset(instance=self.object)

        context['update'] = True

        return context

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(groups, self.request.POST, self.request.FILES, instance=self.get_object())
        # If GET
        else:
            return form_class(groups, instance=self.get_object())

    def form_valid(self, form):
        formset = StudySupportingDataFormset(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)

            # TODO Update the group and restricted status of children
            # TODO REVISE KLUDGE; MAY WANT TO TOTALLY ELIMINATE THESE FIELDS?
            AssayChipSetup.objects.filter(assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)
            AssayChipReadout.objects.filter(chip_setup__assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)
            AssayChipTestResult.objects.filter(chip_readout__chip_setup__assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)
            AssayPlateSetup.objects.filter(assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)
            AssayPlateReadout.objects.filter(setup__assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)
            AssayPlateTestResult.objects.filter(readout__setup__assay_run_id=self.object).update(group=self.object.group, restricted=self.object.restricted)

            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


def compare_cells(current_model, current_filter, setups):
    """Compare cells to discern setups use the same sort and amount of cells"""
    cells = {}

    for setup in setups:
        cells.update(
            {
                setup: sorted(current_model.objects.filter(**{current_filter: setup.id}).values_list(
                    'cell_sample',
                    'cell_biosensor',
                    'cellsample_density',
                    'cellsample_density_unit',
                    'cell_passage'))
            }
        )

    sameness = {setup: {} for setup in setups}
    max_same = 0
    best_setup = setups[0]

    for setup_1 in setups:
        same = 0
        for setup_2 in setups:
            if setup_1 != setup_2:
                if cells.get(setup_1) == cells.get(setup_2):
                    sameness.get(setup_1).update({str(setup_2): True})
                    same += 1
                else:
                    sameness.get(setup_1).update({str(setup_2): False})
        if same > max_same:
            max_same = same
            best_setup = setup_1

    return (best_setup, sameness.get(best_setup))


class AssayRunSummary(ViewershipMixin, DetailView):
    """Displays information for a given study

    Currently only shows data for chip readouts and chip/plate setups
    """
    model = AssayRun
    template_name = 'assays/assayrun_summary.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['setups'] = AssayChipSetup.objects.filter(
            assay_run_id=self.object
        ).prefetch_related(
            'assay_run_id',
            'device',
            'compound',
            'unit',
            'created_by'
        )

        # TODO THIS SAME BUSINESS NEEDS TO BE REFACTORED
        # For chips
        indicative = None
        sameness = {}

        if len(context['setups']) > 1:
            results = compare_cells(AssayChipCells, 'assay_chip', context['setups'])
            indicative = results[0]
            sameness = results[1]
        elif len(context['setups']) == 1:
            indicative = context['setups'][0]

        context['sameness'] = sameness
        context['indicative'] = indicative

        # For plates
        context['plate_setups'] = AssayPlateSetup.objects.filter(
            assay_run_id=self.object
        ).prefetch_related(
            'assay_run_id',
            'assay_layout',
            'created_by'
        )

        indicative = None
        sameness = {}

        if len(context['plate_setups']) > 1:
            results = compare_cells(AssayPlateCells, 'assay_plate', context['plate_setups'])
            indicative = results[0]
            sameness = results[1]
        elif len(context['plate_setups']) == 1:
            indicative = context['plate_setups'][0]

        context['plate_sameness'] = sameness
        context['plate_indicative'] = indicative

        return self.render_to_response(context)


class AssayRunDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete a Setup"""
    model = AssayRun
    template_name = 'assays/assayrun_delete.html'
    success_url = '/assays/editable_studies/'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['chip_setups'] = AssayChipSetup.objects.filter(
            assay_run_id=self.object.id
        ).prefetch_related(
            'compound',
            'unit'
        )
        context['chip_readouts'] = AssayChipReadout.objects.filter(chip_setup=context['chip_setups'])
        context['chip_results'] = AssayChipTestResult.objects.filter(chip_readout=context['chip_readouts'])

        context['plate_setups'] = AssayPlateSetup.objects.filter(assay_run_id=self.object)
        context['plate_readouts'] = AssayPlateReadout.objects.filter(setup=context['plate_setups'])
        context['plate_results'] = AssayPlateTestResult.objects.filter(readout=context['plate_readouts'])

        return self.render_to_response(context)


# Class based view for chip setups
class AssayChipSetupList(LoginRequiredMixin, ListView):
    """Displays a list of Chip Setups"""
    model = AssayChipSetup

    def get_queryset(self):
        queryset = AssayChipSetup.objects.prefetch_related(
            'assay_run_id',
            'device',
            'organ_model',
            'compound',
            'unit',
            'created_by',
            'group',
            'signed_off_by'
        )
        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        return queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )


AssayChipCellsFormset = inlineformset_factory(
    AssayChipSetup,
    AssayChipCells,
    formset=AssayChipCellsInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'cellsample_density': forms.NumberInput(attrs={'style': 'width:100px;'}),
        'cell_passage': forms.TextInput(attrs={'size': 5})
    }
)


# Cloning was recently refactored
class AssayChipSetupAdd(StudyGroupRequiredMixin, CreateView):
    """Add a Chip Setup (with inline for Chip Cells)"""
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_add.html'
    # May want to define form with initial here
    form_class = AssayChipSetupForm

    # Specify that cloning is permitted
    cloning_permitted = True

    def get_form(self, form_class):
        if self.request.method == 'POST':
            form = form_class(self.request.POST)
        elif self.request.GET.get('clone', ''):
            pk = int(self.request.GET.get('clone', ''))
            clone = get_object_or_404(AssayChipSetup, pk=pk)
            form = form_class(instance=clone)
        else:
            form = form_class()

        add_study_fields_to_form(self, form, add_study=True)

        return form

    def get_context_data(self, **kwargs):
        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(
            group__in=groups
        ).order_by(
            '-receipt_date'
        ).prefetch_related(
            'cell_type',
            'supplier',
            'cell_subtype'
        )
        context = super(AssayChipSetupAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = AssayChipCellsFormset(self.request.POST)
            elif self.request.GET.get('clone', ''):
                pk = int(self.request.GET.get('clone', ''))
                clone = get_object_or_404(AssayChipSetup, pk=pk)
                context['formset'] = AssayChipCellsFormset(instance=clone)
            else:
                context['formset'] = AssayChipCellsFormset()

        # Cellsamples will always be the same
        context['cellsamples'] = cellsamples

        return context

    def form_valid(self, form):
        formset = AssayChipCellsFormset(self.request.POST, instance=form.instance, save_as_new=True)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            save_forms_with_tracking(self, form, formset=formset, update=False)
            if data['another']:
                form = self.form_class(
                    instance=self.object,
                    initial={'success': True}
                )
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipSetupDetail(DetailRedirectMixin, DetailView):
    """Details for a Chip Setup"""
    model = AssayChipSetup


# TODO IMPROVE METHOD FOR CLONING
class AssayChipSetupUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update a Chip Setup and Chip Cells inline"""
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_add.html'
    form_class = AssayChipSetupForm

    def get_context_data(self, **kwargs):
        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(
            group__in=groups
        ).order_by(
            '-receipt_date'
        ).prefetch_related(
            'cell_type',
            'supplier',
            'cell_subtype'
        )

        context = super(AssayChipSetupUpdate, self).get_context_data(**kwargs)

        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = AssayChipCellsFormset(self.request.POST, instance=self.object)
            else:
                context['formset'] = AssayChipCellsFormset(instance=self.object)

        context['cellsamples'] = cellsamples
        context['update'] = True

        return context

    def form_valid(self, form):
        formset = AssayChipCellsFormset(self.request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipSetupDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete a Chip Setup and Chip Cells"""
    model = AssayChipSetup
    template_name = 'assays/assaychipsetup_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.assay_run_id_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['readouts'] = AssayChipReadout.objects.filter(chip_setup=self.object)
        context['results'] = AssayChipTestResult.objects.filter(chip_readout=context['readouts'])

        return self.render_to_response(context)


# Class based views for readouts
class AssayChipReadoutList(LoginRequiredMixin, ListView):
    """Displays a list of Chip Readouts"""
    model = AssayChipReadout

    def get_queryset(self):
        queryset = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id__restricted=False
        ).prefetch_related(
            'chip_setup__assay_run_id',
            'chip_setup__compound',
            'chip_setup__unit',
            'created_by',
            'group',
            'signed_off_by'
        )

        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        queryset = queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )

        related_assays = AssayChipReadoutAssay.objects.filter(
            readout_id__in=queryset
        ).prefetch_related(
            'readout_id',
            'assay_id'
        ).order_by(
            'assay_id__assay_short_name'
        )
        related_assays_map = {}

        for assay in related_assays:
            # start appending to a list keyed by the readout ID for all related images
            related_assays_map.setdefault(assay.readout_id_id, []).append(assay)

        for readout in queryset:
            # set an attribute on the readout that is the list created above
            readout.related_assays = related_assays_map.get(readout.id)

        return queryset


ACRAFormSet = inlineformset_factory(
    AssayChipReadout,
    AssayChipReadoutAssay,
    formset=AssayChipReadoutInlineFormset,
    extra=1,
    exclude=[],
)


class AssayChipReadoutAdd(StudyGroupRequiredMixin, CreateView):
    """Add a Chip Readout with inline for Assay Chip Readout Assays"""
    template_name = 'assays/assaychipreadout_add.html'
    form_class = AssayChipReadoutForm
    model = AssayChipReadout

    # Specify that cloning is permitted
    cloning_permitted = True

    def get_form(self, form_class):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        current = None
        if self.request.method == 'POST':
            form = form_class(study, current, self.request.POST, self.request.FILES)
        elif self.request.GET.get('clone', ''):
            pk = int(self.request.GET.get('clone', ''))
            clone = get_object_or_404(AssayChipReadout, pk=pk)
            form = form_class(
                study,
                current,
                instance=clone,
                initial={'file': None}
            )
        else:
            form = form_class(study, current)

        add_study_fields_to_form(self, form)

        return form

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = ACRAFormSet(self.request.POST, self.request.FILES)
            elif self.request.GET.get('clone', ''):
                pk = int(self.request.GET.get('clone', ''))
                clone = get_object_or_404(AssayChipReadout, pk=pk)
                context['formset'] = ACRAFormSet(instance=clone)
            else:
                context['formset'] = ACRAFormSet()

        context['study'] = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        formset = ACRAFormSet(self.request.POST, self.request.FILES, instance=form.instance, save_as_new=True)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            # Get headers
            headers = int(data.get('headers'))

            save_forms_with_tracking(self, form, formset=formset, update=False)

            if formset.files.get('file', ''):
                current_file = formset.files.get('file', '')
                parse_chip_csv(self.object, current_file, headers, form)
            if data['another']:
                form = self.form_class(
                    study,
                    None,
                    instance=self.object,
                    initial={'file': None, 'success': True}
                )
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    def render_to_response(self, context):
        # TODO REFACTOR
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(
            assay_run_id=study
        ).prefetch_related(
            'assay_run_id',
            'device',
            'compound',
            'unit',
            'created_by'
        ).exclude(
            id__in=list(set(exclude_list))
        )
        if not setups:
            return redirect('/assays/'+str(study.id))

        return super(AssayChipReadoutAdd, self).render_to_response(context)


class AssayChipReadoutDetail(DetailRedirectMixin, DetailView):
    """Detail for Chip Readout"""
    model = AssayChipReadout


class AssayChipReadoutUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update Assay Chip Readout and Assay Chip Readout Assays"""
    model = AssayChipReadout
    template_name = 'assays/assaychipreadout_add.html'
    form_class = AssayChipReadoutForm

    def get_form(self, form_class):
        study = self.object.chip_setup.assay_run_id
        current = self.object.chip_setup_id

        # If POST
        if self.request.method == 'POST':
            return form_class(study, current, self.request.POST, self.request.FILES, instance=self.get_object())
        # If GET
        else:
            return form_class(study, current, instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(AssayChipReadoutUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = ACRAFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = ACRAFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = ACRAFormSet(self.request.POST, self.request.FILES, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            # Get headers
            headers = int(data.get('headers'))

            save_forms_with_tracking(self, form, formset=formset, update=True)

            # Save file if it exists
            if formset.files.get('file', ''):
                file = formset.files.get('file', '')
                parse_chip_csv(self.object, file, headers, form)
            # If no file, try to update the qc_status
            else:
                modify_qc_status_chip(self.object, form)
            # Clear data if clear is checked
            if self.request.POST.get('file-clear', ''):
                AssayChipRawData.objects.filter(assay_chip_id=self.object).delete()
            # Otherwise do nothing (the file remained the same)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipReadoutDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete Assay Chip Readout"""
    model = AssayChipReadout
    template_name = 'assays/assaychipreadout_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.chip_setup.assay_run_id_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['results'] = AssayChipTestResult.objects.filter(chip_readout=self.object)

        return self.render_to_response(context)


# Class-based views for test results
class AssayChipTestResultList(LoginRequiredMixin, ListView):
    """Displays a list of Chip Test Results"""
    # model = AssayChipTestResult
    template_name = 'assays/assaychiptestresult_list.html'

    def get_queryset(self):
        queryset = AssayChipResult.objects.prefetch_related(
            'assay_name__assay_id',
            'assay_result__chip_readout__chip_setup',
            'assay_result__chip_readout__chip_setup__compound',
            'assay_result__chip_readout__chip_setup__unit',
            'assay_result__chip_readout__chip_setup__assay_run_id',
            'assay_result__created_by',
            'assay_result__group',
            'assay_result__signed_off_by',
            'result_function',
            'result_type',
            'test_unit'
        )

        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        return queryset.filter(
            assay_result__restricted=False
        ) | queryset.filter(
            assay_result__group__name__in=group_names
        )


ChipTestResultFormSet = inlineformset_factory(
    AssayChipTestResult,
    AssayChipResult,
    formset=ChipTestResultInlineFormset,
    extra=1,
    exclude=[],
    widgets={'value': forms.NumberInput(attrs={'style': 'width:100px;', })}
)


class AssayChipTestResultAdd(StudyGroupRequiredMixin, CreateView):
    """Add a Chip Test Result with inline for individual results"""
    template_name = 'assays/assaychiptestresult_add.html'
    form_class = AssayChipResultForm

    def get_form(self, form_class):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        current = None

        if self.request.method == 'POST':
            form = form_class(study, current, self.request.POST)
        else:
            form = form_class(study, current)

        add_study_fields_to_form(self, form)

        return form

    def get_context_data(self, **kwargs):
        context = super(AssayChipTestResultAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = ChipTestResultFormSet(self.request.POST)
            else:
                context['formset'] = ChipTestResultFormSet()

        context['study'] = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        return context

    def form_valid(self, form):
        formset = ChipTestResultFormSet(self.request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    # TODO REFACTOR
    def render_to_response(self, context):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayChipTestResult.objects.filter(
            chip_readout__isnull=False
        ).values_list(
            'chip_readout',
            flat=True
        )
        readouts = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id=study
        ).exclude(
            id__in=list(set(exclude_list))
        )

        if not readouts:
            return redirect('/assays/'+str(study.id))

        return super(AssayChipTestResultAdd, self).render_to_response(context)


class AssayChipTestResultDetail(DetailRedirectMixin, DetailView):
    """Display details for Chip Test Result"""
    model = AssayChipTestResult


class AssayChipTestResultUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update a Chip Test Result and inline of individual results"""
    model = AssayChipTestResult
    template_name = 'assays/assaychiptestresult_add.html'
    form_class = AssayChipResultForm

    def get_form(self, form_class):
        study = self.object.chip_readout.chip_setup.assay_run_id
        current = self.object.chip_readout_id

        # If POST
        if self.request.method == 'POST':
            return form_class(study, current, self.request.POST, instance=self.get_object())
        # If GET
        else:
            return form_class(study, current, instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(AssayChipTestResultUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = ChipTestResultFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = ChipTestResultFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = ChipTestResultFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayChipTestResultDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete a Chip Test Result"""
    model = AssayChipTestResult
    template_name = 'assays/assaychiptestresult_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.chip_readout.chip_setup.assay_run_id_id)


# Class-based views for study configuration
class StudyConfigurationList(LoginRequiredMixin, ListView):
    """Display a lsit of Study Configurations"""
    model = StudyConfiguration
    template_name = 'assays/studyconfiguration_list.html'


# FormSet for Study Models
StudyModelFormSet = inlineformset_factory(
    StudyConfiguration,
    StudyModel,
    extra=1,
    exclude=[],
    widgets={
        'label': forms.TextInput(attrs={'size': 2}),
        'sequence_number': forms.TextInput(attrs={'size': 2})
    }
)


class StudyConfigurationAdd(OneGroupRequiredMixin, CreateView):
    """Add a Study Configuration with inline for Associtated Models"""
    template_name = 'assays/studyconfiguration_add.html'
    form_class = StudyConfigurationForm

    def get_context_data(self, **kwargs):
        context = super(StudyConfigurationAdd, self).get_context_data(**kwargs)

        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = StudyModelFormSet(self.request.POST)
            else:
                context['formset'] = StudyModelFormSet()

        return context

    def form_valid(self, form):
        formset = StudyModelFormSet(self.request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class StudyConfigurationUpdate(OneGroupRequiredMixin, UpdateView):
    """Update a Study Configuration with inline for Associtated Models"""
    model = StudyConfiguration
    template_name = 'assays/studyconfiguration_add.html'
    form_class = StudyConfigurationForm

    def get_context_data(self, **kwargs):
        context = super(StudyConfigurationUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = StudyModelFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = StudyModelFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = StudyModelFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Class-based views for LAYOUTS
class AssayLayoutList(LoginRequiredMixin, ListView):
    """Display a list of Assay Layouts"""
    model = AssayLayout

    def get_queryset(self):
        # Not bothering with restricted at the moment
        # return AssayLayout.objects.filter(
        # restricted=False
        # ).prefetch_related(
        # 'created_by',
        # 'group',
        # 'device'
        # ) | AssayLayout.objects.filter(
        #     group__in=self.request.user.groups.all()
        # ).prefetch_related('created_by',
        # 'group',
        # 'device'
        # )
        return AssayLayout.objects.filter(
            group__in=self.request.user.groups.all()
        ).prefetch_related(
            'created_by',
            'group',
            'device',
            'signed_off_by'
        )


class AssayLayoutAdd(OneGroupRequiredMixin, CreateView):
    """Add an Assay Layout"""
    model = AssayLayout
    form_class = AssayLayoutForm
    template_name = 'assays/assaylayout_add.html'

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(groups, self.request.POST)
        # If GET
        else:
            return form_class(groups)

    # Test form validity
    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=False)
            # Save assay layout
            save_assay_layout(self.request, self.object, form, False)
            return redirect(self.object.get_post_submission_url())

        else:
            return self.render_to_response(self.get_context_data(form=form))


# TODO Assay Layout Detail does not currently exist (deemed lower priority)
# class AssayLayoutDetail(DetailRedirectMixin, DetailView):
#     model = AssayLayout


class AssayLayoutUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update an Assay Layout"""
    model = AssayLayout
    form_class = AssayLayoutForm
    template_name = 'assays/assaylayout_add.html'

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(groups, self.request.POST, instance=self.get_object())
        # If GET
        else:
            return form_class(groups, instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(AssayLayoutUpdate, self).get_context_data(**kwargs)
        context['update'] = True

        return context

    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=True)
            # Save assay layout
            save_assay_layout(self.request, self.object, form, True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayLayoutDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete an Assay Layout"""
    model = AssayLayout
    template_name = 'assays/assaylayout_delete.html'

    def get_success_url(self):
        return '/assays/assaylayout/'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['setups'] = AssayPlateSetup.objects.filter(assay_layout=self.object)
        context['readouts'] = AssayPlateReadout.objects.filter(setup=context['setups'])
        context['results'] = AssayPlateTestResult.objects.filter(readout=context['readouts'])

        return self.render_to_response(context)


# Class-based views for LAYOUTS
class AssayPlateSetupList(LoginRequiredMixin, ListView):
    """List all Plate Setups"""
    model = AssayPlateSetup

    def get_queryset(self):
        queryset = AssayPlateSetup.objects.prefetch_related(
            'created_by',
            'group',
            'assay_run_id',
            'assay_layout',
            'signed_off_by'
        )

        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        return queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )


# Formset for plate cells
AssayPlateCellsFormset = inlineformset_factory(
    AssayPlateSetup,
    AssayPlateCells,
    formset=AssayPlateCellsInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'cellsample_density': forms.NumberInput(attrs={'style': 'width:100px;', }),
        'cell_passage': forms.TextInput(attrs={'size': 5})
    }
)


# VIEWS FOR ASSAY PLATE (DEVICE) SETUP
class AssayPlateSetupAdd(StudyGroupRequiredMixin, CreateView):
    """Add a Plate Setup with inline for Plate Cells"""
    model = AssayPlateSetup
    form_class = AssayPlateSetupForm
    template_name = 'assays/assayplatesetup_add.html'

    # Specify that cloning is permitted
    cloning_permitted = True

    def get_form(self, form_class):
        if self.request.method == 'POST':
            form = form_class(self.request.POST)
        elif self.request.GET.get('clone', ''):
            pk = int(self.request.GET.get('clone', ''))
            clone = get_object_or_404(AssayPlateSetup, pk=pk)
            form = form_class(instance=clone)
        else:
            form = form_class()

        add_study_fields_to_form(self, form, add_study=True)

        return form

    def get_context_data(self, **kwargs):
        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(
            group__in=groups
        ).order_by(
            '-receipt_date'
        ).prefetch_related(
            'cell_type',
            'supplier',
            'cell_subtype'
        )
        context = super(AssayPlateSetupAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = AssayPlateCellsFormset(self.request.POST)
            elif self.request.GET.get('clone', ''):
                pk = int(self.request.GET.get('clone', ''))
                clone = get_object_or_404(AssayPlateSetup, pk=pk)
                context['formset'] = AssayPlateCellsFormset(instance=clone)
            else:
                context['formset'] = AssayPlateCellsFormset()

        # Cellsamples will always be the same
        context['cellsamples'] = cellsamples

        return context

    def form_valid(self, form):
        formset = AssayPlateCellsFormset(self.request.POST, instance=form.instance, save_as_new=True)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data

            save_forms_with_tracking(self, form, formset=formset, update=False)

            if data['another']:
                form = self.form_class(
                    instance=self.object,
                    initial={'success': True}
                )
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# TODO Assay Layout Detail does not currently exist (deemed lower priority)
class AssayPlateSetupDetail(DetailRedirectMixin, DetailView):
    """Details for a Plate Setup"""
    model = AssayPlateSetup


class AssayPlateSetupUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update a Plate Setup with inline for Plate Cells"""
    model = AssayPlateSetup
    form_class = AssayPlateSetupForm
    template_name = 'assays/assayplatesetup_add.html'

    def get_context_data(self, **kwargs):
        groups = self.request.user.groups.values_list('id', flat=True)
        cellsamples = CellSample.objects.filter(
            group__in=groups
        ).order_by(
            '-receipt_date'
        ).prefetch_related(
            'cell_type',
            'supplier',
            'cell_subtype'
        )
        context = super(AssayPlateSetupUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = AssayPlateCellsFormset(self.request.POST, instance=self.object)
            else:
                context['formset'] = AssayPlateCellsFormset(instance=self.object)

        # Cellsamples will always be the same
        context['cellsamples'] = cellsamples
        # Mark as update
        context['update'] = True

        return context

    def form_valid(self, form):
        formset = AssayPlateCellsFormset(self.request.POST, instance=form.instance)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayPlateSetupDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete a Plate Setup"""
    model = AssayPlateSetup
    template_name = 'assays/assayplatesetup_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.assay_run_id_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['readouts'] = AssayPlateReadout.objects.filter(setup=self.object)
        context['results'] = AssayPlateTestResult.objects.filter(readout=context['readouts'])

        return self.render_to_response(context)


# Class based views for readouts
class AssayPlateReadoutList(LoginRequiredMixin, ListView):
    """Display a list of Plate Readouts"""
    model = AssayPlateReadout

    def get_queryset(self):
        queryset = AssayPlateReadout.objects.prefetch_related(
            'created_by',
            'group',
            'setup__assay_run_id',
            'signed_off_by'
        )

        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        queryset = queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )

        related_assays = AssayPlateReadoutAssay.objects.filter(
            readout_id__in=queryset
        ).prefetch_related(
            'readout_id',
            'assay_id'
        ).order_by(
            'assay_id__assay_short_name'
        )
        related_assays_map = {}

        for assay in related_assays:
            # start appending to a list keyed by the readout ID for all related images
            related_assays_map.setdefault(assay.readout_id_id, []).append(assay)

        for readout in queryset:
            # set an attribute on the readout that is the list created above
            readout.related_assays = related_assays_map.get(readout.id)

        return queryset


APRAFormSet = inlineformset_factory(
    AssayPlateReadout,
    AssayPlateReadoutAssay,
    formset=AssayPlateReadoutInlineFormset,
    extra=1,
    exclude=[],
)


class AssayPlateReadoutAdd(StudyGroupRequiredMixin, CreateView):
    """Add a Plate Readout with inline for Assay Plate Readout Assays"""
    template_name = 'assays/assayplatereadout_add.html'
    form_class = AssayPlateReadoutForm
    model = AssayPlateReadout

    # Specify that cloning is permitted
    cloning_permitted = True

    def get_form(self, form_class):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        current = None
        if self.request.method == 'POST':
            form = form_class(study, current, self.request.POST, self.request.FILES)
        elif self.request.GET.get('clone', ''):
            pk = int(self.request.GET.get('clone', ''))
            clone = get_object_or_404(AssayPlateReadout, pk=pk)
            form = form_class(
                study,
                current,
                instance=clone,
                initial={'file': None}
            )
            # We do not want to keep the file (setup automatically excluded))
        else:
            form = form_class(study, current)

        add_study_fields_to_form(self, form)

        return form

    def get_context_data(self, **kwargs):
        context = super(AssayPlateReadoutAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = APRAFormSet(self.request.POST, self.request.FILES)
            elif self.request.GET.get('clone', ''):
                pk = int(self.request.GET.get('clone', ''))
                clone = get_object_or_404(AssayPlateReadout, pk=pk)
                context['formset'] = APRAFormSet(instance=clone)
            else:
                context['formset'] = APRAFormSet()

        context['study'] = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        return context

    def form_valid(self, form):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        formset = APRAFormSet(self.request.POST, self.request.FILES, instance=form.instance, save_as_new=True)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data

            # Get upload_type
            upload_type = data.get('upload_type')

            save_forms_with_tracking(self, form, formset=formset, update=False)

            if formset.files.get('file', ''):
                current_file = formset.files.get('file', '')
                parse_readout_csv(self.object, current_file, upload_type)
                # Check QC
                modify_qc_status_plate(self.object, form)
            if data['another']:
                form = self.form_class(
                    study,
                    None,
                    instance=self.object,
                    initial={'file': None, 'success': True}
                )
                return self.render_to_response(self.get_context_data(form=form))
            else:
                return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    # TODO REFACTOR
    def render_to_response(self, context):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayPlateReadout.objects.filter(setup__isnull=False).values_list('setup', flat=True)
        setups = AssayPlateSetup.objects.filter(
            assay_run_id=study
        ).prefetch_related(
            'assay_run_id',
            'assay_layout',
            'created_by'
        ).exclude(
            id__in=list(set(exclude_list))
        )

        if not setups:
            return redirect('/assays/'+str(study.id))

        return super(AssayPlateReadoutAdd, self).render_to_response(context)


# TODO NEED TO ADD TEMPLATE
class AssayPlateReadoutDetail(DetailRedirectMixin, DetailView):
    """Details for a Plate Readout"""
    model = AssayPlateReadout


class AssayPlateReadoutUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update a Plate Readout with inline for Assay Plate Readout Assays"""
    model = AssayPlateReadout
    template_name = 'assays/assayplatereadout_add.html'
    form_class = AssayPlateReadoutForm

    def get_form(self, form_class):
        study = self.object.setup.assay_run_id
        current = self.object.setup_id
        if self.request.method == 'POST':
            return form_class(study, current, self.request.POST, self.request.FILES, instance=self.object)
        else:
            return form_class(study, current, instance=self.object)

    def get_context_data(self, **kwargs):
        context = super(AssayPlateReadoutUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = APRAFormSet(self.request.POST, self.request.FILES, instance=self.object)
            else:
                context['formset'] = APRAFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = APRAFormSet(self.request.POST, self.request.FILES, instance=form.instance)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            # Get upload_type
            upload_type = data.get('upload_type')

            save_forms_with_tracking(self, form, formset=formset, update=True)

            # Save file if it exists
            if formset.files.get('file', ''):
                current_file = formset.files.get('file', '')
                parse_readout_csv(self.object, current_file, upload_type)
            # Clear data if clear is checked
            if self.request.POST.get('file-clear', ''):
                # remove_existing_readout(self.object)
                AssayReadout.objects.filter(assay_device_readout=self.object).delete()
            else:
                # Check QC
                modify_qc_status_plate(self.object, form)
            # Otherwise do nothing (the file remained the same)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# TODO ADD CONTEXT
class AssayPlateReadoutDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete an Assay Plate Readout"""
    model = AssayPlateReadout
    template_name = 'assays/assayplatereadout_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.setup.assay_run_id_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        context['results'] = AssayPlateTestResult.objects.filter(readout=self.object)

        return self.render_to_response(context)


# Class-based views for PLATE test results
class AssayPlateTestResultList(LoginRequiredMixin, ListView):
    """Display individual Assa Plate Results"""
    # model = AssayChipTestResult
    template_name = 'assays/assayplatetestresult_list.html'

    def get_queryset(self):
        queryset = AssayPlateResult.objects.prefetch_related(
            'result_function',
            'result_type',
            'test_unit',
            'assay_result__readout__setup__assay_run_id',
            'assay_name__assay_id',
            'assay_result__created_by',
            'assay_result__group',
            'assay_result__signed_off_by'
        )

        group_names = [group.name.replace(' Viewer', '') for group in self.request.user.groups.all()]
        return queryset.filter(
            assay_result__restricted=False
        ) | queryset.filter(
            assay_result__group__name__in=group_names
        )


PlateTestResultFormSet = inlineformset_factory(
    AssayPlateTestResult,
    AssayPlateResult,
    formset=PlateTestResultInlineFormset,
    extra=1,
    exclude=[],
    widgets={'value': forms.NumberInput(attrs={'style': 'width:100px;', })}
)


class AssayPlateTestResultAdd(StudyGroupRequiredMixin, CreateView):
    """Add Plate Test Result with inline for individual Plate Results"""
    template_name = 'assays/assayplatetestresult_add.html'
    form_class = AssayPlateResultForm

    def get_form(self, form_class):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        current = None

        if self.request.method == 'POST':
            form = form_class(study, current, self.request.POST)
        else:
            form = form_class(study, current)

        add_study_fields_to_form(self, form)

        return form

    def get_context_data(self, **kwargs):
        context = super(AssayPlateTestResultAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = PlateTestResultFormSet(self.request.POST)
            else:
                context['formset'] = PlateTestResultFormSet()

        context['study'] = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

        return context

    def form_valid(self, form):
        formset = PlateTestResultFormSet(self.request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    # Redirect when there are no available setups
    # TODO REFACTOR
    def render_to_response(self, context):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        exclude_list = AssayPlateTestResult.objects.filter(readout__isnull=False).values_list('readout', flat=True)
        readouts = AssayPlateReadout.objects.filter(setup__assay_run_id=study).exclude(id__in=list(set(exclude_list)))

        if not readouts:
            return redirect('/assays/'+str(study.id))

        return super(AssayPlateTestResultAdd, self).render_to_response(context)


class AssayPlateTestResultDetail(DetailRedirectMixin, DetailView):
    """Details for Plate Test Results"""
    model = AssayPlateTestResult


class AssayPlateTestResultUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update a Plate Test Result with inline for individual Plate Results"""
    model = AssayPlateTestResult
    template_name = 'assays/assayplatetestresult_add.html'
    form_class = AssayPlateResultForm

    def get_form(self, form_class):
        study = self.object.readout.setup.assay_run_id
        current = self.object.readout_id

        if self.request.method == 'POST':
            return form_class(study, current, self.request.POST, instance=self.object)
        else:
            return form_class(study, current, instance=self.object)

    def get_context_data(self, **kwargs):
        context = super(AssayPlateTestResultUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = PlateTestResultFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = PlateTestResultFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = PlateTestResultFormSet(self.request.POST, instance=self.object)
        # get user via self.request.user
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AssayPlateTestResultDelete(CreatorOrAdminRequiredMixin, DeleteView):
    """Delete a Plate Test Result"""
    model = AssayPlateTestResult
    template_name = 'assays/assayplatetestresult_delete.html'

    def get_success_url(self):
        return '/assays/' + str(self.object.readout.setup.assay_run_id_id)


def get_valid_csv_location(file_name, study_id, device_type):
    media_root = settings.MEDIA_ROOT.replace('mps/../', '', 1)

    valid_chars = '-_.{0}{1}'.format(string.ascii_letters, string.digits)
    # Get only valid chars
    valid_file_name = ''.join(c for c in file_name if c in valid_chars)
    # Replace spaces with underscores
    valid_file_name = re.sub(r'\s+', '_', valid_file_name)

    # Check if name is already in use
    if os.path.isfile(os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '.csv')):
        append = 1
        while os.path.isfile(
            os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '_' + str(append) + '.csv')
        ):
            append += 1
        valid_file_name += '_' + str(append)

    return os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '.csv')


def write_out_csv(file_name, data):
    """Write out a Unicode CSV

    Params:
    file_name -- name of the file to write
    data -- data to write to the file (as a list of lists)
    """
    with open(file_name, 'w') as out_file:
        writer = UnicodeWriter(out_file)
        writer.writerows(data)


def get_csv_media_location(file_name):
    """Returns the location given a full path

    Params:
    file_name -- name of the file to write
    """
    split_name = file_name.split('/')
    csv_onward = '/'.join(split_name[-4:])
    return csv_onward


class ReadoutBulkUpload(ObjectGroupRequiredMixin, UpdateView):
    """Upload an Excel Sheet for storing multiple sets of Readout data at one"""
    model = AssayRun
    template_name = 'assays/readoutbulkupload.html'
    form_class = ReadoutBulkUploadForm

    def get_form(self, form_class):
        # If POST
        if self.request.method == 'POST':
            return form_class(self.request.POST, self.request.FILES, instance=self.get_object())
        # If GET
        else:
            return form_class(instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(ReadoutBulkUpload, self).get_context_data(**kwargs)

        chip_readouts = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id=self.object
        ).prefetch_related('chip_setup')
        plate_readouts = AssayPlateReadout.objects.filter(
            setup__assay_run_id=self.object
        ).prefetch_related('setup')

        # TODO Could use a refactor
        chip_has_data = {}
        for readout in chip_readouts:
            if AssayChipRawData.objects.filter(assay_chip_id=readout):
                chip_has_data.update({readout: True})
        plate_has_data = {}
        for readout in plate_readouts:
            if AssayReadout.objects.filter(assay_device_readout=readout):
                plate_has_data.update({readout: True})

        context['chip_readouts'] = chip_readouts
        context['plate_readouts'] = plate_readouts

        context['chip_has_data'] = chip_has_data
        context['plate_has_data'] = plate_has_data

        context['version'] = len(os.listdir(MEDIA_ROOT + '/excel_templates/')) / 3

        return context

    def form_valid(self, form):
        if form.is_valid():
            csv_root = settings.MEDIA_ROOT.replace('mps/../', '', 1) + '/csv/'

            data = form.cleaned_data
            bulk_file = data.get('bulk_file')

            excel_file = xlrd.open_workbook(file_contents=bulk_file)

            # For the moment, just have headers be equal to two?
            headers = 1
            study = self.object
            study_id = str(self.object.id)

            # Make sure path exists for study
            if not os.path.exists(csv_root + study_id):
                os.makedirs(csv_root + study_id)

            for index, sheet in enumerate(excel_file.sheets()):
                # Skip sheets without anything
                if sheet.nrows < 1:
                    continue

                # Get the header row
                header = [unicode(value) for value in sheet.row_values(0)]

                sheet_type = ''

                if 'CHIP' in header[0].upper() and 'ASSAY' in header[3].upper():
                    sheet_type = 'Chip'

                # Check if plate tabular
                elif 'PLATE' in header[0].upper() and 'WELL' in header[1].upper() and 'ASSAY' in header[2].upper()\
                        and 'FEATURE' in header[3].upper() and 'UNIT' in header[4].upper():
                    sheet_type = 'Tabular'

                # Check if plate block
                elif 'PLATE' in header[0].upper() and 'ASSAY' in header[2].upper() and 'FEATURE' in header[4].upper()\
                        and 'UNIT' in header[6].upper():
                    sheet_type = 'Block'

                if sheet_type == 'Chip':
                    header = [
                        u'Chip ID',
                        u'Time',
                        u'Time Unit',
                        u'Assay',
                        u'Object',
                        u'Value',
                        u'Value Unit',
                        u'QC Status'
                    ]
                    csv_data = {}
                    # Skip header
                    for row_index in range(1, sheet.nrows):
                        row = [stringify_excel_value(value) for value in sheet.row_values(row_index)]

                        # Trim row to exclude validation columns and beyond
                        row = row[:TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX]

                        # Make sure the data is valid before adding it
                        # The first 7 cells need to be filled for a row to be valid
                        if row and all(row[:7]):
                            chip_id = row[0]

                            if chip_id not in csv_data:
                                csv_data.update({
                                    chip_id: [header]
                                })

                            csv_data.get(chip_id).append(row)

                    for chip_id in csv_data:
                        datalist = csv_data.get(chip_id)

                        readout = AssayChipReadout.objects.get(
                            chip_setup__assay_run_id=study,
                            chip_setup__assay_chip_id=chip_id
                        )

                        # Make sure path exists for chip
                        if not os.path.exists(csv_root + study_id + '/chip'):
                            os.makedirs(csv_root + study_id + '/chip')

                        # Get valid file location
                        # Note added csv extension
                        file_loc = get_valid_csv_location(chip_id, study_id, 'chip')
                        # Write the csv
                        write_out_csv(file_loc, datalist)

                        media_loc = get_csv_media_location(file_loc)

                        # Add the file to the readout
                        readout.file = media_loc
                        readout.save()

                        # Note the lack of a form normally used for QC
                        parse_chip_csv(readout, readout.file, headers, None)

                elif sheet_type == 'Tabular':
                    # Header if time
                    if 'TIME' in header[5].upper() and 'UNIT' in header[6].upper():
                        header = [
                            u'Plate ID',
                            u'Well Name',
                            u'Assay',
                            u'Feature',
                            u'Unit',
                            u'Time',
                            u'Time Unit',
                            u'Value'
                        ]
                    # Header if no time
                    else:
                        header = [
                            u'Plate ID',
                            u'Well Name',
                            u'Assay',
                            u'Feature',
                            u'Unit',
                            u'Value'
                        ]
                    csv_data = {}
                    # Skip header
                    for row_index in range(1, sheet.nrows):
                        row = [stringify_excel_value(value) for value in sheet.row_values(row_index)]

                        # Trim row to exclude validation columns and beyond
                        row = row[:TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX]

                        # Make sure the data is valid before adding it
                        # The first 6 cells must be filled (time and time unit are not required)
                        if row and all(row[:6]):
                            plate_id = row[0]

                            if plate_id not in csv_data:
                                csv_data.update({
                                    plate_id: [header]
                                })

                            csv_data.get(plate_id).append(row)

                    for plate_id in csv_data:
                        datalist = csv_data.get(plate_id)

                        readout = AssayPlateReadout.objects.get(
                            setup__assay_run_id=study,
                            setup__assay_plate_id=plate_id
                        )

                        # Make sure path exists for chip
                        if not os.path.exists(csv_root + study_id + '/plate'):
                            os.makedirs(csv_root + study_id + '/plate')

                        # Get valid file location
                        # Note added csv extension
                        file_loc = get_valid_csv_location(plate_id, study_id, 'plate')
                        # Write the csv
                        write_out_csv(file_loc, datalist)

                        media_loc = get_csv_media_location(file_loc)

                        # Add the file to the readout
                        readout.file = media_loc
                        readout.save()

                        # Note the lack of a form normally used for QC
                        parse_readout_csv(readout, readout.file, 'Tabular')

                elif sheet_type == 'Block':
                    csv_data = {}
                    # DO NOT skip header
                    plate_id = None
                    for row_index in range(sheet.nrows):
                        row = [stringify_excel_value(value) for value in sheet.row_values(row_index)]

                        # Trim row to exclude validation columns and beyond
                        row = row[:TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX]

                        if 'PLATE' in row[0].upper():
                            plate_id = row[1]

                            if plate_id not in csv_data:
                                csv_data.update({
                                    plate_id: []
                                })

                        csv_data.get(plate_id).append(row)

                    for plate_id in csv_data:
                        datalist = csv_data.get(plate_id)

                        readout = AssayPlateReadout.objects.get(
                            setup__assay_run_id=study,
                            setup__assay_plate_id=plate_id
                        )

                        # Make sure path exists for chip
                        if not os.path.exists(csv_root + study_id + '/plate'):
                            os.makedirs(csv_root + study_id + '/plate')

                        # Get valid file location
                        # Note added csv extension
                        file_loc = get_valid_csv_location(plate_id, study_id, 'plate')
                        # Write the csv
                        write_out_csv(file_loc, datalist)

                        media_loc = get_csv_media_location(file_loc)

                        # Add the file to the readout
                        readout.file = media_loc
                        readout.save()

                        # Note the lack of a form normally used for QC
                        parse_readout_csv(readout, readout.file, 'Block')

            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

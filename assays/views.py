# coding=utf-8
# IF YOU WANT TO SEE PAST VIEWS, DO NOT RELY ON THE COMMENTED CODE HEREIN
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.http import HttpResponse
# from assays.models import *
from cellsamples.models import CellSample
# TODO TRIM THIS IMPORT
# from assays.admin import *
from assays.models import (
    AssaySetup,
    AssayStudy,
    AssayMatrix,
    AssayMatrixItem
)
from assays.forms import (
    AssayStudyForm,
    StudySupportingDataFormSet,
    AssayInstanceFormSet,
    AssayMatrixForm,
    # AssayMatrixItemFormSet,
    # AssaySetupFormSet,
    # AssaySetupCellFormSet
)
from django import forms

# TODO REVISE SPAGHETTI CODE
from assays.ajax import get_chip_readout_data_as_csv
from assays.utils import (
    MATRIX_PREFETCH,
    MATRIX_ITEM_PREFETCH,
    parse_file_and_save,
    modify_qc_status_plate,
    modify_qc_status_chip,
    save_assay_layout,
    TIME_CONVERSIONS,
    CHIP_DATA_PREFETCH,
    REPLACED_DATA_POINT_CODE,
    EXCLUDED_DATA_POINT_CODE
)

from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
# from django.forms.models import inlineformset_factory
# from django.shortcuts import redirect, get_object_or_404, render_to_response

# from django.contrib.auth.models import Group
# from django.core.exceptions import PermissionDenied
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

from mps.templatetags.custom_filters import ADMIN_SUFFIX, VIEWER_SUFFIX, filter_groups, is_group_editor, is_group_admin

from mps.mixins import (
    LoginRequiredMixin,
    OneGroupRequiredMixin,
    ObjectGroupRequiredMixin,
    StudyGroupRequiredMixin,
    StudyViewershipMixin,
    DetailRedirectMixin,
    AdminRequiredMixin,
    DeletionMixin
    # CreatorOrAdminRequiredMixin,
    # SpecificGroupRequiredMixin
)

from mps.base.models import save_forms_with_tracking
from django.contrib.auth.models import User
from mps.settings import DEFAULT_FROM_EMAIL

# import ujson as json
import os

from mps.settings import MEDIA_ROOT, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX

# TODO Refactor imports
# TODO REFACTOR CERTAIN WHITTLING TO BE IN FORM AS OPPOSED TO VIEW
# TODO Rename get_absolute_url when the function does not actually return the model's URL
# TODO It is probably more semantic to overwrite get_context_data and form_valid in lieu of post and get for updates
# TODO ^ Update Views should be refactored soon
# NOTE THAT YOU NEED TO MODIFY INLINES HERE, NOT IN FORMS


def get_queryset_with_organ_model_map(queryset):
    """Takes a queryset and returns it with a organ model map"""
    setups = AssaySetup.objects.filter(
        organ_model__isnull=False
    ).prefetch_related(
        'study'
    )

    organ_model_map = {}

    for setup in setups:
        organ_model_map.setdefault(
            setup.study_id, {}
        ).update(
            {
                setup.organ_model.model_name: True
            }
        )

    for study in queryset:
        study.organ_models = ',\n'.join(
            sorted(organ_model_map.get(study.id, {}).keys())
        )


# TODO REVIEW PERMISSIONS
# Class-based views for studies
class GroupIndex(OneGroupRequiredMixin, ListView):
    """Displays all of the studies linked to groups that the user is part of"""
    template_name = 'assays/study_list.html'

    def get_queryset(self):
        queryset = AssayStudy.objects.prefetch_related('created_by', 'group', 'signed_off_by')

        # Display to users with either editor or viewer group or if unrestricted
        group_names = [group.name.replace(ADMIN_SUFFIX, '') for group in self.request.user.groups.all()]

        queryset = queryset.filter(group__name__in=group_names)

        get_queryset_with_organ_model_map(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupIndex, self).get_context_data(**kwargs)

        # Adds the word "editable" to the page
        context['editable'] = 'Editable '

        return context


class AssayStudyList(LoginRequiredMixin, ListView):
    """A list of all studies"""
    template_name = 'assays/assaystudy_list.html'
    model = AssayStudy

    def get_queryset(self):
        queryset = AssayStudy.objects.prefetch_related(
            'created_by',
            'group',
            'signed_off_by'
        )

        # Display to users with either editor or viewer group or if unrestricted
        group_names = [group.name.replace(VIEWER_SUFFIX, '').replace(ADMIN_SUFFIX, '') for group in self.request.user.groups.all()]
        queryset = queryset.filter(
            restricted=False
        ) | queryset.filter(
            group__name__in=group_names
        )

        get_queryset_with_organ_model_map(queryset)

        return queryset


class AssayStudyAdd(OneGroupRequiredMixin, CreateView):
    """Add a study"""
    template_name = 'assays/assaystudy_add.html'
    form_class = AssayStudyForm

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(self.request.POST, self.request.FILES, groups=groups)
        # If GET
        else:
            return form_class(groups=groups)

    def get_context_data(self, **kwargs):
        context = super(AssayStudyAdd, self).get_context_data(**kwargs)
        if self.request.POST:
            if 'assay_instance_formset' not in context:
                context['assay_instance_formset'] = AssayInstanceFormSet(self.request.POST)
            if 'supporting_data_formset' not in context:
                context['supporting_data_formset'] = StudySupportingDataFormSet(self.request.POST, self.request.FILES)
        else:
            context['assay_instance_formset'] = AssayInstanceFormSet()
            context['supporting_data_formset'] = StudySupportingDataFormSet()

        return context

    def form_valid(self, form):
        assay_instance_formset = AssayInstanceFormSet(
            self.request.POST,
            instance=form.instance
        )
        supporting_data_formset = StudySupportingDataFormSet(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if form.is_valid() and assay_instance_formset.is_valid() and supporting_data_formset.is_valid():
            save_forms_with_tracking(self, form, formset=[assay_instance_formset, supporting_data_formset], update=False)
            return redirect(
                self.object.get_absolute_url()
            )
        else:
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    assay_instance_formset=assay_instance_formset,
                    supporting_data_formset=supporting_data_formset
                )
            )


# TODO CHANGE
class AssayStudyUpdate(ObjectGroupRequiredMixin, UpdateView):
    """Update the fields of a Study"""
    model = AssayStudy
    template_name = 'assays/assaystudy_add.html'
    form_class = AssayStudyForm

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(self.request.POST, self.request.FILES, instance=self.object, groups=groups)
        # If GET
        else:
            return form_class(instance=self.object, groups=groups)

    def get_context_data(self, **kwargs):
        context = super(AssayStudyUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            if 'assay_instance_formset' not in context:
                context['assay_instance_formset'] = AssayInstanceFormSet(self.request.POST, instance=self.object)
            if 'supporting_data_formset' not in context:
                context['supporting_data_formset'] = StudySupportingDataFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['assay_instance_formset'] = AssayInstanceFormSet(instance=self.object)
            context['supporting_data_formset'] = StudySupportingDataFormSet(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        assay_instance_formset = AssayInstanceFormSet(
            self.request.POST,
            instance=form.instance
        )
        supporting_data_formset = StudySupportingDataFormSet(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )

        if form.is_valid() and assay_instance_formset.is_valid() and supporting_data_formset.is_valid():
            if not is_group_admin(self.request.user, self.object.group.name):
                if form.cleaned_data.get('signed_off', ''):
                    del form.cleaned_data['signed_off']
                form.cleaned_data['restricted'] = self.object.restricted

            if not form.instance.signed_off_by and form.cleaned_data.get('signed_off', ''):
                # Magic strings are in poor taste, should use a template instead
                subject = 'Study Sign Off Detected: {0}'.format(form.instance)
                message = 'Hello Admins,\n\n' \
                          'A study has been signed off on.\n\n' \
                          'Study: {0}\nSign Off By: {1} {2}\nLink: https://mps.csb.pitt.edu{3}\n\n' \
                          'Thanks,\nMPS'.format(
                    form.instance,
                    self.request.user.first_name,
                    self.request.user.last_name,
                    form.instance.get_absolute_url()
                )

                users_to_be_alerted = User.objects.filter(is_superuser=True, is_active=True)

                for user_to_be_alerted in users_to_be_alerted:
                    user_to_be_alerted.email_user(subject, message, DEFAULT_FROM_EMAIL)

            save_forms_with_tracking(self, form, formset=[assay_instance_formset, supporting_data_formset], update=True)
        else:
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    assay_instance_formset=assay_instance_formset,
                    supporting_data_formset=supporting_data_formset
                )
            )


# TODO ADD PERMISSION MIXINS
class AssayStudyIndex(DetailView):
    """Show all chip and plate models associated with the given study"""
    model = AssayStudy
    context_object_name = 'study_index'
    template_name = 'assays/assaystudy_index.html'

    # For permission mixin
    def get_object(self, queryset=None):
        self.study = super(AssayStudyIndex, self).get_object()
        return self.study

    def get_context_data(self, **kwargs):
        context = super(AssayStudyIndex, self).get_context_data(**kwargs)

        matrices = AssayMatrix.objects.filter(study=self.object)

        items = AssayMatrixItem.objects.filter(
            matrix=matrices
        ).prefetch_related(
            *MATRIX_ITEM_PREFETCH
        )

        # Cellsamples will always be the same
        context['matrices'] = matrices
        context['items'] = items

        return context


class AssayStudySummary(DetailView):
    """Displays information for a given study

    Currently only shows data for chip readouts and chip/plate setups
    """
    model = AssayStudy
    template_name = 'assays/assaystudy_summary.html'


# class AssayStudyDelete(AdminRequiredMixin, DeleteView):
#     """Delete a Study"""
#     model = AssayStudy
#     template_name = 'assays/assaystudy_delete.html'
#     success_url = '/assays/editable_studies/'


def get_cell_samples(user, setups=None):
    """Returns the cell samples to be listed in setup views

    Params:
    user - the user in the request
    setups - the setups in question
    """
    user_groups = user.groups.values_list('id', flat=True)

    # Get cell samples with group
    cellsamples_with_group = CellSample.objects.filter(
        group__in=user_groups
    ).prefetch_related(
        'cell_type__organ',
        'supplier',
        'cell_subtype__cell_type'
    )

    current_cell_samples = CellSample.objects.none()

    if setups:
        # Get the currently used cell samples
        current_cell_samples = CellSample.objects.filter(
            assaysetupcell__setup__in=setups
        ).prefetch_related(
            'cell_type__organ',
            'supplier',
            'cell_subtype__cell_type'
        )

    combined_query = cellsamples_with_group | current_cell_samples
    combined_query = combined_query.order_by('-receipt_date').distinct()

    # Return the combination of the querysets
    return combined_query


# TODO NOT THE RIGHT PERMISSION MIXIN
class AssayMatrixAdd(CreateView):
    """Add a matrix"""
    model = AssayMatrix
    template_name = 'assays/assaymatrix_add.html'
    form_class = AssayMatrixForm

    def get_form(self, form_class):
        # Get the study
        study = get_object_or_404(AssayStudy, pk=self.kwargs['study_id'])

        # If POST
        if self.request.method == 'POST':
            return form_class(self.request.POST, self.request.FILES, study=study, user=self.request.user)
        # If GET
        else:
            return form_class(study=study, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AssayMatrixAdd, self).get_context_data(**kwargs)

        cellsamples = get_cell_samples(self.request.user)

        # Cellsamples will always be the same
        context['cellsamples'] = cellsamples

        return context

    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# TODO NOT THE RIGHT PERMISSION MIXIN
class AssayMatrixUpdate(UpdateView):
    model = AssayMatrix
    template_name = 'assays/assaymatrix_add.html'
    form_class = AssayMatrixForm

    def get_form(self, form_class):
        # Get the study
        study = self.object.study

        # If POST
        if self.request.method == 'POST':
            return form_class(self.request.POST, self.request.FILES, instance=self.object, study=study, user=self.request.user)
        # If GET
        else:
            return form_class(instance=self.object, study=study, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AssayMatrixUpdate, self).get_context_data(**kwargs)

        cellsamples = get_cell_samples(self.request.user)

        # Cellsamples will always be the same
        context['cellsamples'] = cellsamples

        context['update'] = True

        return context

    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


# REMOVED FOR NOW TODO BRING BACK EVENTUALLY
# Class-based views for study configuration
# class StudyConfigurationList(LoginRequiredMixin, ListView):
#     """Display a list of Study Configurations"""
#     model = StudyConfiguration
#     template_name = 'assays/studyconfiguration_list.html'
#
#
# # FormSet for Study Models
# StudyModelFormSet = inlineformset_factory(
#     StudyConfiguration,
#     StudyModel,
#     extra=1,
#     exclude=[],
#     widgets={
#         'label': forms.TextInput(attrs={'size': 2}),
#         'sequence_number': forms.TextInput(attrs={'size': 2})
#     }
# )
#
#
# class StudyConfigurationAdd(OneGroupRequiredMixin, CreateView):
#     """Add a Study Configuration with inline for Associtated Models"""
#     template_name = 'assays/studyconfiguration_add.html'
#     form_class = StudyConfigurationForm
#
#     def get_context_data(self, **kwargs):
#         context = super(StudyConfigurationAdd, self).get_context_data(**kwargs)
#
#         if 'formset' not in context:
#             if self.request.POST:
#                 context['formset'] = StudyModelFormSet(self.request.POST)
#             else:
#                 context['formset'] = StudyModelFormSet()
#
#         return context
#
#     def form_valid(self, form):
#         formset = StudyModelFormSet(self.request.POST, instance=form.instance)
#
#         if form.is_valid() and formset.is_valid():
#             save_forms_with_tracking(self, form, formset=formset, update=False)
#             return redirect(self.object.get_post_submission_url())
#         else:
#             return self.render_to_response(self.get_context_data(form=form, formset=formset))
#
#
# class StudyConfigurationUpdate(OneGroupRequiredMixin, UpdateView):
#     """Update a Study Configuration with inline for Associtated Models"""
#     model = StudyConfiguration
#     template_name = 'assays/studyconfiguration_add.html'
#     form_class = StudyConfigurationForm
#
#     def get_context_data(self, **kwargs):
#         context = super(StudyConfigurationUpdate, self).get_context_data(**kwargs)
#         if 'formset' not in context:
#             if self.request.POST:
#                 context['formset'] = StudyModelFormSet(self.request.POST, instance=self.object)
#             else:
#                 context['formset'] = StudyModelFormSet(instance=self.object)
#
#         context['update'] = True
#
#         return context
#
#     def form_valid(self, form):
#         formset = StudyModelFormSet(self.request.POST, instance=self.object)
#
#         if form.is_valid() and formset.is_valid():
#             save_forms_with_tracking(self, form, formset=formset, update=True)
#             return redirect(self.object.get_post_submission_url())
#         else:
#             return self.render_to_response(self.get_context_data(form=form, formset=formset))

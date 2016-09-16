# coding=utf-8

from django.views.generic import ListView, CreateView, UpdateView
# from .models import *
from .forms import *
# Best practice would be to put this in base or something of that sort (avoid spaghetti code)
# Did this ^
from mps.mixins import OneGroupRequiredMixin, SpecificGroupRequiredMixin
from mps.templatetags.custom_filters import filter_groups
from django.shortcuts import redirect

# from mps.templatetags.custom_filters import *
from mps.base.models import save_forms_with_tracking


class CellSampleAdd(OneGroupRequiredMixin, CreateView):
    """Add a Cell Sample"""
    template_name = 'cellsamples/cellsample_add.html'
    form_class = CellSampleForm

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
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=False)
            return redirect('/cellsamples/cellsample')
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellSampleUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Update a Cell Sample"""
    model = CellSample
    template_name = 'cellsamples/cellsample_add.html'
    form_class = CellSampleForm

    required_group_name = 'Change Cell Samples Front'

    def get_form(self, form_class):
        # Get group selection possibilities
        groups = filter_groups(self.request.user)

        # If POST
        if self.request.method == 'POST':
            return form_class(groups, self.request.POST, self.request.FILES, instance=self.get_object())
        # If GET
        else:
            return form_class(groups, instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(CellSampleUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=True)
            return redirect('/cellsamples/cellsample')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSampleList(OneGroupRequiredMixin, ListView):
    """Displays a list of Cell Samples"""
    template_name = 'cellsamples/cellsample_list.html'

    def get_queryset(self):
        groups = self.request.user.groups.values_list('id', flat=True)
        queryset = CellSample.objects.filter(
            group__in=groups
        ).prefetch_related(
            'cell_type',
            'cell_subtype',
            'supplier',
            'group'
        ).select_related(
            'cell_type__organ'
        )
        return queryset


class CellTypeAdd(OneGroupRequiredMixin, CreateView):
    """Add a Cell Type"""
    template_name = 'cellsamples/celltype_add.html'
    form_class = CellTypeForm

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=False)
            return redirect('/cellsamples/celltype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellTypeUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Update a Cell Type"""
    model = CellType
    template_name = 'cellsamples/celltype_add.html'
    form_class = CellTypeForm

    required_group_name = 'Change Cell Samples Front'

    def get_context_data(self, **kwargs):
        context = super(CellTypeUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=True)
            return redirect('/cellsamples/celltype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellTypeList(ListView):
    """Display all Cell Types"""
    template_name = 'cellsamples/celltype_list.html'

    def get_queryset(self):
        queryset = CellType.objects.all().prefetch_related('organ')
        return queryset


# # TODO
class CellSubtypeAdd(OneGroupRequiredMixin, CreateView):
    """Add a Cell Subtype"""
    template_name = 'cellsamples/cellsubtype_add.html'
    form_class = CellSubtypeForm

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=False)
            return redirect('/cellsamples/cellsubtype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSubtypeUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Update a Cell Subtype"""
    model = CellSubtype
    template_name = 'cellsamples/cellsubtype_add.html'
    form_class = CellSubtypeForm

    required_group_name = 'Change Cell Samples Front'

    def get_context_data(self, **kwargs):
        context = super(CellSubtypeUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=None, update=True)
            return redirect('/cellsamples/cellsubtype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSubtypeList(ListView):
    """Display a list of Cell Subtypes"""
    template_name = 'cellsamples/cellsubtype_list.html'

    def get_queryset(self):
        queryset = CellSubtype.objects.all().select_related('cell_type', 'cell_type__organ')
        return queryset

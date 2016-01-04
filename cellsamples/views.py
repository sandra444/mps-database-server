# coding=utf-8

from django.views.generic import ListView, CreateView, UpdateView
from .models import *
from .forms import *
# Best practice would be to put this in base or something of that sort (avoid spaghetti code)
# Did this ^
from mps.mixins import OneGroupRequiredMixin, ObjectGroupRequiredMixin, SpecificGroupRequiredMixin
from django.shortcuts import redirect, get_object_or_404

#from mps.templatetags.custom_filters import *
from django.db.models import Q

class CellSampleAdd(OneGroupRequiredMixin, CreateView):
    template_name = 'cellsamples/cellsample_add.html'
    form_class = CellSampleForm

    def get_context_data(self, **kwargs):
        # Get group selection possibilities
        groups = self.request.user.groups.filter(
            ~Q(name__contains="Add ") & ~Q(name__contains="Change ") & ~Q(name__contains="Delete "))
        context = super(CellSampleAdd, self).get_context_data(**kwargs)
        context['groups'] = groups
        return context

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/cellsample')
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellSampleUpdate(SpecificGroupRequiredMixin, UpdateView):
    model = CellSample
    template_name = 'cellsamples/cellsample_add.html'
    form_class = CellSampleForm

    required_group_name = 'Change Cell Samples Front'

    def get_context_data(self, **kwargs):
        # Get group selection possibilities
        groups = self.request.user.groups.filter(
            ~Q(name__contains="Add ") & ~Q(name__contains="Change ") & ~Q(name__contains="Delete "))
        context = super(CellSampleUpdate, self).get_context_data(**kwargs)
        context['groups'] = groups
        context['update'] = True
        return context

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/cellsample')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSampleList(OneGroupRequiredMixin, ListView):
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
            'cell_type__cell_subtype',
            'cell_type__organ',
        )
        return queryset


class CellTypeAdd(OneGroupRequiredMixin, CreateView):
    template_name = 'cellsamples/celltype_add.html'
    form_class = CellTypeForm

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/celltype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellTypeUpdate(SpecificGroupRequiredMixin, UpdateView):
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
            self.object = form.save()
            self.object.modified_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/celltype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellTypeList(ListView):
    template_name = 'cellsamples/celltype_list.html'

    def get_queryset(self):
        queryset = CellType.objects.all().prefetch_related('cell_subtype','organ')
        return queryset


# # TODO
class CellSubtypeAdd(OneGroupRequiredMixin, CreateView):
    template_name = 'cellsamples/cellsubtype_add.html'
    form_class = CellSubtypeForm

    # Test form validity
    def form_valid(self, form):
        # get user via self.request.user
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/cellsubtype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSubtypeUpdate(SpecificGroupRequiredMixin, UpdateView):
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
            self.object = form.save()
            self.object.modified_by = self.request.user
            # Save Cell Sample
            self.object.save()
            return redirect('/cellsamples/cellsubtype')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CellSubtypeList(ListView):
    template_name = 'cellsamples/cellsubtype_list.html'

    def get_queryset(self):
        queryset = CellSubtype.objects.all().select_related('cell_type','cell_type__organ')
        return queryset

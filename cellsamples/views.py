# coding=utf-8

from django.views.generic import ListView, CreateView, UpdateView
from .models import *
from .forms import *
# Best practice would be to put this in base or something of that sort (avoid spaghetti code)
from assays.views import LoginRequiredMixin, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group

from mps.filters import *
from django.db.models import Q

class CellSampleAdd(LoginRequiredMixin, CreateView):
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

    def get(self, request, **kwargs):
        self.object = None
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
            return PermissionDenied(request, 'You must be a member of at least one group')
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellSampleUpdate(LoginRequiredMixin, UpdateView):
    model = CellSample
    template_name = 'cellsamples/cellsample_add.html'
    form_class = CellSampleForm

    def get_context_data(self, **kwargs):
        # Get group selection possibilities
        groups = self.request.user.groups.filter(
            ~Q(name__contains="Add ") & ~Q(name__contains="Change ") & ~Q(name__contains="Delete "))
        context = super(CellSampleUpdate, self).get_context_data(**kwargs)
        context['groups'] = groups
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

    def get(self, request, **kwargs):
        self.object = self.get_object()
        if not has_group(request.user, self.object.group):
            return PermissionDenied(request,'You must be a member of ' + str(self.object.group))
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

class CellSampleList(ListView):
    template_name = 'cellsamples/cellsample_list.html'

    def get_queryset(self):
        groups = self.request.user.groups.values_list('id', flat=True)
        queryset = CellSample.objects.filter(group__in=groups).prefetch_related('cell_type', 'supplier').select_related('cell_type__cell_subtype', 'cell_type__organ')
        return queryset


class CellTypeAdd(LoginRequiredMixin, CreateView):
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

    def get(self, request, **kwargs):
        self.object = None
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
            return PermissionDenied(request, 'You must be a member of at least one group')
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))


# Note that updating a model clears technically blank fields (exclude in form to avoid this)
class CellTypeUpdate(LoginRequiredMixin, UpdateView):
    model = CellType
    template_name = 'cellsamples/celltype_add.html'
    form_class = CellTypeForm

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

    def get(self, request, **kwargs):
        self.object = self.get_object()
        if len(request.user.groups.values_list('pk', flat=True)) == 0:
            return PermissionDenied(request, 'You must be a member of at least one group')
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

class CellTypeList(ListView):
    template_name = 'cellsamples/celltype_list.html'

    def get_queryset(self):
        queryset = CellType.objects.all().prefetch_related('cell_subtype','organ')
        return queryset

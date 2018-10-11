from django import forms
from .models import Compound, CompoundTarget
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from mps.mixins import SpecificGroupRequiredMixin
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from .forms import CompoundTargetInlineFormset, CompoundForm
from django.shortcuts import redirect
from django.forms.models import inlineformset_factory
from mps.base.models import save_forms_with_tracking


class CompoundsList(ListView):
    """Display a list of compounds (not to be confused with CompoundReport"""
    model = Compound
    template_name = 'compounds/compounds_list.html'
    # If variable pagination is desired, just jam that into GET too
    # paginate_by = 50
    #
    # def get_queryset(self):
    #     try:
    #         name = self.request.GET['name']
    #     except:
    #         name = ''
    #     if (name != ''):
    #         object_list = self.model.objects.filter(name__icontains = name)
    #     else:
    #         object_list = self.model.objects.all()
    #     return object_list


class CompoundsDetail(DetailView):
    """Show a Compounds details (no editing)"""
    model = Compound
    template_name = 'compounds/compounds_detail.html'

    def get_object(self, queryset=None):
        obj = super(CompoundsDetail, self).get_object(queryset)

        # If there is a compound
        if obj:
            # Get the associated targets
            targets = CompoundTarget.objects.filter(compound=obj)
            # For each target, split up the actions so they can be individual labels
            for target in targets:
                target.actions = [action for action in target.action.split(', ') if action]
            obj.targets = targets

        return obj

    def get_context_data(self, **kwargs):
        compounds = list(Compound.objects.all().order_by('name').values_list('id', flat=True))
        current = compounds.index(int(self.kwargs.get('pk')))

        if current == 0:
            previous_compound = compounds[-1]
        else:
            previous_compound = compounds[current - 1]
        if current == len(compounds)-1:
            next_compound = compounds[0]
        else:
            next_compound = compounds[current + 1]

        context = super(CompoundsDetail, self).get_context_data(**kwargs)

        context.update({'previous': previous_compound, 'next': next_compound})
        return context

CompoundTargetFormset = inlineformset_factory(
    Compound,
    CompoundTarget,
    formset=CompoundTargetInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'name': forms.Textarea(attrs={'size': 25, 'rows': 1}),
        'uniprot_id': forms.TextInput(attrs={'size': 10}),
        'pharmacological_action': forms.TextInput(attrs={'size': 7}),
        'organism': forms.TextInput(attrs={'size': 7}),
        'type': forms.TextInput(attrs={'size': 11}),
    }
)


class CompoundsAdd(SpecificGroupRequiredMixin, CreateView):
    """Add a compound"""
    form_class = CompoundForm
    template_name = 'compounds/compounds_add.html'

    required_group_name = 'Add Compounds Front'

    def get_context_data(self, **kwargs):
        context = super(CompoundsAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = CompoundTargetFormset(self.request.POST)
            else:
                context['formset'] = CompoundTargetFormset()

        return context

    def form_valid(self, form):
        formset = CompoundTargetFormset(self.request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))


class CompoundsUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Update a Compound"""
    model = Compound
    form_class = CompoundForm
    template_name = 'compounds/compounds_add.html'

    required_group_name = 'Change Compounds Front'

    def get_context_data(self, **kwargs):
        context = super(CompoundsUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = CompoundTargetFormset(self.request.POST)
            else:
                context['formset'] = CompoundTargetFormset(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = CompoundTargetFormset(self.request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))


# TODO OLD COMPOUNDS UPDATE
# CompoundSummaryFormset = inlineformset_factory(
#     Compound,
#     CompoundSummary,
#     formset=CompoundSummaryInlineFormset,
#     extra=1,
#     exclude=[],
#     widgets={
#         'summary': forms.Textarea(attrs={'size': 500})
#     }
# )
#
# CompoundPropertyFormset = inlineformset_factory(
#     Compound,
#     CompoundProperty,
#     formset=CompoundPropertyInlineFormset,
#     exclude=[],
#     extra=1
# )
#
#
# class CompoundsUpdate(SpecificGroupRequiredMixin, UpdateView):
#     model = Compound
#     template_name = 'compounds/compounds_update.html'
#
#     required_group_name = 'Change Compounds Front'
#
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         formset_summary = CompoundSummaryFormset(instance=self.object)
#         formset_property = CompoundPropertyFormset(instance=self.object)
#         return self.render_to_response(
#             self.get_context_data(formset_summary=formset_summary,
#                                   formset_property=formset_property))
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#
#         formset_summary = CompoundSummaryFormset(self.request.POST, instance=self.object)
#         formset_property = CompoundPropertyFormset(self.request.POST, instance=self.object)
#
#         if formset_summary.is_valid() and formset_property.is_valid():
#             formset_summary.save()
#             formset_property.save()
#             self.object.modified_by = self.request.user
#             # Save the Compound to keep tracking data
#             self.object.save()
#             return redirect(self.object.get_post_submission_url())
#         else:
#             return self.render_to_response(
#             self.get_context_data(formset_summary=formset_summary,
#                                   formset_property=formset_property))


# Currently, compounds report basically begins as just a compounds list
class CompoundsReport(ListView):
    """Displays page for a Compound Report"""
    model = Compound
    template_name = 'compounds/compounds_report.html'

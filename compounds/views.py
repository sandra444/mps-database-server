from .models import Compound
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from mps.mixins import OneGroupRequiredMixin
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from .forms import *
from django.shortcuts import redirect
from django.forms.models import inlineformset_factory

class CompoundsList(ListView):
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
    model = Compound
    template_name = 'compounds/compounds_detail.html'

    def get_context_data(self, **kwargs):
        compounds = list(Compound.objects.all().order_by('name').values_list('id', flat=True))
        current = compounds.index(int(self.kwargs.get('pk')))

        if current == 0:
            previous = compounds[-1]
        else:
            previous = compounds[current - 1]
        if current == len(compounds)-1:
            next = compounds[0]
        else:
            next = compounds[current + 1]

        context = super(CompoundsDetail, self).get_context_data(**kwargs)

        context.update({'previous':previous, 'next':next})
        return context


class CompoundsAdd(OneGroupRequiredMixin, CreateView):
    form_class = CompoundForm
    template_name = 'compounds/compounds_add.html'

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.object.created_by = self.request.user
            # Save Compound
            self.object.save()
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

CompoundSummaryFormset = inlineformset_factory(
    Compound,
    CompoundSummary,
    formset=CompoundSummaryInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'summary': forms.Textarea(attrs={'size': 500})
    }
)

CompoundPropertyFormset = inlineformset_factory(
    Compound,
    CompoundProperty,
    formset=CompoundPropertyInlineFormset,
    exclude=[],
    extra=1
)


# DON'T BE DECEIVED! THE FRONT-END UPDATE HAS ACCESS ONLY TO THE SUMMARIES AND PROPERTIES
class CompoundsUpdate(OneGroupRequiredMixin, UpdateView):
    model = Compound
    template_name = 'compounds/compounds_update.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset_summary = CompoundSummaryFormset(instance=self.object)
        formset_property = CompoundPropertyFormset(instance=self.object)
        return self.render_to_response(
            self.get_context_data(formset_summary=formset_summary,
                                  formset_property=formset_property))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        formset_summary = CompoundSummaryFormset(self.request.POST, instance=self.object)
        formset_property = CompoundPropertyFormset(self.request.POST, instance=self.object)

        if formset_summary.is_valid() and formset_property.is_valid():
            formset_summary.save()
            formset_property.save()
            self.object.modified_by = self.request.user
            # Save the Compound to keep tracking data
            self.object.save()
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(
            self.get_context_data(formset_summary=formset_summary,
                                  formset_property=formset_property))


# Currently, compounds report basically begins as just a compounds list
class CompoundsReport(ListView):
    model = Compound
    template_name = 'compounds/compounds_report.html'

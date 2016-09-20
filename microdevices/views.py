from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django import forms
from django.forms.models import inlineformset_factory
from .forms import MicrodeviceForm, OrganModelForm, OrganModelProtocolInlineFormset
from .models import Microdevice, OrganModel, ValidatedAssay, OrganModelProtocol
from mps.mixins import SpecificGroupRequiredMixin
from mps.base.models import save_forms_with_tracking


class OrganModelList(ListView):
    """Displays list of Organ Models"""
    template_name = 'microdevices/organmodel_list.html'

    def get_queryset(self):
        return OrganModel.objects.prefetch_related('organ', 'center', 'device').all()


class MicrodeviceList(ListView):
    """Displays list of Microdevices"""
    template_name = 'microdevices/microdevice_list.html'

    def get_queryset(self):
        return Microdevice.objects.prefetch_related('organ', 'center', 'manufacturer').all()


class OrganModelDetail(DetailView):
    """Displays details for an Organ Model"""
    model = OrganModel
    template_name = 'microdevices/organmodel_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrganModelDetail, self).get_context_data(**kwargs)

        assays = ValidatedAssay.objects.filter(organ_model=self.object).prefetch_related('assay', 'assay__assay_type')

        if self.object.center and any(i in self.object.center.groups.all() for i in self.request.user.groups.all()):
            protocols = OrganModelProtocol.objects.filter(
                organ_model=self.object
            ).order_by('-version')
        else:
            protocols = None

        context.update({
            'assays': assays,
            'protocols': protocols,
        })

        return context


class MicrodeviceDetail(DetailView):
    """Displays details for a Device"""
    model = Microdevice
    template_name = 'microdevices/microdevice_detail.html'


class MicrodeviceAdd(SpecificGroupRequiredMixin, CreateView):
    """Allows the addition of Devices"""
    model = Microdevice
    template_name = 'microdevices/microdevice_add.html'
    form_class = MicrodeviceForm

    required_group_name = 'Add Microdevices Front'

    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=False, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class MicrodeviceUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Allows Devices to be updated"""
    model = Microdevice
    template_name = 'microdevices/microdevice_add.html'
    form_class = MicrodeviceForm

    required_group_name = 'Change Microdevices Front'

    def get_context_data(self, **kwargs):
        context = super(MicrodeviceUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    def form_valid(self, form):
        if form.is_valid():
            save_forms_with_tracking(self, form, formset=False, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

OrganModelProtocolFormset = inlineformset_factory(
    OrganModel,
    OrganModelProtocol,
    formset=OrganModelProtocolInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'version': forms.TextInput(attrs={'size': 10})
    }
)


class OrganModelAdd(SpecificGroupRequiredMixin, CreateView):
    """Allows the addition of Organ Models"""
    model = OrganModel
    template_name = 'microdevices/organmodel_add.html'
    form_class = OrganModelForm

    required_group_name = 'Add Microdevices Front'

    def get_context_data(self, **kwargs):
        context = super(OrganModelAdd, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = OrganModelProtocolFormset(self.request.POST, self.request.FILES)
            else:
                context['formset'] = OrganModelProtocolFormset()

        return context

    def form_valid(self, form):
        formset = OrganModelProtocolFormset(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=False)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class OrganModelUpdate(SpecificGroupRequiredMixin, UpdateView):
    """Allows Organ Models to be updated"""
    model = OrganModel
    template_name = 'microdevices/organmodel_add.html'
    form_class = OrganModelForm

    required_group_name = 'Change Microdevices Front'

    def get_context_data(self, **kwargs):
        context = super(OrganModelUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = OrganModelProtocolFormset(
                    self.request.POST,
                    self.request.FILES,
                    instance=self.object
                )
            else:
                context['formset'] = OrganModelProtocolFormset(instance=self.object)

        context['update'] = True

        return context

    def form_valid(self, form):
        formset = OrganModelProtocolFormset(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if form.is_valid() and formset.is_valid():
            save_forms_with_tracking(self, form, formset=formset, update=True)
            return redirect(self.object.get_post_submission_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

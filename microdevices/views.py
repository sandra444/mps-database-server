from microdevices.models import Microdevice, OrganModel, ValidatedAssay, OrganModelProtocol
from django.views.generic import DetailView, CreateView, UpdateView
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from django.forms.models import inlineformset_factory
from .forms import *
from mps.mixins import SpecificGroupRequiredMixin

# class MicrodeviceList(ListView):
#     model = Microdevice
#     template_name = 'microdevices/microdevice_list.html'


# Why is this not class based again?
def microdevice_list(request, *args, **kwargs):
    c = RequestContext(request)

    models = OrganModel.objects.prefetch_related('organ','center','device').all()
    devices = Microdevice.objects.prefetch_related('organ','center','manufacturer').all()

    c.update({
        'models': models,
        'devices': devices,
    })

    return render_to_response('microdevices/microdevice_list.html', c)


# Why is this not class based again?
def organ_model_detail(request, *args, **kwargs):
    c = RequestContext(request)

    model = get_object_or_404(OrganModel, pk=kwargs.get('pk'))
    assays = ValidatedAssay.objects.filter(organ_model=model).prefetch_related('assay','assay__assay_type')
    protocols = OrganModelProtocol.objects.filter(organ_model=model).order_by('-version')

    c.update({
        'model': model,
        'assays': assays,
        'protocols': protocols,
    })

    return render_to_response('microdevices/organ_model_detail.html', c)


class MicrodeviceDetail(DetailView):
    model = Microdevice
    template_name = 'microdevices/microdevice_detail.html'


class MicrodeviceAdd(SpecificGroupRequiredMixin, CreateView):
    model = Microdevice
    template_name = 'microdevices/microdevice_add.html'
    form_class = MicrodeviceForm

    required_group_name = 'Change Microdevices Front'

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            self.object.modified_by = self.request.user
            self.object.save()
            return redirect('/microdevices/')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class MicrodeviceUpdate(SpecificGroupRequiredMixin, UpdateView):
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
            self.object = form.save()
            self.object.modified_by = self.request.user
            self.object.save()
            return redirect('/microdevices/')
        else:
            return self.render_to_response(self.get_context_data(form=form))

OrganModelProtocolFormset = inlineformset_factory(
    OrganModel,
    OrganModelProtocol,
    formset=OrganModelProtocolInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'version': forms.TextInput(attrs={'size': 5})
    }
)


class OrganModelAdd(SpecificGroupRequiredMixin, CreateView):
    model = OrganModel
    template_name = 'microdevices/organ_model_add.html'
    form_class = OrganModelForm

    required_group_name = 'Change Microdevices Front'

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
            self.object = form.save()
            self.object.modified_by = self.request.user
            self.object.save()
            formset.save()
            return redirect('/microdevices/')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class OrganModelUpdate(SpecificGroupRequiredMixin, UpdateView):
    model = OrganModel
    template_name = 'microdevices/organ_model_add.html'
    form_class = OrganModelForm

    required_group_name = 'Change Microdevices Front'

    def get_context_data(self, **kwargs):
        context = super(OrganModelUpdate, self).get_context_data(**kwargs)
        if 'formset' not in context:
            if self.request.POST:
                context['formset'] = OrganModelProtocolFormset(self.request.POST, self.request.FILES, instance=self.object)
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
            self.object = form.save()
            self.object.modified_by = self.request.user
            self.object.save()
            formset.save()
            return redirect('/microdevices/')
        else:
            return self.render_to_response(self.get_context_data(form=form))

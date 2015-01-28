from microdevices.models import Microdevice, OrganModel
from django.views.generic import DetailView
from django.shortcuts import render_to_response
from django.template import RequestContext

# class MicrodeviceList(ListView):
#     model = Microdevice
#     template_name = 'microdevices/microdevice_list.html'

def microdevice_list(request, *args, **kwargs):
    c = RequestContext(request)

    models = OrganModel.objects.prefetch_related('organ','center','device').all()
    devices = Microdevice.objects.prefetch_related('organ','center','manufacturer').all()

    c.update({
        'models': models,
        'devices': devices,
    })

    return render_to_response('microdevices/microdevice_list.html', c)


class MicrodeviceDetail(DetailView):
    model = Microdevice
    template_name = 'microdevices/microdevice_detail.html'

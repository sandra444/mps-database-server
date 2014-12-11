from microdevices.models import Microdevice
from django.views.generic import ListView, DetailView


class MicrodeviceList(ListView):
    model = Microdevice
    template_name = 'microdevices/microdevice_list.html'


class MicrodeviceDetail(DetailView):
    model = Microdevice
    template_name = 'microdevices/microdevice_detail.html'

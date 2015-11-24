from django import forms
from django.forms.models import BaseInlineFormSet
from .models import *

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')


class MicrodeviceForm(forms.ModelForm):

    class Meta(object):
        model = Microdevice
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OrganModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganModelForm, self).__init__(*args, **kwargs)
        self.fields['device'].queryset = Microdevice.objects.filter(device_type='chip')

    class Meta(object):
        model = OrganModel
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OrganModelProtocolInlineFormset(BaseInlineFormSet):

    class Meta(object):
        model = OrganModelProtocol
        exclude = ('',)

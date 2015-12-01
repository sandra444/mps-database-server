from django import forms
from django.forms.models import BaseInlineFormSet
from .models import *
from assays.models import AssayChipSetup

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

    def clean(self):
        forms_data = [f for f in self.forms if f.cleaned_data]

        for form in forms_data:
            data = form.cleaned_data
            protocol_id = data.get('id', '')
            delete_checked = data.get('DELETE', False)

            # Make sure that no protocol in use is checked for deletion
            if protocol_id and delete_checked:
                if AssayChipSetup.objects.filter(organ_model_protocol=protocol_id):
                    raise forms.ValidationError('You cannot remove protocols that are referenced by a chip setup.')

from django import forms
from assays.models import AssayChipReadout

class AssayResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }

class AssayChipReadoutForm(forms.ModelForm):

    class Meta(object):
        model = AssayChipReadout
        exclude = ('created_by','modified_by','signed_off_by','signed_off_date','locked')

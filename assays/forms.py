from django import forms
from assays.models import AssayChipReadout, AssayChipSetup, AssayTestResult, AssayChipCells, AssayResult

class AssayResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        model = AssayTestResult
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }
        exclude = ('assay_device_readout','group',)

class AssayChipReadoutForm(forms.ModelForm):

    another = forms.BooleanField(required=False)

    class Meta(object):
        model = AssayChipReadout
        widgets = {
            'notebook_page': forms.TextInput(attrs={'size': 5}),
        }
        exclude = ('created_by','modified_by','signed_off_by','signed_off_date','locked', 'group')

class AssayChipSetupForm(forms.ModelForm):

    another = forms.BooleanField(required=False)

    class Meta(object):
        model = AssayChipSetup
        widgets = {
            'concentration': forms.TextInput(attrs={'size': 5}),
            'notebook_page': forms.TextInput(attrs={'size': 5}),
        }
        # Assay Run ID is always bound to the parent Study
        exclude = ('assay_run_id','group')

class AssayChipCellsInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayChipCells

class TestResultInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayResult

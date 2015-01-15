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

    def clean(self):
        super(forms.ModelForm, self).clean()
        # Don't need to perform this check if no test type
        if 'chip_test_type' in self.cleaned_data:
            type = self.cleaned_data['chip_test_type']
            compound = self.cleaned_data['compound']
            concentration = self.cleaned_data['concentration']
            unit = self.cleaned_data['unit']
            if type == 'compound' and (not compound or not concentration or not unit):
                raise forms.ValidationError('Please complete all data for compound.')
        return self.cleaned_data

class AssayChipCellsInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayChipCells

    def clean(self):
        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Number of cellsamples
        cellsamples = 0
        for form in forms_data:
            try:
                if form.cleaned_data:
                    cellsamples += 1
            except AttributeError:
                pass
        if cellsamples < 1:
            raise forms.ValidationError('You must have at least one cellsample.')

class TestResultInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayResult

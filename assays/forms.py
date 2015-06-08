from django import forms
from assays.models import *
from compounds.models import Compound

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')
# Excluding restricted is likewise useful
restricted = ('restricted',)
# Group
group = ('group',)

class AssayResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        model = AssayTestResult
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }
        exclude = group + tracking + restricted

    # Set chip setup to unique instead of throwing error in validation
    # def clean(self):
    #     super(forms.ModelForm, self).clean()
    #
    #     if 'chip_setup' in self.cleaned_data and AssayTestResult.objects.filter(chip_setup=self.cleaned_data.get('chip_setup','')):
    #         raise forms.ValidationError('A readout for the given setup already exists!')
    #
    #     return self.cleaned_data

class AssayChipReadoutForm(forms.ModelForm):

    another = forms.BooleanField(required=False)
    headers = forms.CharField(required=True)

    class Meta(object):
        model = AssayChipReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'treatment_time_length': forms.NumberInput(attrs={'style':'width:174px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = group + tracking + restricted


    # def clean(self):
        # Set chip setup to unique instead of throwing error in validation
    #     super(forms.ModelForm, self).clean()
    #
    #     if 'chip_setup' in self.cleaned_data and AssayChipReadout.objects.filter(chip_setup=self.cleaned_data.get('chip_setup','')):
    #         raise forms.ValidationError('A readout for the given setup already exists!')
    #
    #     return self.cleaned_data

class AssayChipSetupForm(forms.ModelForm):

    another = forms.BooleanField(required=False)

    class Meta(object):
        model = AssayChipSetup
        widgets = {
            'concentration': forms.NumberInput(attrs={'style':'width:50px;'}),
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
            'variance': forms.Textarea(attrs={'cols':50, 'rows': 2}),
        }
        # Assay Run ID is always bound to the parent Study
        exclude = ('assay_run_id','group') + tracking + restricted

    def clean(self):
        super(forms.ModelForm, self).clean()

        # Check to see if compound data is complete if: 1.) compound test type 2.) compound is selected (negative control)
        type = self.cleaned_data.get('chip_test_type', '')
        compound = self.cleaned_data.get('compound', '')
        concentration = self.cleaned_data.get('concentration', '')
        unit = self.cleaned_data.get('unit', '')
        if type == 'compound' and not all([compound,concentration,unit]) or (compound and not all([concentration,unit])):
            raise forms.ValidationError('Please complete all data for compound.')
        return self.cleaned_data

class AssayChipCellsInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayChipCells
        exclude = ('',)

    # def clean(self):
    #     forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
    #
    #     #Does not require a minimum number of cellsamples at the moment
    #     Number of cellsamples
    #     cellsamples = 0
    #     for form in forms_data:
    #         try:
    #             if form.cleaned_data:
    #                 cellsamples += 1
    #         except AttributeError:
    #             pass
    #     if cellsamples < 1:
    #         raise forms.ValidationError('You must have at least one cellsample.')

class TestResultInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayResult
        exclude = ('',)

    def clean(self):
        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Number of results
        results = 0
        for form in forms_data:
            try:
                if form.cleaned_data:
                    results += 1
            except AttributeError:
                pass
        if results < 1:
            raise forms.ValidationError('You must have at least one result.')


class StudyConfigurationForm(forms.ModelForm):

    class Meta(object):
        model = StudyConfiguration
        widgets = {
            'media_composition': forms.Textarea(attrs={'cols':50, 'rows': 3}),
            'hardware_description': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = ('',)


# Forms for plates may become more useful later
class AssayLayoutForm(forms.ModelForm):

    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)

    class Meta(object):
        model = AssayLayout
        exclude = tracking + restricted


# Forms for plates may become more useful later
class AssayDeviceSetupForm(forms.ModelForm):

    class Meta(object):
        model = AssayDeviceSetup
        exclude = ('assay_run_id','group') + tracking + restricted


class AssayPlateCellsInlineFormset(forms.models.BaseInlineFormSet):

    class Meta(object):
        model = AssayPlateCells
        exclude = ('',)


class AssayDeviceReadoutForm(forms.ModelForm):

    class Meta(object):
        model = AssayDeviceReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'treatment_time_length': forms.NumberInput(attrs={'style':'width:174px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = group + tracking + restricted

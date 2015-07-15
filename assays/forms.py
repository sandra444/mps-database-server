from django import forms
from django.forms.models import BaseInlineFormSet
from assays.models import *
from compounds.models import Compound

# TODO REFACTOR WHITTLING TO BE HERE IN LIEU OF VIEW
# TODO REFACTOR FK QUERYSETS TO AVOID N+1

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')
# Excluding restricted is likewise useful
restricted = ('restricted',)
# Group
group = ('group',)

# SUBJECT TO CHANGE
class CloneableForm(forms.ModelForm):
    another = forms.BooleanField(required=False, initial=False)
    success = forms.BooleanField(required=False, initial=False)

# SUBJECT TO CHANGE AND REQUIRES TESTING
class CloneableBaseInlineFormSet(BaseInlineFormSet):
    """Overrides create form for the sake of using save_as_new for the purpose of cloning"""
    def _construct_form(self, i, **kwargs):
        form = super(BaseInlineFormSet, self)._construct_form(i, **kwargs)
        # Removed code below
        # if self.save_as_new:
        #     # Remove the primary key from the form's data, we are only
        #     # creating new instances
        #     form.data[form.add_prefix(self._pk_field.name)] = None
        #
        #     # Remove the foreign key from the form's data
        #     form.data[form.add_prefix(self.fk.name)] = None

        # Set the fk value here so that the form can do its validation.
        fk_value = self.instance.pk
        if self.fk.rel.field_name != self.fk.rel.to._meta.pk.name:
            fk_value = getattr(self.instance, self.fk.rel.field_name)
            fk_value = getattr(fk_value, 'pk', fk_value)
        setattr(form.instance, self.fk.get_attname(), fk_value)
        return form

class AssayRunForm(forms.ModelForm):
    def __init__(self,groups,*args,**kwargs):
        super (AssayRunForm,self).__init__(*args,**kwargs)
        self.fields['group'].queryset = groups

    class Meta(object):
        model = AssayRun
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        exclude = tracking

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # clean the form data, before validation
        data = super(AssayRunForm, self).clean()

        if not any([data['toxicity'],data['efficacy'],data['disease'],data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')

        if data['assay_run_id'].startswith('-'):
            raise forms.ValidationError('Error with assay_run_id; please try again')

        return data


class AssayChipResultForm(forms.ModelForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayChipResultForm,self).__init__(*args,**kwargs)
        exclude_list = AssayChipTestResult.objects.filter(chip_readout__isnull=False).values_list('chip_readout', flat=True)
        readouts = AssayChipReadout.objects.filter(chip_setup__assay_run_id=study).exclude(id__in=list(set(exclude_list)))
        if current:
            readouts = readouts | AssayChipReadout.objects.filter(pk=current)
        self.fields['chip_readout'].queryset = readouts

    class Meta(object):
        model = AssayChipTestResult
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }
        exclude = group + tracking + restricted

    # Set chip setup to unique instead of throwing error in validation
    # def clean(self):
    #     super(forms.ModelForm, self).clean()
    #
    #     if 'chip_setup' in self.cleaned_data and AssayChipTestResult.objects.filter(chip_setup=self.cleaned_data.get('chip_setup','')):
    #         raise forms.ValidationError('A readout for the given setup already exists!')
    #
    #     return self.cleaned_data

class AssayChipReadoutForm(CloneableForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayChipReadoutForm,self).__init__(*args,**kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(unit_type='T')
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayChipSetup.objects.filter(pk=current)
        self.fields['chip_setup'].queryset = setups

    headers = forms.CharField(required=True, initial=1)

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

class AssayChipSetupForm(CloneableForm):

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

class AssayChipCellsInlineFormset(CloneableBaseInlineFormSet):

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

class ChipTestResultInlineFormset(BaseInlineFormSet):
    def __init__(self,*args,**kwargs):
        super (ChipTestResultInlineFormset,self).__init__(*args,**kwargs)
        unit_queryset = PhysicalUnits.objects.filter(test_result=True).order_by('unit_type', 'index_order')
        for form in self.forms:
            form.fields['test_unit'].queryset = unit_queryset

    class Meta(object):
        model = AssayChipResult
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

    def __init__(self,groups,*args,**kwargs):
        super (AssayLayoutForm,self).__init__(*args,**kwargs)
        self.fields['group'].queryset = groups
        self.fields['device'].queryset = Microdevice.objects.filter(row_labels__isnull=False, number_of_columns__isnull=False)

    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    concunit = forms.ModelChoiceField(queryset=PhysicalUnits.objects.filter(unit_type='C'), required=False, initial=4)

    class Meta(object):
        model = AssayLayout
        exclude = tracking + restricted


class AssayPlateSetupForm(CloneableForm):

    class Meta(object):
        model = AssayPlateSetup
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = ('assay_run_id','group') + tracking + restricted


class AssayPlateCellsInlineFormset(CloneableBaseInlineFormSet):

    class Meta(object):
        model = AssayPlateCells
        exclude = ('',)


class AssayPlateReadoutForm(CloneableForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayPlateReadoutForm,self).__init__(*args,**kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(unit_type='T')
        exclude_list = AssayPlateReadout.objects.filter(setup__isnull=False).values_list('setup', flat=True)
        setups = AssayPlateSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'assay_layout',
            'created_by').exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayPlateSetup.objects.filter(pk=current)
        self.fields['setup'].queryset = setups

    upload_type = forms.ChoiceField(choices=(('Tabular', 'Tabular'), ('Block', 'Block')))

    class Meta(object):
        model = AssayPlateReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'treatment_time_length': forms.NumberInput(attrs={'style':'width:174px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = group + tracking + restricted


class AssayPlateResultForm(forms.ModelForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayPlateResultForm,self).__init__(*args,**kwargs)
        exclude_list = AssayPlateTestResult.objects.filter(readout__isnull=False).values_list('readout', flat=True)
        readouts = AssayPlateReadout.objects.filter(setup__assay_run_id=study).exclude(id__in=list(set(exclude_list)))
        if current:
            readouts = readouts | AssayPlateReadout.objects.filter(pk=current)
        self.fields['readout'].queryset = readouts

    class Meta(object):
        model = AssayPlateTestResult
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }
        exclude = group + tracking + restricted


class PlateTestResultInlineFormset(BaseInlineFormSet):
    def __init__(self,*args,**kwargs):
        super (PlateTestResultInlineFormset,self).__init__(*args,**kwargs)
        unit_queryset = PhysicalUnits.objects.filter(test_result=True).order_by('unit_type', 'index_order')
        for form in self.forms:
            form.fields['test_unit'].queryset = unit_queryset
        
    class Meta(object):
        model = AssayPlateResult
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

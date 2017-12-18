from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory, BaseModelFormSet, modelformset_factory
from cellsamples.models import Biosensor, CellSample
# STOP USING WILDCARD IMPORTS
from assays.models import *
from compounds.models import Compound, CompoundInstance, CompoundSupplier
from microdevices.models import MicrophysiologyCenter
from mps.forms import SignOffMixin
# Use regular expressions for a string split at one point
import re
import string
import collections
from captcha.fields import CaptchaField
import ujson as json

import datetime
from django.utils import timezone
from django.utils.encoding import force_str

from .utils import (
    validate_file,
    get_chip_details,
    get_plate_details,
    TIME_CONVERSIONS,
    EXCLUDED_DATA_POINT_CODE
)
from django.utils import timezone

from mps.templatetags.custom_filters import is_group_admin, ADMIN_SUFFIX

from mps.templatetags.custom_filters import filter_groups

# TODO REFACTOR WHITTLING TO BE HERE IN LIEU OF VIEW
# TODO REFACTOR FK QUERYSETS TO AVOID N+1

# These are all of the tracking fields
tracking = (
    'created_by',
    'created_on',
    'modified_on',
    'modified_by',
    'signed_off_by',
    'signed_off_date',
    'locked',
    'restricted'
)
# Excluding restricted is likewise useful
restricted = ('restricted',)
# Group
group = ('group',)

# TODO REMOVE RESTRICTED

# Overwrite options
# DEPRECATED
OVERWRITE_OPTIONS_BULK = forms.ChoiceField(
    choices=(
        ('mark_conflicting_data', 'Replace Conflicting Data'),
        # ('mark_all_old_data', 'Replace All Current Study Data'),
        ('keep_conflicting_data', 'Add New Data and Keep Current Data'),
        # ('delete_conflicting_data', 'Delete Conflicting Data'),
        # ('delete_all_old_data', 'Delete All Old Data')
    ),
    initial='mark_conflicting_data'
)

OVERWRITE_OPTIONS_INDIVIDUAL = forms.ChoiceField(
    choices=(
        ('mark_conflicting_data', 'Replace Conflicting Data'),
        ('mark_all_old_data', 'Replace All Current Readout Data'),
        ('keep_conflicting_data', 'Add New Data and Keep Current Data'),
        # ('delete_conflicting_data', 'Delete Conflicting Data'),
        # ('delete_all_old_data', 'Delete All Old Data')
    ),
    initial='mark_conflicting_data'
)


# SUBJECT TO CHANGE
class CloneableForm(forms.ModelForm):
    """Convenience class for adding clone fields"""
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


# NOTE: No longer allows sign offs through this form
class AssayRunForm(forms.ModelForm):
    """Frontend Form for Studies"""
    def __init__(self, groups, *args, **kwargs):
        """Init the Study Form

        Parameters:
        groups -- a queryset of groups (allows us to avoid N+1 problem)
        """
        super(AssayRunForm, self).__init__(*args, **kwargs)

        self.fields['group'].queryset = groups

    class Meta(object):
        model = AssayRun
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 100}),
        }
        exclude = tracking + restricted + ('access_groups', 'signed_off_notes')

    def clean(self):
        """Checks for at least one study type and deformed assay_run_ids"""

        # clean the form data, before validation
        data = super(AssayRunForm, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')

        if data['assay_run_id'].startswith('-'):
            raise forms.ValidationError('Error with assay_run_id; please try again')



class StudySupportingDataInlineFormSet(BaseInlineFormSet):
    """Form for Study Supporting Data (as part of an inline)"""
    class Meta(object):
        model = StudySupportingData
        exclude = ('',)



# DEPRECATED
class AssayRunAccessForm(forms.ModelForm):
    """Form for changing access to studies"""
    def __init__(self, *args, **kwargs):
        super(AssayRunAccessForm, self).__init__(*args, **kwargs)
        groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
        groups_with_center_full = Group.objects.filter(
            id__in=groups_with_center
        ).exclude(
            id=self.instance.group.id
        ).order_by(
            'name'
        )
        self.fields['access_groups'].queryset = groups_with_center_full

    class Meta(object):
        model = AssayRun
        fields = ['access_groups']


class AssayChipResultForm(SignOffMixin, forms.ModelForm):
    """Frontend form for Chip Test Results"""
    def __init__(self, study, current, *args, **kwargs):
        """Init the Chip Test Results Form

        Parameters:
        study -- the study the result is from (to filter Readout dropdown)
        current -- the currently selected readout (if the Test Result is being updated)
        """
        super(AssayChipResultForm, self).__init__(*args, **kwargs)
        exclude_list = AssayChipTestResult.objects.filter(
            chip_readout__isnull=False
        ).values_list(
            'chip_readout',
            flat=True
        )
        readouts = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id=study
        ).exclude(
            id__in=list(set(exclude_list))
        )
        if current:
            readouts = readouts | AssayChipReadout.objects.filter(pk=current)
        readouts = readouts.prefetch_related('chip_setup', 'chip_setup__unit', 'chip_setup__compound')
        self.fields['chip_readout'].queryset = readouts

    class Meta(object):
        model = AssayChipTestResult
        widgets = {
            'summary': forms.Textarea(attrs={'cols': 75, 'rows': 3}),
        }
        exclude = group + tracking + restricted


class AssayChipReadoutForm(SignOffMixin, CloneableForm):
    """Frontend form for Chip Readouts"""
    overwrite_option = OVERWRITE_OPTIONS_INDIVIDUAL

    # EVIL WAY TO GET PREVIEW DATA
    preview_data = forms.BooleanField(initial=False, required=False)

    def __init__(self, study, current, *args, **kwargs):
        """Init the Chip Readout Form

        Parameters:
        study -- the study the readout is from (to filter setup dropdown)
        current -- the currently selected setup (if the Readout is being updated)

        Additional fields (not part of model):
        headers -- specifies the number of header lines in the uploaded csv

        kwargs:
        request -- the current request
        """
        self.request = kwargs.pop('request', None)

        super(AssayChipReadoutForm, self).__init__(*args, **kwargs)

        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(
            unit_type__unit_type='Time'
        ).order_by('scale_factor')
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by'
        ).exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayChipSetup.objects.filter(pk=current)
        self.fields['chip_setup'].queryset = setups

    # Specifies the number of headers in the uploaded csv
    # headers = forms.CharField(required=True, initial=1)

    class Meta(object):
        model = AssayChipReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'treatment_time_length': forms.NumberInput(attrs={'style': 'width:174px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = group + tracking + restricted

    # Set chip setup to unique instead of throwing error in validation
    def clean(self):
        super(AssayChipReadoutForm, self).clean()

        setup = self.cleaned_data.get('chip_setup')
        if setup:
            self.instance.chip_setup = setup

        if setup and self.request and self.request.FILES:
            test_file = self.cleaned_data.get('file')
            file_data = validate_file(
                self,
                test_file,
                'Chip',
                # headers=headers,
                # chip_details=chip_details,
                readout=self.instance,
                study=setup.assay_run_id
            )
            # Evil attempt to acquire preview data
            self.cleaned_data['preview_data'] = file_data


class AssayChipSetupForm(SignOffMixin, CloneableForm):
    """Frontend form for Chip Setups"""
    def __init__(self, *args, **kwargs):
        """Init Chip Setup Form

        Filters physical units to include only concentrations and %
        Filters devices to only include devices labelled as "chips"
        """
        super(AssayChipSetupForm, self).__init__(*args, **kwargs)
        # Filter on concentration but make a special exception for percent (%)
        self.fields['unit'].queryset = PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')
        # Filter devices to be only microchips (or "chips" like the venous system)
        # self.fields['device'].queryset = Microdevice.objects.filter(device_type='chip')

    class Meta(object):
        model = AssayChipSetup
        widgets = {
            'concentration': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'variance': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }
        # Assay Run ID is always bound to the parent Study
        exclude = ('assay_run_id', 'group') + tracking + restricted

    def clean(self):
        """Cleans the Chip Setup Form

        Ensures the the name is unique in the current study
        Ensures that the data for a compound is complete
        Prevents changes to the chip if data has been uploaded (avoiding conflicts between data and entries)
        """
        super(AssayChipSetupForm, self).clean()

        # Make sure the barcode/ID is unique in the study
        if AssayChipSetup.objects.filter(
                assay_run_id=self.instance.assay_run_id,
                assay_chip_id=self.cleaned_data.get('assay_chip_id')
        ).exclude(id=self.instance.id):
            raise forms.ValidationError({'assay_chip_id': ['ID/Barcode must be unique within study.']})

        # THIS CHECK IS NO LONGER PERFORMED
        # Check to see if compound data is complete if: 1.) compound test type 2.) compound is selected
        # current_type = self.cleaned_data.get('chip_test_type', '')
        # compound = self.cleaned_data.get('compound', '')
        # concentration = self.cleaned_data.get('concentration', '')
        # unit = self.cleaned_data.get('unit', '')
        # if current_type == 'compound' and not all([compound, concentration, unit]) \
        #         or (compound and not all([concentration, unit])):
        #     raise forms.ValidationError('Please complete all data for compound.')

        # RENAMING CHIPS WITH DATA IS NOW ALLOWED
        # Check to see if data has been uploaded for this setup
        # Prevent changing chip id if this is the case
        # Get readouts
        # readout = AssayChipReadout.objects.filter(chip_setup=self.instance)
        # if readout:
        #     if AssayChipRawData.objects.filter(assay_chip_id=readout) \
        #             and self.cleaned_data.get('assay_chip_id') != self.instance.assay_chip_id:
        #         raise forms.ValidationError(
        #             {'assay_chip_id': ['Chip ID/Barcode cannot be changed after data has been uploaded.']}
        #         )


def update_compound_instance_and_supplier():
    """This function is intended to unify the processes involved in updating instances and suppliers"""
    pass

# Converts: days -> minutes, hours -> minutes, minutes->minutes
# TIME_CONVERSIONS = [
#     ('day', 1440),
#     ('hour', 60),
#     ('minute', 1)
# ]
#
# TIME_CONVERSIONS = collections.OrderedDict(TIME_CONVERSIONS)


class AssayCompoundInstanceInlineFormSet(CloneableBaseInlineFormSet):
    """Frontend Inline FormSet for Compound Instances"""
    class Meta(object):
        model = AssayCompoundInstance
        exclude = ('',)

    def __init__(self, *args, **kwargs):
        """Init Chip Setup Form

        Filters physical units to include only Concentration
        """
        super(AssayCompoundInstanceInlineFormSet, self).__init__(*args, **kwargs)
        # Filter on Time
        # time_unit_queryset = PhysicalUnits.objects.filter(
        #     unit_type__unit_type='Time'
        # ).order_by(
        #     'base_unit',
        #     'scale_factor'
        # )

        # Filter compound instances
        compound_instances = CompoundInstance.objects.all().prefetch_related(
            'compound',
            'supplier'
        )
        compound_instances_dic = {
            instance.id: instance for instance in compound_instances
        }

        # Filter on concentration but make a special exception for percent (%)
        concentration_unit_queryset = PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')

        for form in self.forms:
            # form.fields['start_time_unit'].queryset = time_unit_queryset
            # form.fields['duration_unit'].queryset = time_unit_queryset
            form.fields['concentration_unit'].queryset = concentration_unit_queryset
            form.fields['compound_instance'].queryset = compound_instances

            # All available compounds
            form.fields['compound'] = forms.ModelChoiceField(queryset=Compound.objects.all())
            # Text field (un-saved) for supplier
            form.fields['supplier_text'] = forms.CharField()
            # Text field (un-saved) for lot
            form.fields['lot_text'] = forms.CharField()
            # Receipt date
            form.fields['receipt_date'] = forms.DateField(required=False)

            # Add fields for splitting time into days, hours, and minutes
            # Times are trickier to fill in, uses formula that prioritizes larger denominations
            for time_unit in TIME_CONVERSIONS.keys():
                # Create fields for Days, Hours, Minutes
                form.fields['addition_time_' + time_unit] = forms.FloatField(initial=0)
                form.fields['duration_' + time_unit] = forms.FloatField(initial=0)
                # Change style
                form.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
                form.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'

            # If instance, apply initial values
            if form.instance.compound_instance_id:
                current_compound_instance = compound_instances_dic.get(form.instance.compound_instance_id)

                form.fields['compound'].initial = current_compound_instance.compound
                form.fields['supplier_text'].initial = current_compound_instance.supplier.name
                form.fields['lot_text'].initial = current_compound_instance.lot
                form.fields['receipt_date'].initial = current_compound_instance.receipt_date

                # Fill additional time
                addition_time_in_minutes_remaining = form.instance.addition_time
                for time_unit, conversion in TIME_CONVERSIONS.items():
                    initial_time_for_current_field = int(addition_time_in_minutes_remaining / conversion)
                    if initial_time_for_current_field:
                        form.fields['addition_time_' + time_unit].initial = initial_time_for_current_field
                        addition_time_in_minutes_remaining -= initial_time_for_current_field * conversion
                # Add fractions of minutes if necessary
                if addition_time_in_minutes_remaining:
                    form.fields['addition_time_minute'].initial += addition_time_in_minutes_remaining

                # Fill duration
                duration_in_minutes_remaining = form.instance.duration
                for time_unit, conversion in TIME_CONVERSIONS.items():
                    initial_time_for_current_field = int(duration_in_minutes_remaining / conversion)
                    if initial_time_for_current_field:
                        form.fields['duration_' + time_unit].initial = initial_time_for_current_field
                        duration_in_minutes_remaining -= initial_time_for_current_field * conversion
                # Add fractions of minutes if necessary
                if duration_in_minutes_remaining:
                    form.fields['duration_minute'].initial += duration_in_minutes_remaining

            # Set CSS class to receipt date to use date picker
            form.fields['receipt_date'].widget.attrs['class'] = 'datepicker-input'

    def clean(self):
        """Checks to make sure duration is valid"""
        for index, form in enumerate(self.forms):
            current_data = form.cleaned_data

            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                addition_time = 0
                duration = 0
                for time_unit, conversion in TIME_CONVERSIONS.items():
                    addition_time += current_data.get('addition_time_' + time_unit, 0) * conversion
                    duration += current_data.get('duration_' + time_unit, 0) * conversion

                if duration <= 0:
                    form.add_error('duration', 'Duration cannot be zero or negative.')

    # TODO THIS IS NOT DRY
    def save(self, commit=True):
        # Get forms_data (excluding those with delete or no data)
        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        forms_to_delete = [f for f in self.forms if f.cleaned_data and f.cleaned_data.get('DELETE', False)]

        # Forms to be deleted
        for form in forms_to_delete:
            instance = super(forms.ModelForm, form).save(commit=False)

            if instance and instance.id and commit:
                instance.delete()

        chip_setup = self.instance

        # Get all chip setup assay compound instances
        assay_compound_instances = {
            (
                instance.compound_instance.id,
                instance.concentration,
                instance.concentration_unit.id,
                instance.addition_time,
                instance.duration
            ): True for instance in AssayCompoundInstance.objects.filter(
                chip_setup=chip_setup
            ).prefetch_related(
                'compound_instance__compound',
                'concentration_unit'
            )
        }

        # Get all Compound Instances
        compound_instances = {
            (
                instance.compound.id,
                instance.supplier.id,
                instance.lot,
                instance.receipt_date
            ): instance for instance in CompoundInstance.objects.all().prefetch_related(
                'compound',
                'supplier'
            )
        }

        # Get all suppliers
        suppliers = {
            supplier.name: supplier for supplier in CompoundSupplier.objects.all()
        }

        # Forms to save
        for form in forms_data:
            instance = super(forms.ModelForm, form).save(commit=False)

            current_data = form.cleaned_data

            compound = current_data.get('compound')
            supplier_text = current_data.get('supplier_text').strip()
            lot_text = current_data.get('lot_text').strip()
            receipt_date = current_data.get('receipt_date')

            # Should be acquired straight from form
            # concentration = current_data.get('concentration')
            # concentration_unit = current_data.get('concentration_unit')

            addition_time = 0
            duration = 0
            for time_unit, conversion in TIME_CONVERSIONS.items():
                addition_time += current_data.get('addition_time_' + time_unit, 0) * conversion
                duration += current_data.get('duration_' + time_unit, 0) * conversion

            # Check if the supplier already exists
            supplier = suppliers.get(supplier_text, '')
            # Otherwise create the supplier
            if not supplier:
                supplier = CompoundSupplier(
                    name=supplier_text,
                    created_by=chip_setup.created_by,
                    created_on=chip_setup.created_on,
                    modified_by=chip_setup.modified_by,
                    modified_on=chip_setup.modified_on
                )
                if commit:
                    supplier.save()
                suppliers.update({
                    supplier_text: supplier
                })

            # Check if compound instance exists
            compound_instance = compound_instances.get((compound.id, supplier.id, lot_text, receipt_date), '')
            if not compound_instance:
                compound_instance = CompoundInstance(
                    compound=compound,
                    supplier=supplier,
                    lot=lot_text,
                    receipt_date=receipt_date,
                    created_by=chip_setup.created_by,
                    created_on=chip_setup.created_on,
                    modified_by=chip_setup.modified_by,
                    modified_on=chip_setup.modified_on
                )
                if commit:
                    compound_instance.save()
                compound_instances.update({
                    (compound.id, supplier.id, lot_text, receipt_date): compound_instance
                })

            # Update the instance with new data
            instance.chip_setup = chip_setup
            instance.compound_instance = compound_instance

            instance.addition_time = addition_time
            instance.duration = duration

            # Save the AssayCompoundInstance
            if commit:
                conflicting_assay_compound_instance = assay_compound_instances.get(
                    (
                        instance.compound_instance.id,
                        instance.concentration,
                        instance.concentration_unit.id,
                        instance.addition_time,
                        instance.duration
                    ), None
                )
                if not conflicting_assay_compound_instance:
                    instance.save()

            assay_compound_instances.update({
                (
                    instance.compound_instance.id,
                    instance.concentration,
                    instance.concentration_unit.id,
                    instance.addition_time,
                    instance.duration
                ): True
            })
            # AssayCompoundInstance(
            #     chip_setup=chip_setup,
            #     compound_instance=compound_instance,
            #     addition_time=addition_time,
            #     # start_time_unit=start_time_unit,
            #     duration=duration,
            #     # duration_unit=duration_unit,
            #     concentration=concentration,
            #     concentration_unit=concentration_unit
            # ).save()


class AssayChipCellsInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline Formset for Chip Cells"""

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
    """Frontend inline formset for Individual Chip Results"""
    def __init__(self, *args, **kwargs):
        """Init the Chip Result Inline

        Filters units so that only those marked 'test' appear in the dropdown
        """
        self.study = kwargs.pop('study', None)
        super(ChipTestResultInlineFormset, self).__init__(*args, **kwargs)
        assay_queryset = AssayInstance.objects.filter(
            study=self.study
        )
        unit_queryset = PhysicalUnits.objects.filter(
            availability__icontains='test'
        ).order_by('unit_type', 'base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['assay_name'].queryset = assay_queryset
            form.fields['test_unit'].queryset = unit_queryset

    class Meta(object):
        model = AssayChipResult
        exclude = ('',)

    def clean(self):
        """Clean Result Inline

        Prevents submission with no results
        """
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


class StudyConfigurationForm(SignOffMixin, forms.ModelForm):
    """Frontend Form for Study Configurations"""
    class Meta(object):
        model = StudyConfiguration
        widgets = {
            'name': forms.Textarea(attrs={'cols': 50, 'rows': 1}),
            'media_composition': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'hardware_description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = ('',)


# Forms for plates may become more useful later
class AssayLayoutForm(SignOffMixin, forms.ModelForm):
    """Frontend Form for Assay Layouts

    Additional fields (not part of model):
    compound -- dropdown for selecting compounds to add to the Layout map
    concentration_unit -- dropdown for selecting a concentration unit for the Layout map
    """
    def __init__(self, groups, *args, **kwargs):
        super(AssayLayoutForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = groups
        self.fields['device'].queryset = Microdevice.objects.filter(
            device_type='plate'
        )

        for time_unit in TIME_CONVERSIONS.keys():
            # Create fields for Days, Hours, Minutes
            self.fields['addition_time_' + time_unit] = forms.FloatField(initial=0, required=False)
            self.fields['duration_' + time_unit] = forms.FloatField(initial=0, required=False)
            # Change style
            self.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
            self.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'

        # Set CSS class to receipt date to use date picker
        # Set CSS class to receipt date to use date picker
        self.fields['receipt_date'].widget.attrs['class'] = 'datepicker-input'

    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    concentration_unit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )
    concentration = forms.FloatField(required=False)

    # Text field (un-saved) for supplier
    supplier_text = forms.CharField(required=False)
    # Text field (un-saved) for lot
    lot_text = forms.CharField(required=False)
    # Receipt date
    receipt_date = forms.DateField(required=False)

    class Meta(object):
        model = AssayLayout
        widgets = {
            'layout_name': forms.TextInput(attrs={'size': 35}),
        }
        exclude = tracking + restricted


class AssayPlateSetupForm(SignOffMixin, CloneableForm):
    """Frontend Form for Plate Setups"""
    def __init__(self, *args, **kwargs):
        """Init Plate Setup Form

        Orders AssayLayouts such that standard layouts appear first (does not currently filter)
        """
        super(AssayPlateSetupForm, self).__init__(*args, **kwargs)
        # Should the queryset be restricted by group?
        self.fields['assay_layout'].queryset = AssayLayout.objects.all().order_by('-standard', 'layout_name')

    class Meta(object):
        model = AssayPlateSetup
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = ('assay_run_id', 'group') + tracking + restricted

    def clean(self):
        """Clean Plate Setup Form

        Ensures that the given ID is unique for the current study
        Prevents changes to the setup if there is data uploaded
        """

        super(forms.ModelForm, self).clean()

        # Make sure the barcode/id is unique in the study
        if AssayPlateSetup.objects.filter(
                assay_run_id=self.instance.assay_run_id,
                assay_plate_id=self.cleaned_data.get('assay_plate_id')
        ).exclude(id=self.instance.id):
            raise forms.ValidationError({'assay_plate_id': ['ID/Barcode must be unique within study.']})

        # Check to see if data has been uploaded for this setup
        # Prevent changing the assay layout if this is the case
        # Prevent changing plate id if this is the case
        # Get readouts
        readout = AssayPlateReadout.objects.filter(setup=self.instance)
        if readout:
            if AssayReadout.objects.filter(
                    assay_device_readout=readout
            ) and self.cleaned_data.get('assay_layout') != self.instance.assay_layout:
                raise forms.ValidationError(
                    {'assay_layout': ['Assay layout cannot be changed after data has been uploaded.']}
                )
            # RENAMING PLATES WITH DATA IS NOW ALLOWED
            # if AssayReadout.objects.filter(
            #         assay_device_readout=readout
            # ) and self.cleaned_data.get('assay_plate_id') != self.instance.assay_plate_id:
            #     raise forms.ValidationError(
            #         {'assay_plate_id': ['Plate ID/Barcode cannot be changed after data has been uploaded.']}
            #     )


class AssayPlateCellsInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline Formset for Plate Cells"""
    class Meta(object):
        model = AssayPlateCells
        exclude = ('',)


class AssayPlateReadoutForm(SignOffMixin, CloneableForm):
    """Frontend Form for Assay Plate Readouts"""
    def __init__(self, study, current, *args, **kwargs):
        """Init Assay Plate Readout Form

        Parameters:
        study -- the current study (for filtering Setups)
        current -- the current setup (if the Readout is being updated)

        Additional fields (not part of model):
        upload_type -- specifies whether the upload is in tabular or block format

        Filters units to be only time units
        Filters Setups to exclude Setups used by other Readouts
        """
        super(AssayPlateReadoutForm, self).__init__(*args, **kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(
            unit_type__unit_type='Time'
        ).order_by('scale_factor')
        exclude_list = AssayPlateReadout.objects.filter(setup__isnull=False).values_list('setup', flat=True)
        setups = AssayPlateSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'assay_layout',
            'created_by').exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayPlateSetup.objects.filter(pk=current)
        self.fields['setup'].queryset = setups

    # upload_type = forms.ChoiceField(choices=(('Block', 'Block'), ('Tabular', 'Tabular')))

    overwrite_option = OVERWRITE_OPTIONS_INDIVIDUAL

    class Meta(object):
        model = AssayPlateReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'treatment_time_length': forms.NumberInput(attrs={'style': 'width:174px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = group + tracking + restricted


class AssayPlateResultForm(SignOffMixin, forms.ModelForm):
    """Frontend Form for Plate Test Results"""
    def __init__(self, study, current, *args, **kwargs):
        """Init Plate Test Results Form

        Parameters:
        study -- the current study (for filtering Readouts)
        current -- the current Results (if the Results are being updated)

        Filters Readouts to exclude Readouts being used by other Test Results
        """
        super(AssayPlateResultForm, self).__init__(*args, **kwargs)
        exclude_list = AssayPlateTestResult.objects.filter(readout__isnull=False).values_list('readout', flat=True)
        readouts = AssayPlateReadout.objects.filter(setup__assay_run_id=study).exclude(id__in=list(set(exclude_list)))
        if current:
            readouts = readouts | AssayPlateReadout.objects.filter(pk=current)
        readouts = readouts.prefetch_related('setup')
        self.fields['readout'].queryset = readouts

    class Meta(object):
        model = AssayPlateTestResult
        widgets = {
            'summary': forms.Textarea(attrs={'cols': 75, 'rows': 3}),
        }
        exclude = group + tracking + restricted


class PlateTestResultInlineFormset(BaseInlineFormSet):
    """Frontend inline for Individual Plate Results"""
    def __init__(self, *args, **kwargs):
        """Init Plate Result Inline

        Filters units such that only 'test' units appear
        """
        super(PlateTestResultInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__icontains='test'
        ).order_by('unit_type', 'base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['test_unit'].queryset = unit_queryset

    class Meta(object):
        model = AssayPlateResult
        exclude = ('',)

    def clean(self):
        """Clean Plate Results Inline

        Prevents submission with no Results
        """
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


def label_to_number(label):
    """Returns a numeric index from an alphabetical index"""
    num = 0
    for char in label:
        if char in string.ascii_letters:
            num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num


def process_readout_value(value):
    """Returns processed readout value and whether or not to mark it invalid"""

    # Try to parse as a float
    try:
        value = float(value)
        return {'value': value, 'quality': u''}

    except ValueError:
        # If not a float, take slice of all but first character and try again
        sliced_value = value[1:]

        try:
            sliced_value = float(sliced_value)
            return {'value': sliced_value, 'quality': EXCLUDED_DATA_POINT_CODE}

        except ValueError:
            return None


def get_row_and_column(well_id, offset):
    """Takes a well ID in the form A1 and returns a row and column index as a tuple

    Params:
    well_id - the well ID as a string
    offset - offset to resulting row and column indexes (to start at zero, for instance)
    """
    # Split the well into alphabetical and numeric
    row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well_id)

    # PLEASE NOTE THAT THE VALUES ARE OFFSET BY ONE (to begin with 0)
    # Convert row_label to a number
    row_label = label_to_number(row_label) - offset
    # Convert column label to an integer
    column_label = int(column_label) - offset

    # Note that the parentheses are not redundant, this is a tuple
    return (row_label, column_label)


class AssayPlateReadoutInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline for Assay Plate Readout Assays (APRA)"""

    # EVIL WAY TO GET PREVIEW DATA
    preview_data = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        """Init APRA inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayPlateReadoutInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__icontains='readout'
        ).order_by('unit_type', 'base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['readout_unit'].queryset = unit_queryset

    def clean(self):
        """Clean APRA Inline

        Validate unique, existing PLATE READOUTS
        """
        if self.data.get('setup', ''):
            setup_pk = int(self.data.get('setup'))
        else:
            raise forms.ValidationError('Please choose a plate setup.')
        setup = AssayPlateSetup.objects.get(pk=setup_pk)
        setup_id = setup.assay_plate_id

        # TODO REVIEW
        # Get upload type
        # upload_type = self.data.get('upload_type')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        plate_details = get_plate_details(self=self)

        assays = plate_details.get(setup_id, {}).get('assays', {})
        features = plate_details.get(setup_id, {}).get('features', {})
        assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

        # If there is already a file in the database and it is not being replaced or cleared
        # (check for clear is implicit)
        if self.instance.file and not forms_data[0].files:
            saved_data = AssayReadout.objects.filter(assay_device_readout=self.instance).prefetch_related('assay')

            for raw in saved_data:
                assay = raw.assay.assay_id.assay_name.upper()
                value_unit = raw.assay.readout_unit.unit
                feature = raw.assay.feature

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "{}" because it is in your uploaded data.'.format(assay))
                # Raise error if feature does not correspond?
                elif feature not in features:
                    raise forms.ValidationError(
                        'You can not remove the feature "{}" because it is in your uploaded data.'.format(feature))
                elif (assay, feature) not in assay_feature_to_unit:
                    raise forms.ValidationError(
                        'You can not change the assay-feature pair "{0}-{1}" '
                        'because it is in your uploaded data'.format(assay, feature)
                    )
                # Raise error if value_unit not equal to one listed in APRA
                # Note use of features to unit (unlike chips)
                if value_unit != assay_feature_to_unit.get((assay, feature), ''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"'
                        % (value_unit, assay_feature_to_unit.get((assay, feature), ''))
                    )

        # TODO what shall a uniqueness check look like?
        # If there is a new file
        if forms_data[0].files:
            test_file = forms_data[0].files.get('file', '')
            file_data = validate_file(
                self,
                test_file,
                'Plate',
                plate_details=plate_details,
                # upload_type=upload_type,
                study=setup.assay_run_id,
            )
            # Evil attempt to acquire preview data
            self.forms[0].cleaned_data['preview_data'] = file_data

        return self.forms


# DEPRECATED
class AssayChipReadoutInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline for Chip Readout Assays (ACRA)"""

    # EVIL WAY TO GET PREVIEW DATA
    preview_data = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        """Init ACRA Inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayChipReadoutInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__icontains='readout'
        ).order_by('unit_type', 'base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['readout_unit'].queryset = unit_queryset

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""
        if self.data.get('chip_setup', ''):
            setup_pk = int(self.data.get('chip_setup'))
        else:
            raise forms.ValidationError('Please choose a chip setup.')
        setup = AssayChipSetup.objects.get(pk=setup_pk)
        # setup_id = setup.assay_chip_id

        # # Throw error if headers is not valid
        # try:
        #     headers = int(self.data.get('headers', '')) if self.data.get('headers', '') else 0
        # except:
        #     raise forms.ValidationError('Please make number of headers a valid number.')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # chip_details = get_chip_details(self=self)
        #
        # assays = chip_details.get(setup_id, {}).get('assays', {})

        # If there is already a file in the database and it is not being replaced or cleared
        #  (check for clear is implicit)
        # if self.instance.file and not forms_data[0].files:
        #     new_time_unit = self.instance.timeunit
        #     old_time_unit = AssayChipReadout.objects.get(id=self.instance.id).timeunit
        #
        #     # Fail if time unit does not match
        #     if new_time_unit != old_time_unit:
        #         raise forms.ValidationError(
        #             'The time unit "%s" does not correspond with the selected readout time unit of "%s"'
        #             % (new_time_unit, old_time_unit))
        #
        #     saved_data = AssayChipRawData.objects.filter(assay_chip_id=self.instance).prefetch_related(
        #         'assay_id__assay_id'
        #     )
        #
        #     for raw in saved_data:
        #         assay = raw.assay_id.assay_id.assay_name.upper()
        #         value_unit = raw.assay_id.readout_unit.unit
        #
        #         # Raise error when an assay does not exist
        #         if assay not in assays:
        #             raise forms.ValidationError(
        #                 'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
        #         # Raise error if value_unit not equal to one listed in ACRA
        #         elif value_unit not in assays.get(assay, ''):
        #             raise forms.ValidationError(
        #                 'The current value unit "%s" does not correspond with the readout units "%s"'
        #                 % (value_unit, assays.get(assay, ''))
        #             )

        # If there is a new file
        if forms_data and forms_data[0].files:
            test_file = forms_data[0].files.get('file', '')
            file_data = validate_file(
                self,
                test_file,
                'Chip',
                # headers=headers,
                # chip_details=chip_details,
                plate_details=None,
                study=setup.assay_run_id,
            )
            # Evil attempt to acquire preview data
            self.forms[0].cleaned_data['preview_data'] = file_data

        return self.forms


# Now uses unicode instead of string
def stringify_excel_value(value):
    """Given an excel value, return a unicode cast of it

    This also converts floats to integers when possible
    """
    # If the value is just a string literal, return it
    if type(value) == str or type(value) == unicode:
        return unicode(value)
    else:
        try:
            # If the value can be an integer, make it into one
            if int(value) == float(value):
                return unicode(int(value))
            else:
                return unicode(float(value))
        except:
            return unicode(value)


# SPAGHETTI CODE FIND A BETTER PLACE TO PUT THIS?
def valid_chip_row(row):
    """Confirm that a row is valid"""
    return row and all(row[:5] + [row[6]])


def get_bulk_datalist(sheet):
    """Get a list of lists where each list is a row and each entry is a value"""
    # Get datalist
    datalist = []

    # Include the first row (the header)
    for row_index in range(sheet.nrows):
        datalist.append([stringify_excel_value(value) for value in sheet.row_values(row_index)])

    return datalist


class ReadoutBulkUploadForm(forms.ModelForm):
    """Form for Bulk Uploads"""
    # Now in Study (AssayRun) to make saving easier
    # bulk_file = forms.FileField()

    overwrite_option = OVERWRITE_OPTIONS_BULK

    # EVIL WAY TO GET PREVIEW DATA
    preview_data = forms.BooleanField(initial=False, required=False)

    class Meta(object):
        model = AssayRun
        fields = ('bulk_file',)

    def __init__(self, *args, **kwargs):
        """Init the Bulk Form

        kwargs:
        request -- the current request
        """
        self.request = kwargs.pop('request', None)

        super(ReadoutBulkUploadForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(ReadoutBulkUploadForm, self).clean()

        # Get the study in question
        study = self.instance

        # test_file = None

        if self.request and self.request.FILES:
            test_file = data.get('bulk_file', '')

            file_data = validate_file(
                self,
                test_file,
                'Bulk',
                # headers=headers,
                study=study
            )

            # Evil attempt to acquire preview data
            self.cleaned_data['preview_data'] = file_data

        # Removed, someone might want to use this interface to remove data
        # if not test_file:
        #     raise forms.ValidationError('No file was supplied.')

        return self.cleaned_data


class AssayInstanceInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        """Init APRA inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayInstanceInlineFormSet, self).__init__(*args, **kwargs)

        target_queryset = AssayTarget.objects.all().order_by('name')

        method_queryset = AssayMethod.objects.all().order_by('name')

        unit_queryset = PhysicalUnits.objects.filter(
            availability__icontains='readout'
        ).order_by('unit_type', 'base_unit', 'scale_factor')

        for form in self.forms:
            form.fields['target'].queryset = target_queryset
            form.fields['method'].queryset = method_queryset
            form.fields['unit'].queryset = unit_queryset


class ReadyForSignOffForm(forms.Form):
    captcha = CaptchaField()
    message = forms.TextInput()


# TODO PLEASE REVIEW
class AssayStudyForm(SignOffMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """Init the Study Form

        Kwargs:
        groups -- a queryset of groups (allows us to avoid N+1 problem)
        """
        self.groups = kwargs.pop('groups', None)
        super(AssayStudyForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = self.groups

    class Meta(object):
        model = AssayStudy
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        exclude = tracking


StudySupportingDataFormSet = inlineformset_factory(
    AssayStudy,
    AssayStudySupportingData,
    formset=StudySupportingDataInlineFormSet,
    extra=1,
    exclude=[],
    widgets={
        'description': forms.Textarea(attrs={'rows': 3}),
    }
)

AssayInstanceFormSet = inlineformset_factory(
    AssayStudy,
    AssayInstance,
    formset=AssayInstanceInlineFormSet,
    extra=1,
    exclude=[]
)


class AssayMatrixFormOLD(SignOffMixin, forms.ModelForm):
    class Meta(object):
        model = AssayMatrix
        exclude = ('study',) + tracking
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'variance_from_organ_model_protocol': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayMatrixFormOLD, self).__init__(*args, **kwargs)

        if self.study:
            self.instance.study = self.study

        for time_unit in TIME_CONVERSIONS.keys():
            # Create fields for Days, Hours, Minutes
            self.fields['addition_time_' + time_unit] = forms.FloatField(initial=0, required=False)
            self.fields['duration_' + time_unit] = forms.FloatField(initial=0, required=False)
            # self.fields['addition_time_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
            # self.fields['duration_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
            # Change style
            self.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
            self.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'
            # self.fields['addition_time_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'
            # self.fields['duration_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'

        # Set CSS class to receipt date to use date picker
        self.fields['receipt_date'].widget.attrs['class'] = 'datepicker-input'
        self.fields['item_setup_date'].widget.attrs['class'] = 'datepicker-input'

        # Set the widgets for some additional fields
        self.fields['item_name'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_scientist'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_notes'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['setup_variance_from_organ_model_protocol'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['item_notebook_page'].widget.attrs['style'] = 'width:50px;'
        self.fields['cell_sample'].widget.attrs['style'] = 'width:50px;'
        self.fields['passage'].widget.attrs['style'] = 'width:50px;'

    ### ADDITIONAL MATRIX FIELDS (unsaved)
    number_of_items = forms.IntegerField(required=False)

    ### ITEM FIELD HELPERS
    action = forms.ChoiceField(choices=(
        ('add_name', 'Add Names/IDs*'),
        ('add_date', 'Add Setup Date*'),
        ('add_notes', 'Add Notes/Notebook Information'),
        ('add_device', 'Add Device/Organ Model Information*'),
        ('add_settings', 'Add Settings'),
        ('add_compounds', 'Add Compounds'),
        ('add_cells', 'Add Cells'),
        ('copy', 'Copy Contents'),
        ('clear', 'Clear Contents')
    ))

    ### ADDING ITEM FIELDS
    item_name = forms.CharField(required=False)

    item_setup_date = forms.DateField(required=False)

    item_scientist = forms.CharField(required=False)
    item_notebook = forms.CharField(required=False)
    item_notebook_page = forms.CharField(required=False)
    item_notes = forms.CharField(required=False)

    ### ADDING SETUP FIELDS
    setup_device = forms.ModelChoiceField(queryset=Microdevice.objects.all().order_by('name'), required=False)
    setup_organ_model = forms.ModelChoiceField(queryset=OrganModel.objects.all().order_by('name'), required=False)
    setup_organ_model_protocol = forms.ModelChoiceField(queryset=OrganModelProtocol.objects.none(), required=False)
    setup_variance_from_organ_model_protocol = forms.CharField(required=False)

    ### ADDING SETUP CELLS
    cell_sample = forms.IntegerField(required=False)
    biosensor = forms.ModelChoiceField(
        queryset=Biosensor.objects.all().prefetch_related('supplier'),
        required=False,
        # Default is naive
        initial=2
    )
    density = forms.FloatField(required=False)

    # TODO THIS IS TO BE HAMMERED OUT
    density_unit = forms.ModelChoiceField(
        queryset=PhysicalUnits.objects.filter(availability__contains='cell'),
        required=False
    )

    passage = forms.CharField(required=False)

    ### ?ADDING SETUP SETTINGS

    ### ADDING COMPOUNDS
    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    concentration_unit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )
    concentration = forms.FloatField(required=False)

    ### INCREMENTER
    concentration_increment = forms.FloatField(required=False, initial=1)
    concentration_increment_type = forms.ChoiceField(choices=(
        ('/', 'Divide'),
        ('*', 'Multiply'),
        ('+', 'Add'),
        ('-', 'Subtract')
    ))
    concentration_increment_direction = forms.ChoiceField(choices=(
        ('lrd', 'Left to Right and Down'),
        ('rlu', 'Right to Left and Up')
    ))

    # Text field (un-saved) for supplier
    supplier_text = forms.CharField(required=False, initial='N/A')
    # Text field (un-saved) for lot
    lot_text = forms.CharField(required=False, initial='N/A')
    # Receipt date
    receipt_date = forms.DateField(required=False)

    # Contains all item information
    item_data = forms.CharField(required=False, initial='{}')
    setup_data = forms.CharField(required=False, initial='{}')
    setup_set_data = forms.CharField(required=False, initial='{}')

    # Curious way to communicate models to be saved to save (no repeat queries)
    items_to_consider = forms.BooleanField(required=False)
    items_to_purge = forms.BooleanField(required=False)
    # item_to_setup_map = forms.BooleanField(required=False)
    setups_to_consider = forms.BooleanField(required=False)
    # suppliers_to_consider = forms.BooleanField(required=False)
    # supplier_to_compound_instance = forms.BooleanField(required=False)
    # compound_instances_to_consider = forms.BooleanField(required=False)
    # compound_instance_to_assay_compound = forms.BooleanField(required=False)
    compounds_to_consider = forms.BooleanField(required=False)
    # compound_to_setup_map = forms.BooleanField(required=False)
    cells_to_consider = forms.BooleanField(required=False)
    # cell_to_setup_map = forms.BooleanField(required=False)
    settings_to_consider = forms.BooleanField(required=False)
    # setting_to_setup_map = forms.BooleanField(required=False)

    def clean_item_data(self):
        current_json = self.cleaned_data['item_data']
        try:
            json.loads(current_json)
        except:
            raise forms.ValidationError('Invalid data in item data.')
        return current_json

    def clean_setup_data(self):
        current_json = self.cleaned_data['setup_data']
        try:
            json.loads(current_json)
        except:
            raise forms.ValidationError('Invalid data in setup data.')
        return current_json

    def clean_setup_set_data(self):
        current_json = self.cleaned_data['setup_set_data']
        try:
            json.loads(current_json)
        except:
            raise forms.ValidationError('Invalid data in setup sets data.')
        return current_json

    def clean(self):
        # clean the form data, before validation
        data = super(AssayMatrixForm, self).clean()

        # Study is excluded, so unique_together constraint is manual
        if AssayMatrix.objects.filter(
                name=data.get('name', ''),
                study=self.instance.study
        ).exists() and not self.instance.id:
            raise forms.ValidationError({'name': ['A matrix with this name already exists in this study.']})

        # Goofy, just trying to get things to work
        try:
            self.instance = super(forms.ModelForm, self).save(commit=False)
        except:
            pass

        # PLEASE NOTE: IF THERE ARE COMPOUNDS, CELLS, SETTINGS TO BE SAVED, THEN THERE ARE NEW SETUPS
        self.cleaned_data['items_to_consider'] = []
        self.cleaned_data['items_to_purge'] = []
        #self.cleaned_data['item_to_setup_map'] = {}
        self.cleaned_data['setups_to_consider'] = {}
        # self.cleaned_data['suppliers_to_consider'] = {}
        # self.cleaned_data['supplier_to_compound_instance'] = {}
        self.cleaned_data['compounds_to_consider'] = {}
        #self.cleaned_data['assay_compound_to_setup_map'] = {}
        # self.cleaned_data['compound_instances_to_consider'] = {}
        # self.cleaned_data['compound_instance_to_assay_compound'] = {}
        self.cleaned_data['cells_to_consider'] = {}
        #self.cleaned_data['cell_to_setup_map'] = {}
        self.cleaned_data['settings_to_consider'] = {}
        #self.cleaned_data['setting_to_setup_map'] = {}

        # COPY-PASTED: NEED TO CHANGE
        current_data = self.cleaned_data

        # Get all setup compounds
        compounds = {
            (
                compound.compound_instance.id,
                compound.concentration,
                compound.concentration_unit.id,
                compound.addition_time,
                compound.duration
            ): compound for compound in AssaySetupCompound.objects.all().prefetch_related(
                'compound_instance__compound',
                'concentration_unit'
            )
        }

        setup_compound_id_to_index = {}
        duplicate_compound_indexes = {}

        cells = {
            (
                cell.cell_sample.id,
                cell.biosensor.id,
                cell.density,
                cell.density_unit.id,
                cell.passage
            ): cell for cell in AssaySetupCell.objects.all().prefetch_related(
                'cell_sample',
                'biosensor',
                'density_unit'
            )
        }

        setup_cell_id_to_index = {}
        duplicate_cell_indexes = {}

        settings = {
            (
                setting.setting.name,
                setting.unit.id,
                # setting.addition_time,
                # setting.duration
            ): setting for setting in AssaySetupSetting.objects.all().prefetch_related(
                'setting',
                'unit'
            )
        }

        setup_setting_id_to_index = {}
        duplicate_setting_indexes = {}

        # Get all Compound Instances
        compound_instances = {
            (
                instance.compound.id,
                instance.supplier.id,
                instance.lot,
                instance.receipt_date
            ): instance for instance in CompoundInstance.objects.all().prefetch_related(
                'compound',
                'supplier'
            )
        }

        # Get all suppliers
        suppliers = {
            supplier.name: supplier for supplier in CompoundSupplier.objects.all()
        }

        # TODO PUT THIS IN FORM
        setup_set_data = json.loads(current_data.get('setup_set_data', '{}'))

        compound_data = setup_set_data.get('compounds', {})

        for compound, index in compound_data.items():
            compound = json.loads(compound)

            compound_id = compound.get('compound_id', None)
            supplier_text = compound.get('supplier_text', '').strip()
            lot_text = compound.get('lot_text', '').strip()
            receipt_date = compound.get('receipt_date', None)

            try:
                concentration = float(compound.get('concentration', None))
            except (TypeError, ValueError) as e:
                concentration = None
            concentration_unit_id = compound.get('concentration_unit_id', None)

            try:
                addition_time = float(compound.get('addition_time', None))
            except (TypeError, ValueError) as e:
                addition_time = None
            try:
                duration = float(compound.get('duration', None))
            except (TypeError, ValueError) as e:
                duration = None

            if receipt_date:
                try:
                    receipt_date = datetime.datetime.strptime(receipt_date, '%Y-%m-%d').date()
                # TODO This catch clause is evil
                except:
                    raise forms.ValidationError('Improperly set receipt date: {0}.'.format(receipt_date))
            else:
                receipt_date = None

            if duration <= 0:
                raise forms.ValidationError('Duration cannot be zero or negative.')

            # Check if the supplier already exists
            supplier = suppliers.get(supplier_text, '')
            # Otherwise create the supplier
            if not supplier:
                supplier = CompoundSupplier(
                    name=supplier_text,
                    created_by=self.user,
                    created_on=timezone.now(),
                    modified_by=self.user,
                    modified_on=timezone.now()
                )
                # Go ahead and save the supplier
                try:
                    supplier.full_clean()
                    supplier.save()
                except forms.ValidationError as e:
                    raise forms.ValidationError('Invalid compound supplier given.')
                suppliers.update({
                    supplier_text: supplier
                })

            # Check if compound instance exists
            compound_instance = compound_instances.get((compound_id, supplier.id, lot_text, receipt_date), '')

            if not compound_instance:
                compound_instance = CompoundInstance(
                    compound_id=compound_id,
                    supplier=supplier,
                    lot=lot_text,
                    receipt_date=receipt_date,
                    created_by=self.user,
                    created_on=timezone.now(),
                    modified_by=self.user,
                    modified_on=timezone.now()
                )
                # Go ahead and save the compound instance (tries will be considered straight submission)
                try:
                    compound_instance.full_clean()
                    compound_instance.save()
                except forms.ValidationError as e:
                    # TODO
                    raise forms.ValidationError(unicode(e))
                compound_instances.update({
                    (compound_id, supplier.id, lot_text, receipt_date): compound_instance
                })

            compound = AssaySetupCompound(
                compound_instance=compound_instance,
                concentration=concentration,
                concentration_unit_id=concentration_unit_id,
                addition_time=addition_time,
                duration=duration
            )

            conflicting_compound = compounds.get(
                (
                    compound.compound_instance.id,
                    compound.concentration,
                    compound.concentration_unit.id,
                    compound.addition_time,
                    compound.duration
                ), None
            )
            if not conflicting_compound:
                try:
                    compound.full_clean()
                except forms.ValidationError as e:
                    raise forms.ValidationError(unicode(e))
            else:
                compound = conflicting_compound
                if compound.id not in setup_compound_id_to_index:
                    setup_compound_id_to_index.update({
                        compound.id: index
                    })
                else:
                    duplicate_compound_indexes.update({
                        index: setup_compound_id_to_index.get(compound.id)
                    })

            compounds.update({
                (
                    compound.compound_instance.id,
                    compound.concentration,
                    compound.concentration_unit.id,
                    compound.addition_time,
                    compound.duration
                ): compound
            })

            self.cleaned_data['compounds_to_consider'].update({
                index: compound
            })

        cell_data = setup_set_data.get('cells', {})

        for cell, index in cell_data.items():
            cell = json.loads(cell)

            # This is a little too verbose
            try:
                cell_sample_id = int(cell.get('cell_sample_id', None))
            except (TypeError, ValueError) as e:
                cell_sample_id = None
            try:
                biosensor_id = int(cell.get('biosensor_id', None))
            except (TypeError, ValueError) as e:
                biosensor_id = None
            try:
                density = float(cell.get('density', None))
            except (TypeError, ValueError) as e:
                density = None
            try:
                density_unit_id = int(cell.get('density_unit_id', None))
            except (TypeError, ValueError) as e:
                density_unit_id = None
            passage = cell.get('passage', '')

            cell = AssaySetupCell(
                cell_sample_id=cell_sample_id,
                biosensor_id=biosensor_id,
                density=density,
                density_unit_id=density_unit_id,
                passage=passage
            )

            conflicting_cell= cells.get(
                (
                    cell_sample_id,
                    biosensor_id,
                    density,
                    density_unit_id,
                    passage
                ), None
            )

            if not conflicting_cell:
                try:
                    cell.full_clean()
                except forms.ValidationError as e:
                    raise forms.ValidationError(unicode(e))
            else:
                cell = conflicting_cell
                if cell.id not in setup_cell_id_to_index:
                    setup_cell_id_to_index.update({
                        cell.id: index
                    })
                else:
                    duplicate_cell_indexes.update({
                        index: setup_cell_id_to_index.get(cell.id)
                    })

            cells.update({
                (
                    cell_sample_id,
                    biosensor_id,
                    density,
                    density_unit_id,
                    passage
                ): cell
            })

            self.cleaned_data['cells_to_consider'].update({
                index: cell
            })

        setting_data = setup_set_data.get('settings', {})

        for setting, index in setting_data.items():
            setting = json.loads(setting)

            # This is a little too verbose
            setting_id = setting.get('setting_id', None)
            unit_id = setting.get('unit_id', None)
            value = setting.get('value', None)
            # addition_time
            # duration

            setting = AssaySetupSetting(
                setting_id=setting_id,
                unit_id=unit_id,
                value=value
            )

            conflicting_setting = settings.get(
                (
                    setting_id,
                    unit_id,
                    value
                ), None
            )

            if not conflicting_setting:
                try:
                    setting.full_clean()
                except forms.ValidationError as e:
                    raise forms.ValidationError(unicode(e))
            else:
                setting = conflicting_setting
                if setting.id not in setup_setting_id_to_index:
                    setup_setting_id_to_index.update({
                        setting.id: index
                    })
                else:
                    duplicate_setting_indexes.update({
                        index: setup_setting_id_to_index.get(setting.id)
                    })

            settings.update({
                (
                    setting_id,
                    unit_id,
                    value
                ): setting
            })

            self.cleaned_data['settings_to_consider'].update({
                index: setting
            })

        setups = {}

        if self.instance.pk:
            # Get existing matrix setups
            # Be sure this applies only to the current matrix
            setup_queryset = AssaySetup.objects.filter(
                matrix_id=self.instance.id
            ).prefetch_related(
                'matrix',
                'device',
                'organ_model_protocol',
                # 'compounds_set',
                # 'cells_set',
                # 'settings_set'
            )

            for setup in setup_queryset:
                compound_set_ids = setup.compounds.values_list('id', flat=True)
                compound_set_indexes = tuple(sorted((
                    setup_compound_id_to_index.setdefault(
                        compound_id, len(compound_data)
                    ) for compound_id in compound_set_ids
                )))

                cell_set_ids = setup.cells.values_list('id', flat=True)
                cell_set_indexes = tuple(sorted((
                    setup_cell_id_to_index.setdefault(
                        cell_id, len(cell_data)
                    ) for cell_id in cell_set_ids
                )))

                setting_set_ids = setup.settings.values_list('id', flat=True)
                setting_set_indexes = tuple(sorted((
                    setup_setting_id_to_index.setdefault(
                        setting_id, len(setting_data)
                    ) for setting_id in setting_set_ids
                )))

                setups.update({
                    (
                        # setup.matrix_id,
                        setup.device_id,
                        setup.organ_model_id,
                        setup.organ_model_protocol_id,
                        setup.variance_from_organ_model_protocol,
                        compound_set_indexes,
                        cell_set_indexes,
                        setting_set_indexes
                    ): setup
                })

        setup_id_to_index = {}
        setup_indexes = {}
        duplicate_setup_indexes = {}

        # TODO PUT THIS IN FORM
        setup_data = json.loads(current_data.get('setup_data', '{}'))

        for setup, index in setup_data.items():
            setup = json.loads(setup)

            try:
                device_id = int(setup.get('device_id', None))
            except (TypeError, ValueError) as e:
                raise forms.ValidationError('All ids must be entered as integers.')

            try:
                organ_model_id = int(setup.get('organ_model_id', None))
            except (TypeError, ValueError) as e:
                organ_model_id = None

            try:
                organ_model_protocol_id = int(setup.get('organ_model_protocol_id', None))
            except (TypeError, ValueError) as e:
                organ_model_protocol_id = None

            variance_from_organ_model_protocol = setup.get('variance_from_organ_model_protocol', '')

            compound_set = tuple(
                set(
                    sorted([duplicate_compound_indexes.get(compound_index, compound_index) for compound_index in setup.get('compounds', [])])
                )
            )
            cell_set = tuple(
                set(
                    sorted([duplicate_cell_indexes.get(cell_index, cell_index) for cell_index in setup.get('cells', [])])
                )
            )
            setting_set = tuple(
                set(
                    sorted([duplicate_setting_indexes.get(setting_index, setting_index) for setting_index in setup.get('settings', [])])
                )
            )

            # More than a little unusual, it is already a dict? I guess I might want to make sure things are in order
            setup = {
                'setup_index': index,
                'device_id': device_id,
                'organ_model_id': organ_model_id,
                'organ_model_protocol_id': organ_model_protocol_id,
                'variance_from_organ_model_protocol': variance_from_organ_model_protocol,
                'compounds': compound_set,
                'cells': cell_set,
                'setting': setting_set
            }

            conflicting_setup = setups.get(
                (
                    device_id,
                    organ_model_id,
                    organ_model_protocol_id,
                    variance_from_organ_model_protocol,
                    compound_set,
                    cell_set,
                    setting_set
                ), None
            )

            if not conflicting_setup:
                # Contrived due to special circumstances
                # Adding the M2M here won't quite work because they likely won't exist!
                try:
                    AssaySetup(
                        matrix=self.instance,
                        device_id=device_id,
                        organ_model_id=organ_model_id,
                        organ_model_protocol_id=organ_model_protocol_id,
                        variance_from_organ_model_protocol=variance_from_organ_model_protocol
                    ).full_clean()
                except forms.ValidationError as e:
                    raise forms.ValidationError(unicode(e))

                setups.update({
                    (
                        device_id,
                        organ_model_id,
                        organ_model_protocol_id,
                        variance_from_organ_model_protocol,
                        compound_set,
                        cell_set,
                        setting_set
                    ): setup
                })
            else:
                setup = conflicting_setup
                if not type(setup) == dict:
                    if setup.id not in setup_id_to_index:
                        setup_id_to_index.update({
                            setup.id: index
                        })
                    else:
                        duplicate_setup_indexes.update({
                            index: setup_id_to_index.get(setup.id)
                        })
                else:
                    duplicate_setup_indexes.update({
                        index: setup.get('setup_index')
                    })

            # Below should be done now, I think
            # TODO NEED TO THINK ABOUT HOW TO REDIRECT UNSAVED DUPLICATES (may or may not occur, good to check)
            setup_indexes.update({
                index: setup
            })

        item_names = {
            item.name: True for item in AssayMatrixItem.objects.filter(
                study=self.instance.study
            ).prefetch_related(
                'study'
            )
        }

        item_indexes = {}

        item_data = json.loads(current_data.get('item_data', '{}'))

        # TODO PREVENT ITEMS WITH DATA FROM BEING DELETED
        for item in item_data.values():
            ignore = True
            for key, value in item.items():
                if value and key not in ['id', 'column_index', 'row_index']:
                    ignore = False
                    break

            if ignore and item.get('id', '') and self.instance.id:
                try:
                    item = AssayMatrixItem.objects.get(id=item.get('id', ''), study_id=self.instance.study.id, matrix_id=self.instance.id)
                    # TODO MAKE SURE TO CHECK FOR RELATED DATA BEFORE ACTUALLY ADDING TO PURGE
                    self.cleaned_data['items_to_purge'].append(item)

                except:
                    raise forms.ValidationError('A chip/well updated incorrectly.')

            if ignore:
                continue

            try:
                current_row_index = item.get('row_index', None)
                current_column_index = item.get('column_index', None)

                if current_row_index is '':
                    current_row_index = None

                if current_column_index is '':
                    current_column_index = None

                item.update({
                    'row_index': int(current_row_index),
                    'column_index': int(current_column_index)
                })
            except (TypeError, ValueError) as e:
                raise forms.ValidationError('Row and column indexes must be numeric.')

            # TODO NEED TO CHANGE FAILURE TIME TO BE SPLIT INTO DAY HOUR MINUTE
            try:
                current_failure_time = item.get('failure_time', None)

                if current_failure_time is '':
                    current_failure_time = None

                item.update({
                    'failure_time': current_failure_time
                })
            except (TypeError, ValueError) as e:
                raise forms.ValidationError('Failure time must be numeric.')

            try:
                setup_date_as_date = datetime.datetime.strptime(item.get('setup_date', ''), '%Y-%m-%d').date()
                item.update({
                    'setup_date': setup_date_as_date
                })
            # TODO This catch clause is evil
            except:
                raise forms.ValidationError('Improperly set date: {0}.'.format(item.get('setup_date', '')))

            # Check the indices
            if item_indexes.get(
                    (item.get('column_index'), item.get('row_index')), None
            ):
                raise forms.ValidationError('Duplicate row and column indexes are not allowed.')

            item_indexes.update({
                (item.get('column_index'), item.get('row_index')): True
            })

            # Don't bother with unmodified existing items
            if item.get('id', None) and not item.get('modified', None):
                continue

            if item.get('name', '') in item_names and not item.get('id', ''):
                raise forms.ValidationError(
                    'The name: "{0}" is in use in this study. Make sure names are unique.'.format(
                        item.get('name', '')
                    )
                )

            setup_index = duplicate_setup_indexes.get(item.get('setup_index', None), item.get('setup_index', None))

            if setup_index not in setup_indexes:
                raise forms.ValidationError('All chips/wells need a device.')

            self.cleaned_data['setups_to_consider'].update({
                setup_index: setup_indexes.get(setup_index)
            })

            current_id = item.get('id', None)

            fields_dict = {
                'study': self.instance.study,
                'matrix': self.instance,
                'name': item.get('name', ''),
                'setup_date': item.get('setup_date', None),
                # 'failure_time': item.get('failure_time', None),
                'failure_reason_id': item.get('failure_reason_id', None),
                'scientist': item.get('scientist', ''),
                'notebook': item.get('notebook', ''),
                'notebook_page': item.get('notebook_page', ''),
                'notes': item.get('notes', ''),
                'row_index': item.get('row_index', None),
                'column_index': item.get('column_index', None)
            }

            if current_id and self.instance.id:
                try:
                    item = AssayMatrixItem.objects.get(id=current_id, study_id=self.instance.study.id, matrix_id=self.instance.id)
                    item.__dict__.update(fields_dict)

                except:
                    raise forms.ValidationError('A chip/well updated incorrectly.')
            else:
                item = AssayMatrixItem(**fields_dict)

                try:
                    item.full_clean()
                except forms.ValidationError as e:
                    raise forms.ValidationError(unicode(e))

            item_names.update({
                item.name: True
            })

            self.cleaned_data['items_to_consider'].append([item, setup_index])

        return self.cleaned_data

    def save(self, commit=True):
        this_matrix = self.instance

        if this_matrix.pk is None:
            # TODO TODO TODO Modify matrix if necessary
            this_matrix.save()
        else:
            this_matrix = super(AssayMatrixForm, self).save()
            this_matrix.save()

        for index, compound in self.cleaned_data['compounds_to_consider'].items():
            compound.save()

        for index, cell in self.cleaned_data['cells_to_consider'].items():
            cell.save()

        for index, setting in self.cleaned_data['settings_to_consider'].items():
            setting.save()

        setup_index_to_saved_setup =  {}
        for index, setup in self.cleaned_data['setups_to_consider'].items():
            if type(setup) != dict:
                setup_index_to_saved_setup.update({
                    index: setup
                })
                continue

            # Save setup here
            new_setup = AssaySetup(
                matrix=this_matrix,
                device_id=setup.get('device_id'),
                organ_model_id=setup.get('organ_model_id', None),
                organ_model_protocol_id=setup.get('organ_model_protocol_id', None),
                variance_from_organ_model_protocol=setup.get('variance_from_organ_model_protocol', None)
            )

            new_setup.save()

            for cell_index in setup.get('cells', []):
                new_setup.cells.add(self.cleaned_data['cells_to_consider'].get(cell_index))

            for compound_index in setup.get('compounds', []):
                new_setup.compounds.add(self.cleaned_data['compounds_to_consider'].get(compound_index))

            for setting_index in setup.get('settings', []):
                new_setup.settings.add(self.cleaned_data['settings_to_consider'].get(setting_index))

            setup_index_to_saved_setup.update({
                index: new_setup
            })

        for item_setup_index in self.cleaned_data['items_to_consider']:
            item = item_setup_index[0]
            setup = setup_index_to_saved_setup.get(item_setup_index[1])
            # Unmodified items are currently double saved
            item.setup = setup
            item.matrix = this_matrix
            item.save()
            # If this item is being deleted (TODO)

        for item in self.cleaned_data['items_to_purge']:
            item.delete()

        return this_matrix


# TODO ADD STUDY
class AssayMatrixForm(SignOffMixin, forms.ModelForm):
    class Meta(object):
        model = AssayMatrix
        exclude = ('study',) + tracking
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'variance_from_organ_model_protocol': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayMatrixForm, self).__init__(*args, **kwargs)

        if self.study:
            self.instance.study = self.study

        for time_unit in TIME_CONVERSIONS.keys():
            # Create fields for Days, Hours, Minutes
            self.fields['addition_time_' + time_unit] = forms.FloatField(initial=0, required=False)
            self.fields['duration_' + time_unit] = forms.FloatField(initial=0, required=False)
            # self.fields['addition_time_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
            # self.fields['duration_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
            # Change style
            self.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
            self.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'
            # self.fields['addition_time_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'
            # self.fields['duration_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'

        # Set CSS class to receipt date to use date picker
        self.fields['receipt_date'].widget.attrs['class'] = 'datepicker-input'
        self.fields['item_setup_date'].widget.attrs['class'] = 'datepicker-input'

        # Set the widgets for some additional fields
        self.fields['item_name'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_scientist'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_notes'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['setup_variance_from_organ_model_protocol'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['item_notebook_page'].widget.attrs['style'] = 'width:50px;'
        self.fields['cell_sample'].widget.attrs['style'] = 'width:50px;'
        self.fields['passage'].widget.attrs['style'] = 'width:50px;'

    ### ADDITIONAL MATRIX FIELDS (unsaved)
    number_of_items = forms.IntegerField(required=False)

    ### ITEM FIELD HELPERS
    action = forms.ChoiceField(choices=(
        ('add_name', 'Add Names/IDs*'),
        ('add_date', 'Add Setup Date*'),
        ('add_notes', 'Add Notes/Notebook Information'),
        ('add_device', 'Add Device/Organ Model Information*'),
        ('add_settings', 'Add Settings'),
        ('add_compounds', 'Add Compounds'),
        ('add_cells', 'Add Cells'),
        ('copy', 'Copy Contents'),
        ('clear', 'Clear Contents')
    ))

    ### ADDING ITEM FIELDS
    item_name = forms.CharField(required=False)

    item_setup_date = forms.DateField(required=False)

    item_scientist = forms.CharField(required=False)
    item_notebook = forms.CharField(required=False)
    item_notebook_page = forms.CharField(required=False)
    item_notes = forms.CharField(required=False)

    ### ADDING SETUP FIELDS
    setup_device = forms.ModelChoiceField(queryset=Microdevice.objects.all().order_by('name'), required=False)
    setup_organ_model = forms.ModelChoiceField(queryset=OrganModel.objects.all().order_by('name'), required=False)
    setup_organ_model_protocol = forms.ModelChoiceField(queryset=OrganModelProtocol.objects.none(), required=False)
    setup_variance_from_organ_model_protocol = forms.CharField(required=False)

    ### ADDING SETUP CELLS
    cell_sample = forms.IntegerField(required=False)
    biosensor = forms.ModelChoiceField(
        queryset=Biosensor.objects.all().prefetch_related('supplier'),
        required=False,
        # Default is naive
        initial=2
    )
    density = forms.FloatField(required=False)

    # TODO THIS IS TO BE HAMMERED OUT
    density_unit = forms.ModelChoiceField(
        queryset=PhysicalUnits.objects.filter(availability__contains='cell'),
        required=False
    )

    passage = forms.CharField(required=False)

    ### ?ADDING SETUP SETTINGS

    ### ADDING COMPOUNDS
    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    concentration_unit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )
    concentration = forms.FloatField(required=False)

    ### INCREMENTER
    concentration_increment = forms.FloatField(required=False, initial=1)
    concentration_increment_type = forms.ChoiceField(choices=(
        ('/', 'Divide'),
        ('*', 'Multiply'),
        ('+', 'Add'),
        ('-', 'Subtract')
    ))
    concentration_increment_direction = forms.ChoiceField(choices=(
        ('lrd', 'Left to Right and Down'),
        ('rlu', 'Right to Left and Up')
    ))

    # Text field (un-saved) for supplier
    supplier_text = forms.CharField(required=False, initial='N/A')
    # Text field (un-saved) for lot
    lot_text = forms.CharField(required=False, initial='N/A')
    # Receipt date
    receipt_date = forms.DateField(required=False)


class AssaySetupCompoundForm(forms.ModelForm):
    class Meta(object):
        model = AssaySetupCompound
        exclude = tracking

    def __init__(self, *args, **kwargs):
        # self.static_choices = kwargs.pop('static_choices', None)
        super(AssaySetupCompoundForm, self).__init__(*args, **kwargs)


# TODO: IDEALLY THE CHOICES WILL BE PASSED VIA A KWARG
class AssaySetupCompoundFormSet(BaseInlineFormSet):
    cached_fields = []

    def __init__(self, *args, **kwargs):
        # TODO EVENTUALLY PASS WITH KWARG
        self.cached_fields = kwargs.pop('cached_fields', None)
        # print 'FormSet: ', self.static_choices
        super(AssaySetupCompoundFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupCompoundFormSet, self)._construct_form(i, **kwargs)
        for cache_field in self.cached_fields:
            field = form.fields[cache_field]
            field.cache_choices = True
            choices = getattr(self, '_cached_%s_choices' %
                              cache_field, None)
            if choices is None:
                choices = self.cached_fields.get(cache_field, None)

                if choices is None:
                    choices = list(field.choices)

                setattr(self, '_cached_%s_choices' % cache_field,
                        choices)

            field.choice_cache = choices
        return form


class AssaySetupCellForm(forms.ModelForm):
    class Meta(object):
        model = AssaySetupCell
        exclude = tracking

    def __init__(self, *args, **kwargs):
        # self.static_choices = kwargs.pop('static_choices', None)
        super(AssaySetupCellForm, self).__init__(*args, **kwargs)


# TODO: IDEALLY THE CHOICES WILL BE PASSED VIA A KWARG
class AssaySetupCellFormSet(BaseInlineFormSet):
    cached_fields = []

    def __init__(self, *args, **kwargs):
        # TODO EVENTUALLY PASS WITH KWARG
        self.cached_fields = kwargs.pop('cached_fields', None)
        super(AssaySetupCellFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupCellFormSet, self)._construct_form(i, **kwargs)
        for cache_field in self.cached_fields:
            field = form.fields[cache_field]
            field.cache_choices = True
            choices = getattr(self, '_cached_%s_choices' %
                              cache_field, None)
            if choices is None:
                choices = self.cached_fields.get(cache_field, None)

                if choices is None:
                    choices = list(field.choices)

                setattr(self, '_cached_%s_choices' % cache_field,
                        choices)

            field.choice_cache = choices
        return form


class AssaySetupSettingForm(forms.ModelForm):
    class Meta(object):
        model = AssaySetupCell
        exclude = tracking

    def __init__(self, *args, **kwargs):
        # self.static_choices = kwargs.pop('static_choices', None)
        super(AssaySetupSettingForm, self).__init__(*args, **kwargs)


# TODO: IDEALLY THE CHOICES WILL BE PASSED VIA A KWARG
class AssaySetupSettingFormSet(BaseInlineFormSet):
    cached_fields = []

    def __init__(self, *args, **kwargs):
        # TODO EVENTUALLY PASS WITH KWARG
        self.cached_fields = kwargs.pop('cached_fields', None)
        super(AssaySetupSettingFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupSettingFormSet, self)._construct_form(i, **kwargs)
        for cache_field in self.cached_fields:
            field = form.fields[cache_field]
            field.cache_choices = True
            choices = getattr(self, '_cached_%s_choices' %
                              cache_field, None)
            if choices is None:
                choices = self.cached_fields.get(cache_field, None)

                if choices is None:
                    choices = list(field.choices)

                setattr(self, '_cached_%s_choices' % cache_field,
                        choices)

            field.choice_cache = choices
        return form

AssaySetupCompoundFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupCompound,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCompoundForm,
    formset=AssaySetupCompoundFormSet
)
AssaySetupCellFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupCell,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCellForm,
    formset=AssaySetupCellFormSet
)
AssaySetupSettingFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupSetting,
    extra=1,
    exclude=[tracking],
    form=AssaySetupSettingForm,
    formset=AssaySetupSettingFormSet
)


class AssayMatrixItemForm(forms.ModelForm):
    class Meta(object):
        model = AssayMatrixItem
        exclude = ('study',) + tracking


# TODO ADD STUDY
# TODO NEED TO TEST
# TODO NEED TO IMPROVE PERFORMANCE (UNACCEPTABLY BAD AT THE MOMENT)
# Early attempt to have a nested formset to keep items, compounds, cells, and settings together
class AssayMatrixItemFormSet(BaseInlineFormSet):
    cached_fields = []

    compound_choices = []
    cell_choices = []
    setting_choices = []

    def __init__(self, *args, **kwargs):
        # Get the study
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayMatrixItemFormSet, self).__init__(*args, **kwargs)

        self.cached_fields = {
            'device': tuple(Microdevice.objects.all().values_list('id', 'id')),
            'organ_model': tuple(OrganModel.objects.all().values_list('id', 'id')),
            'organ_model_protocol': tuple(OrganModelProtocol.objects.all().values_list('id', 'id')),
            'failure_reason': tuple(AssayFailureReason.objects.all().values_list('id', 'id')),
        }

        # Here lies the nested formsets
        addition_location_choices = tuple(MicrodeviceSection.objects.all().values_list('id', 'id'))

        compound_instance_choices = tuple(CompoundInstance.objects.all().values_list('id', 'id'))

        concentration_unit_choices = tuple((PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ) | PhysicalUnits.objects.filter(unit='%')).values_list('id', 'id'))

        self.compound_choices = {
            'compound_instance': compound_instance_choices,
            'concentration_unit': concentration_unit_choices,
            'addition_location': addition_location_choices
        }

        self.cell_choices = {
            'cell_sample': tuple(CellSample.objects.all().values_list('id', 'id')),
            'biosensor': tuple(Biosensor.objects.all().values_list('id', 'id')),
            'density_unit': tuple(PhysicalUnits.objects.filter(availability__contains='cell').values_list('id', 'id')),
            'addition_location': addition_location_choices
        }

        self.setting_choices = {
            'setting': tuple(AssaySetting.objects.all().values_list('id', 'id')),
            'unit': tuple(PhysicalUnits.objects.all().values_list('id', 'id')),
            'addition_location': addition_location_choices
        }

        for form in self.forms:
            if self.study:
                form.instance.study = self.study


    def add_fields(self, form, index):
        super(AssayMatrixItemFormSet, self).add_fields(form, index)

        form.nested_formset_names = (
            'compounds',
            'cells',
            'settings'
        )

        form.compounds = AssaySetupCompoundFormSetFactory(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            prefix='compound-%s-%s' % (
                form.prefix,
                AssaySetupCompoundFormSetFactory.get_default_prefix()),
            # extra=1
            cached_fields=self.compound_choices
        )

        form.cells = AssaySetupCellFormSetFactory(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            prefix='cell-%s-%s' % (
                form.prefix,
                AssaySetupCellFormSetFactory.get_default_prefix()),
            # extra=1
            cached_fields=self.cell_choices
        )

        form.settings = AssaySetupSettingFormSetFactory(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            prefix='setting-%s-%s' % (
                form.prefix,
                AssaySetupSettingFormSetFactory.get_default_prefix()),
            # extra=1
            cached_fields=self.setting_choices
        )

    def _construct_form(self, i, **kwargs):
        form = super(AssayMatrixItemFormSet, self)._construct_form(i, **kwargs)
        for cache_field in self.cached_fields:
            field = form.fields[cache_field]
            field.cache_choices = True
            choices = getattr(self, '_cached_%s_choices' %
                              cache_field, None)
            if choices is None:
                choices = self.cached_fields.get(cache_field, None)

                if choices is None:
                    choices = list(field.choices)

                setattr(self, '_cached_%s_choices' % cache_field,
                        choices)

            field.choice_cache = choices
        return form

    def is_valid(self):
        result = super(AssayMatrixItemFormSet, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                for formset_name in form.nested_formset_names:
                    if hasattr(form, formset_name):
                        result = result and form.__dict__.get(formset_name).is_valid()

        return result

    def save(self, commit=True):
        result = super(AssayMatrixItemFormSet, self).save(commit=commit)

        for form in self.forms:
            for formset_name in form.nested_formset_names:
                if hasattr(form, formset_name):
                    if not self._should_delete_form(form):
                        form.__dict__.get(formset_name).save(commit=commit)

        return result

AssayMatrixItemFormSetFactory = inlineformset_factory(
    AssayMatrix,
    AssayMatrixItem,
    formset=AssayMatrixItemFormSet,
    form=AssayMatrixItemForm,
    extra=1,
    exclude=('study',) + tracking
)


# OLD SIGN OFF STUFF, NEED TO MOVE TO ASSAY STUDY TODO TODO TODO
class AssayRunSignOffForm(SignOffMixin, forms.ModelForm):
    class Meta(object):
        model = AssayRun
        fields = ['signed_off', 'signed_off_notes']
        widgets = {
            'signed_off_notes': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }


class AssayRunStakeholderSignOffForm(SignOffMixin, forms.ModelForm):
    class Meta(object):
        model = AssayRunStakeholder
        fields = ['signed_off', 'signed_off_notes']
        widgets = {
            'signed_off_notes': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }


class AssayRunStakeholderFormSet(BaseInlineFormSet):
    class Meta(object):
        model = AssayRunStakeholder

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AssayRunStakeholderFormSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            # TODO FILTER OUT THOSE USER ISN'T ADMIN OF
            # TODO REVIEW
            user_admin_groups = self.user.groups.filter(name__contains=ADMIN_SUFFIX)
            potential_groups = [group.name.replace(ADMIN_SUFFIX, '') for group in user_admin_groups]
            queryset = super(AssayRunStakeholderFormSet, self).get_queryset()
            # Only include unsigned off forms that user is admin of!
            self._queryset = queryset.filter(
                group__name__in=potential_groups,
                signed_off_by=None
            )
        return self._queryset

    def save(self, commit=True):
        for form in self.forms:
            signed_off = form.cleaned_data.get('signed_off', False)
            if signed_off and is_group_admin(self.user, form.instance.group.name):
                form.instance.signed_off_by = self.user
                form.instance.signed_off_date = timezone.now()
                form.save(commit=True)

# Really, all factories should be declared like so (will have to do this for upcoming revision)
assay_run_stakeholder_sign_off_formset_factory = inlineformset_factory(
    AssayRun,
    AssayRunStakeholder,
    form=AssayRunStakeholderSignOffForm,
    formset=AssayRunStakeholderFormSet,
    extra=0,
    can_delete=False
)

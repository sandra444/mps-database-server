import csv

from django import forms
from django.forms.models import BaseInlineFormSet
from assays.models import *
from compounds.models import Compound
# Use regular expressions for a string split at one point
import re
import string
import xlrd

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


class AssayChipResultForm(forms.ModelForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayChipResultForm,self).__init__(*args,**kwargs)
        exclude_list = AssayChipTestResult.objects.filter(chip_readout__isnull=False).values_list('chip_readout', flat=True)
        readouts = AssayChipReadout.objects.filter(chip_setup__assay_run_id=study).exclude(id__in=list(set(exclude_list)))
        if current:
            readouts = readouts | AssayChipReadout.objects.filter(pk=current)
        readouts = readouts.prefetch_related('chip_setup', 'chip_setup__unit', 'chip_setup__compound')
        self.fields['chip_readout'].queryset = readouts

    class Meta(object):
        model = AssayChipTestResult
        widgets = {
            'summary': forms.Textarea(attrs={'cols':75, 'rows': 3}),
        }
        exclude = group + tracking + restricted

    # Set chip setup to unique instead of throwing error in validation
    # def clean(self):
    #     super(forms.ModelForm, self).clean()
    #
    #     if 'chip_setup' in self.cleaned_data and AssayChipTestResult.objects.filter(chip_setup=self.cleaned_data.get('chip_setup','')):
    #         raise forms.ValidationError('A readout for the given setup already exists!')


class AssayChipReadoutForm(CloneableForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayChipReadoutForm,self).__init__(*args,**kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(unit_type='T').order_by('scale_factor')
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


class AssayChipSetupForm(CloneableForm):
    def __init__(self,*args,**kwargs):
        super (AssayChipSetupForm,self).__init__(*args,**kwargs)
        # Filter on concentration but make a special exception for percent (%)
        self.fields['unit'].queryset = PhysicalUnits.objects.filter(unit_type='C').order_by('base_unit', 'scale_factor') | PhysicalUnits.objects.filter(unit='%')

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

        # Make sure the barcode/ID is unique in the study
        if AssayChipSetup.objects.filter(assay_run_id=self.instance.assay_run_id, assay_chip_id=self.cleaned_data.get('assay_chip_id')).exclude(id=self.instance.id):
            raise forms.ValidationError({'assay_chip_id' : ['ID/Barcode must be unique within study.',]})

        # Check to see if compound data is complete if: 1.) compound test type 2.) compound is selected (negative control)
        type = self.cleaned_data.get('chip_test_type', '')
        compound = self.cleaned_data.get('compound', '')
        concentration = self.cleaned_data.get('concentration', '')
        unit = self.cleaned_data.get('unit', '')
        if type == 'compound' and not all([compound,concentration,unit]) or (compound and not all([concentration,unit])):
            raise forms.ValidationError('Please complete all data for compound.')


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
        unit_queryset = PhysicalUnits.objects.filter(availability__contains='test').order_by('base_unit', 'scale_factor')
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
            'name': forms.Textarea(attrs={'cols':50, 'rows': 1}),
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
    # Notice the special exception for %
    concunit = forms.ModelChoiceField(queryset=(PhysicalUnits.objects.filter(unit_type='C') | PhysicalUnits.objects.filter(unit='%')
), required=False, initial=4)

    class Meta(object):
        model = AssayLayout
        widgets = {
            'layout_name': forms.TextInput(attrs={'size':35}),
        }
        exclude = tracking + restricted


class AssayPlateSetupForm(CloneableForm):
    def __init__(self,*args,**kwargs):
        super (AssayPlateSetupForm,self).__init__(*args,**kwargs)
        # Should the queryset be restricted by group?
        self.fields['assay_layout'].queryset = AssayLayout.objects.all().order_by('-standard', 'layout_name')

    class Meta(object):
        model = AssayPlateSetup
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style':'width:50px;',}),
            'notes': forms.Textarea(attrs={'cols':50, 'rows': 3}),
        }
        exclude = ('assay_run_id','group') + tracking + restricted

    def clean(self):
        super(forms.ModelForm, self).clean()

        # Make sure the barcode/id is unique in the study
        if AssayPlateSetup.objects.filter(assay_run_id=self.instance.assay_run_id, assay_plate_id=self.cleaned_data.get('assay_plate_id')).exclude(id=self.instance.id):
            raise forms.ValidationError({'assay_plate_id' : ['ID/Barcode must be unique within study.',]})

        # Check to see if data has been uploaded for this setup
        # Prevent changing the assay layout if this is the case
        # Get readouts
        readout = AssayPlateReadout.objects.filter(setup=self.instance)
        if readout:
            if AssayReadout.objects.filter(assay_device_readout=readout) and self.cleaned_data.get('assay_layout') != self.instance.assay_layout:
                raise forms.ValidationError({'assay_layout' : ['Assay layout cannot be changed after data has been uploaded.',]})


class AssayPlateCellsInlineFormset(CloneableBaseInlineFormSet):

    class Meta(object):
        model = AssayPlateCells
        exclude = ('',)


class AssayPlateReadoutForm(CloneableForm):
    def __init__(self,study,current,*args,**kwargs):
        super (AssayPlateReadoutForm,self).__init__(*args,**kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(unit_type='T').order_by('scale_factor')
        exclude_list = AssayPlateReadout.objects.filter(setup__isnull=False).values_list('setup', flat=True)
        setups = AssayPlateSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'assay_layout',
            'created_by').exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayPlateSetup.objects.filter(pk=current)
        self.fields['setup'].queryset = setups

    upload_type = forms.ChoiceField(choices=(('Block', 'Block'), ('Tabular', 'Tabular')))

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
        readouts = readouts.prefetch_related('setup')
        self.fields['readout'].queryset = readouts

    class Meta(object):
        model = AssayPlateTestResult
        widgets = {
            'summary': forms.Textarea(attrs={'cols':75, 'rows': 3}),
        }
        exclude = group + tracking + restricted


class PlateTestResultInlineFormset(BaseInlineFormSet):
    def __init__(self,*args,**kwargs):
        super (PlateTestResultInlineFormset,self).__init__(*args,**kwargs)
        unit_queryset = PhysicalUnits.objects.filter(availability__contains='test').order_by('base_unit', 'scale_factor')
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


# This function turns a label to a number
def label_to_number(label):
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
            return {'value': sliced_value, 'quality': 'X'}

        except ValueError:
            return None


def validate_plate_readout_file(
        upload_type,
        assays,
        features,
        assay_feature_to_unit,
        datalist,
        number_of_rows,
        number_of_columns,
        readout_time_unit,
        sheet=''
):
    if upload_type == 'Block':
        # Number of assays found
        assays_found = 0
        # Number of data blocks found
        data_blocks_found = 0

        for row_index, line in enumerate(datalist):
            # If line is blank, skip it
            if not line:
                continue

            # If this line is a header
            # NOTE THAT ASSAYS AND FEATURES ARE IN PAIRS
            # Headers should look like:
            # ASSAY, {{ASSAY}}, FEATURE, {{FEATURE}}, READOUT UNIT, {{READOUT UNIT}}, TIME, {{TIME}}. TIME UNIT, {{TIME UNIT}}
            if line[0].upper().strip() == 'ASSAY':
                # Throw error if header too short
                if len(line) < 6:
                    raise forms.ValidationError(
                        sheet + 'Header row: {} is too short'.format(line))

                assay = line[1].upper().strip()
                feature = line[3]

                assays_found += 1

                val_unit = line[5].strip()

                # TODO OLD
                # TODO REVISE
                # Raise error if feature does not exist
                if feature not in features:
                    raise forms.ValidationError(
                        sheet + 'No feature with the name "%s" exists; please change your file or add this feature' % feature)
                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        sheet + 'No assay with the name "%s" exists; please change your file or add this assay' % assay)
                # Raise error if assay-feature pair is not listed
                if (assay, feature) not in assay_feature_to_unit:
                    raise forms.ValidationError(
                        sheet + 'The assay-feature pair "{0}-{1}" was not recognized'.format(assay, feature))
                # Raise error if val_unit not equal to one listed in APRA
                if val_unit != assay_feature_to_unit.get((assay, feature), ''):
                    raise forms.ValidationError(
                        sheet + 'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, assay_feature_to_unit.get((assay, feature), '')))

                # Fail if time given without time units
                if len(line) < 10 and len(line) > 6 and any(line[6:]):
                    raise forms.ValidationError(
                        sheet + 'Header row: {} improperly configured'.format(line))

                if len(line) >= 10 and any(line[6:]):
                    time = line[7].strip()
                    time_unit = line[9].strip()

                    # Fail if time is not numeric
                    try:
                        float(time)
                    except:
                        raise forms.ValidationError(
                            sheet + 'The time "{}" is invalid. Please only enter numeric times'.format(time))

                    # Fail if time unit does not match
                    # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                    if time_unit[0] != readout_time_unit[0]:
                        raise forms.ValidationError('The time unit "{}" does not correspond with the selected readout time unit of "{}"'.format(time_unit, readout_time_unit))

            # Otherwise the line contains datapoints for the current assay
            else:
                # TODO REVISE HOW DATA_BLOCKS ARE ACQUIRED
                if data_blocks_found == 0 or (row_index-assays_found) % number_of_rows == 0:
                    data_blocks_found += 1

                # This should handle blocks that have too many rows or do not have a header
                if data_blocks_found > assays_found:
                    raise forms.ValidationError(
                    sheet + 'All plate data must have an assay associated with it. Please add a header line.')

                # This is to deal with an EXCESS of columns
                if len(line) > number_of_columns:
                    raise forms.ValidationError(
                        sheet + "The number of columns does not correspond with the device's dimensions:{}".format(line))

                # For every value in the line
                for value in line:
                    # Check every value to make sure it can resolve to a float
                    # Keep empty strings, though they technically can not be converted to floats
                    if value != '':
                        processed_value = process_readout_value(value)

                        if processed_value is None:
                            raise forms.ValidationError(
                                sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(value))
                    # try:
                    #     # Keep empty strings, though they technically can not be converted to floats
                    #     if val != '':
                    #         float(val)
                    # except:
                    #     raise forms.ValidationError(
                    #         sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(val))

    # If not block, then it is TABULAR data
    else:
        # Purge empty lines, they are useless for tabular uploads
        datalist = [row for row in datalist if any(row)]
        # The first line SHOULD be the header
        header = datalist[0]

        # TODO OLD REVISE
        # if header[1].lower().strip() == 'time':
        #     # The features are the third column of the header onward
        #     features = header[3:]
        #     time_specified = True
        # else:
        #     # The features are the third column of the header onward
        #     features = header[1:]
        #     time_specified = False
        #
        # # Fail if there are no features
        # if len(features) < 1:
        #     raise forms.ValidationError(
        #         sheet + 'The file does not contain any features')
        #
        # for feature in features:
        #     # Get associated assay
        #     assay = features_to_assay.get(feature, '')
        #     # Raise error if feature does not exist
        #     if feature not in features_to_assay:
        #         raise forms.ValidationError(
        #             sheet + 'No feature with the name "%s" exists; please change your file or add this feature' % feature)
        #     # Raise error when an assay does not exist
        #     if assay not in assays:
        #         raise forms.ValidationError(
        #             sheet + 'No assay with the name "%s" exists; please change your file or add this assay' % assay)

        # TODO REVISE
        if header < 5:
            raise forms.ValidationError(
                sheet + 'Please specify Well, Assay, Feature, Feature Unit, [Time, Time Unit], and Value in header.')
        if 'TIME' in header[4].upper() and (len(header) < 7 or 'UNIT' not in header[5].upper()):
            raise forms.ValidationError(
                sheet + 'If you are specifying time, you must also specify the time unit')

        if 'TIME' in header[4].upper() and 'UNIT' in header[5].upper():
            time_specified = True
        else:
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # The well identifier given
            well = row[0]
            assay = row[1].upper().strip()
            feature = row[2]
            val_unit = row[3]

            # Raise error if feature does not exist
            if feature not in features:
                raise forms.ValidationError(
                    sheet + 'No feature with the name "%s" exists; please change your file or add this feature' % feature)
            # Raise error when an assay does not exist
            if assay not in assays:
                raise forms.ValidationError(
                    sheet + 'No assay with the name "%s" exists; please change your file or add this assay' % assay)
            # Raise error if assay-feature pair is not listed
            if (assay, feature) not in assay_feature_to_unit:
                raise forms.ValidationError(
                    sheet + 'The assay-feature pair "{0}-{1}" was not recognized'.format(assay, feature))
            # Raise error if val_unit not equal to one listed in APRA
            if val_unit != assay_feature_to_unit.get((assay, feature), ''):
                raise forms.ValidationError(
                    sheet + 'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, assay_feature_to_unit.get((assay, feature), '')))

            # If time is specified
            if time_specified:
                time = row[4]
                time_unit = row[5].strip().lower()
                value = row[6]

                # Check time unit
                # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                if time_unit[0] != readout_time_unit[0]:
                    raise forms.ValidationError(
                        sheet + 'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (time_unit, readout_time_unit))

                # Check time
                try:
                    float(time)
                except:
                    raise forms.ValidationError(
                        sheet + 'Error while parsing time "{}"'.format(time))

            # If time is not specified
            else:
                value = row[4]

            # Check if well id is valid
            try:
                # Split the well into alphabetical and numeric
                row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well)
                # Convert row_label to a number
                row_label = label_to_number(row_label)
                # Convert column label to an integer
                column_label = int(column_label)

                if row_label > number_of_rows:
                    raise forms.ValidationError(
                        sheet + "The number of rows does not correspond with the device's dimensions")

                if column_label > number_of_columns:
                    raise forms.ValidationError(
                        sheet + "The number of columns does not correspond with the device's dimensions")

            except:
                raise forms.ValidationError(
                sheet + 'Error parsing the well ID: {}'.format(well))

            # Check every value to make sure it can resolve to a float
            # Keep empty strings, though they technically can not be converted to floats
            if value != '':
                processed_value = process_readout_value(value)
                if processed_value is None:
                    raise forms.ValidationError(
                        sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(value))
            # try:
            #     if value != '':
            #         float(value)
            # except:
            #     raise forms.ValidationError(
            #         sheet + 'The value {} is invalid; please make sure all values are numerical'.format(value))

            # TODO OLD
            # if time_specified:
            #     # Values are the slice of the fourth item onward
            #     values = row[3:]
            #     time = row[1]
            #     time_unit = row[2]
            #
            #     # Check time unit
            #     # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
            #     if time_unit[0] != readout_time_unit[0]:
            #         raise forms.ValidationError(
            #             sheet + 'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (time_unit, readout_time_unit))
            #
            #     # Check time
            #     try:
            #         float(time)
            #     except:
            #         raise forms.ValidationError(
            #             sheet + 'Error while parsing time "{}"'.format(time))
            # else:
            #     # Values are the slice of the first item onward
            #     values = row[1:]
            #     time = 0
            #     time_unit = None
            #
            # for column_index, value in enumerate(values):
            #     #feature = features[column_index]
            #
            #     # Check if all the values can be parsed as floats
            #     try:
            #         if value != '':
            #             float(value)
            #     except:
            #         raise forms.ValidationError(
            #             sheet + 'The value {} is invalid; please make sure all values are numerical'.format(value))


class AssayPlateReadoutInlineFormset(CloneableBaseInlineFormSet):
    def __init__(self,*args,**kwargs):
        super (AssayPlateReadoutInlineFormset,self).__init__(*args,**kwargs)
        unit_queryset = PhysicalUnits.objects.filter(availability__contains='readout').order_by('base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['readout_unit'].queryset = unit_queryset

    def clean(self):
        """Validate unique, existing PLATE READOUTS"""

        # TODO REVIEW
        # Get upload type
        upload_type = self.data.get('upload_type')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        assays = {}
        features = {}
        assay_feature_to_unit = {}
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    feature = form.cleaned_data.get('feature')
                    readout_unit = form.cleaned_data.get('readout_unit').unit

                    # Add feature
                    features.update({feature:True})
                    # Normal assay name
                    assays.update({assay_name:True})
                    if (assay_name, feature) not in assay_feature_to_unit:
                        assay_feature_to_unit.update({(assay_name, feature): readout_unit})
                    else:
                        raise forms.ValidationError('Assay-Feature pairs must be unique.')
                    # Short assay name
                    assays.update({assay_short_name:True})
                    assay_feature_to_unit.update({(assay_short_name, feature): readout_unit})

            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

        # If there is already a file in the database and it is not being replaced or cleared (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:
            saved_data = AssayReadout.objects.filter(assay_device_readout=self.instance).prefetch_related('assay')

            for raw in saved_data:

                assay = raw.assay.assay_id.assay_name.upper()
                val_unit = raw.assay.readout_unit.unit
                feature = raw.assay.feature

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
                # Raise error if feature does not correspond?
                if feature not in features:
                    raise forms.ValidationError(
                        'You can not remove the feature "{}" because it is in your uploaded data.'.format(feature))
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "{}" because it is in your uploaded data.'.format(assay))
                if (assay, feature) not in assay_feature_to_unit:
                    raise forms.ValidationError(
                        'You can not change the assay-feature pair "{0}-{1}" because it is in your uploaded data'.format(assay, feature))
                # Raise error if val_unit not equal to one listed in APRA
                # Note use of features to unit (unlike chips)
                if val_unit != assay_feature_to_unit.get((assay, feature), ''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"' % (val_unit, assay_feature_to_unit.get((assay, feature), '')))

        # TODO what shall a uniqueness check look like?
        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file','')

            datareader = csv.reader(test_file, delimiter=',')
            datalist = list(datareader)

            # Acquire number of rows and columns
            number_of_rows = self.instance.setup.assay_layout.device.number_of_rows
            number_of_columns = self.instance.setup.assay_layout.device.number_of_columns

            # Tedious way of getting timeunit; probably should refactor
            readout_time_unit = PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit

            validate_plate_readout_file(
                upload_type,
                assays,
                features,
                assay_feature_to_unit,
                datalist,
                number_of_rows,
                number_of_columns,
                readout_time_unit
            )

def validate_chip_readout_file(
    headers,
    datalist,
    assays,
    short_names,
    readout_time_unit,
    sheet=''
):
    # All unique rows based on ('assay_id', 'field_id', 'elapsed_time')
    unique = {}

    # Read headers going onward
    for line in datalist[headers:]:
        # Set line to ignore QC and all after
        line = line[:6]

        # Some lines may not be long enough (have sufficient commas), ignore such lines
        # Some lines may be empty or incomplete, ignore these as well
        if len(line) < 6 or not all(line):
            continue

        time = line[0]
        time_unit = line[1].strip().lower()
        assay = line[2].upper()
        field = line[3]
        val = line[4]
        val_unit = line[5].strip()
        # Raise error when an assay does not exist
        if assay not in assays and assay not in short_names:
            raise forms.ValidationError(
                sheet + 'No assay with the name "%s" exists; please change your file or add this assay' % assay)
        # Raise error if val_unit not equal to one listed in ACRA
        if val_unit != assays.get(assay, '') and val_unit != short_names.get(assay, ''):
            if assay in assays:
                raise forms.ValidationError(
                    sheet + 'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, assays.get(assay, '')))
            else:
                raise forms.ValidationError(
                    sheet + 'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, short_names.get(assay, '')))
        # Fail if time unit does not match
        # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
        if time_unit[0] != readout_time_unit[0]:
            raise forms.ValidationError(
                sheet + 'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (time_unit, readout_time_unit))
        if (time,assay,field) not in unique:
            unique.update({(time,assay,field):True})
        else:
            raise forms.ValidationError(
                sheet + 'File contains duplicate reading %s' % str((time,assay,field)))
        # Check every value to make sure it can resolve to a float
        try:
            # Keep empty strings, though they technically can not be converted to floats
            if val != '':
                float(val)
        except:
            raise forms.ValidationError(
                    sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(val))


class AssayChipReadoutInlineFormset(CloneableBaseInlineFormSet):
    def __init__(self,*args,**kwargs):
        super (AssayChipReadoutInlineFormset,self).__init__(*args,**kwargs)
        unit_queryset = PhysicalUnits.objects.filter(availability__contains='readout').order_by('base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['readout_unit'].queryset = unit_queryset

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # Throw error if headers is not valid
        try:
            headers = int(self.data.get('headers','')) if self.data.get('headers') else 0
        except:
            raise forms.ValidationError('Please make number of headers a valid number.')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Dic of assay names from inline with respective unit as value
        assays = {}
        short_names = {}
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    unit = form.cleaned_data.get('readout_unit').unit
                    if assay_name not in assays:
                        assays.update({assay_name:unit})
                        short_names.update({assay_short_name:unit})
                    else:
                        raise forms.ValidationError(
                            'Duplicate assays are not permitted; please blank out or change the duplicate')
            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

        # If there is already a file in the database and it is not being replaced or cleared (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:
            new_time_unit = self.instance.timeunit
            old_time_unit = AssayChipReadout.objects.get(id=self.instance.id).timeunit

            # Fail if time unit does not match
            if new_time_unit != old_time_unit:
                raise forms.ValidationError(
                    'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (new_time_unit, old_time_unit))

            saved_data = AssayChipRawData.objects.filter(assay_chip_id=self.instance).prefetch_related('assay_id')

            for raw in saved_data:

                assay = raw.assay_id.assay_id.assay_name.upper()
                val_unit = raw.assay_id.readout_unit.unit

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
                # Raise error if val_unit not equal to one listed in ACRA
                if val_unit != assays.get(assay, ''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"' % (val_unit, assays.get(assay, '')))

        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file','')

            datareader = csv.reader(test_file, delimiter=',')
            datalist = list(datareader)

            # Tedious way of getting timeunit; probably should refactor
            readout_time_unit = PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit

            validate_chip_readout_file(
                headers,
                datalist,
                assays,
                short_names,
                readout_time_unit
            )

def get_bulk_datalist(sheet):
    # Get datalist
    datalist = []

    # Exclude first row (the header)
    for row_index in range(1,sheet.nrows):
        datalist.append([str(value) for value in sheet.row_values(row_index)])

    return datalist


class ReadoutBulkUploadForm(forms.ModelForm):

    bulk_file = forms.FileField()

    class Meta(object):
        model = AssayRun
        fields = ('bulk_file',)

    def clean_bulk_file(self):
        data = super(ReadoutBulkUploadForm, self).clean()

        # Get the study in question
        study = self.instance

        test_file = data.get('bulk_file','')

        if not test_file:
            raise forms.ValidationError('No file was not supplied.')

        file_data = test_file.file.read()

        try:
            excel_file = xlrd.open_workbook(file_contents=file_data)

        except:
            raise forms.ValidationError('The given file does not appear to be a properly formatted Excel file.')

        # For the moment, just have headers be equal to one?
        headers = 1
        sheet_names = excel_file.sheet_names()

        for index, sheet in enumerate(excel_file.sheets()):
            sheet_name = sheet_names[index]

            # Skip sheets without anything
            if sheet.nrows < 1:
                continue

            # Get the header row
            header = sheet.row_values(0)
            # Upper to ignore case
            chip_or_plate_cell = str(header[0]).upper()

            if not chip_or_plate_cell or 'CHIP' not in chip_or_plate_cell and 'PLATE' not in chip_or_plate_cell:
                raise forms.ValidationError(
                    'The sheet "{}" does not specify whether it is for a chip or a plate.'.format(sheet_name)
                )

            # If ambiguous whether it is chip or plate
            if 'CHIP' in chip_or_plate_cell and 'PLATE' in chip_or_plate_cell:
                raise forms.ValidationError(
                    'The sheet "{}" specifies both chip and plate in its first cell.'.format(sheet_name)
                )

            # Get the listed setup
            if type(header[1]) == float:
                setup = str(int(header[1]))
            else:
                setup = str(header[1])

            # Get datalist
            datalist = get_bulk_datalist(sheet)

            # If chip and success thus far
            if 'CHIP' in chip_or_plate_cell:
                readout = AssayChipReadout.objects.filter(chip_setup__assay_run_id=study, chip_setup__assay_chip_id=setup)

                if not readout:
                    raise forms.ValidationError(
                        'No chip readout for the barcode/ID "{}" exists for this study.'.format(setup)
                    )

                # Get the actual readout object
                readout = readout[0]

                # Get readout time unit
                readout_time_unit = readout.timeunit.unit

                # Get assay chip readout assays for readout
                ACRA = AssayChipReadoutAssay.objects.filter(readout_id=readout)

                assays = {}
                short_names = {}

                # Get long and short assay names
                # Make sure they are upper
                for assay in ACRA:
                    assays.update({assay.assay_id.assay_name.upper(): assay.readout_unit.unit})
                    short_names.update({assay.assay_id.assay_short_name.upper(): assay.readout_unit.unit})

                # Validate this sheet
                validate_chip_readout_file(
                    headers,
                    datalist,
                    assays,
                    short_names,
                    readout_time_unit,
                    'Sheet "' + sheet_name + '": '
                )

            # If plate and success thus far
            else:
                readout = AssayPlateReadout.objects.filter(setup__assay_run_id=study, setup__assay_plate_id=setup)

                if not readout:
                    raise forms.ValidationError(
                        'No plate readout for the barcode/ID "{}" exists for this study.'.format(setup)
                    )

                # Get the actual readout object
                readout = readout[0]

                upload_type = str(header[3]).upper()

                if not upload_type or ('TAB' not in upload_type and 'BLOCK' not in upload_type):
                    raise forms.ValidationError(
                        'Sheet "{}" does not properly specify Tabular or Block format.'.format(sheet_name)
                    )

                if 'BLOCK' in upload_type:
                    upload_type = 'Block'

                else:
                    upload_type = 'Tabular'

                # Get readout time unit
                readout_time_unit = readout.timeunit.unit

                # Get number of rows and number of columns
                number_of_rows = readout.setup.assay_layout.device.number_of_rows
                number_of_columns = readout.setup.assay_layout.device.number_of_columns

                # Get assay plate readout assays for readout
                APRA = AssayPlateReadoutAssay.objects.filter(readout_id=readout)

                # TODO REVIEW
                assays = {}
                features = {}
                assay_feature_to_unit = {}

                # Get long and short assay names
                for assay in APRA:
                    assay_name = assay.assay_id.assay_name.upper()
                    assay_short_name = assay.assay_id.assay_short_name.upper()
                    feature = assay.feature
                    readout_unit = assay.readout_unit.unit
                    # Add feature
                    features.update({feature:True})
                    # Normal assay name
                    assays.update({assay_name:True})
                    assay_feature_to_unit.update({(assay_name, feature): readout_unit})
                    # Short assay name
                    assays.update({assay_short_name:True})
                    assay_feature_to_unit.update({(assay_short_name, feature): readout_unit})


                validate_plate_readout_file(
                    upload_type,
                    assays,
                    features,
                    assay_feature_to_unit,
                    datalist,
                    number_of_rows,
                    number_of_columns,
                    readout_time_unit,
                    'Sheet "' + sheet_name + '": '
                )

        return file_data

import csv

from django import forms
from django.forms.models import BaseInlineFormSet
from assays.models import *
from compounds.models import Compound
from mps.forms import SignOffMixin
# Use regular expressions for a string split at one point
import re
import string
import xlrd

from chardet.universaldetector import UniversalDetector

# TODO REFACTOR WHITTLING TO BE HERE IN LIEU OF VIEW
# TODO REFACTOR FK QUERYSETS TO AVOID N+1

from mps.settings import TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')
# Excluding restricted is likewise useful
restricted = ('restricted',)
# Group
group = ('group',)

# Overwrite options
OVERWRITE_OPTIONS = forms.ChoiceField(
    choices=(
        ('keep_conflicting_data', 'Keep Confilicting Data as Replicate'),
        ('mark_conflicting_data', 'Mark Conflicting Data'),
        ('mark_all_old_data', 'Mark All Old Data'),
        ('delete_conflicting_data', 'Delete Conflicting Data'),
        ('delete_all_old_data', 'Delete All Old Data')
    ),
    initial='Keep Confilicting Data as Replicate'
)

def charset_detect(in_file, chunk_size=4096):
    """Use chardet library to detect what encoding is being used"""
    in_file.seek(0)
    chardet_detector = UniversalDetector()
    chardet_detector.reset()
    while 1:
        chunk = in_file.read(chunk_size)
        if not chunk:
            break
        chardet_detector.feed(chunk)
        if chardet_detector.done:
            break
    chardet_detector.close()
    in_file.seek(0)
    return chardet_detector.result


def unicode_csv_reader(in_file, dialect=csv.excel, **kwargs):
    """Returns the contents of a csv in unicode"""
    chardet_results = charset_detect(in_file)
    encoding = chardet_results.get('encoding')
    csv_reader = csv.reader(in_file, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell.decode(encoding)) for cell in row]


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


class AssayRunForm(SignOffMixin, forms.ModelForm):
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
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        exclude = tracking

    def clean(self):
        """Checks for at least one study type and deformed assay_run_ids"""

        # clean the form data, before validation
        data = super(AssayRunForm, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')

        if data['assay_run_id'].startswith('-'):
            raise forms.ValidationError('Error with assay_run_id; please try again')


class StudySupportingDataInlineFormset(BaseInlineFormSet):
    """Form for Study Supporting Data (as part of an inline)"""
    class Meta(object):
        model = StudySupportingData
        exclude = ('',)


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
    overwrite_option = OVERWRITE_OPTIONS

    def __init__(self, study, current, *args, **kwargs):
        """Init the Chip Readout Form

        Parameters:
        study -- the study the readout is from (to filter setup dropdown)
        current -- the currently selected setup (if the Readout is being updated)

        Additional fields (not part of model):
        headers -- specifies the number of header lines in the uploaded csv
        """
        super(AssayChipReadoutForm, self).__init__(*args, **kwargs)
        self.fields['timeunit'].queryset = PhysicalUnits.objects.filter(
            unit_type__unit_type='Time'
        ).order_by('scale_factor')
        exclude_list = AssayChipReadout.objects.filter(chip_setup__isnull=False).values_list('chip_setup', flat=True)
        setups = AssayChipSetup.objects.filter(assay_run_id=study).prefetch_related(
            'assay_run_id', 'device',
            'compound', 'unit',
            'created_by').exclude(id__in=list(set(exclude_list)))
        if current:
            setups = setups | AssayChipSetup.objects.filter(pk=current)
        self.fields['chip_setup'].queryset = setups

    # Specifies the number of headers in the uploaded csv
    headers = forms.CharField(required=True, initial=1)

    class Meta(object):
        model = AssayChipReadout
        widgets = {
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'treatment_time_length': forms.NumberInput(attrs={'style': 'width:174px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = group + tracking + restricted

    # Set chip setup to unique instead of throwing error in validation


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
        self.fields['device'].queryset = Microdevice.objects.filter(device_type='chip')

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
        super(forms.ModelForm, self).clean()

        # Make sure the barcode/ID is unique in the study
        if AssayChipSetup.objects.filter(
                assay_run_id=self.instance.assay_run_id,
                assay_chip_id=self.cleaned_data.get('assay_chip_id')
        ).exclude(id=self.instance.id):
            raise forms.ValidationError({'assay_chip_id': ['ID/Barcode must be unique within study.']})

        # Check to see if compound data is complete if: 1.) compound test type 2.) compound is selected
        current_type = self.cleaned_data.get('chip_test_type', '')
        compound = self.cleaned_data.get('compound', '')
        concentration = self.cleaned_data.get('concentration', '')
        unit = self.cleaned_data.get('unit', '')
        if current_type == 'compound' and not all([compound, concentration, unit]) \
                or (compound and not all([concentration, unit])):
            raise forms.ValidationError('Please complete all data for compound.')

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
        super(ChipTestResultInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__contains='test'
        ).order_by('base_unit', 'scale_factor')
        for form in self.forms:
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
    concunit -- dropdown for selecting a concentration unit for the Layout map
    """
    def __init__(self, groups, *args, **kwargs):
        super(AssayLayoutForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = groups
        self.fields['device'].queryset = Microdevice.objects.filter(
            device_type='plate'
        )

    compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    concunit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )

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
        current -- the current Readout (if the Readout is being updated)

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

    upload_type = forms.ChoiceField(choices=(('Block', 'Block'), ('Tabular', 'Tabular')))
    overwrite_option = OVERWRITE_OPTIONS

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
            availability__contains='test'
        ).order_by('base_unit', 'scale_factor')
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
            return {'value': sliced_value, 'quality': 'X'}

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

    return (row_label, column_label)


# def get_tabular_data(datalist, plate_details, sheet=''):
#     """Consolidated way for acquiring tabular data"""
#     pass


# def get_block_data(datalist, plate_details, sheet=''):
#     """Consolidated way for acquiring block data"""
#     pass


def validate_plate_readout_file(
        upload_type,
        datalist,
        plate_details,
        sheet=''
):
    """Validates a Plate Readout CSV file"""
    if upload_type == 'Block':
        # Number of assays found
        assays_found = 0
        # Number of data blocks found
        data_blocks_found = 0

        number_of_rows = u''
        number_of_columns = u''

        for row_index, line in enumerate(datalist):
            # If line is blank, skip it
            if not line:
                continue

            # If this line is a header
            # NOTE THAT ASSAYS AND FEATURES ARE IN PAIRS
            # Headers should look like:
            # PLATE ID, {{}}, ASSAY, {{}}, FEATURE, {{}}, READOUT UNIT, {{}}, TIME, {{}}. TIME UNIT, {{}}
            if 'PLATE' in line[0].upper().strip():
                # Throw error if header too short
                if len(line) < 8:
                    raise forms.ValidationError(
                        sheet + 'Header row: {} is too short'.format(line))

                plate_id = line[1]

                if plate_id not in plate_details:
                    raise forms.ValidationError(
                        sheet + 'The Plate ID "{0}" was not recognized.'
                                ' Make sure a readout for this plate exists.'.format(plate_id)
                    )

                # Set to correct set of assays, features, and pairs
                assays = plate_details.get(plate_id, {}).get('assays', {})
                features = plate_details.get(plate_id, {}).get('features', {})
                assay_feature_to_unit = plate_details.get(plate_id, {}).get('assay_feature_to_unit', {})

                readout_time_unit = plate_details.get(plate_id, {}).get('timeunit', 'X')
                number_of_rows = plate_details.get(plate_id, {}).get('number_of_rows', 0)
                number_of_columns = plate_details.get(plate_id, {}).get('number_of_columns', 0)

                assay = line[3].upper().strip()
                feature = line[5]

                assays_found += 1

                val_unit = line[7].strip()

                # TODO OLD
                # TODO REVISE
                # Raise error if feature does not exist
                if feature not in features:
                    raise forms.ValidationError(
                        sheet + 'Plate-%s: No feature with the name "%s" exists; '
                                'please change your file or add this feature'
                        % (plate_id, feature)
                    )
                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        sheet + 'Plate-%s: '
                                'No assay with the name "%s" exists; please change your file or add this assay'
                        % (plate_id, assay)
                    )
                # Raise error if assay-feature pair is not listed
                elif (assay, feature) not in assay_feature_to_unit:
                    raise forms.ValidationError(
                        sheet + 'Plate-{0}: The assay-feature pair "{1}-{2}" was not recognized'.format(
                            plate_id,
                            assay,
                            feature
                        )
                    )
                # Raise error if val_unit not equal to one listed in APRA
                elif val_unit != assay_feature_to_unit.get((assay, feature), ''):
                    raise forms.ValidationError(
                        sheet + 'Plate-%s: '
                                'The value unit "%s" does not correspond with the selected readout unit of "%s"'
                        % (plate_id, val_unit, assay_feature_to_unit.get((assay, feature), ''))
                    )

                # Fail if time given without time units
                if len(line) < 12 and len(line) > 8 and any(line[8:]):
                    raise forms.ValidationError(
                        sheet + 'Header row: {} improperly configured'.format(line))

                if len(line) >= 12 and any(line[8:]):
                    time = line[9].strip()
                    time_unit = line[11].strip()

                    # Fail if time is not numeric
                    try:
                        if time != '':
                            float(time)
                    except:
                        raise forms.ValidationError(
                            sheet + 'The time "{}" is invalid. Please only enter numeric times'.format(time))

                    # Fail if time unit does not match
                    # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                    if time_unit and (time_unit[0] != readout_time_unit[0]):
                        raise forms.ValidationError(
                            sheet +
                            'Plate-{0}: The time unit "{1}" does not correspond with '
                            'the selected readout time unit of "{2}"'.format(plate_id, time_unit, readout_time_unit)
                        )

            # Otherwise the line contains datapoints for the current assay
            else:
                # TODO REVISE HOW DATA_BLOCKS ARE ACQUIRED
                if data_blocks_found == 0 or (row_index-assays_found) % number_of_rows == 0:
                    data_blocks_found += 1

                # This should handle blocks that have too many rows or do not have a header
                # Don't throw an error if there are not any meaningful values
                if data_blocks_found > assays_found and any(line[:number_of_columns]):
                    raise forms.ValidationError(
                        sheet + 'All plate data must have an assay associated with it. Please add a header line '
                                'and/or make sure there are no blank lines between blocks')

                # TODO NOTE: THIS IS DEPENDENT ON THE LOCATION OF THE TEMPLATE'S VALIDATION CELLS
                # TODO AS A RESULT,
                trimmed_line = [val for val in line[:TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX] if val]

                # This is to deal with an EXCESS of columns
                if len(trimmed_line) > number_of_columns:
                    raise forms.ValidationError(
                        sheet + "Plate-{0}: The number of columns does not correspond "
                                "with the device's dimensions:{1}".format(plate_id, line)
                    )

                # For every value in the line (breaking at number of columns)
                for value in line[:number_of_columns]:
                    # Check every value to make sure it can resolve to a float
                    # Keep empty strings, though they technically can not be converted to floats
                    if value != '':
                        processed_value = process_readout_value(value)

                        if processed_value is None:
                            raise forms.ValidationError(
                                sheet + 'The value "%s" is invalid; please make sure all values are numerical'
                                % str(value)
                            )
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
        # All lines that do not have anything in their first 8 cells are purged
        datalist = [row for row in datalist if any(row[:8])]
        # The first line SHOULD be the header
        header = datalist[0]

        # TODO REVISE
        if len(header) < 6:
            raise forms.ValidationError(
                sheet + 'Please specify Plate ID, Well, Assay, Feature, Feature Unit, [Time, Time Unit], '
                        'and Value in header.')
        if 'TIME' in header[5].upper() and (len(header) < 8 or 'UNIT' not in header[6].upper()):
            raise forms.ValidationError(
                sheet + 'If you are specifying time, you must also specify the time unit')

        if 'TIME' in header[5].upper() and 'UNIT' in header[6].upper():
            time_specified = True
        else:
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # Plate ID given
            plate_id = row[0]

            if plate_id not in plate_details:
                raise forms.ValidationError(
                    sheet + 'The Plate ID "{0}" was not recognized.'
                            ' Make sure a readout for this plate exists.'.format(plate_id)
                )

            # Set to correct set of assays, features, and pairs
            assays = plate_details.get(plate_id, {}).get('assays', {})
            features = plate_details.get(plate_id, {}).get('features', {})
            assay_feature_to_unit = plate_details.get(plate_id, {}).get('assay_feature_to_unit', {})

            readout_time_unit = plate_details.get(plate_id, {}).get('timeunit', 'X')
            number_of_rows = plate_details.get(plate_id, {}).get('number_of_rows', 0)
            number_of_columns = plate_details.get(plate_id, {}).get('number_of_columns', 0)

            # The well identifier given
            well = row[1]
            assay = row[2].upper().strip()
            feature = row[3]
            val_unit = row[4]

            # Raise error if feature does not exist
            if feature not in features:
                raise forms.ValidationError(
                    sheet + 'Plate-%s: '
                            'No feature with the name "%s" exists; please change your file or add this feature'
                    % (plate_id, feature)
                )
            # Raise error when an assay does not exist
            elif assay not in assays:
                raise forms.ValidationError(
                    sheet + 'Plate-%s: No assay with the name "%s" exists; please change your file or add this assay'
                    % (plate_id, assay)
                )
            # Raise error if assay-feature pair is not listed
            elif (assay, feature) not in assay_feature_to_unit:
                raise forms.ValidationError(
                    sheet + 'Plate-{0}: The assay-feature pair "{1}-{2}" was not recognized'.format(
                        plate_id, assay, feature
                    )
                )
            # Raise error if val_unit not equal to one listed in APRA
            elif val_unit != assay_feature_to_unit.get((assay, feature), ''):
                raise forms.ValidationError(
                    sheet + 'Plate-%s: The value unit "%s" does not correspond with the selected readout unit of "%s"'
                    % (plate_id, val_unit, assay_feature_to_unit.get((assay, feature), ''))
                )

            # If time is specified
            if time_specified:
                time = row[5]
                time_unit = row[6].strip().lower()
                value = row[7]

                # Check time unit
                # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                if not time_unit or (time_unit[0] != readout_time_unit[0]):
                    raise forms.ValidationError(
                        sheet + 'Plate-%s: The time unit "%s" does not correspond with the selected readout time unit '
                                'of "%s"'
                        % (plate_id, time_unit, readout_time_unit)
                    )

                # Check time
                try:
                    float(time)
                except:
                    raise forms.ValidationError(
                        sheet + 'Error while parsing time "{}"'.format(time))

            # If time is not specified
            else:
                value = row[5]

            # Check if well id is valid
            try:
                # Split the well into alphabetical and numeric
                row_label, column_label = get_row_and_column(well, 0)

                if row_label > number_of_rows:
                    raise forms.ValidationError(
                        sheet + "Plate-{0}: The number of rows does not correspond with the device's dimensions".format(
                            plate_id
                        )
                    )

                if column_label > number_of_columns:
                    raise forms.ValidationError(
                        sheet + "Plate-{0}: The number of columns does not correspond "
                        "with the device's dimensions".format(
                            plate_id
                        )
                    )

            except:
                raise forms.ValidationError(
                    sheet + 'Plate-{0}: Error parsing the well ID: {1}'.format(plate_id, well)
                )

            # Check every value to make sure it can resolve to a float
            # Keep empty strings, though they technically can not be converted to floats
            if value != '':
                processed_value = process_readout_value(value)
                if processed_value is None:
                    raise forms.ValidationError(
                        sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(value))


class AssayPlateReadoutInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline for Assay Plate Readout Assays (APRA)"""
    def __init__(self, *args, **kwargs):
        """Init APRA inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayPlateReadoutInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__contains='readout'
        ).order_by('base_unit', 'scale_factor')
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
        setup_id = AssayPlateSetup.objects.get(pk=setup_pk).assay_plate_id

        # TODO REVIEW
        # Get upload type
        upload_type = self.data.get('upload_type')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        plate_details = get_plate_details(self)

        assays = plate_details.get(setup_id, {}).get('assays', {})
        features = plate_details.get(setup_id, {}).get('features', {})
        assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

        # If there is already a file in the database and it is not being replaced or cleared
        # (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:
            saved_data = AssayReadout.objects.filter(assay_device_readout=self.instance).prefetch_related('assay')

            for raw in saved_data:
                assay = raw.assay.assay_id.assay_name.upper()
                val_unit = raw.assay.readout_unit.unit
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
                # Raise error if val_unit not equal to one listed in APRA
                # Note use of features to unit (unlike chips)
                if val_unit != assay_feature_to_unit.get((assay, feature), ''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"'
                        % (val_unit, assay_feature_to_unit.get((assay, feature), ''))
                    )

        # TODO what shall a uniqueness check look like?
        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file', '')
            file_data = process_file(self, test_file, plate_details=plate_details, upload_type=upload_type)
            return file_data


def validate_chip_readout_file(
    headers,
    datalist,
    chip_details,
    sheet=''
):
    """Validates CSV Uploads for Chip Readouts"""
    # A list of errors
    errors = []

    # Confirm that there is only one chip_id given if this is not a bulk upload
    if not sheet:
        for line in datalist[headers:]:
            if chip_details and line and line[0] not in chip_details:
                errors.append(
                    'Chip ID "{0}" does not match current Chip ID. '
                    'You cannot upload data for multiple chips in this interface. '
                    'If you want to upload multiple set of data, '
                    'use the "Upload Excel File of Readout Data" interface instead. '
                    .format(line[0])
                )

    # Likely to change
    # Duplicates are now permitted
    # All unique rows based on ('chip_id', 'assay_id', 'field_id', 'elapsed_time')
    # unique = {}

    # Read headers going onward
    for line in datalist[headers:]:
        # Set line to ignore QC and all after
        line = line[:7]

        # Some lines may not be long enough (have sufficient commas), ignore such lines
        # Some lines may be empty or incomplete, ignore these as well
        if not valid_chip_row(line):
            continue

        chip_id = line[0]
        time = line[1]
        time_unit = line[2].strip().lower()
        assay = line[3].upper()
        # Not currently used
        # current_object = line[4]
        val = line[5]
        val_unit = line[6].strip()

        if chip_id not in chip_details:
            errors.append(
                sheet + 'No Chip with the ID "{0}" exists; please change your file or add this assay.'.format(chip_id)
            )

        assays = chip_details.get(chip_id, {}).get('assays', {})
        readout_time_unit = chip_details.get(chip_id, {}).get('timeunit', 'X')

        # Raise error when an assay does not exist
        if assay not in assays:
            errors.append(
                sheet + 'Chip-%s: No assay with the name "%s" exists; please change your file or add this assay'
                % (chip_id, assay)
            )
        # Raise error if val_unit not equal to one listed in ACRA
        elif val_unit != assays.get(assay, ''):
            errors.append(
                sheet + 'Chip-%s: The value unit "%s" does not correspond with the selected readout unit of "%s"'
                % (chip_id, val_unit, assays.get(assay, ''))
            )

        # Fail if time unit does not match
        # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
        if not time_unit or (time_unit[0] != readout_time_unit[0]):
            errors.append(
                sheet + 'Chip-%s: The time unit "%s" does not correspond with the selected readout time unit of "%s"'
                % (chip_id, time_unit, readout_time_unit)
            )
        # if (chip_id, time, assay, current_object) not in unique:
        #     unique.update({(chip_id, time, assay, current_object): True})
        # else:
        #     raise forms.ValidationError(
        #         sheet + 'File contains duplicate reading %s' % str((chip_id, time, assay, current_object))
        #     )
        # Check every value to make sure it can resolve to a float
        try:
            # Keep empty strings, though they technically can not be converted to floats
            if val != '':
                float(val)
        except:
            errors.append(
                sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(val)
            )

        # Check to make certain the time is a valid float
        try:
            float(time)

        except:
            errors.append(
                sheet + 'The time "%s" is invalid; please make sure all times are numerical' % str(time)
            )

    if errors:
        raise forms.ValidationError(errors)


class AssayChipReadoutInlineFormset(CloneableBaseInlineFormSet):
    """Frontend Inline for Chip Readout Assays (ACRA)"""
    def __init__(self, *args, **kwargs):
        """Init ACRA Inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayChipReadoutInlineFormset, self).__init__(*args, **kwargs)
        unit_queryset = PhysicalUnits.objects.filter(
            availability__contains='readout'
        ).order_by('base_unit', 'scale_factor')
        for form in self.forms:
            form.fields['readout_unit'].queryset = unit_queryset

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""
        if self.data.get('chip_setup', ''):
            setup_pk = int(self.data.get('chip_setup'))
        else:
            raise forms.ValidationError('Please choose a chip setup.')
        setup_id = AssayChipSetup.objects.get(pk=setup_pk).assay_chip_id

        # Throw error if headers is not valid
        try:
            headers = int(self.data.get('headers', '')) if self.data.get('headers', '') else 0
        except:
            raise forms.ValidationError('Please make number of headers a valid number.')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        chip_details = get_chip_details(self)

        assays = chip_details.get(setup_id, {}).get('assays', {})

        # If there is already a file in the database and it is not being replaced or cleared
        #  (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:
            new_time_unit = self.instance.timeunit
            old_time_unit = AssayChipReadout.objects.get(id=self.instance.id).timeunit

            # Fail if time unit does not match
            if new_time_unit != old_time_unit:
                raise forms.ValidationError(
                    'The time unit "%s" does not correspond with the selected readout time unit of "%s"'
                    % (new_time_unit, old_time_unit))

            saved_data = AssayChipRawData.objects.filter(assay_chip_id=self.instance).prefetch_related(
                'assay_id__assay_id'
            )

            for raw in saved_data:

                assay = raw.assay_id.assay_id.assay_name.upper()
                val_unit = raw.assay_id.readout_unit.unit

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
                # Raise error if val_unit not equal to one listed in ACRA
                elif val_unit != assays.get(assay, ''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"'
                        % (val_unit, assays.get(assay, ''))
                    )

        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file', '')
            file_data = process_file(self, test_file, headers=headers, chip_details=chip_details, plate_details=None)
            return file_data


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


# TODO FIX ORDER OF ARGUMENTS
def get_sheet_type(header, sheet_name=''):
    """Get the sheet type from a given header (chip, tabular, block, or unknown)

    Param:
    header - the header in question
    sheet_name - the sheet name for reporting errors (default empty string)
    """
    # From the header we need to discern the type of upload
    # Check if chip
    if 'CHIP' in header[0].upper() and 'ASSAY' in header[3].upper():
        sheet_type = 'Chip'

    # Check if plate tabular
    elif 'PLATE' in header[0].upper() and 'WELL' in header[1].upper() and 'ASSAY' in header[2].upper()\
            and 'FEATURE' in header[3].upper() and 'UNIT' in header[4].upper():
        sheet_type = 'Tabular'

    # Check if plate block
    elif 'PLATE' in header[0].upper() and 'ASSAY' in header[2].upper() and 'FEATURE' in header[4].upper()\
            and 'UNIT' in header[6].upper():
        sheet_type = 'Block'

    # Throw error if can not be determined
    else:
        # For if we decide not to throw errors
        sheet_type = 'Unknown'
        raise forms.ValidationError(
            'The header of sheet "{0}" was not recognized.'.format(sheet_name)
        )

    return sheet_type


def get_chip_details(self, study=None, readout=None):
    """Get the assays and units as a dictionary with chip ID as the key

    Params:
    self - the form in question
    study - the study in question
    readout - the readout in question
    """
    if study:
        readouts = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id=study
        ).prefetch_related(
            'chip_setup__assay_run_id'
        )
    elif readout:
        readouts = AssayChipReadout.objects.filter(pk=readout.id).prefetch_related(
            'chip_setup__assay_run_id'
        )
    else:
        readouts = None

    chip_details = {}

    # If this is for a bulk upload
    if readouts:
        for readout in readouts:
            setup_id = readout.chip_setup.assay_chip_id

            chip_details.update({setup_id: {
                'assays': {},
                'timeunit': None,
            }})
            current_assays = chip_details.get(setup_id, {}).get('assays', {})

            timeunit = readout.timeunit.unit
            chip_details.get(setup_id, {}).update({'timeunit': timeunit})

            assays = AssayChipReadoutAssay.objects.filter(
                readout_id=readout
            ).prefetch_related(
                'readout_id',
                'readout_unit',
                'assay_id'
            )

            for assay in assays:
                readout_unit = assay.readout_unit.unit
                assay_name = assay.assay_id.assay_name.upper()
                assay_short_name = assay.assay_id.assay_short_name.upper()

                current_assays.update({
                    assay_name: readout_unit,
                    assay_short_name: readout_unit
                })
    # If this is for an individual upload
    else:
        if self.data.get('chip_setup', ''):
            setup_pk = int(self.data.get('chip_setup'))
        else:
            raise forms.ValidationError('Please choose a chip setup.')
        setup_id = AssayChipSetup.objects.get(pk=setup_pk).assay_chip_id

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Dic of assay names from inline with respective unit as value
        chip_details.update({setup_id: {
            'assays': {},
             # Tedious way of getting timeunit; probably should refactor
            'timeunit': PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit,
        }})

        current_assays = chip_details.get(setup_id, {}).get('assays', {})
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    unit = form.cleaned_data.get('readout_unit').unit
                    if assay_name not in current_assays:
                        current_assays.update({
                            assay_name: unit,
                            assay_short_name: unit
                        })
                    else:
                        raise forms.ValidationError(
                            'Duplicate assays are not permitted; please blank out or change the duplicate')
            except AttributeError:
                pass
        if len(current_assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

    return chip_details


def get_plate_details(self, study=None, readout=None):
    """Get the assays and units as a dictionary with plate ID as the key

    Params:
    self - the form in question
    study - the study in question
    readout - the readout in question
    """
    if study:
        readouts = AssayPlateReadout.objects.filter(
            setup__assay_run_id=study
        ).prefetch_related(
            'setup__assay_run_id'
        )
    elif readout:
        readouts = AssayPlateReadout.objects.filter(
            pk=readout.id
        ).prefetch_related(
            'setup__assay_run_id'
        )
    else:
        readouts = None

    plate_details = {}

    # If this is for a bulk upload
    if readouts:
        for readout in readouts:
            setup_id = readout.setup.assay_plate_id

            plate_details.update({
                setup_id: {
                    'assays': {},
                    'features': {},
                    'assay_feature_to_unit': {},
                    'timeunit': readout.timeunit.unit,
                    'number_of_rows': readout.setup.assay_layout.device.number_of_rows,
                    'number_of_columns': readout.setup.assay_layout.device.number_of_columns
                }
            })

            current_assays = plate_details.get(setup_id, {}).get('assays', {})
            current_features = plate_details.get(setup_id, {}).get('features', {})
            current_assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

            assays = AssayPlateReadoutAssay.objects.filter(
                readout_id=readout
            ).prefetch_related(
                'readout_unit',
                'assay_id'
            )

            for assay in assays:
                readout_unit = assay.readout_unit.unit
                assay_name = assay.assay_id.assay_name.upper()
                assay_short_name = assay.assay_id.assay_short_name.upper()
                feature = assay.feature

                current_assays.update({
                    assay_name: True,
                    assay_short_name: True
                })

                current_features.update({feature: True})

                current_assay_feature_to_unit.update({
                    (assay_name, feature): readout_unit,
                    (assay_short_name, feature): readout_unit
                })
    # If this is for an individual upload
    else:
        if self.data.get('setup', ''):
            setup_pk = int(self.data.get('setup'))
        else:
            raise forms.ValidationError('Please choose a plate setup.')
        setup_id = AssayPlateSetup.objects.get(pk=setup_pk).assay_plate_id

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        plate_details.update({
            setup_id: {
                'assays': {},
                'features': {},
                'assay_feature_to_unit': {},
                'timeunit': PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit,
                'number_of_rows': self.instance.setup.assay_layout.device.number_of_columns,
                'number_of_columns': self.instance.setup.assay_layout.device.number_of_columns
            }
        })

        features = plate_details.get(setup_id, {}).get('features', {})
        assays = plate_details.get(setup_id, {}).get('assays', {})
        assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    feature = form.cleaned_data.get('feature')
                    readout_unit = form.cleaned_data.get('readout_unit').unit

                    # Add feature
                    features.update({feature: True})
                    # Normal assay name
                    assays.update({
                        assay_name: True,
                        assay_short_name: True
                    })
                    if (assay_name, feature) not in assay_feature_to_unit:
                        assay_feature_to_unit.update({
                            (assay_name, feature): readout_unit,
                            (assay_short_name, feature): readout_unit
                        })
                    else:
                        raise forms.ValidationError('Assay-Feature pairs must be unique.')

            # Do nothing if invalid
            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

    return plate_details


def process_file(self, test_file, headers=1, chip_details=None, plate_details=None, study=None, readout=None, upload_type=None):
    """Get data from a file: returns read data from excel and datalist from csv

    Params:
    self - the form in question
    test_file - the file in question
    headers - the number of header rows (default=1)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    study - the study in question (optional)
    readout - the readout in question (optional)
    upload_type - upload type for plates (optional)
    """
    try:
        file_data = test_file.read()
        excel_file = xlrd.open_workbook(file_contents=file_data)
        validate_excel_file(self, excel_file, headers, study, readout,
                            chip_details, plate_details, upload_type)

        return file_data

    # If this fails, it isn't an Excel file, so try reading it as text
    except xlrd.XLRDError:
        datareader = unicode_csv_reader(test_file, delimiter=',')
        datalist = list(datareader)
        # raise forms.ValidationError('The given file does not appear to be a properly formatted Excel file.')
        validate_csv_file(self, datalist, study, readout,
                          chip_details, plate_details, headers, upload_type)

        return datalist


# TODO NEEDS REVISION
def validate_excel_file(self, excel_file, headers=1, study=None, readout=None,
                        chip_details=None, plate_details=None, upload_type=None):
    """Validate an excel file

    Params:
    self - the form in question
    excel_file - the excel_file as an xlrd object
    headers - the number of header rows (default=1)
    study - the study in question (optional)
    readout - the readout in question (optional)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    upload_type - upload type for plates (optional)
    """
    sheet_names = excel_file.sheet_names()

    for index, sheet in enumerate(excel_file.sheets()):
        sheet_name = sheet_names[index]

        # Skip sheets without anything
        if sheet.nrows < 1:
            continue

        # Get datalist
        datalist = get_bulk_datalist(sheet)

        # Get the header row
        header = [unicode(value) for value in sheet.row_values(0)]

        # From the header we need to discern the type of upload
        sheet_type = get_sheet_type(header, sheet_name)

        # If chip
        if sheet_type == 'Chip':
            if not chip_details:
                chip_details = get_chip_details(self, study, readout)

            # Validate this sheet
            validate_chip_readout_file(
                headers,
                datalist,
                chip_details,
                'Sheet "' + sheet_name + '": '
            )
        # If plate
        else:
            if not plate_details:
                plate_details = get_plate_details(self, study, readout)

            if upload_type:
                sheet_type = upload_type

            validate_plate_readout_file(
                sheet_type,
                datalist,
                plate_details,
                'Sheet "' + sheet_name + '": '
            )


# TODO NEEDS REVISION
def validate_csv_file(self, datalist, study=None, readout=None,
                      chip_details=None, plate_details=None, headers=1, upload_type=None):
    """Validates a CSV file

    Params:
    self - the form in question
    datalist - the data as a list of lists
    study - the study in question (optional)
    readout - the readout in question (optional)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    headers - the number of header rows (default=1)
    upload_type - upload type for plates (optional)
    """
    # From the header we need to discern the type of upload
    header = datalist[0]
    sheet_type = get_sheet_type(header, 'CSV')

    if sheet_type == 'Chip':
        if not chip_details:
            chip_details = get_chip_details(self, study, readout)

        validate_chip_readout_file(
            headers,
            datalist,
            chip_details
        )
    else:
        if not plate_details:
            plate_details = get_plate_details(self, study, readout)

        validate_plate_readout_file(
            upload_type,
            datalist,
            plate_details
        )


class ReadoutBulkUploadForm(forms.ModelForm):
    """Form for Bulk Uploads"""
    bulk_file = forms.FileField()

    overwrite_option = OVERWRITE_OPTIONS

    class Meta(object):
        model = AssayRun
        fields = ('bulk_file',)

    def clean_bulk_file(self):
        data = super(ReadoutBulkUploadForm, self).clean()

        # Get the study in question
        study = self.instance

        test_file = data.get('bulk_file', '')

        if not test_file:
            raise forms.ValidationError('No file was supplied.')

        # For the moment, just have headers be equal to one?
        headers = 1

        file_data = process_file(self, test_file, headers=headers, study=study)

        return file_data

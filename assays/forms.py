import datetime
from django import forms
from django.contrib.auth.models import Group
from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
    BaseModelFormSet,
    modelformset_factory,
)
from cellsamples.models import Biosensor
from assays.models import (
    AssayStudyConfiguration,
    AssayStudy,
    AssayStudySupportingData,
    AssayStudyAssay,
    AssayMatrix,
    AssayCategory,
    TEST_TYPE_CHOICES,
    PhysicalUnits,
    AssaySampleLocation,
    AssaySetting,
    AssaySetupCompound,
    AssaySetupCell,
    AssaySetupSetting,
    AssayMatrixItem,
    AssayStudyStakeholder,
    AssayTarget,
    AssayMethod,
    AssayStudyModel,
    AssayStudySet,
    AssayReference,
    AssayStudyReference,
    AssayStudySetReference,
    AssayTarget,
    AssayMeasurementType,
    AssayMethod,
    AssaySetting,
    AssaySupplier,
    AssayCategory,
    AssayPlateReaderMap,
    AssayPlateReaderMapItem,
    AssayPlateReaderMapItemValue,
    AssayPlateReaderMapDataFile,
    AssayPlateReaderMapDataFileBlock,
    assay_plate_reader_time_unit_choices,
    assay_plate_reader_main_well_use_choices,
    assay_plate_reader_blank_well_use_choices,
    assay_plate_reader_map_info_plate_size_choices,
    assay_plate_reader_volume_unit_choices,
    assay_plate_reader_file_delimiter_choices,
    upload_file_location,
)
from compounds.models import Compound, CompoundInstance, CompoundSupplier
from microdevices.models import (
    MicrophysiologyCenter,
    Microdevice,
    OrganModel,
    OrganModelProtocol
)
from mps.forms import SignOffMixin, BootstrapForm, tracking
import string
from captcha.fields import CaptchaField

from .utils import (
    # validate_file,
    # get_chip_details,
    # get_plate_details,
    TIME_CONVERSIONS,
    # EXCLUDED_DATA_POINT_CODE,
    AssayFileProcessor,
    get_user_accessible_studies,
    plate_reader_data_file_process_data,
    CALIBRATION_CURVE_MASTER_DICT,
    calibration_choices,
)

from django.utils import timezone

from mps.templatetags.custom_filters import is_group_admin, filter_groups, ADMIN_SUFFIX

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from mps.settings import MEDIA_ROOT
import ujson as json
import os
import csv
import re

# TODO REFACTOR WHITTLING TO BE HERE IN LIEU OF VIEW
# TODO REFACTOR FK QUERYSETS TO AVOID N+1

# These are all of the tracking fields
# tracking = (
#     'created_by',
#     'created_on',
#     'modified_on',
#     'modified_by',
#     'signed_off_by',
#     'signed_off_date',
#     'locked',
#     'restricted'
# )
# Excluding restricted is likewise useful
restricted = ('restricted',)
# Group
group = ('group',)


def get_dic_for_custom_choice_field(form, filters=None):
    dic = {}

    fields = form.custom_fields
    parent = form.model

    for field in fields:
        model = parent._meta.get_field(field).related_model
        if filters and filters.get(field, None):
            dic.update({
                field: {str(instance.id): instance for instance in model.objects.filter(**filters.get(field))}
            })
        else:
            dic.update({
                field: {str(instance.id): instance for instance in model.objects.all()}
            })

    return dic


# DEPRECATED NO LONGER NEEDED AS CHARFIELDS NOW STRIP AUTOMATICALLY
class ModelFormStripWhiteSpace(BootstrapForm):
    """Strips the whitespace from char and text fields"""
    def clean(self):
        cd = self.cleaned_data
        for field_name, field in list(self.fields.items()):
            if isinstance(field, forms.CharField):
                if self.fields[field_name].required and not cd.get(field_name, None):
                    self.add_error(field_name, "This is a required field.")
                else:
                    cd[field_name] = cd[field_name].strip()

        return super(ModelFormStripWhiteSpace, self).clean()


class ModelFormSplitTime(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super(ModelFormSplitTime, self).__init__(*args, **kwargs)

        for time_unit in list(TIME_CONVERSIONS.keys()):
            if self.fields.get('addition_time', None):
                # Create fields for Days, Hours, Minutes
                self.fields['addition_time_' + time_unit] = forms.FloatField(
                    initial=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'style': 'width:75px;'
                    })
                )
                # Set default
                self.fields['addition_time_' + time_unit].widget.attrs['data-default'] = 0
            if self.fields.get('duration', None):
                self.fields['duration_' + time_unit] = forms.FloatField(
                    initial=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'style': 'width:75px;'
                    })
                )
                # Set default
                self.fields['duration_' + time_unit].widget.attrs['data-default'] = 0

        # Fill additional time
        if self.fields.get('addition_time', None):
            addition_time_in_minutes_remaining = getattr(self.instance, 'addition_time', 0)
            if not addition_time_in_minutes_remaining:
                addition_time_in_minutes_remaining = 0
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                initial_time_for_current_field = int(addition_time_in_minutes_remaining / conversion)
                if initial_time_for_current_field:
                    self.fields['addition_time_' + time_unit].initial = initial_time_for_current_field
                    addition_time_in_minutes_remaining -= initial_time_for_current_field * conversion
            # Add fractions of minutes if necessary
            if addition_time_in_minutes_remaining:
                self.fields['addition_time_minute'].initial += addition_time_in_minutes_remaining

        # Fill duration
        if self.fields.get('duration', None):
            duration_in_minutes_remaining = getattr(self.instance, 'duration', 0)
            if not duration_in_minutes_remaining:
                duration_in_minutes_remaining = 0
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                initial_time_for_current_field = int(duration_in_minutes_remaining / conversion)
                if initial_time_for_current_field:
                    self.fields['duration_' + time_unit].initial = initial_time_for_current_field
                    duration_in_minutes_remaining -= initial_time_for_current_field * conversion
            # Add fractions of minutes if necessary
            if duration_in_minutes_remaining:
                self.fields['duration_minute'].initial += duration_in_minutes_remaining

    def clean(self):
        cleaned_data = super(ModelFormSplitTime, self).clean()

        if cleaned_data and not cleaned_data.get('DELETE', False):
            cleaned_data.update({
                'addition_time': 0,
                'duration': 0
            })
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                cleaned_data.update({
                    'addition_time': cleaned_data.get('addition_time') + cleaned_data.get('addition_time_' + time_unit,
                                                                                          0) * conversion,
                    'duration': cleaned_data.get('duration') + cleaned_data.get('duration_' + time_unit, 0) * conversion
                })

        return cleaned_data


class BaseModelFormSetForcedUniqueness(BaseModelFormSet):
    def clean(self):
        self.validate_unique()

    def validate_unique(self):
        # Collect unique_checks and date_checks to run from all the forms.
        all_unique_checks = set()
        all_date_checks = set()
        forms_to_delete = self.deleted_forms
        valid_forms = [form for form in self.forms if form not in forms_to_delete and form.is_valid()]
        for form in valid_forms:
            # exclude = form._get_validation_exclusions()
            # unique_checks, date_checks = form.instance._get_unique_checks(exclude=exclude)
            unique_checks, date_checks = form.instance._get_unique_checks()
            all_unique_checks = all_unique_checks.union(set(unique_checks))
            all_date_checks = all_date_checks.union(set(date_checks))

        errors = []
        # Do each of the unique checks (unique and unique_together)
        for uclass, unique_check in all_unique_checks:
            seen_data = set()
            for form in valid_forms:
                # PLEASE NOTE: SPECIAL EXCEPTION FOR FORMS WITH NO ID TO AVOID TRIGGERING ID DUPLICATE
                if unique_check == ('id',) and not form.cleaned_data.get('id', ''):
                    # IN POOR TASTE, BUT EXPEDIENT
                    continue

                # get data for each field of each of unique_check
                # PLEASE NOTE THAT THIS GETS ALL FIELDS, EVEN IF NOT IN THE FORM
                row_data = (
                    form.cleaned_data[field] if field in form.cleaned_data else getattr(form.instance, field, None) for field in unique_check
                )

                # Reduce Model instances to their primary key values
                row_data = tuple(d._get_pk_val() if hasattr(d, '_get_pk_val') else d for d in row_data)
                # if row_data and None not in row_data:
                # if we've already seen it then we have a uniqueness failure
                if row_data in seen_data:
                    # poke error messages into the right places and mark
                    # the form as invalid
                    errors.append(self.get_unique_error_message(unique_check))
                    form._errors[NON_FIELD_ERRORS] = self.error_class([self.get_form_error()])
                    # remove the data from the cleaned_data dict since it was invalid
                    for field in unique_check:
                        if field in form.cleaned_data:
                            del form.cleaned_data[field]
                # mark the data as seen
                seen_data.add(row_data)
        # iterate over each of the date checks now
        for date_check in all_date_checks:
            seen_data = set()
            uclass, lookup, field, unique_for = date_check
            for form in valid_forms:
                # see if we have data for both fields
                if (form.cleaned_data and form.cleaned_data[field] is not None and form.cleaned_data[unique_for] is not None):
                    # if it's a date lookup we need to get the data for all the fields
                    if lookup == 'date':
                        date = form.cleaned_data[unique_for]
                        date_data = (date.year, date.month, date.day)
                    # otherwise it's just the attribute on the date/datetime
                    # object
                    else:
                        date_data = (getattr(form.cleaned_data[unique_for], lookup),)
                    data = (form.cleaned_data[field],) + date_data
                    # if we've already seen it then we have a uniqueness failure
                    if data in seen_data:
                        # poke error messages into the right places and mark
                        # the form as invalid
                        errors.append(self.get_date_error_message(date_check))
                        form._errors[NON_FIELD_ERRORS] = self.error_class([self.get_form_error()])
                        # remove the data from the cleaned_data dict since it was invalid
                        del form.cleaned_data[field]
                    # mark the data as seen
                    seen_data.add(data)

        if errors:
            raise forms.ValidationError(errors)


# TODO TODO TODO WILL NEED TO CHANGE THIS WITH DJANGO VERSION NO DOUBT
class BaseInlineFormSetForcedUniqueness(BaseModelFormSetForcedUniqueness, BaseInlineFormSet):
    def clean(self):
        self.validate_unique()


class DicModelChoiceField(forms.Field):
    """Special field using dictionary instead of queryset as choices

    This is to prevent ludicrous numbers of queries
    """
    widget = forms.TextInput

    def __init__(self, name, parent, dic, *args, **kwargs):
        self.name = name
        self.parent = parent
        self.dic = dic
        self.model = self.parent._meta.get_field(self.name).related_model

        super(DicModelChoiceField, self).__init__(*args, **kwargs)

        # Make sure required is set properly
        self.required = self.widget.required = not (
            self.parent._meta.get_field(self.name).null
            and
            self.parent._meta.get_field(self.name).blank
        )

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            value = self.dic.get(self.name).get(value)
        except:
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

    def valid_value(self, value):
        """Check to see if the provided value is a valid choice"""
        if str(value.id) in self.dic.get(self.name):
            return True
        return False


class AssayStudyConfigurationForm(SignOffMixin, BootstrapForm):
    """Frontend Form for Study Configurations"""
    class Meta(object):
        model = AssayStudyConfiguration
        widgets = {
            'name': forms.Textarea(attrs={'cols': 50, 'rows': 1}),
            'media_composition': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'hardware_description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = tracking


class AssayStudyModelForm(BootstrapForm):
    class Meta(object):
        model = AssayStudyModel
        exclude = ('' ,)

    def __init__(self, *args, **kwargs):
        super(AssayStudyModelForm, self).__init__(*args, **kwargs)
        self.fields['label'].widget.attrs.update({
            'size': '4',
            'max_length': '2'
        })
        self.fields['sequence_number'].widget.attrs.update({
            'size': '4',
            'max_length': '2'
        })
        self.fields['output'].widget.attrs.update({
            'size': '20',
            'max_length': '20'
        })


# FormSet for Study Models
AssayStudyModelFormSet = inlineformset_factory(
    AssayStudyConfiguration,
    AssayStudyModel,
    extra=1,
    form=AssayStudyModelForm,
    widgets={
        'label': forms.TextInput(attrs={'size': 2}),
        'sequence_number': forms.TextInput(attrs={'size': 2})
    }
)


def label_to_number(label):
    """Returns a numeric index from an alphabetical index"""
    num = 0
    for char in label:
        if char in string.ascii_letters:
            num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num


# Now uses unicode instead of string
def stringify_excel_value(value):
    """Given an excel value, return a unicode cast of it

    This also converts floats to integers when possible
    """
    # If the value is just a string literal, return it
    if type(value) == str or type(value) == str:
        return str(value)
    else:
        try:
            # If the value can be an integer, make it into one
            if int(value) == float(value):
                return str(int(value))
            else:
                return str(float(value))
        except:
            return str(value)


class AssayStudyAssayInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        """Init APRA inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayStudyAssayInlineFormSet, self).__init__(*args, **kwargs)

        target_queryset = AssayTarget.objects.all().order_by('name')

        method_queryset = AssayMethod.objects.all().order_by('name')

        # unit_queryset = PhysicalUnits.objects.filter(
        #     availability__icontains='readout'
        # ).order_by('unit_type__unit_type', 'base_unit__unit', 'scale_factor')

        unit_queryset = PhysicalUnits.objects.order_by('unit_type__unit_type', 'base_unit__unit', 'scale_factor')

        category_queryset = AssayCategory.objects.all().order_by('name')

        for form in self.forms:
            form.fields['target'].queryset = target_queryset
            form.fields['method'].queryset = method_queryset
            form.fields['unit'].queryset = unit_queryset

            form.fields['category'] = forms.ModelChoiceField(
                queryset=category_queryset,
                required=False,
                empty_label='All'
            )


class ReadyForSignOffForm(forms.Form):
    captcha = CaptchaField()
    message = forms.TextInput()


# TODO PLEASE REVIEW
class AssayStudyForm(SignOffMixin, BootstrapForm):
    def __init__(self, *args, **kwargs):
        """Init the Study Form

        Kwargs:
        groups -- a queryset of groups (allows us to avoid N+1 problem)
        """
        super(AssayStudyForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = filter_groups(self.user)

        # Crudely force required class
        for current_field in ['total_device_volume', 'flow_rate', 'number_of_relevant_cells']:
            self.fields[current_field].widget.attrs['class'] += ' required'

    class Meta(object):
        model = AssayStudy
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 100}),
        }
        exclude = tracking + restricted + ('access_groups', 'signed_off_notes', 'bulk_file', 'collaborator_groups')

    def clean(self):
        """Checks for at least one study type"""
        # clean the form data, before validation
        data = super(AssayStudyForm, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization'], data['pbpk_steady_state'], data['pbpk_bolus']]):
            raise forms.ValidationError('Please select at least one study type')

        if data.get('pbpk_steady_state', '') and (not data.get('number_of_relevant_cells', '') or not data.get('flow_rate', '')):
            raise forms.ValidationError('Continuous Infusion PBPK Requires Number of Cells Per MPS Model and Flow Rate')

        if data.get('pbpk_bolus', '') and (not data.get('number_of_relevant_cells', '') or not data.get('total_device_volume', '')):
            raise forms.ValidationError('Bolus PBPK Requires Number of Cells Per MPS Model and Total Device Volume')



class AssayStudyFormAdmin(BootstrapForm):
    """Admin Form for Assay Runs (now referred to as Studies)"""
    class Meta(object):
        model = AssayStudy
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 10}),
            'signed_off_notes': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)

    def __init__(self, *args, **kwargs):
        super(AssayStudyFormAdmin, self).__init__(*args, **kwargs)

        groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
        groups_with_center_full = Group.objects.filter(
            id__in=groups_with_center
        ).order_by(
            'name'
        )

        self.fields['group'].queryset = groups_with_center_full

        groups_without_repeat = groups_with_center_full

        if self.instance and getattr(self.instance, 'group', ''):
            groups_without_repeat.exclude(pk=self.instance.group.id)

        self.fields['access_groups'].queryset = groups_without_repeat
        self.fields['collaborator_groups'].queryset = groups_without_repeat

        # Crudely force required class
        for current_field in ['total_device_volume', 'flow_rate', 'number_of_relevant_cells']:
            self.fields[current_field].widget.attrs['class'] += ' required'

    def clean(self):
        # clean the form data, before validation
        data = super(AssayStudyFormAdmin, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization'], data['pbpk_steady_state'], data['pbpk_bolus']]):
            raise forms.ValidationError('Please select at least one study type')

        if data.get('pbpk_steady_state', '') and (not data.get('number_of_relevant_cells', '') or not data.get('flow_rate', '')):
            raise forms.ValidationError('Continuous Infusion PBPK Requires Number of Cells Per MPS Model and Flow Rate')

        if data.get('pbpk_bolus', '') and (not data.get('number_of_relevant_cells', '') or not data.get('total_device_volume', '')):
            raise forms.ValidationError('Bolus PBPK Requires Number of Cells Per MPS Model and Total Device Volume')


class AssayStudySupportingDataForm(BootstrapForm):
    class Meta(object):
        model = AssayStudySupportingData
        exclude = ('',)


class AssayStudyAssayForm(BootstrapForm):
    class Meta(object):
        model = AssayStudyAssay
        exclude = ('',)


class AssayStudySupportingDataInlineFormSet(BaseInlineFormSet):
    """Form for Study Supporting Data (as part of an inline)"""
    class Meta(object):
        model = AssayStudySupportingData
        exclude = ('',)

AssayStudySupportingDataFormSetFactory = inlineformset_factory(
    AssayStudy,
    AssayStudySupportingData,
    form=AssayStudySupportingDataForm,
    formset=AssayStudySupportingDataInlineFormSet,
    extra=1,
    exclude=[],
    widgets={
        'description': forms.Textarea(attrs={'rows': 3}),
    }
)

AssayStudyAssayFormSetFactory = inlineformset_factory(
    AssayStudy,
    AssayStudyAssay,
    form=AssayStudyAssayForm,
    formset=AssayStudyAssayInlineFormSet,
    extra=1,
    exclude=[]
)


class SetupFormsMixin(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super(SetupFormsMixin, self).__init__(*args, **kwargs)

        sections_with_times = (
            'compound',
            'cell',
            'setting'
        )

        for time_unit in list(TIME_CONVERSIONS.keys()):
            for current_section in sections_with_times:
                # Create fields for Days, Hours, Minutes
                self.fields[current_section + '_addition_time_' + time_unit] = forms.FloatField(
                    initial=0,
                    required=False,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control required',
                        'style': 'width:75px;'
                    })
                )
                self.fields[current_section + '_duration_' + time_unit] = forms.FloatField(
                    initial=0,
                    required=False,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control required',
                        'style': 'width:75px;'
                    })
                )

        self.fields['cell_cell_sample'].widget.attrs['style'] = 'width:75px;'
        self.fields['cell_passage'].widget.attrs['style'] = 'width:75px;'

        # DUMB, BAD (can't have them be "actually" required or they prevent submission
        add_required_to = [
            'cell_cell_sample',
            'cell_biosensor',
            'cell_density',
            'cell_density_unit',
            'cell_addition_location',
            'setting_setting',
            'setting_unit',
            'setting_value',
            'setting_addition_location',
            'compound_compound',
            'compound_concentration_unit',
            'compound_concentration',
            'compound_addition_location',
        ]

        for current_field in add_required_to:
            self.fields[current_field].widget.attrs['class'] += ' required'

            # Sloppy
            if hasattr(self.fields[current_field], '_queryset'):
                if hasattr(self.fields[current_field]._queryset, 'model'):
                    # Usually one would use a hyphen rather than an underscore
                    # self.fields[field].widget.attrs['data-app'] = self.fields[field]._queryset.model._meta.app_label
                    self.fields[current_field].widget.attrs['data_app'] = self.fields[current_field]._queryset.model._meta.app_label

                    # self.fields[field].widget.attrs['data-model'] = self.fields[field]._queryset.model._meta.object_name
                    self.fields[current_field].widget.attrs['data_model'] = self.fields[current_field]._queryset.model._meta.object_name

                    self.fields[current_field].widget.attrs['data_verbose_name'] = self.fields[current_field]._queryset.model._meta.verbose_name

                    # Possibly dumber
                    if hasattr(self.fields[current_field]._queryset.model, 'get_add_url_manager'):
                        self.fields[current_field].widget.attrs['data_add_url'] = self.fields[current_field]._queryset.model.get_add_url_manager()

    ### ADDING SETUP CELLS
    cell_cell_sample = forms.IntegerField(required=False)
    cell_biosensor = forms.ModelChoiceField(
        queryset=Biosensor.objects.all().prefetch_related('supplier'),
        required=False,
        # Default is naive
        initial=2
    )
    cell_density = forms.FloatField(required=False)

    # TODO THIS IS TO BE HAMMERED OUT
    cell_density_unit = forms.ModelChoiceField(
        queryset=PhysicalUnits.objects.filter(
            availability__contains='cell'
        ).order_by('unit'),
        required=False
    )

    cell_passage = forms.CharField(required=False)

    cell_addition_location = forms.ModelChoiceField(queryset=AssaySampleLocation.objects.all().order_by('name'), required=False)

    ### ?ADDING SETUP SETTINGS
    setting_setting = forms.ModelChoiceField(queryset=AssaySetting.objects.all().order_by('name'), required=False)
    setting_unit = forms.ModelChoiceField(queryset=PhysicalUnits.objects.all().order_by('base_unit','scale_factor'), required=False)

    setting_value = forms.CharField(required=False)

    setting_addition_location = forms.ModelChoiceField(
        queryset=AssaySampleLocation.objects.all().order_by('name'),
        required=False
    )

    ### ADDING COMPOUNDS
    compound_compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    compound_concentration_unit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit__unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )
    compound_concentration = forms.FloatField(required=False)

    compound_addition_location = forms.ModelChoiceField(
        queryset=AssaySampleLocation.objects.all().order_by('name'),
        required=False
    )
    # Text field (un-saved) for supplier
    compound_supplier_text = forms.CharField(
        required=False,
        initial=''
    )
    # Text field (un-saved) for lot
    compound_lot_text = forms.CharField(
        required=False,
        initial=''
    )
    # Receipt date
    compound_receipt_date = forms.DateField(required=False)


# TODO ADD STUDY
class AssayMatrixForm(SetupFormsMixin, SignOffMixin, BootstrapForm):
    class Meta(object):
        model = AssayMatrix
        exclude = ('study',) + tracking
        widgets = {
            'number_of_columns': forms.NumberInput(attrs={'style': 'width: 100px;'}),
            'number_of_rows': forms.NumberInput(attrs={'style': 'width: 100px;'}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'variance_from_organ_model_protocol': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        # self.user = kwargs.pop('user', None)
        super(AssayMatrixForm, self).__init__(*args, **kwargs)

        if self.study:
            self.instance.study = self.study

        # sections_with_times = (
        #     'compound',
        #     'cell',
        #     'setting'
        # )
        #
        # for time_unit in list(TIME_CONVERSIONS.keys()):
        #     for current_section in sections_with_times:
        #         # Create fields for Days, Hours, Minutes
        #         self.fields[current_section + '_addition_time_' + time_unit] = forms.FloatField(
        #             initial=0,
        #             required=False,
        #             widget=forms.NumberInput(attrs={
        #                 'class': 'form-control',
        #                 'style': 'width:75px;'
        #             })
        #         )
        #         self.fields[current_section + '_duration_' + time_unit] = forms.FloatField(
        #             initial=0,
        #             required=False,
        #             widget=forms.NumberInput(attrs={
        #                 'class': 'form-control',
        #                 'style': 'width:75px;'
        #             })
        #         )

        # Changing these things in init is bad
        self.fields['matrix_item_notebook_page'].widget.attrs['style'] = 'width:75px;'
        # self.fields['cell_cell_sample'].widget.attrs['style'] = 'width:75px;'
        # self.fields['cell_passage'].widget.attrs['style'] = 'width:75px;'

        # Make sure no selectize
        # CONTRIVED
        self.fields['matrix_item_full_organ_model'].widget.attrs['class'] = 'no-selectize'
        self.fields['matrix_item_full_organ_model_protocol'].widget.attrs['class'] = 'no-selectize'

        # No selectize on action either (hides things, looks odd)
        # CONTRIVED
        # self.fields['action'].widget.attrs['class'] += ' no-selectize'

        # DUMB, BAD (can't have them be "actually" required or they prevent submission
        add_required_to = [
            'matrix_item_name',
            'matrix_item_setup_date',
            'matrix_item_test_type',
            'matrix_item_name',
            'matrix_item_device',
            'matrix_item_organ_model',
        ]

        for current_field in add_required_to:
            self.fields[current_field].widget.attrs['class'] += ' required'

    ### ADDITIONAL MATRIX FIELDS (unsaved)
    number_of_items = forms.IntegerField(required=False)

    ### ITEM FIELD HELPERS
    # action = forms.ChoiceField(choices=(
    #     ('', 'Please Select an Action'),
    #     ('add_name', 'Add Names/IDs*'),
    #     ('add_test_type', 'Add Test Type*'),
    #     ('add_date', 'Add Setup Date*'),
    #     ('add_device', 'Add Device/MPS Model Information*'),
    #     ('add_settings', 'Add Settings'),
    #     ('add_compounds', 'Add Compounds'),
    #     ('add_cells', 'Add Cells'),
    #     ('add_notes', 'Add Notes/Notebook Information'),
    #     # ADD BACK LATER
    #     # ('copy', 'Copy Contents'),
    #     # TODO TODO TODO TENTATIVE
    #     # ('clear', 'Clear Contents'),
    #     ('delete', 'Delete Selected'),
    # ), required=False)

    # The matrix_item isn't just to be annoying, I want to avoid conflicts with other fields
    ### ADDING ITEM FIELDS
    matrix_item_name = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 1}),
        label='Matrix Item Name'
    )

    matrix_item_setup_date = forms.DateField(
        required=False,
        label='Matrix Item Setup Date'
    )
    # Foolish!
    matrix_item_setup_date_popup = forms.DateField(required=False)

    matrix_item_test_type = forms.ChoiceField(
        required=False,
        choices=TEST_TYPE_CHOICES,
        label='Matrix Item Test Type'
    )

    matrix_item_scientist = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 1}),
        label='Scientist'
    )
    matrix_item_notebook = forms.CharField(
        required=False,
        label='Notebook'
    )
    matrix_item_notebook_page = forms.CharField(
        required=False,
        label='Notebook Page'
    )
    matrix_item_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Notes'
    )

    ### ADDING SETUP FIELDS
    matrix_item_device = forms.ModelChoiceField(
        queryset=Microdevice.objects.all().order_by('name'),
        required=False,
        label='Matrix Item Device'
    )
    matrix_item_organ_model = forms.ModelChoiceField(
        queryset=OrganModel.objects.all().order_by('name'),
        required=False,
        label='Matrix Item MPS Model'
    )
    matrix_item_organ_model_protocol = forms.ModelChoiceField(
        queryset=OrganModelProtocol.objects.all().order_by('version'),
        required=False,
        label='Matrix Item MPS Model Version'
    )
    matrix_item_variance_from_organ_model_protocol = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Matrix Item Variance from Protocol'
    )

    matrix_item_full_organ_model = forms.ModelChoiceField(
        queryset=OrganModel.objects.all().order_by('name'),
        required=False
    )
    matrix_item_full_organ_model_protocol = forms.ModelChoiceField(
        queryset=OrganModelProtocol.objects.all(),
        required=False
    )

    ### INCREMENTER
    compound_concentration_increment = forms.FloatField(required=False, initial=1)
    compound_concentration_increment_type = forms.ChoiceField(
        choices=(
            ('/', 'Divide'),
            ('*', 'Multiply'),
            ('+', 'Add'),
            ('-', 'Subtract')
        ),
        required=False
    )
    compound_concentration_increment_direction = forms.ChoiceField(
        choices=(
            ('lr', 'Left to Right'),
            ('d', 'Down'),
            ('rl', 'Right to Left'),
            ('u', 'Up'),
            ('lrd', 'Left to Right and Down'),
            ('rlu', 'Right to Left and Up')
        ),
        required=False,
        initial='lr'
    )

    # Options for deletion
    delete_option = forms.ChoiceField(
        required=False,
        choices=(
            ('all', 'Everything'),
            ('cell', 'Cells'),
            ('compound', 'Compounds'),
            ('setting', 'Settings'),
        ),
        label='Delete Option'
    )

    # FORCE UNIQUENESS CHECK
    def clean(self):
        super(AssayMatrixForm, self).clean()

        if AssayMatrix.objects.filter(
                study_id=self.instance.study.id,
                name=self.cleaned_data.get('name', '')
        ).exclude(pk=self.instance.pk).count():
            raise forms.ValidationError({'name': ['Matrix name must be unique within study.']})


class AssaySetupCompoundForm(ModelFormSplitTime):
    compound = forms.CharField()

    class Meta(object):
        model = AssaySetupCompound
        exclude = tracking


# TODO: IDEALLY THE CHOICES WILL BE PASSED VIA A KWARG
class AssaySetupCompoundFormSet(BaseModelFormSetForcedUniqueness):
    custom_fields = (
        'matrix_item',
        'compound_instance',
        'concentration_unit',
        'addition_location'
    )

    def __init__(self, *args, **kwargs):
        # TODO EVENTUALLY PASS WITH KWARG
        # self.suppliers = kwargs.pop('suppliers', None)
        # self.compound_instances = kwargs.pop('compound_instances', None)
        # self.compound_instances_dic = kwargs.pop('compound_instances_dic', None)
        # self.setup_compounds = kwargs.pop('setup_compounds', None)
        # Get all chip setup assay compound instances
        self.matrix = kwargs.pop('matrix', None)
        self.setup_compounds = {
            (
                instance.matrix_item_id,
                instance.compound_instance_id,
                instance.concentration,
                instance.concentration_unit_id,
                instance.addition_time,
                instance.duration,
                instance.addition_location_id
            ): True for instance in AssaySetupCompound.objects.filter(
                matrix_item__matrix=self.matrix
            )
        }

        self.compound_instances = {}
        self.compound_instances_dic = {}

        for instance in CompoundInstance.objects.all().prefetch_related('supplier'):
            self.compound_instances.update({
                (
                    instance.compound_id,
                    instance.supplier_id,
                    instance.lot,
                    instance.receipt_date
                ): instance
            })
            # NOTE use of name instead of id!
            self.compound_instances_dic.update({
                instance.id: (
                    instance.compound_id,
                    instance.supplier.name,
                    instance.lot,
                    instance.receipt_date
                )
            })

        # Get all suppliers
        self.suppliers = {
            supplier.name: supplier for supplier in CompoundSupplier.objects.all()
        }

        super(AssaySetupCompoundFormSet, self).__init__(*args, **kwargs)

        filters = {'matrix_item': {'matrix_id': self.matrix.id}}
        self.dic = get_dic_for_custom_choice_field(self, filters=filters)

        for form in self.forms:
            for field in self.custom_fields:
                form.fields[field] = DicModelChoiceField(field, self.model, self.dic)

            # Purge all classes
            for field in form.fields:
                form.fields[field].widget.attrs['class'] = ''

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupCompoundFormSet, self)._construct_form(i, **kwargs)

        # Text field (un-saved) for supplier
        form.fields['supplier_text'] = forms.CharField(initial='N/A', required=False)
        # Text field (un-saved) for lot
        form.fields['lot_text'] = forms.CharField(initial='N/A', required=False)
        # Receipt date
        form.fields['receipt_date'] = forms.DateField(required=False)

        if form.instance:
            current_compound_instance_id = form.instance.compound_instance_id
        else:
            current_compound_instance_id = None

        if current_compound_instance_id:
            current_compound_instance = self.compound_instances_dic.get(current_compound_instance_id)

            # form.fields['compound'].initial = current_compound_instance.compound
            # form.fields['supplier_text'].initial = current_compound_instance.supplier.name
            # form.fields['lot_text'].initial = current_compound_instance.lot
            # form.fields['receipt_date'].initial = current_compound_instance.receipt_date
            form.fields['compound'].initial = current_compound_instance[0]
            form.fields['supplier_text'].initial = current_compound_instance[1]
            form.fields['lot_text'].initial = current_compound_instance[2]
            form.fields['receipt_date'].initial = current_compound_instance[3]

        return form

    # TODO TODO TODO
    # Will either have to decouple compound instance and supplier or else have a dic ALL FORMSETS reference
    # Ostensibly, I can pass a pointer to a dictionary so that all of the formsets see the same thing
    def save(self, commit=True):
        # Get forms_data (excluding those with delete or no data)
        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        forms_to_delete = [f for f in self.forms if f.cleaned_data and f.cleaned_data.get('DELETE', False)]

        # Forms to be deleted
        for form in forms_to_delete:
            try:
                instance = BootstrapForm.save(form, commit=False)

                if instance and instance.id and commit:
                    instance.delete()
            # ValueError here indicates that the instance couldn't even validate and so should be ignored
            except ValueError:
                pass

        # Forms to save
        for form in forms_data:
            instance = BootstrapForm.save(form, commit=False)

            matrix_item = instance.matrix_item

            current_data = form.cleaned_data

            # Bad
            if not current_data.get('supplier_text'):
                current_data['supplier_text'] = 'N/A'

            if not current_data.get('lot_text'):
                current_data['lot_text'] = 'N/A'

            compound_id = int(current_data.get('compound'))
            supplier_text = current_data.get('supplier_text').strip()
            lot_text = current_data.get('lot_text').strip()
            receipt_date = current_data.get('receipt_date')

            # Should be acquired straight from form
            # concentration = current_data.get('concentration')
            # concentration_unit = current_data.get('concentration_unit')

            addition_time = 0
            duration = 0
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                addition_time += current_data.get('addition_time_' + time_unit, 0) * conversion
                duration += current_data.get('duration_' + time_unit, 0) * conversion

            # Check if the supplier already exists
            supplier = self.suppliers.get(supplier_text, '')
            # Otherwise create the supplier
            if not supplier:
                supplier = CompoundSupplier(
                    name=supplier_text,
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
                )
                # if commit:
                #     supplier.save()
                # Always save the supplier
                supplier.save()
                self.suppliers.update({
                    supplier_text: supplier
                })

            # Check if compound instance exists
            compound_instance = self.compound_instances.get((compound_id, supplier.id, lot_text, receipt_date), '')
            if not compound_instance:
                compound_instance = CompoundInstance(
                    compound_id=compound_id,
                    supplier=supplier,
                    lot=lot_text,
                    receipt_date=receipt_date,
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
                )
                # if commit:
                #     compound_instance.save()
                # ALWAYS MAKE A NEW COMPOUND INSTANCE
                compound_instance.save()
                self.compound_instances.update({
                    (compound_id, supplier.id, lot_text, receipt_date): compound_instance
                })

            # Update the instance with new data
            # instance.matrix_item = matrix_item
            instance.compound_instance = compound_instance

            instance.addition_time = addition_time
            instance.duration = duration

            # Save the instance
            if commit:
                conflicting_assay_compound_instance = self.setup_compounds.get(
                    (
                        instance.matrix_item_id,
                        instance.compound_instance_id,
                        instance.concentration,
                        instance.concentration_unit_id,
                        instance.addition_time,
                        instance.duration,
                        instance.addition_location_id
                    ), None
                )
                # If there is not conflict or if this is an update
                if not conflicting_assay_compound_instance:
                    instance.save()

                # Do nothing otherwise (it already exists)

            self.setup_compounds.update({
                (
                    instance.matrix_item_id,
                    instance.compound_instance_id,
                    instance.concentration,
                    instance.concentration_unit_id,
                    instance.addition_time,
                    instance.duration,
                    instance.addition_location_id
                ): True
            })


# UGLY SOLUTION
class AssaySetupCompoundInlineFormSet(BaseInlineFormSet):
    """Frontend Inline FormSet for Compound Instances"""
    class Meta(object):
        model = AssaySetupCompound
        exclude = ('',)

    def __init__(self, *args, **kwargs):
        """Init Chip Setup Form

        Filters physical units to include only Concentration
        """
        super(AssaySetupCompoundInlineFormSet, self).__init__(*args, **kwargs)
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
            'base_unit__unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')

        for form in self.forms:
            # form.fields['start_time_unit'].queryset = time_unit_queryset
            # form.fields['duration_unit'].queryset = time_unit_queryset
            form.fields['concentration_unit'].queryset = concentration_unit_queryset
            form.fields['compound_instance'].queryset = compound_instances

            # All available compounds
            form.fields['compound'] = forms.ModelChoiceField(
                queryset=Compound.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            # Text field (un-saved) for supplier
            form.fields['supplier_text'] = forms.CharField(
                initial='',
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=False
            )
            # Text field (un-saved) for lot
            form.fields['lot_text'] = forms.CharField(
                initial='',
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=False
            )
            # Receipt date
            form.fields['receipt_date'] = forms.DateField(
                required=False,
                widget=forms.DateInput(attrs={
                    'class': 'form-control datepicker-input',
                    'autocomplete': 'off'
                })
            )
            # If instance, apply initial values
            if form.instance.compound_instance_id:
                current_compound_instance = compound_instances_dic.get(form.instance.compound_instance_id)

                form.fields['compound'].initial = current_compound_instance.compound
                form.fields['supplier_text'].initial = current_compound_instance.supplier.name
                form.fields['lot_text'].initial = current_compound_instance.lot
                form.fields['receipt_date'].initial = current_compound_instance.receipt_date

            # VERY SLOPPY
            form.fields['compound'].widget.attrs['class'] += ' required'

            current_field = 'compound'
            if hasattr(form.fields[current_field], '_queryset'):
                if hasattr(form.fields[current_field]._queryset, 'model'):
                    # Usually one would use a hyphen rather than an underscore
                    # form.fields[field].widget.attrs['data-app'] = form.fields[field]._queryset.model._meta.app_label
                    form.fields[current_field].widget.attrs['data_app'] = form.fields[current_field]._queryset.model._meta.app_label

                    # form.fields[field].widget.attrs['data-model'] = form.fields[field]._queryset.model._meta.object_name
                    form.fields[current_field].widget.attrs['data_model'] = form.fields[current_field]._queryset.model._meta.object_name

                    form.fields[current_field].widget.attrs['data_verbose_name'] = form.fields[current_field]._queryset.model._meta.verbose_name

                    # Possibly dumber
                    if hasattr(form.fields[current_field]._queryset.model, 'get_add_url_manager'):
                        form.fields[current_field].widget.attrs['data_add_url'] = form.fields[current_field]._queryset.model.get_add_url_manager()

    # TODO THIS IS NOT DRY
    def save(self, commit=True):
        # Get forms_data (excluding those with delete or no data)
        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        forms_to_delete = [f for f in self.forms if f.cleaned_data and f.cleaned_data.get('DELETE', False)]

        # Forms to be deleted
        for form in forms_to_delete:
            instance = super(BootstrapForm, form).save(commit=False)

            if instance and instance.id and commit:
                instance.delete()

        matrix_item = self.instance

        # Get all chip setup assay compound instances
        assay_compound_instances = {
            (
                instance.compound_instance.id,
                instance.concentration,
                instance.concentration_unit.id,
                instance.addition_time,
                instance.duration,
                instance.addition_location_id
            ): True for instance in AssaySetupCompound.objects.filter(
            matrix_item_id=matrix_item.id
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
            instance = super(BootstrapForm, form).save(commit=False)

            current_data = form.cleaned_data

            # Bad
            if not current_data.get('supplier_text'):
                current_data['supplier_text'] = 'N/A'

            if not current_data.get('lot_text'):
                current_data['lot_text'] = 'N/A'

            compound = current_data.get('compound')
            supplier_text = current_data.get('supplier_text').strip()
            lot_text = current_data.get('lot_text').strip()
            receipt_date = current_data.get('receipt_date')

            # Should be acquired straight from form
            # concentration = current_data.get('concentration')
            # concentration_unit = current_data.get('concentration_unit')

            addition_time = 0
            duration = 0
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                addition_time += current_data.get('addition_time_' + time_unit, 0) * conversion
                duration += current_data.get('duration_' + time_unit, 0) * conversion

            # Check if the supplier already exists
            supplier = suppliers.get(supplier_text, '')
            # Otherwise create the supplier
            if not supplier:
                supplier = CompoundSupplier(
                    name=supplier_text,
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
                )
                # if commit:
                #     supplier.save()
                # Always save the supplier
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
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
                )
                # if commit:
                #     compound_instance.save()
                # ALWAYS MAKE A NEW COMPOUND INSTANCE
                compound_instance.save()
                compound_instances.update({
                    (compound.id, supplier.id, lot_text, receipt_date): compound_instance
                })

            # Update the instance with new data
            instance.matrix_item = matrix_item
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
                        instance.duration,
                        instance.addition_location_id
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
                    instance.duration,
                    instance.addition_location_id
                ): True
            })


class AssaySetupCellForm(ModelFormSplitTime):
    class Meta(object):
        model = AssaySetupCell
        exclude = tracking

    def __init__(self, *args, **kwargs):
        # self.static_choices = kwargs.pop('static_choices', None)
        super(AssaySetupCellForm, self).__init__(*args, **kwargs)

        # Change widget size
        self.fields['cell_sample'].widget.attrs['style'] = 'width:75px;'
        self.fields['passage'].widget.attrs['style'] = 'width:75px;'

        self.fields['density_unit'].queryset = PhysicalUnits.objects.filter(availability__contains='cell').order_by('unit')


# TODO: IDEALLY THE CHOICES WILL BE PASSED VIA A KWARG
class AssaySetupCellFormSet(BaseModelFormSetForcedUniqueness):
    custom_fields = (
        'matrix_item',
        'cell_sample',
        'biosensor',
        'density_unit',
        'addition_location'
    )

    def __init__(self, *args, **kwargs):
        self.matrix = kwargs.pop('matrix', None)
        super(AssaySetupCellFormSet, self).__init__(*args, **kwargs)

        filters = {'matrix_item': {'matrix_id': self.matrix.id}}
        self.dic = get_dic_for_custom_choice_field(self, filters=filters)

        for form in self.forms:
            for field in self.custom_fields:
                form.fields[field] = DicModelChoiceField(field, self.model, self.dic)

            # Purge all classes
            for field in form.fields:
                form.fields[field].widget.attrs['class'] = ''


class AssaySetupSettingForm(ModelFormSplitTime):
    class Meta(object):
        model = AssaySetupCell
        exclude = tracking


class AssaySetupSettingFormSet(BaseModelFormSetForcedUniqueness):
    custom_fields = (
        'matrix_item',
        'setting',
        'unit',
        'addition_location'
    )

    def __init__(self, *args, **kwargs):
        self.matrix = kwargs.pop('matrix', None)
        super(AssaySetupSettingFormSet, self).__init__(*args, **kwargs)

        filters = {'matrix_item': {'matrix_id': self.matrix.id }}
        self.dic = get_dic_for_custom_choice_field(self, filters=filters)

        for form in self.forms:
            for field in self.custom_fields:
                form.fields[field] = DicModelChoiceField(field, self.model, self.dic)

            # Purge all classes
            for field in form.fields:
                form.fields[field].widget.attrs['class'] = ''

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupSettingFormSet, self)._construct_form(i, **kwargs)
        for time_unit in list(TIME_CONVERSIONS.keys()):
            # Create fields for Days, Hours, Minutes
            form.fields['addition_time_' + time_unit] = forms.FloatField(initial=0)
            form.fields['duration_' + time_unit] = forms.FloatField(initial=0)
            # Change style
            # form.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:75px;'
            # form.fields['duration_' + time_unit].widget.attrs['style'] = 'width:75px;'

        if form.instance.addition_time:
            # Fill additional time
            addition_time_in_minutes_remaining = form.instance.addition_time
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                initial_time_for_current_field = int(addition_time_in_minutes_remaining / conversion)
                if initial_time_for_current_field:
                    form.fields['addition_time_' + time_unit].initial = initial_time_for_current_field
                    addition_time_in_minutes_remaining -= initial_time_for_current_field * conversion
            # Add fractions of minutes if necessary
            if addition_time_in_minutes_remaining:
                form.fields['addition_time_minute'].initial += addition_time_in_minutes_remaining

        if form.instance.duration:
            # Fill duration
            duration_in_minutes_remaining = form.instance.duration
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
                initial_time_for_current_field = int(duration_in_minutes_remaining / conversion)
                if initial_time_for_current_field:
                    form.fields['duration_' + time_unit].initial = initial_time_for_current_field
                    duration_in_minutes_remaining -= initial_time_for_current_field * conversion
            # Add fractions of minutes if necessary
            if duration_in_minutes_remaining:
                form.fields['duration_minute'].initial += duration_in_minutes_remaining

        return form


AssaySetupCompoundFormSetFactory = modelformset_factory(
    AssaySetupCompound,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCompoundForm,
    formset=AssaySetupCompoundFormSet,
    can_delete=True
)
AssaySetupCellFormSetFactory = modelformset_factory(
    AssaySetupCell,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCellForm,
    formset=AssaySetupCellFormSet,
    can_delete=True
)
AssaySetupSettingFormSetFactory = modelformset_factory(
    AssaySetupSetting,
    extra=1,
    exclude=[tracking],
    form=AssaySetupSettingForm,
    formset=AssaySetupSettingFormSet,
    can_delete=True
)
AssaySetupCompoundInlineFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupCompound,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCompoundForm,
    formset=AssaySetupCompoundInlineFormSet,
    can_delete=True
)
AssaySetupCellInlineFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupCell,
    extra=1,
    exclude=[tracking],
    form=AssaySetupCellForm,
    # formset=AssaySetupCellFormSet,
    can_delete=True
)
AssaySetupSettingInlineFormSetFactory = inlineformset_factory(
    AssayMatrixItem,
    AssaySetupSetting,
    extra=1,
    exclude=[tracking],
    form=AssaySetupSettingForm,
    # formset=AssaySetupSettingFormSet,
    can_delete=True
)


class AssayMatrixItemFullForm(SignOffMixin, BootstrapForm):
    """Frontend form for Items"""
    class Meta(object):
        model = AssayMatrixItem
        widgets = {
            'concentration': forms.NumberInput(attrs={'style': 'width:75px;'}),
            'notebook_page': forms.NumberInput(attrs={'style': 'width:75px;'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'variance_from_organ_model_protocol': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }
        # Assay Run ID is always bound to the parent Study
        exclude = ('study', 'matrix', 'column_index', 'row_index') + tracking + restricted

    def clean(self):
        """Cleans the Chip Setup Form

        Ensures the the name is unique in the current study
        Ensures that the data for a compound is complete
        Prevents changes to the chip if data has been uploaded (avoiding conflicts between data and entries)
        """
        super(AssayMatrixItemFullForm, self).clean()

        # Make sure the barcode/ID is unique in the study
        if AssayMatrixItem.objects.filter(
                study_id=self.instance.study.id,
                name=self.cleaned_data.get('name')
        ).exclude(id=self.instance.id):
            raise forms.ValidationError({'name': ['ID/Barcode must be unique within study.']})

        # Make sure the device matches if necessary
        if self.instance.matrix.device and (self.instance.matrix.device != self.cleaned_data.get('device')):
            raise forms.ValidationError(
                {'device': ['The item\'s device must match the one specified in the Matrix: "{}"'.format(self.instance.matrix.device)]}
            )


class AssayMatrixItemForm(forms.ModelForm):
    class Meta(object):
        model = AssayMatrixItem
        exclude = ('study', 'matrix') + tracking


# TODO NEED TO TEST
class AssayMatrixItemFormSet(BaseInlineFormSetForcedUniqueness):
    custom_fields = (
        'device',
        'organ_model',
        'organ_model_protocol',
        'failure_reason'
    )

    def __init__(self, *args, **kwargs):
        # Get the study
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayMatrixItemFormSet, self).__init__(*args, **kwargs)

        if not self.study:
            self.study = self.instance.study

        self.dic = get_dic_for_custom_choice_field(self)

        for form in self.forms:
            for field in self.custom_fields:
                form.fields[field] = DicModelChoiceField(field, self.model, self.dic)

            if self.study:
                form.instance.study = self.study

            if form.instance.pk:
                form.instance.modified_by = self.user
            else:
                form.instance.created_by = self.user

        self.invalid_matrix_item_names = {
            item.name: item.id for item in AssayMatrixItem.objects.filter(study_id=self.study.id)
        }

    def clean(self):
        super(AssayMatrixItemFormSet, self).clean()

        for index, form in enumerate(self.forms):
            current_data = form.cleaned_data

            if current_data and not current_data.get('DELETE', False):
                if self.instance.number_of_columns:
                    if current_data.get('column_index') > self.instance.number_of_columns:
                        raise forms.ValidationError(
                            'An Item extends beyond the columns of the Matrix.'
                            ' Increase the size of the Matrix and/or delete the offending Item if necessary.'
                        )
                    if current_data.get('row_index') > self.instance.number_of_rows:
                        raise forms.ValidationError(
                            'An Item extends beyond the rows of the Matrix.'
                            ' Increase the size of the Matrix and/or delete the offending Item if necessary.'
                        )

                # Make sure the barcode/ID is unique in the study
                conflicting_name_item_id = self.invalid_matrix_item_names.get(current_data.get('name'), None)
                if conflicting_name_item_id and conflicting_name_item_id != form.instance.pk:
                    form.add_error('name', 'This name conflicts with existing Item names in this Study.')

                # Make sure the device matches if necessary
                if self.instance.device and (self.instance.device != current_data.get('device')):
                    form.add_error('device', 'This device conflicts with the one listed in the Matrix.')

AssayMatrixItemFormSetFactory = inlineformset_factory(
    AssayMatrix,
    AssayMatrixItem,
    formset=AssayMatrixItemFormSet,
    form=AssayMatrixItemForm,
    extra=1,
    exclude=('study',) + tracking
)


class AssayStudyDeleteForm(forms.ModelForm):
    class Meta(object):
        model = AssayStudy
        fields = []


class AssayStudySignOffForm(SignOffMixin, BootstrapForm):
    class Meta(object):
        model = AssayStudy
        fields = ['signed_off', 'signed_off_notes']
        widgets = {
            'signed_off_notes': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }


class AssayStudyStakeholderSignOffForm(SignOffMixin, BootstrapForm):
    class Meta(object):
        model = AssayStudyStakeholder
        fields = ['signed_off', 'signed_off_notes']
        widgets = {
            'signed_off_notes': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }


class AssayStudyStakeholderFormSet(BaseInlineFormSet):
    class Meta(object):
        model = AssayStudyStakeholder

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AssayStudyStakeholderFormSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            # TODO FILTER OUT THOSE USER ISN'T ADMIN OF
            # TODO REVIEW
            user_admin_groups = self.user.groups.filter(name__contains=ADMIN_SUFFIX)
            potential_groups = [group.name.replace(ADMIN_SUFFIX, '') for group in user_admin_groups]
            queryset = super(AssayStudyStakeholderFormSet, self).get_queryset()
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
AssayStudyStakeholderFormSetFactory = inlineformset_factory(
    AssayStudy,
    AssayStudyStakeholder,
    form=AssayStudyStakeholderSignOffForm,
    formset=AssayStudyStakeholderFormSet,
    extra=0,
    can_delete=False
)


class AssayStudyDataUploadForm(BootstrapForm):
    """Form for Bulk Uploads"""
    # Excluded for now
    # overwrite_option = OVERWRITE_OPTIONS_BULK

    # EVIL WAY TO GET PREVIEW DATA
    preview_data = forms.BooleanField(initial=False, required=False)

    class Meta(object):
        model = AssayStudy
        fields = ('bulk_file',)

    def __init__(self, *args, **kwargs):
        """Init the Bulk Form

        kwargs:
        request -- the current request
        """
        self.request = kwargs.pop('request', None)

        super(AssayStudyDataUploadForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(AssayStudyDataUploadForm, self).clean()

        # Get the study in question
        study = self.instance

        # test_file = None

        # TODO TODO TODO TODO TODO
        if self.request and self.request.FILES and data.get('bulk_file'):
            # Make sure that this isn't the current file
            if not study.bulk_file or study.bulk_file != data.get('bulk_file'):
                test_file = data.get('bulk_file', '')

                file_processor = AssayFileProcessor(test_file, study, self.request.user)
                # Process the file
                file_processor.process_file()

                # Evil attempt to acquire preview data
                self.cleaned_data['preview_data'] = file_processor.preview_data

        return self.cleaned_data


class AssayStudySetForm(SignOffMixin, BootstrapForm):
    class Meta(object):
        model = AssayStudySet
        exclude = tracking
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10})
        }

    def __init__(self, *args, **kwargs):
        super(AssayStudySetForm, self).__init__(*args, **kwargs)

        study_queryset = get_user_accessible_studies(
            self.user
        ).prefetch_related(
            'group__microphysiologycenter_set',
        )
        assay_queryset = AssayStudyAssay.objects.filter(
            study_id__in=study_queryset.values_list('id', flat=True)
        ).prefetch_related(
            'target',
            'method',
            'unit'
        )

        self.fields['studies'].queryset = study_queryset
        self.fields['assays'].queryset = assay_queryset

        # CONTRIVED
        self.fields['studies'].widget.attrs['class'] = 'no-selectize'
        self.fields['assays'].widget.attrs['class'] = 'no-selectize'


class AssayReferenceForm(BootstrapForm):

    query_term = forms.CharField(
        initial='',
        required=False,
        label='PubMed ID / DOI'
    )

    class Meta(object):
        model = AssayReference
        exclude = tracking
        widgets = {
            'query_term': forms.Textarea(attrs={'rows': 1}),
            'title': forms.Textarea(attrs={'rows': 2}),
            'authors': forms.Textarea(attrs={'rows': 1}),
            'abstract': forms.Textarea(attrs={'rows': 10}),
            'publication': forms.Textarea(attrs={'rows': 1}),
        }

AssayStudyReferenceFormSetFactory = inlineformset_factory(
    AssayStudy,
    AssayStudyReference,
    extra=1,
    exclude=[]
)

AssayStudySetReferenceFormSetFactory = inlineformset_factory(
    AssayStudySet,
    AssayStudySetReference,
    extra=1,
    exclude=[]
)


# Convoluted
def process_error_for_study_new(prefix, row, column, full_error):
    current_error = dict(full_error)
    modified_error = []

    for error_field, error_values in current_error.items():
        for error_value in error_values:
            modified_error.append([
                '|'.join([str(x) for x in [
                    prefix,
                    row,
                    column,
                    error_field
                ]]) + '-' + error_value
            ])

    return modified_error


# Perhaps it would have been more intelligent to leverage the forms in the add
# There would have been different consquences for doing so, but consistency
class AssayStudyFormNew(SetupFormsMixin, SignOffMixin, BootstrapForm):
    setup_data = forms.CharField(required=False)
    processed_setup_data = forms.CharField(required=False)
    number_of_items = forms.CharField(required=False)
    test_type = forms.ChoiceField(
        initial='control',
        choices=TEST_TYPE_CHOICES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        """Init the Study Form

        Kwargs:
        groups -- a queryset of groups (allows us to avoid N+1 problem)
        """
        super(AssayStudyFormNew, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = filter_groups(self.user)

        # Make sure there are only organ models with versions
        # Removed for now
        # self.fields['organ_model'].queryset = OrganModel.objects.filter(
        #     organmodelprotocol__isnull=False
        # ).distinct()

        # SLOPPY
        self.fields['test_type'].widget.attrs['class'] += ' no-selectize test-type required'
        # Bad
        self.fields['test_type'].widget.attrs['style'] = 'width:100px;'
        self.fields['number_of_items'].widget.attrs['class'] = 'form-control number-of-items required'
        # Bad
        # self.fields['number_of_items'].widget.attrs['style'] = 'margin-top:10px;'

        # Crudely force required class
        for current_field in ['total_device_volume', 'flow_rate', 'number_of_relevant_cells']:
            self.fields[current_field].widget.attrs['class'] += ' required'

    class Meta(object):
        model = AssayStudy
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 100}),
        }
        exclude = tracking + restricted + ('access_groups', 'signed_off_notes', 'bulk_file')

    def clean(self):
        """Checks for at least one study type"""
        # clean the form data, before validation
        data = super(AssayStudyFormNew, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization'], data['pbpk_steady_state'], data['pbpk_bolus']]):
            raise forms.ValidationError('Please select at least one study type')

        if data.get('pbpk_steady_state', '') and (not data.get('number_of_relevant_cells', '') or not data.get('flow_rate', '')):
            raise forms.ValidationError('Continuous Infusion PBPK Requires Number of Cells Per MPS Model and Flow Rate')

        if data.get('pbpk_bolus', '') and (not data.get('number_of_relevant_cells', '') or not data.get('total_device_volume', '')):
            raise forms.ValidationError('Bolus PBPK Requires Number of Cells Per MPS Model and Total Device Volume')

        # SLOPPY NOT DRY
        new_setup_data = {}
        new_matrix = None
        new_items = None
        new_related = None

        errors = {'organ_model': [], 'setup_data': []}
        current_errors = errors.get('setup_data')

        # study = super(AssayStudyFormNew, self).save(commit=False)

        if self.cleaned_data.get('setup_data', None):
            all_setup_data = json.loads(self.cleaned_data.get('setup_data', '[]'))
        else:
            all_setup_data = []

        # Never consider if no model
        if not self.cleaned_data.get('organ_model', None):
            all_setup_data = []

        # Catch technically empty setup data
        setup_data_is_empty = True

        for group_set in all_setup_data:
            if group_set:
                setup_data_is_empty = not any(group_set.values())

        if setup_data_is_empty:
            all_setup_data = []

        # if commit and all_setup_data:
        # SEE BASE MODELS FOR WHY COMMIT IS NOT HERE
        if all_setup_data:
            created_by = self.user
            created_on = timezone.now()

            current_item_number = 1

            # CRUDE: JUST MAKE ONE LARGE ROW?
            # number_of_items = 0
            #
            # for setup_group in all_setup_data:
            #     number_of_items += int(setup_group.get('number_of_items', '0'))

            # Find max for number of columns
            number_of_columns = 0
            for setup_group in all_setup_data:
                if int(setup_group.get('number_of_items', '0')) > number_of_columns:
                    number_of_columns = int(setup_group.get('number_of_items', '0'))

            new_matrix = AssayMatrix(
                name=data.get('name', ''),
                # Does not work with plates at the moment
                representation='chips',
                # study=self.instance,
                device=None,
                number_of_rows=len(all_setup_data),
                number_of_columns=number_of_columns,
                # number_of_rows=1,
                # number_of_columns=number_of_items,
                created_by=created_by,
                created_on=created_on,
                modified_by=created_by,
                modified_on=created_on,
            )

            try:
                new_matrix.full_clean(exclude=['study'])
            except forms.ValidationError as e:
                errors.get('organ_model').append(e.values())

            # new_matrix.save()

            # COMPOUND STUFF BECAUSE COMPOUND SCHEMA IS MISERABLE
            # Get all chip setup assay compound instances
            assay_compound_instances = {}

            # Get all Compound Instances
            compound_instances = {
                (
                    instance.compound.id,
                    instance.supplier.id,
                    instance.lot,
                    str(instance.receipt_date)
                ): instance for instance in CompoundInstance.objects.all().prefetch_related(
                    'compound',
                    'supplier'
                )
            }

            # Get all suppliers
            suppliers = {
                supplier.name: supplier for supplier in CompoundSupplier.objects.all()
            }

            new_items = []
            new_related = {}

            # NOTE: ROW IS DERIVED FROM THE GROUP IN QUESTION
            # ALL ITEMS IN THE GROUP ARE IN THE COLUMNS OF SAID ROW
            for setup_row, setup_group in enumerate(all_setup_data):
                items_in_group = int(setup_group.pop('number_of_items', '0'))
                test_type = setup_group.get('test_type', '')

                # To break out to prevent repeat errors
                group_has_error = False

                for iteration in range(items_in_group):
                    new_item = AssayMatrixItem(
                        # study=study,
                        # matrix=new_matrix,
                        name=str(current_item_number),
                        # JUST MAKE SETUP DATE THE STUDY DATE FOR NOW
                        setup_date=data.get('start_date', ''),
                        row_index=setup_row,
                        column_index=iteration,
                        # column_index=current_item_number-1,
                        # device=study.organ_model.device,
                        # organ_model=study.organ_model,
                        # organ_model_protocol=study.organ_model_protocol,
                        test_type=test_type,
                        created_by=created_by,
                        created_on=created_on,
                        modified_by=created_by,
                        modified_on=created_on,
                    )

                    try:
                        new_item.full_clean(exclude=[
                            'study',
                            'matrix',
                            'device',
                            'organ_model',
                            'organ_model_protocol',
                        ])
                        new_items.append(new_item)

                    except forms.ValidationError as e:
                        # raise forms.ValidationError(e)
                        errors.get('organ_model').append(e.values())
                        group_has_error = True

                    current_related_list = new_related.setdefault(
                        str(len(new_items)), []
                    )

                    # new_item.save()
                    for prefix, current_objects in setup_group.items():
                        for setup_column, current_object in enumerate(current_objects):
                            if prefix in ['cell', 'compound', 'setting'] and current_object:
                                current_object.update({
                                    'matrix_item': new_item,
                                })
                                if prefix == 'cell':
                                    new_cell = AssaySetupCell(**current_object)

                                    try:
                                        new_cell.full_clean(exclude=['matrix_item'])
                                        current_related_list.append(new_cell)
                                    except forms.ValidationError as e:
                                        # raise forms.ValidationError(e)
                                        current_errors.append(
                                            process_error_for_study_new(
                                                prefix,
                                                setup_row,
                                                setup_column,
                                                e
                                            )
                                        )
                                        group_has_error = True

                                    # new_cell.save()
                                elif prefix == 'setting':
                                    new_setting = AssaySetupSetting(**current_object)
                                    try:
                                        new_setting.full_clean(exclude=['matrix_item'])
                                        current_related_list.append(new_setting)
                                    except forms.ValidationError as e:
                                        # raise forms.ValidationError(e)
                                        current_errors.append(
                                            process_error_for_study_new(
                                                prefix,
                                                setup_row,
                                                setup_column,
                                                e
                                            )
                                        )
                                        group_has_error = True

                                    # new_setting.save()
                                elif prefix == 'compound':
                                    # CONFUSING NOT DRY BAD
                                    compound = int(current_object.get('compound_id', '0'))
                                    supplier_text = current_object.get('supplier_text', 'N/A').strip()
                                    lot_text = current_object.get('lot_text', 'N/A').strip()
                                    receipt_date = current_object.get('receipt_date', '')

                                    # NOTE THE DEFAULT, PLEASE DO THIS IN A WAY THAT IS MORE DRY
                                    if not supplier_text:
                                        supplier_text = 'N/A'

                                    if not lot_text:
                                        lot_text = 'N/A'

                                    # Check if the supplier already exists
                                    supplier = suppliers.get(supplier_text, '')

                                    concentration = current_object.get('concentration', '0')
                                    # Annoying, bad
                                    if not concentration:
                                        concentration = 0.0
                                    else:
                                        concentration = float(concentration)
                                    concentration_unit_id = int(current_object.get('concentration_unit_id', '0'))
                                    addition_location_id = int(current_object.get('addition_location_id', '0'))

                                    addition_time = current_object.get('addition_time', '0')
                                    duration = current_object.get('duration', '0')

                                    if not addition_time:
                                        addition_time = 0.0
                                    else:
                                        addition_time = float(addition_time)

                                    if not duration:
                                        duration = 0.0
                                    else:
                                        duration = float(duration)

                                    # Otherwise create the supplier
                                    if not supplier:
                                        supplier = CompoundSupplier(
                                            name=supplier_text,
                                            created_by=created_by,
                                            created_on=created_on,
                                            modified_by=created_by,
                                            modified_on=created_on,
                                        )
                                        try:
                                            supplier.full_clean()
                                            supplier.save()
                                        except forms.ValidationError as e:
                                            # raise forms.ValidationError(e)
                                            current_errors.append(
                                                process_error_for_study_new(
                                                    prefix,
                                                    setup_row,
                                                    setup_column,
                                                    e
                                                )
                                            )
                                            group_has_error = True

                                        suppliers.update({
                                            supplier_text: supplier
                                        })

                                    # FRUSTRATING EXCEPTION
                                    if not receipt_date:
                                        receipt_date = None

                                    # Check if compound instance exists
                                    compound_instance = compound_instances.get((compound, supplier.id, lot_text, str(receipt_date)), '')

                                    if not compound_instance:
                                        compound_instance = CompoundInstance(
                                            compound_id=compound,
                                            supplier=supplier,
                                            lot=lot_text,
                                            receipt_date=receipt_date,
                                            created_by=created_by,
                                            created_on=created_on,
                                            modified_by=created_by,
                                            modified_on=created_on,
                                        )
                                        try:
                                            compound_instance.full_clean()
                                            compound_instance.save()
                                        except forms.ValidationError as e:
                                            # raise forms.ValidationError(e)
                                            current_errors.append(
                                                process_error_for_study_new(
                                                    prefix,
                                                    setup_row,
                                                    setup_column,
                                                    e
                                                )
                                            )
                                            group_has_error = True

                                        compound_instances.update({
                                            (compound, supplier.id, lot_text, str(receipt_date)): compound_instance
                                        })

                                    # Save the AssayCompoundInstance
                                    conflicting_assay_compound_instance = assay_compound_instances.get(
                                        (
                                            # new_item.id,
                                            current_item_number,
                                            compound_instance.id,
                                            concentration,
                                            concentration_unit_id,
                                            addition_time,
                                            duration,
                                            addition_location_id
                                        ), None
                                    )
                                    if not conflicting_assay_compound_instance:
                                        new_compound = AssaySetupCompound(
                                            # matrix_item_id=new_item.id,
                                            compound_instance_id=compound_instance.id,
                                            concentration=concentration,
                                            concentration_unit_id=concentration_unit_id,
                                            addition_time=addition_time,
                                            duration=duration,
                                            addition_location_id=addition_location_id
                                        )

                                        try:
                                            new_compound.full_clean(exclude=['matrix_item'])
                                            current_related_list.append(new_compound)
                                        except forms.ValidationError as e:
                                            # raise forms.ValidationError(e)
                                            current_errors.append(
                                                process_error_for_study_new(
                                                    prefix,
                                                    setup_row,
                                                    setup_column,
                                                    e
                                                )
                                            )
                                            group_has_error = True

                                        # new_compound.save()

                                    assay_compound_instances.update({
                                        (
                                            # new_item.id,
                                            current_item_number,
                                            compound_instance.id,
                                            concentration,
                                            concentration_unit_id,
                                            addition_time,
                                            duration,
                                            addition_location_id
                                        ): True
                                    })

                    current_item_number += 1

                    # Don't keep iterating through this group if there is a problem
                    if group_has_error:
                        break

        if current_errors:
            errors.get('organ_model').append(['Please review the table below for errors.'])
            raise forms.ValidationError(errors)

        new_setup_data.update({
            'new_matrix': new_matrix,
            'new_items': new_items,
            'new_related': new_related,
        })

        data.update({
            'processed_setup_data': new_setup_data
        })

        return data

    def save(self, commit=True):
        # PLEASE SEE BASE MODELS
        # study = super(AssayStudyFormNew, self).save(commit)
        study = super(AssayStudyFormNew, self).save()

        # VERY SLOPPY
        created_by = self.user
        created_on = timezone.now()

        study.created_by = created_by
        study.created_on = created_on
        study.modified_by = created_by
        study.modified_on = created_on

        study.save()
        # SLOPPY: REVISE

        study_id = study.id

        if study.organ_model_id:
            device_id = study.organ_model.device_id
        else:
            device_id = None

        organ_model_id = study.organ_model_id
        organ_model_protocol_id = study.organ_model_protocol_id

        all_setup_data = self.cleaned_data.get('processed_setup_data', None)

        if all_setup_data:
            new_matrix = all_setup_data.get('new_matrix', None)
            new_items = all_setup_data.get('new_items', None)
            new_related = all_setup_data.get('new_related', None)

            if new_matrix:
                new_matrix.study_id = study_id
                new_matrix.save()
                new_matrix_id = new_matrix.id

                new_item_ids = {}

                for new_item in new_items:
                    # ADD MATRIX and tracking
                    new_item.matrix_id = new_matrix_id
                    new_item.study_id = study_id
                    new_item.device_id = device_id
                    new_item.organ_model_id = organ_model_id
                    new_item.organ_model_protocol_id = organ_model_protocol_id
                    new_item.save()

                    new_item_ids.update({
                        new_item.name: new_item.id
                    })

                for current_item_name, new_related_data_set in new_related.items():
                    new_item_id = new_item_ids.get(current_item_name, None)

                    if new_item_id:
                        for new_related_data in new_related_data_set:
                            # ADD MATRIX ITEM
                            new_related_data.matrix_item_id = new_item_id
                            new_related_data.save()

        return study


class AssayMatrixFormNew(SetupFormsMixin, SignOffMixin, BootstrapForm):
    # ADD test_types
    test_type = forms.ChoiceField(
        initial='control',
        choices=TEST_TYPE_CHOICES
    )

    class Meta(object):
        model = AssayMatrix
        # ODD
        fields = []

    def __init__(self, *args, **kwargs):
        """Init the Study Form

        Kwargs:
        user -- the user in question
        """
        # PROBABLY DON'T NEED THIS?
        # self.user = kwargs.pop('user', None)
        super(AssayMatrixFormNew, self).__init__(*args, **kwargs)

        # SLOPPY
        self.fields['test_type'].widget.attrs['class'] += ' no-selectize test-type'
        # Bad
        self.fields['test_type'].widget.attrs['style'] = 'width:100px;'


# PLEASE NOTE CRUDE HANDLING OF m2m
class AssayTargetForm(BootstrapForm):
    # For adding to category m2m
    category = forms.ModelMultipleChoiceField(
        queryset=AssayCategory.objects.all().order_by('name'),
        # Should this be required?
        required=False,
        # empty_label='All'
    )

    class Meta(object):
        model = AssayTarget
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(AssayTargetForm, self).__init__(*args, **kwargs)

        # Get category if possible
        if self.instance and self.instance.id:
            self.initial_categories = AssayCategory.objects.filter(
                targets__id=self.instance.id
            )
            self.fields['category'].initial = (
                self.initial_categories
            )
        else:
            self.initial_categories = AssayCategory.objects.none()

        # Sort the methods
        # Would it be better to have this applied to all method queries?
        self.fields['methods'].queryset = AssayMethod.objects.all().order_by('name')

    def save(self, commit=True):
        new_target = super(AssayTargetForm, self).save(commit)

        if commit:
            if self.cleaned_data.get('category', None):
                for current_category in self.cleaned_data.get('category', None):
                    current_category.targets.add(self.instance)

            # Permit removals for the moment
            # Crude removal
            for initial_category in self.initial_categories:
                if initial_category not in self.cleaned_data.get('category', None):
                    initial_category.targets.remove(self.instance)

        return new_target


class AssayTargetRestrictedForm(BootstrapForm):
    # For adding to category m2m
    category = forms.ModelMultipleChoiceField(
        queryset=AssayCategory.objects.all().order_by('name'),
        # Should this be required?
        required=False,
        # empty_label='All'
    )
    # We don't actually want restricted users to meddle with the methods straight (they could remove methods)
    method_proxy = forms.ModelMultipleChoiceField(
        queryset=AssayMethod.objects.all().order_by('name'),
        label='Methods'
    )

    class Meta(object):
        model = AssayTarget
        fields = ['category', 'method_proxy']

    def __init__(self, *args, **kwargs):
        super(AssayTargetRestrictedForm, self).__init__(*args, **kwargs)

        # Get category if possible
        # (It should always be possible, this form is for editing)
        if self.instance and self.instance.id:
            self.fields['category'].initial = (
                AssayCategory.objects.filter(
                    targets__id=self.instance.id
                )
            )
            self.fields['method_proxy'].initial = (
                self.instance.methods.all()
            )
    def save(self, commit=True):
        new_target = super(AssayTargetRestrictedForm, self).save(commit)

        if commit:
            if self.cleaned_data.get('category', None):
                for current_category in self.cleaned_data.get('category', None):
                    current_category.targets.add(self.instance)
            if self.cleaned_data.get('method_proxy', None):
                for current_method in self.cleaned_data.get('method_proxy', None):
                    self.instance.methods.add(current_method)

        return new_target


class AssayMethodForm(BootstrapForm):
    # For adding to target m2m
    targets = forms.ModelMultipleChoiceField(
        queryset=AssayTarget.objects.all().order_by('name'),
        # No longer required to prevent circularity with Target
        required=False
    )

    class Meta(object):
        model = AssayMethod
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(AssayMethodForm, self).__init__(*args, **kwargs)

        # Get target if possible
        if self.instance and self.instance.id:
            self.initial_targets = AssayTarget.objects.filter(
                methods__id=self.instance.id
            )
            self.fields['targets'].initial = (
                self.initial_targets
            )
        else:
            self.initial_targets = AssayTarget.objects.none()

    def save(self, commit=True):
        new_method = super(AssayMethodForm, self).save(commit)

        if commit:
            for current_target in self.cleaned_data.get('targets', None):
                current_target.methods.add(self.instance)

            # Permit removals for the moment
            # Crude removal
            for initial_target in self.initial_targets:
                if initial_target not in self.cleaned_data.get('targets', None):
                    initial_target.methods.remove(self.instance)

        return new_method


class AssayMethodRestrictedForm(BootstrapForm):
    # For adding to target m2m
    targets = forms.ModelMultipleChoiceField(
        queryset=AssayTarget.objects.all().order_by('name'),
        # No longer required to prevent circularity with Target
        required=False
    )

    class Meta(object):
        model = AssayMethod
        # Only include the target, we don't want anything else to change
        fields = ['targets']

    def __init__(self, *args, **kwargs):
        super(AssayMethodRestrictedForm, self).__init__(*args, **kwargs)

        # Get target if possible
        # (It should always be possible, this form is only for editing)
        if self.instance and self.instance.id:
            self.fields['targets'].initial = (
                AssayTarget.objects.filter(
                    methods__id=self.instance.id
                )
            )

    def save(self, commit=True):
        new_method = super(AssayMethodRestrictedForm, self).save(commit)

        if commit:
            # In the restricted form, one is allowed to add targets ONLY
            for current_target in self.cleaned_data.get('targets', None):
                current_target.methods.add(self.instance)

        return new_method


class PhysicalUnitsForm(BootstrapForm):
    class Meta(object):
        model = PhysicalUnits
        exclude = tracking + ('availability',)

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


class AssayMeasurementTypeForm(BootstrapForm):
    class Meta(object):
        model = AssayMeasurementType
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


class AssaySampleLocationForm(BootstrapForm):
    class Meta(object):
        model = AssaySampleLocation
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


class AssaySettingForm(BootstrapForm):
    class Meta(object):
        model = AssaySetting
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


class AssaySupplierForm(BootstrapForm):
    class Meta(object):
        model = AssaySupplier
        exclude = tracking

        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


#####
# sck - ASSAY PLATE MAP START


# monkey patch to display method target and unit combo as needed in the assay plate map page
class AbstractClassAssayStudyAssay(AssayStudyAssay):
    class Meta:
        proxy = True

    def __str__(self):
        # return 'TARGET: {0}  METHOD: {1}  UNIT: {2}'.format(self.target, self.method, self.unit)
        return '{2}  --- TARGET: {0} by METHOD: {1}'.format(self.target, self.method, self.unit)


# Get info to populate pick lists; no qc needed on this form, just to use on webpage to allow user selections
class AssayPlateReadMapAdditionalInfoForm(forms.Form):
    """Form for Assay Plate Reader Map add/update/view extra info for dropdowns that are just used in GUI (not saved)."""

    def __init__(self, *args, **kwargs):
        study_id = kwargs.pop('study_id', None)
        self.user = kwargs.pop('user', None)
        super(AssayPlateReadMapAdditionalInfoForm, self).__init__(*args, **kwargs)
        # note that the non-selectized versions are manipulated in javascript to facilitate the plate map
        # they are not displayed to the user (they are hidden)
        # something did very early in development...probably would do differently now
        self.fields['se_matrix_item'].queryset = AssayMatrixItem.objects.filter(study_id=study_id).order_by('name',)
        self.fields['ns_matrix_item'].queryset = AssayMatrixItem.objects.filter(study_id=study_id).order_by('name',)
        self.fields['ns_matrix_item'].widget.attrs.update({'class': 'no-selectize'})
        self.fields['ns_location'].widget.attrs.update({'class': 'no-selectize'})
        self.fields['se_matrix'].queryset = AssayMatrix.objects.filter(
            study_id=study_id
        ).order_by('name',)
        self.fields['se_matrix'].widget.attrs.update({'class': ' required'})
        self.fields['se_platemap'].queryset = AssayPlateReaderMap.objects.filter(
            study_id=study_id
        ).order_by('name',)
        self.fields['se_platemap'].widget.attrs.update({'class': ' required'})

    # before got to development of calibration/processing the data
    ns_matrix_item = forms.ModelChoiceField(
        queryset=AssayMatrixItem.objects.none(),
        required=False,
    )
    se_matrix_item = forms.ModelChoiceField(
        queryset=AssayMatrixItem.objects.none(),
        required=False,
    )
    se_matrix = forms.ModelChoiceField(
        queryset=AssayMatrix.objects.none(),
        required=False,
    )
    se_platemap = forms.ModelChoiceField(
        queryset=AssayPlateReaderMap.objects.none(),
        required=False,
    )
    se_main_well_use = forms.ChoiceField(
        choices=assay_plate_reader_main_well_use_choices
    )
    se_blank_well_use = forms.ChoiceField(
        choices=assay_plate_reader_blank_well_use_choices
    )
    se_time_unit = forms.ChoiceField(
        choices=assay_plate_reader_time_unit_choices
    )
    se_location = forms.ModelChoiceField(
         queryset=AssaySampleLocation.objects.all().order_by(
             'name'
         ),
         required=False,
    )
    ns_location = forms.ModelChoiceField(
         queryset=AssaySampleLocation.objects.all(),
         required=False,
    )
    se_increment_operation = forms.ChoiceField(
        choices=(('divide', 'Divide'), ('multiply', 'Multiply'), ('subtract', 'Subtract'), ('add', 'Add'))
    )
    form_number_time = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_time.widget.attrs.update({'class': 'form-control'})
    form_number_default_time = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_default_time.widget.attrs.update({'class': 'form-control'})
    form_number_standard_value = forms.DecimalField(
        required=False,
        initial=0,
    )
    form_number_standard_value.widget.attrs.update({'class': 'form-control'})
    form_number_dilution_factor = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_dilution_factor.widget.attrs.update({'class': 'form-control'})
    form_number_collection_volume = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_collection_volume.widget.attrs.update({'class': 'form-control'})
    form_number_collection_time = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_collection_time.widget.attrs.update({'class': 'form-control'})
    form_number_increment_value = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_number_increment_value.widget.attrs.update({'class': 'form-control'})


# Parent for plate reader map page
class AssayPlateReaderMapForm(BootstrapForm):
    """Form for Assay Plate Reader Map"""

    class Meta(object):
        model = AssayPlateReaderMap
        fields = [
            # 'id', do not need in queryset
            'name',
            'description',
            'device',
            'study_assay',
            'time_unit',
            'volume_unit',
            'standard_unit',
            'cell_count',
            'standard_molecular_weight',
            'well_volume'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        # self.user = kwargs.pop('user', None)
        super(AssayPlateReaderMapForm, self).__init__(*args, **kwargs)

        # need these or get blank study_assay in the update page (add page worked okay without)
        if not self.study and self.instance.study:
            self.study = self.instance.study
        if self.study:
            self.instance.study = self.study

        # plate map instance - note, based on model, this is the name, use .id for the pk
        my_instance = self.instance

        # note that, if leave selectize on, will need to change js file $("#id_device").val(matrix_size);
        # for tips on working with selectize, search in path for HANDY
        # self.fields['device'].widget.attrs['class'] += ' no-selectize'
        self.fields['name'].initial = "map-" + datetime.datetime.now().strftime("%Y%m%d")+"-"+datetime.datetime.now().strftime('%H:%M:%S')
        self.fields['name'].widget.attrs['class'] += ' required'
        self.fields['device'].widget.attrs['class'] += ' required'
        self.fields['time_unit'].widget.attrs['class'] += ' required'
        self.fields['standard_unit'].widget.attrs['class'] += ' required'
        self.fields['study_assay'].queryset = AbstractClassAssayStudyAssay.objects.filter(
            study_id=self.study
        ).prefetch_related(
            'target',
            'method',
            'unit',
        )
        self.fields['study_assay'].widget.attrs['class'] += ' required'
        # the selectize was causing PROBLEMS, I turned it off this field
        # HANDY - turn of selectize at the form level
        # self.fields['volume_unit'].widget.attrs.update({'class': 'no-selectize'})
        # self.fields['volume_unit'].widget.attrs['class'] += ' form-control'
        self.fields['standard_molecular_weight'].widget.attrs['class'] += ' form-control'

        ######
        # START section to deal with raw data showing in the plate map after file assignment
        # this will populate a dropdown that lets the user pick which file block to see on the page (map and calibrate)
        # For the dropdown, only look for those file blocks that have a populated file block id
        # get a record in the table with the plate index of 0 and that have a file block id
        as_value_formset_with_file_block = AssayPlateReaderMapItemValue.objects.filter(
            assayplatereadermap=my_instance.id
        ).prefetch_related(
            'assayplatereadermapitem',
        ).filter(
            assayplatereadermapitem__plate_index=0
        ).filter(
            assayplatereadermapdatafileblock__isnull=False
        ).order_by(
            'assayplatereadermapdatafileblock__id',
        )

        distinct_plate_map_with_select_string = []
        distinct_plate_map_with_block_pk = []
        number_filed_combos = len(as_value_formset_with_file_block)

        # print("print number of filed combos-forms.py: ", number_filed_combos)

        # queryset should have one record for each value SET that HAS a file-block associated to it
        # make a choice list/field for the file-block combos for this plate map
        if number_filed_combos > 0:
            i = 0
            for record in as_value_formset_with_file_block:
                short_file_name = os.path.basename(str(record.assayplatereadermapdatafile.plate_reader_file))
                data_block_label = str(record.assayplatereadermapdatafileblock.data_block)
                data_block_metadata = record.assayplatereadermapdatafileblock.data_block_metadata
                # data_file_id_str = str(record.assayplatereadermapdatafile.id)
                data_file_block_id_str = str(record.assayplatereadermapdatafileblock.id)
                # make a choice tuple list for showing selections and a choice tuple list of containing the file pk and block pk for javascript
                pick_value = str(i)
                pick_string = 'FILE: ' + short_file_name + ' BLOCK: ' + data_block_label + '  ' + data_block_metadata
                # pick_string_pk = data_file_id_str + '-' + data_file_block_id_str
                pick_string_block_pk = data_file_block_id_str
                distinct_plate_map_with_select_string.append((pick_value, pick_string))
                distinct_plate_map_with_block_pk.append((pick_value, pick_string_block_pk))
                # print("looking for unique blocks counter ", i)
                i = i + 1

        # self.fields['ns_file_pk_block_pk'].widget.attrs['class'] += ' no-selectize'
        self.fields['form_number_file_block_combos'].required = False
        self.fields['form_number_file_block_combos'].initial = number_filed_combos

        # file block options associated with a specific plate map
        self.fields['se_block_select_string'].required = False
        self.fields['se_block_select_string'].widget.attrs['class'] += ' required'
        self.fields['se_block_select_string'].choices = distinct_plate_map_with_select_string
        self.fields['ns_block_select_pk'].required = False
        self.fields['ns_block_select_pk'].widget.attrs.update({'class': 'no-selectize'})
        self.fields['ns_block_select_pk'].choices = distinct_plate_map_with_block_pk

        self.fields['se_form_calibration_curve'].widget.attrs.update({'class': ' required'})
        self.fields['form_make_mifc_on_submit'].widget.attrs.update({'class': ' big-checkbox'})
        self.fields['se_form_calibration_curve'].required = False
        self.fields['se_form_blank_handling'].required = False
        self.fields['radio_replicate_handling_average_or_not'].required = False

        # HANDY - save problems, this is likely the cause (required fields!)
        # self.fields['form_data_processing_multiplier_string'].required = False
        #
        # self.fields['form_data_processing_multiplier_string_short'].required = False
        # self.fields['form_data_processing_multiplier_value_short'].required = False

        # these multiplier fields were added to explain the multiplier in a table
        # the long string was unacceptable to the project PI
        # these really don't have to be form fields (not needed for data processing), but it was just easier/faster
        # self.fields['form_data_processing_multiplier_string1'].required = False
        # self.fields['form_data_processing_multiplier_string2'].required = False
        # self.fields['form_data_processing_multiplier_string3'].required = False
        # self.fields['form_data_processing_multiplier_string4'].required = False
        # self.fields['form_data_processing_multiplier_string5'].required = False
        # self.fields['form_data_processing_multiplier_string6'].required = False
        # self.fields['form_data_processing_multiplier_string7'].required = False
        # self.fields['form_data_processing_multiplier_string8'].required = False
        # self.fields['form_data_processing_multiplier_string9'].required = False

        # calibration fields - only a few are really needed as form fields (eg the calibration curve used, bounds)
        # many are not really needed in the data processing and could be handled differently
        self.fields['form_data_parsable_message'].required = False
        self.fields['form_calibration_curve_method_used'].required = False
        # self.fields['form_calibration_equation'].required = False
        # self.fields['form_calibration_rsquared'].required = False

        # self.fields['form_calibration_parameter_1_string'].required = False
        # self.fields['form_calibration_parameter_2_string'].required = False
        # self.fields['form_calibration_parameter_3_string'].required = False
        # self.fields['form_calibration_parameter_4_string'].required = False
        # self.fields['form_calibration_parameter_5_string'].required = False
        # self.fields['form_calibration_parameter_1_value'].required = False
        # self.fields['form_calibration_parameter_2_value'].required = False
        # self.fields['form_calibration_parameter_3_value'].required = False
        # self.fields['form_calibration_parameter_4_value'].required = False
        # self.fields['form_calibration_parameter_5_value'].required = False
        self.fields['form_calibration_standard_fitted_min_for_e'].required = False
        self.fields['form_calibration_standard_fitted_max_for_e'].required = False
        self.fields['form_calibration_sample_blank_average'].required = False
        self.fields['form_calibration_standard_standard0_average'].required = False
        self.fields['form_calibration_method'].required = False
        self.fields['form_calibration_target'].required = False
        self.fields['form_calibration_unit'].required = False
        self.fields['form_number_standards_this_plate'].required = False
        self.fields['form_hold_the_data_block_metadata_string'].required = False
        self.fields['form_hold_the_omits_string'].required = False
        self.fields['form_hold_the_notes_string'].required = False

        # Need a valid choice field.
        # When the selected plate map has standards, the user will never see this field and will not need it.
        # If the plate does not have standards, the user will need the option to pick to borrow standards from another plate.
        # Lab representative (ie Richard) indicated that standards, standard blanks, and sample blanks would all be borrowed from the same plate!

        # does this plate map have standards?
        does_this_plate_have_standards = AssayPlateReaderMapItem.objects.filter(
            assayplatereadermap=my_instance.id
        ).filter(
            well_use='standard'
        )
        number_standards_wells_on_plate = len(does_this_plate_have_standards)

        choiceBorrowData = (0, 'Select One'),
        choiceBorrowDataToPlateMap = (0, 0),

        if number_standards_wells_on_plate > 0:
            # left - file block pk in both
            # right is a string of the data block meta data for selection of data block pk (left)
            choiceBorrowData = choiceBorrowData
            # right is plate map pk
            choiceBorrowDataToPlateMap = choiceBorrowDataToPlateMap
        else:
            # if we have to borrow standards, need a list to pick from - add to choiceBorrowData
            # need to borrow standards from another plate
            # 20200510 - moving this to here from ajax call. Might move back depending on performance.
            # most users will not do it this way....
            as_value_formset_with_file_block_standard = AssayPlateReaderMapItemValue.objects.filter(
                study_id=self.study
            ).filter(
                assayplatereadermapdatafileblock__isnull=False
            ).prefetch_related(
                'assayplatereadermapdatafileblock',
                'assayplatereadermap',
                'assayplatereadermapitem',
            ).filter(
                assayplatereadermapitem__well_use='standard'
            ).order_by(
                'assayplatereadermapdatafileblock__id', 'assayplatereadermapitem__well_use'
            )

            # print('as_value_formset_with_file_block_standard')
            # print(as_value_formset_with_file_block_standard)

            prev_file = "none"
            prev_data_block_file_specific_pk = 0

            # queryset should have one record for each value SET that HAS a file-block and at least one standard associated to it
            if len(as_value_formset_with_file_block_standard) > 0:
                for record in as_value_formset_with_file_block_standard:

                    short_file_name = os.path.basename(str(record.assayplatereadermapdatafile.plate_reader_file))
                    # this is the data block of the file (for file 0 to something...)
                    data_block_file_specific_pk = record.assayplatereadermapdatafileblock.data_block

                    if prev_file == short_file_name and prev_data_block_file_specific_pk == data_block_file_specific_pk:
                        pass
                    else:
                        data_platemap_pk = record.assayplatereadermap_id
                        data_platemap_name = record.assayplatereadermap.name
                        data_block_metadata = record.assayplatereadermapdatafileblock.data_block_metadata
                        data_block_database_pk = record.assayplatereadermapdatafileblock.id

                        # make a choice tuple list for showing selections and a choice tuple list of containing the file pk and block pk for javascript
                        pick_string = 'PLATEMAP: ' + data_platemap_name + '  FILE: ' + short_file_name + '  BLOCK: ' + data_block_metadata + ' (' + str(
                            data_block_file_specific_pk) + ')'

                        addString1 = (data_block_database_pk, pick_string),
                        choiceBorrowData = choiceBorrowData + addString1
                        addString2 = (data_block_database_pk, data_platemap_pk),
                        choiceBorrowDataToPlateMap = choiceBorrowDataToPlateMap + (addString2)

                    prev_file = short_file_name
                    prev_data_block_file_specific_pk = data_block_file_specific_pk

        # print('choiceBorrowData')
        # print(choiceBorrowData)
        # print('choiceBorrowDataToPlateMap')
        # print(choiceBorrowDataToPlateMap)

        self.fields['se_block_standard_borrow_string'].choices = choiceBorrowData
        self.fields['ns_block_standard_borrow_string_to_block_pk_back_to_platemap_pk'].choices = choiceBorrowDataToPlateMap
        self.fields['ns_block_standard_borrow_string_to_block_pk_back_to_platemap_pk'].required = False
        self.fields['se_block_standard_borrow_string'].widget.attrs['class'] += ' required'
        self.fields['se_block_standard_borrow_string'].required = False

    # enable the selection of a plate to borrow standards from by letting the user see a string of info about the DATA BLOCK (not just the plate map!)
    se_block_standard_borrow_string = forms.ChoiceField()
    ns_block_standard_borrow_string_to_block_pk_back_to_platemap_pk = forms.ChoiceField()

    # pk of the file block borrowing when no standards on the current plate (store it here)
    form_block_standard_borrow_pk_single_for_storage = forms.IntegerField(
        required=False,
    )
    # pk of the plate map associated with the file block borrowing when no standards on the current plate (store it here)
    form_block_standard_borrow_pk_platemap_single_for_storage = forms.IntegerField(
        required=False,
    )
    # here here, remove these next two after checking other way works
    # form_hold_the_study_id = forms.IntegerField(
    #     required=False,
    # )
    # form_hold_the_platemap_id = forms.IntegerField(
    #     required=False,
    # )
    form_hold_the_data_block_metadata_string = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_hold_the_omits_string = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_hold_the_notes_string = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_block_file_data_block_selected_pk_for_storage = forms.IntegerField(
        required=False,
    )

    form_number_file_block_combos = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # string of selected file block (selected in dropdown)
    se_block_select_string = forms.ChoiceField()
    # pk of selected file block (stays lined up with the string)
    ns_block_select_pk = forms.ChoiceField()

    # END section to deal with raw data showing in the plate map after file assignment and deal with standard in a different file block

    # print(calibration_choices)

    # processing the data fields added
    se_form_calibration_curve = forms.ChoiceField(
        choices=(
            calibration_choices
            # ('select_one', 'Select One'),
            # ('no_calibration', 'No Calibration'),
            # ('best_fit', 'Best Fit'),
            # ('logistic4', '4 Parameter Logistic w/fitted bounds'),
            # ('logistic4a0', '4 Parameter Logistic w/lower bound = 0'),
            # ('logistic4f', '4 Parameter Logistic w/user specified bound(s)'),
            # ('linear', 'Linear w/fitted intercept'),
            # ('linear0', 'Linear w/intercept = 0'),
            # ('log', 'Logarithmic'),
            # ('poly2', 'Quadratic Polynomial'),

            # ('select_one', 'Select One (n = standard concentration, s = signal)'),
            # ('no_calibration', 'No Calibration'),
            # ('best_fit', 'Best Fit'),
            # ('logistic4', '4 Parameter Logistic (s = ((A-D)/(1.0+((n/C)**B))) + D)'),
            # ('linear', 'Linear w/fitted intercept (s = B*n + A)'),
            # ('linear0', 'Linear w/intercept = 0 (s = B*n)'),
            # ('log', 'Logarithmic (s = B*ln(n) + A)'),
            # ('poly2', 'Polynomial (s = C*n**2 + B*n + A)'),

            )
    )

    # forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # se_form_blank_handling = forms.ChoiceField(widget=forms.RadioSelect(attrs={'disabled': 'disabled'}),
    se_form_blank_handling = forms.ChoiceField(
        choices=(('subtracteachfromeach', 'Subtracting Average STANDARD Blanks from STANDARDS and Average SAMPLE Blanks from SAMPLES'),
                 ('subtractstandardfromstandard', 'Subtracting Average STANDARD Blanks from STANDARDS (ignore sample blanks)'),
                 ('subtractsamplefromsample', 'Subtracting Average SAMPLE Blanks from SAMPLES (ignore standard blanks)'),
                 ('subtractstandardfromall', 'Subtracting Average STANDARD Blanks from the STANDARDS and SAMPLES'),
                 ('subtractsamplefromall', 'Subtracting Average SAMPLE Blanks from the STANDARDS and SAMPLES'),
                 ('ignore', 'Ignoring the Blanks')), initial='subtracteachfromeach'
    )

    form_min_standard = forms.DecimalField(
        required=False,

    )
    form_min_standard.widget.attrs.update({'class': 'form-control'})

    form_max_standard = forms.DecimalField(
        required=False,

    )
    form_max_standard.widget.attrs.update({'class': 'form-control'})

    form_logistic4_A = forms.DecimalField(
        required=False,

    )
    form_logistic4_A.widget.attrs.update({'class': 'form-control'})

    form_logistic4_D = forms.DecimalField(
        required=False,
    )
    form_logistic4_D.widget.attrs.update({'class': 'form-control'})

    form_data_processing_multiplier = forms.DecimalField(
        required=False,
        initial=1,
    )
    form_data_processing_multiplier.widget.attrs.update({'class': 'form-control'})

    # works but only one line
    # form_data_processing_multiplier_string = forms.CharField(
    #     required=False,
    #     initial="",
    # )
    # works but only one line
    # form_data_processing_multiplier_string = forms.CharField()
    # form_data_processing_multiplier_string.widget.attrs.update({'required': False, 'initial': ""})

    # HANDY - how to make an extra field a widget so can manipulate it eg readonly
    # form_data_processing_multiplier_string = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 3, 'readonly': 'readonly', 'required': False})
    # )
    #
    # form_data_processing_multiplier_string_short = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 1, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_value_short = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 1, 'readonly': 'readonly'}))
    #
    # form_data_processing_multiplier_string1 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string2 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string3 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string4 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string5 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string6 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string7 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string8 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    # form_data_processing_multiplier_string9 = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))

    form_data_parsable_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'readonly': 'readonly', 'required': False})
    )

    form_calibration_curve_method_used = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'required': False, 'initial': '-'})
    )

    # form_calibration_equation = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly', 'required': False, 'initial': '-'})
    # )
    # form_calibration_rsquared = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )

    radio_replicate_handling_average_or_not = forms.ChoiceField(
        # widget=forms.RadioSelect(attrs={'id': 'value'}),
        widget=forms.RadioSelect,
        choices=[
            ('average', 'Show Averages the Replicate Samples'),
            ('each', 'Show Each Sample')])
            # ('average', 'Send the Average of the Replicates to the Study Summary'),
            # ('each', 'Send Each Replicates Value to the Study Summary')])
    radio_standard_option_use_or_not = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect,
        choices=[('no_calibration', 'No Calibration'), ('pick_block', 'Pick a Block of Data with Standards')])

    # going to need to pass some calibration parameters
    # think the max I will need is 5 for 5 parameter logistic
    # going to need to keep track of order
    # form_calibration_parameter_1_string = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_2_string = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    # )
    # form_calibration_parameter_3_string = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    # )
    # form_calibration_parameter_4_string = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    # )
    # form_calibration_parameter_5_string = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_1_value = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_2_value = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_3_value = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_4_value = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    # form_calibration_parameter_5_value = forms.CharField(
    #     widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    # )
    form_calibration_standard_fitted_min_for_e = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    )
    form_calibration_standard_fitted_max_for_e = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    )
    form_calibration_sample_blank_average = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    )
    form_calibration_standard_standard0_average = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly','initial': '-'})
    )
    form_calibration_method = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_calibration_target = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_calibration_unit = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'initial': '-'})
    )
    form_number_standards_this_plate = forms.IntegerField(
        required=False,
        initial=1,
    )
    form_make_mifc_on_submit = forms.BooleanField(required=False)

    # Let them name the maps the same if they really want to. Does not really matter to me
    # def clean(self):
    #     # FORCE UNIQUE - this will return back to the form instead of showing the user an error
    #     cleaned_data = super(AssayPlateReaderMapForm, self).clean()
    #
    #     if AssayPlateReaderMap.objects.filter(
    #             study_id=self.instance.study.id,
    #             name=self.cleaned_data.get('name', '')
    #     ).exclude(pk=self.instance.pk).count():
    #         raise forms.ValidationError({'name': ['Plate Map name must be unique within study. This plate map is now corrupted. Go back to the Plate Map List and click to Add Plate Map and start again.']})
    #
    #     return cleaned_data

    def clean(self):
        # First thing in clean
        # Call super for data
        data = super(AssayPlateReaderMapForm, self).clean()
        # After initial stuff done
        self.process_file(save=False, calledme='clean')
        return data

    def save(self, commit=True):
                # First thing in save
        # Make sure to pass commit to the super call (don't want accidental saves)
        map = super(AssayPlateReaderMapForm, self).save(commit=commit)

        # Only save the file if commit is true
        if commit:
            self.process_file(save=True, calledme="save")
        return map

    def process_file(self, save=False, calledme="c"):
        #### START When saving AssayPlateReaderMapUpdate after a calibration
        # if user checked the box to send to study summary, make that happen

        data = self.cleaned_data
        # study = get_object_or_404(AssayStudy, pk=self.kwargs['study_id'])

        if data.get('form_make_mifc_on_submit'):
            # search term MIFC - if MIFC changes, this will need changed
            # make a list of column headers for the mifc file
            # could use COLUMN_HEADERS, but need to append one
            column_table_headers_average = [
                'Chip ID',
                'Cross Reference',
                'Assay Plate ID',
                'Assay Well ID',
                'Day',

                'Hour',
                'Minute',
                'Target/Analyte',
                'Subtarget',
                'Method/Kit',

                'Sample Location',
                'Value',
                'Value Unit',
                'Replicate',
                'Caution Flag',

                'Exclude',
                'Notes',
                'Processing Details',
            ]
            # search term MIFC - if MIFC changes, this will need changed
            # Make a dictionary of headers in utils and header needed in the mifc file
            utils_key_column_header = {
                'matrix_item_name': 'Chip ID',
                'cross_reference': 'Cross Reference',
                'plate_name': 'Assay Plate ID',
                'well_name': 'Assay Well ID',
                'day': 'Day',
                'hour': 'Hour',
                'minute': 'Minute',
                'target': 'Target/Analyte',
                'subtarget': 'Subtarget',
                'method': 'Method/Kit',
                'location_name': 'Sample Location',
                'processed_value': 'Value',
                'unit': 'Value Unit',
                'replicate': 'Replicate',
                'caution_flag': 'Caution Flag',
                'exclude': 'Exclude',
                'notes': 'Notes',
                'sendmessage': 'Processing Details'}

            # print(".unit ",data.get('standard_unit').unit)
            # print(".id ", data.get('standard_unit').id)
            # .unit
            # µg / mL
            # .id
            # 6
            # print(".unit ",data.get('standard_unit').unit)
            # print(".id ", data.get('standard_unit').id)

            if data.get('form_block_standard_borrow_pk_single_for_storage') == None:
                borrowed_block_pk = -1
            else:
                borrowed_block_pk = data.get('form_block_standard_borrow_pk_single_for_storage')

            if data.get('form_block_standard_borrow_pk_platemap_single_for_storage') == None:
                borrowed_platemap_pk = -1
            else:
                borrowed_platemap_pk = data.get(
                    'form_block_standard_borrow_pk_platemap_single_for_storage')

            # 20201104 when no_calibration is selected, the _used field does not get populated..deal with it here
            use_curve = 'no_calibration'
            use_curve_long = data.get('form_calibration_curve_method_used')
            if data.get('se_form_calibration_curve') == 'no_calibration' or data.get('se_form_calibration_curve') == 'select_one':
                use_curve_long = 'no_calibration'
            else:
                use_curve = find_a_key_by_value_in_dictionary(CALIBRATION_CURVE_MASTER_DICT, use_curve_long)

            if len(use_curve.strip()) == 0:
                err_msg = "The calibration method " + use_curve_long + " was not found in the cross reference list."
                # print(err_msg)
                raise forms.ValidationError(err_msg)

            # form.instance.study
            # make a dictionary to send to the utils.py when call the function
            set_dict = {
                'called_from': 'form_save',
                'study': self.instance.study.id,
                'pk_platemap': self.instance.id,
                'pk_data_block': data.get('form_block_file_data_block_selected_pk_for_storage'),
                'plate_name': data.get('name'),
                'form_calibration_curve': use_curve,
                'multiplier': data.get('form_data_processing_multiplier'),
                'unit': data.get('form_calibration_unit'),
                'standard_unit': data.get('standard_unit').unit,
                'form_min_standard': data.get('form_calibration_standard_fitted_min_for_e'),
                'form_max_standard': data.get('form_calibration_standard_fitted_max_for_e'),
                'form_logistic4_A': data.get('form_logistic4_A'),
                'form_logistic4_D': data.get('form_logistic4_D'),
                'form_blank_handling': data.get('se_form_blank_handling'),
                'radio_standard_option_use_or_not': data.get('radio_standard_option_use_or_not'),
                'radio_replicate_handling_average_or_not_0': data.get(
                    'radio_replicate_handling_average_or_not'),
                'borrowed_block_pk': borrowed_block_pk,
                'borrowed_platemap_pk': borrowed_platemap_pk,
                'count_standards_current_plate': data.get('form_number_standards_this_plate'),
                'target': data.get('form_calibration_target'),
                'method': data.get('form_calibration_method'),
                'time_unit': data.get('time_unit'),
                'volume_unit': data.get('volume_unit'),
                'user_notes': data.get('form_hold_the_notes_string'),
                'user_omits': data.get('form_hold_the_omits_string'),
                'plate_size': data.get('device'),
            }

            # this function is in utils.py that returns data
            data_mover = plate_reader_data_file_process_data(set_dict)
            # what comes back is a dictionary of
            list_of_dicts = data_mover[9]
            list_of_lists_mifc_headers_row_0 = [None] * (len(list_of_dicts) + 1)
            list_of_lists_mifc_headers_row_0[0] = column_table_headers_average
            i = 1
            # print(" ")
            for each_dict_in_list in list_of_dicts:
                list_each_row = []
                for this_mifc_header in column_table_headers_average:
                    # print("this_mifc_header ", this_mifc_header)
                    # find the key in the dictionary that we need
                    utils_dict_header = find_a_key_by_value_in_dictionary(utils_key_column_header,
                                                                          this_mifc_header)
                    # print("utils_dict_header ", utils_dict_header)
                    # print("this_mifc_header ", this_mifc_header)
                    # get the value that is associated with this header in the dict
                    this_value = each_dict_in_list.get(utils_dict_header)
                    # print("this_value ", this_value)
                    # add the value to the list for this dict in the list of dicts
                    list_each_row.append(this_value)
                # when down with the dictionary, add the completely list for this row to the list of lists
                # print("list_each_row ", list_each_row)
                list_of_lists_mifc_headers_row_0[i] = list_each_row
                i = i + 1

            # print("  ")
            # print('list_of_lists_mifc_headers_row_0')
            # print(list_of_lists_mifc_headers_row_0)
            # print("  ")

            # First make a csv from the list_of_lists (using list_of_lists_mifc_headers_row_0)

            # or self.objects.study
            my_study = self.instance.study
            # my_user = self.request.user
            my_user = self.user
            my_platemap = self.instance
            my_data_block_pk = data.get('form_block_file_data_block_selected_pk_for_storage')

            platenamestring1 = str(my_platemap)
            metadatastring1 = str(data.get('form_hold_the_data_block_metadata_string'))

            # print("study ",my_study)
            # print("platemap ",my_platemap)
            # print("user ",my_user)
            # print("data block ", my_data_block_pk)

            # Specify the file for use with the file uploader class
            # some of these caused errors in the file name so remove them
            # Luke and Quinn voted for all the symbols out instead of a few

            platenamestring = re.sub('[^a-zA-Z0-9_]', '', platenamestring1)
            metadatastring = re.sub('[^a-zA-Z0-9_]', '', metadatastring1)

            name_the_file = 'PLATE-{}-{}--METADATA-{}-{}'.format(
                                my_platemap.id, platenamestring,
                                my_data_block_pk, metadatastring
                            )
            # print("name_the_file ",name_the_file)

            bulk_location = upload_file_location(
                my_study,
                name_the_file
            )

            # Make sure study has directories
            if not os.path.exists(MEDIA_ROOT + '/data_points/{}'.format(my_study.id)):
                os.makedirs(MEDIA_ROOT + '/data_points/{}'.format(my_study.id))

            # Need to import from models
            # Avoid magic string, use media location
            file_location = MEDIA_ROOT.replace('mps/../', '', 1) + '/' + bulk_location + '.csv'

            # Should make a csv writer to avoid repetition
            file_to_write = open(file_location, 'w')
            csv_writer = csv.writer(file_to_write, dialect=csv.excel)

            # Add the UTF-8 BOM
            list_of_lists_mifc_headers_row_0[0][0] = '\ufeff' + list_of_lists_mifc_headers_row_0[0][0]

            # print("!!!!!!!!")
            # Write the lines here here uncomment this
            i = 0
            for one_line_of_data in list_of_lists_mifc_headers_row_0:
                print(i, "-", one_line_of_data)
                csv_writer.writerow(one_line_of_data)
                i = i + 1

            file_to_write.close()
            new_mifc_file = open(file_location, 'rb')

            file_processor = AssayFileProcessor(new_mifc_file,
                                                my_study,
                                                my_user, save=save,
                                                full_path='/media/' + bulk_location + '.csv')

            # Process the file
            file_processor.process_file()
        #### END When saving AssayPlateReaderMapUpdate after a calibration


# this finds the key for the value provided as thisHeader
def find_a_key_by_value_in_dictionary(this_dict, this_header):
    """This is a function to find a key by value."""
    my_key = ''
    for key, value in this_dict.items():
        if value == this_header:
            my_key = key
            break
    return my_key

# There should be a complete set of items for each saved plate map (one for each well in the selected plate)
class AssayPlateReaderMapItemForm(forms.ModelForm):
    """Form for Assay Plate Reader Map Item"""

    class Meta(object):
        model = AssayPlateReaderMapItem
        # exclude = tracking + ('study',)
        fields = [
            # 'id', do not need
            'matrix_item',
            'location',
            'name',
            # 'row_index',
            # 'column_index',
            'plate_index',
            'standard_value',
            'dilution_factor',
            'collection_volume',
            'collection_time',
            'default_time',
            'well_use',
        ]

    # keep here for reference of what not to do if want form to be selectized
    # def __init__(self, *args, **kwargs):
    #     super(AssayPlateReaderMapItemForm, self).__init__(*args, **kwargs)
    #     self.fields['name'].widget.attrs.update({'class': ' no-selectize'})

    # # 20200428 for user entered information
    # # 20200609 these are adding too much overhead, and did not use in data process, so remove these
    # form_user_entered_notes = forms.CharField(
    #     initial='-',
    #     required=False,
    #     widget=forms.Textarea(attrs={'cols': 10, 'rows': 1}),
    # )
    # form_user_entered_omit_from_average = forms.BooleanField(required=False, )

###########
# 20200522 getting rid of the value form all together since not allowing editing after values attached to plate map.
# GET RID OF THIS
# # Item VALUES are sets that correspond to items. Each set should have a match to a well in the plate map.
# # If not file/blocks attached to plate map, will have one set of values (with one value for each item)
# # If one file/block attached to plate map, will have two sets of values (one for the file, one null file) etc.
# class AssayPlateReaderMapItemValueForm(forms.ModelForm):
#     """Form for Assay Plate Reader Map Item Value"""
#
#     # 20200113 - changing so this formset is only called when adding and when update or view when no data are yet attached
#
#     class Meta(object):
#         model = AssayPlateReaderMapItemValue
#         # it is worth noting that there is a nuance to excluding or setting fields
#         # exclude = tracking + ('study', )
#         fields = [
#             # 'id', do not need
#             # 'assayplatereadermapdatafile', do not need
#             # 'assayplatereadermapitem', do not need
#             # next item - can remove later - do not need since, if there are matches, this formset will not be called
#             # but check rest is working first since will also affect formset (the custom_fields)
#             # 'assayplatereadermapdatafileblock',
#             'plate_index',
#             'raw_value',
#             'time',
#             'well_use',
#         ]
###########


# Formset for items
# IMPORTANT - custom_fields remove the select options for all the formsets - saves ALOT of page load time is long lists
class AssayPlateReaderMapItemFormSet(BaseInlineFormSetForcedUniqueness):
    custom_fields = (
        'matrix_item',
        'location',
    )

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayPlateReaderMapItemFormSet, self).__init__(*args, **kwargs)

        if not self.study:
            self.study = self.instance.study

        # use the filter to get matrix items in this study ONLY - makes the dic much smaller
        # HANDY - this speed up the custom_fields
        filters = {'matrix_item': {'study_id': self.study.id}}
        self.dic = get_dic_for_custom_choice_field(self, filters=filters)
        for form in self.forms:
            for field in self.custom_fields:
                form.fields[field] = DicModelChoiceField(field, self.model, self.dic)

            if self.study:
                form.instance.study = self.study
            if form.instance.pk:
                form.instance.modified_by = self.user
            else:
                form.instance.created_by = self.user

        # print(self.queryset)

###########
# 20200522 getting rid of the value form all together since not allowing editing after values attached to plate map.
# # GET RID OF THIS
# # Formset for item values
# class AssayPlateReaderMapItemValueFormSet(BaseInlineFormSetForcedUniqueness):
#     # changed way this worked on 20200114 and do not need this field any more
#     # custom_fields = (
#     #     'assayplatereadermapdatafileblock',
#     # )
#
#     def __init__(self, *args, **kwargs):
#         self.study = kwargs.pop('study', None)
#         self.user = kwargs.pop('user', None)
#         super(AssayPlateReaderMapItemValueFormSet, self).__init__(*args, **kwargs)
#
#         if not self.study:
#             self.study = self.instance.study
#
#         # changed way this worked on 20200114 and do not need this field any more - skip making the dic...
#         # # use the filter to get matrix items in this study ONLY - makes the dic much smaller
#         # # this speed up the custom_fields
#         # filters = {'assayplatereadermapdatafileblock': {'study_id': self.study.id}}
#         # self.dic = get_dic_for_custom_choice_field(self, filters=filters)
#         # # print(self.dic)
#         #
#         for form in self.forms:
#             # for field in self.custom_fields:
#             #     form.fields[field] = DicModelChoiceField(field, self.model, self.dic)
#
#             if self.study:
#                 form.instance.study = self.study
#             if form.instance.pk:
#                 form.instance.modified_by = self.user
#             else:
#                 form.instance.created_by = self.user
#
#         # HANDY had this up before the self.forms loop, but needed to move it down to work
#         # HANDY to know how to print a queryset to the console
#         # self.queryset = self.queryset.order_by('assayplatereadermapdatafile', 'assayplatereadermapdatafileblock', 'plate_index')
#         # https://stackoverflow.com/questions/13387446/changing-the-display-order-of-forms-in-a-formset
#         # print(self.queryset)
#         self.queryset = self.queryset.order_by('assayplatereadermapdatafileblock', 'plate_index')
#         # print(self.queryset)
###########


# Formset factory for item and value
# https://stackoverflow.com/questions/29881734/creating-django-form-from-more-than-two-models
AssayPlateReaderMapItemFormSetFactory = inlineformset_factory(
    AssayPlateReaderMap,
    AssayPlateReaderMapItem,
    formset=AssayPlateReaderMapItemFormSet,
    form=AssayPlateReaderMapItemForm,
    extra=1,
    exclude=tracking + ('study',),
)

###########
# 20200522 getting rid of the value form all together since not allowing editing after values attached to plate map.
# # GET RID OF THIS
# AssayPlateReaderMapItemValueFormSetFactory = inlineformset_factory(
#     AssayPlateReaderMap,
#     AssayPlateReaderMapItemValue,
#     formset=AssayPlateReaderMapItemValueFormSet,
#     form=AssayPlateReaderMapItemValueForm,
#     extra=1,
#     exclude=tracking + ('study',),
# )
##########


# end plate reader map page
#####


#####
# Start plate reader file page

# Add a plate reader file to the study (just add the file and check the file extension, no data processing)
class AssayPlateReaderMapDataFileAddForm(BootstrapForm):
    """Form for Plate Reader Data File Upload"""

    class Meta(object):
        model = AssayPlateReaderMapDataFile
        fields = ('plate_reader_file', )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.study = kwargs.pop('study', None)
        super(AssayPlateReaderMapDataFileAddForm, self).__init__(*args, **kwargs)

        # need or blank study_assay in the update page (add page worked okay)
        if not self.study and self.instance.study:
            self.study = self.instance.study
        if self.study:
            self.instance.study = self.study

    # check the file extension of the loaded file to make sure the user is not adding spreadsheet files
    # https://medium.com/@literallywords/server-side-file-extension-validation-in-django-2-1-b8c8bc3245a0
    def clean_plate_reader_file(self):
        data = self.cleaned_data['plate_reader_file']
        # Run file extension check
        file_extension = os.path.splitext(data.name)[1]
        if file_extension not in ['.csv', '.tsv', '.txt']:
            if '.xl' in file_extension or '.wk' in file_extension or '.12' in file_extension:
                raise ValidationError(
                     "This appears to be an spreadsheet file. To upload, export to a tab delimited file and try again.",
                     code='invalid'
                )
            else:
                raise ValidationError(
                     "Invalid file extension - must be in ['.csv', '.tsv', '.txt']",
                     code='invalid'
                )
        return data

# UPDATE and VIEW (ADD is separate - above) - user routed here after adding a file to complete other needed info
class AssayPlateReaderMapDataFileForm(BootstrapForm):
    """Form for Assay Plate Reader Map Data File"""

    class Meta(object):
        model = AssayPlateReaderMapDataFile
        fields = ['id', 'description', 'file_delimiter', 'upload_plate_size', 'plate_reader_file', ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'upload_plate_size': forms.TextInput(attrs={'readonly': 'readonly',
                                                 'style': 'border-style: none;',
                                                 'style': 'background-color: transparent;'
                                                        }),
        }

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)
        # self.user = kwargs.pop('user', None)
        # # ??
        # filename_only = kwargs.pop('extra', 0)
        super(AssayPlateReaderMapDataFileForm, self).__init__(*args, **kwargs)

        # need this because, remember, the plate map doesn't come WITH a study, must tell it which
        if not self.study and self.instance.study:
            self.study = self.instance.study
            # print("file form self.study ",self.study)
        if self.study:
            self.instance.study = self.study
            # print("file form self.instance.study ",self.instance.study)

        my_instance = self.instance
        # print("file form my_instance ", my_instance)

        # to display the file name without the whole path
        form_filename_only = os.path.basename(str(my_instance.plate_reader_file))
        self.fields['form_filename_only'].initial = form_filename_only

        # self.fields['se_file_format_select'].widget.attrs['class'] += ' required'

    se_form_plate_size = forms.ChoiceField(
        required=False,
        choices=assay_plate_reader_map_info_plate_size_choices
    )
    form_number_blocks = forms.IntegerField(
        required=False,
        initial=1,
    )
    form_number_blank_columns = forms.IntegerField(
        required=False,
        initial=0,
    )
    form_number_blank_rows = forms.IntegerField(
        required=False,
        initial=0,
    )
    form_filename_only = forms.CharField(
        required=False,
    )
    # PI wants to select options for file processing
    # Currently, the choices for file formats are HARDCODED here
    # if we actually iron out the "sanctioned" file formats, these could go into a table and be available in the admin
    # BUT, reading/processing of the format would still need to be build, so maybe better NOT to put in admin....

    se_file_format_select = forms.ChoiceField(
        required=False,
        initial=0,
        choices=(
            (0, 'COMPUTERS BEST GUESS'),
            (1, 'Softmax Pro 5.3 Molecular Devices M5 (UPDDI DoO)'),
            (10, 'Single data block with 1 column of row labels and 1 row of column headers'),

            # (96, 'One 96 plate (8 lines by 12 columns) starting at line 1 column 1 (CSV) - requested by Larry V.'),
            # (384, 'One 384 plate (16 lines by 24 columns) starting at line 1 column 1 (CSV) - requested by Larry V.'),
            # (2, 'Wallac EnVision Manager Version 1.12 (EnVision)'),
            (9999, 'USER CUSTOMIZES by Setting Format Information'),
        )
    )


class AssayPlateReaderMapDataFileBlockForm(forms.ModelForm):
    """Form for Assay Plate Reader Data File Block """

    class Meta(object):
        model = AssayPlateReaderMapDataFileBlock
        # fields = ('id', 'data_block', 'data_block_metadata', 'line_start', 'line_end', 'delimited_start', 'delimited_end', 'over_write_sample_time', 'assayplatereadermap'])
        exclude = tracking + ('study',)

        # this could go in AssayPlateReaderMapDataFileBlockForm or AssayPlateReaderMapFileBlockFormSet
        # but if do in formset, the widgets down get the form control!
        # fields = ('id', 'data_block', 'data_block_metadata', 'line_start', 'line_end', 'delimited_start', 'delimited_end', 'over_write_sample_time', 'assayplatereadermap')
        widgets = {
            # 'form_selected_plate_map_time_unit': forms.TextInput(attrs={'readonly': 'readonly',
            #                                                             'style': 'background-color: transparent;',
            #                                                             }),
            'data_block': forms.NumberInput(attrs={'readonly': 'readonly',
                                                   # 'style': 'box-shadow:inset 0px, 0px 0px ;',
                                                   # 'style': 'border-style: none;',
                                                   # 'style': 'border-width: 0;',
                                                   # 'style': 'border-color: transparent;',
                                                   'style': 'background-color: transparent;',
                                                   }),
            'line_start': forms.NumberInput(attrs={'class': 'form-control '}),
            'line_end': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'line_end': forms.NumberInput(attrs={'class': 'form-control required'}),
            # 'line_end': forms.NumberInput(attrs={'readonly': 'readonly',
            #                                      'style': 'background-color: transparent;',}),
            'delimited_start': forms.NumberInput(attrs={'class': 'form-control '}),
            'delimited_end': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'delimited_end': forms.NumberInput(attrs={'readonly': 'readonly',
            #                                           'style': 'background-color: transparent;',}),
            'over_write_sample_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'form_selected_plate_map_time_unit': forms.NumberInput(attrs={'readonly': 'readonly',
                                                                          'style': 'background-color: transparent;',}),
            'data_block_metadata': forms.Textarea(attrs={'cols': 80, 'rows': 1, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Get the study
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayPlateReaderMapDataFileBlockForm, self).__init__(*args, **kwargs)

        # this made the dropdown behave when copied with the formset!
        # SUPER IMPORTANT and HANDY when need to copy formsets with dropdowns - if have selectized, it is a big mess
        self.fields['assayplatereadermap'].widget.attrs.update({'class': ' no-selectize required'})

    # not currently using to limit what is removed from the map item table - consider added this feature later
    form_changed_something_in_block = forms.IntegerField(
        initial=0,
        required=False,
    )
    form_selected_plate_map_time_unit = forms.CharField(
        required=False,
    )

# formsets
class AssayPlateReaderMapFileBlockFormSet(BaseInlineFormSetForcedUniqueness):
    custom_fields_for_limiting_list = (
        'assayplatereadermap',
    )

    # tried putting this in the Form, but had some issues
    # print(self.fields['assayplatereadermap'].queryset)
    # #
    # # next line makes it work
    # self.study = 293
    # print(self.study)
    # self.fields['assayplatereadermap'].queryset = AssayPlateReaderMap.objects.filter(
    #     study_id=self.study
    # )
    #
    # # print(self.fields['assayplatereadermap'].queryset)

    def __init__(self, *args, **kwargs):
        # Get the study
        self.study = kwargs.pop('study', None)
        self.user = kwargs.pop('user', None)
        super(AssayPlateReaderMapFileBlockFormSet, self).__init__(*args, **kwargs)

        if not self.study:
            self.study = self.instance.study

        idx = 0
        for formset in self.forms:
            for field in self.custom_fields_for_limiting_list:
                formset.fields[field].queryset = AssayPlateReaderMap.objects.filter(
                    study_id=self.study
                    # study_id=293
                )
            if self.study:
                formset.instance.study = self.study
            if formset.instance.pk:
                formset.instance.modified_by = self.user
            else:
                formset.instance.created_by = self.user
            idx = idx + 1


AssayPlateReaderMapDataFileBlockFormSetFactory = inlineformset_factory(
    AssayPlateReaderMapDataFile,
    AssayPlateReaderMapDataFileBlock,
    formset=AssayPlateReaderMapFileBlockFormSet,
    form=AssayPlateReaderMapDataFileBlockForm,
    extra=1,
    exclude=tracking + ('study',),
)


# ASSAY PLATE MAP END
#####

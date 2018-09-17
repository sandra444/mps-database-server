from django import forms
from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
    BaseModelFormSet,
    modelformset_factory,
)
from cellsamples.models import Biosensor
# STOP USING WILDCARD IMPORTS
from assays.models import *
from compounds.models import Compound, CompoundInstance, CompoundSupplier
from microdevices.models import MicrophysiologyCenter
from mps.forms import SignOffMixin
import string
from captcha.fields import CaptchaField

from .utils import (
    # validate_file,
    # get_chip_details,
    # get_plate_details,
    TIME_CONVERSIONS,
    # EXCLUDED_DATA_POINT_CODE,
    AssayFileProcessor
)
from django.utils import timezone

from mps.templatetags.custom_filters import is_group_admin, ADMIN_SUFFIX

from django.core.exceptions import NON_FIELD_ERRORS

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
class ModelFormStripWhiteSpace(forms.ModelForm):
    """Strips the whitespace from char and text fields"""
    def clean(self):
        cd = self.cleaned_data
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                if self.fields[field_name].required and not cd.get(field_name, None):
                    self.add_error(field_name, "This is a required field.")
                else:
                    cd[field_name] = cd[field_name].strip()

        return super(ModelFormStripWhiteSpace, self).clean()


class ModelFormSplitTime(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelFormSplitTime, self).__init__(*args, **kwargs)

        for time_unit in TIME_CONVERSIONS.keys():
            if self.fields.get('addition_time', None):
                # Create fields for Days, Hours, Minutes
                self.fields['addition_time_' + time_unit] = forms.FloatField(initial=0)
                # Change style
                self.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
            if self.fields.get('duration', None):
                self.fields['duration_' + time_unit] = forms.FloatField(initial=0)
                self.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'

        # Fill additional time
        if self.fields.get('addition_time', None):
            addition_time_in_minutes_remaining = getattr(self.instance, 'addition_time', 0)
            if not addition_time_in_minutes_remaining:
                addition_time_in_minutes_remaining = 0
            for time_unit, conversion in TIME_CONVERSIONS.items():
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
            for time_unit, conversion in TIME_CONVERSIONS.items():
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
            for time_unit, conversion in TIME_CONVERSIONS.items():
                cleaned_data.update({
                    'addition_time': cleaned_data.get('addition_time') + cleaned_data.get('addition_time_' + time_unit,
                                                                                          0) * conversion,
                    'duration': cleaned_data.get('duration') + cleaned_data.get('duration_' + time_unit, 0) * conversion
                })

            if self.fields.get('duration', None) is not None and cleaned_data.get('duration') <= 0:
                raise forms.ValidationError({'duration': ['Duration cannot be zero or negative.']})

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
                if unique_check == (u'id',) and not form.cleaned_data.get('id', ''):
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
        "Check to see if the provided value is a valid choice"
        if unicode(value.id) in self.dic.get(self.name):
            return True
        return False


class AssayStudyConfigurationForm(SignOffMixin, forms.ModelForm):
    """Frontend Form for Study Configurations"""
    class Meta(object):
        model = AssayStudyConfiguration
        widgets = {
            'name': forms.Textarea(attrs={'cols': 50, 'rows': 1}),
            'media_composition': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
            'hardware_description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
        exclude = tracking


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


class AssayStudyAssayInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        """Init APRA inline

        Filters units so that only units marked 'readout' appear
        """
        super(AssayStudyAssayInlineFormSet, self).__init__(*args, **kwargs)

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
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 100}),
        }
        exclude = tracking + restricted + ('access_groups', 'signed_off_notes', 'bulk_file')

    def clean(self):
        """Checks for at least one study type"""
        # clean the form data, before validation
        data = super(AssayStudyForm, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')


class AssayStudyFormAdmin(forms.ModelForm):
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

        if self.instance:
            groups_without_repeat.exclude(pk=self.instance.group.id)

        self.fields['access_groups'].queryset = groups_without_repeat

    def clean(self):
        # clean the form data, before validation
        data = super(AssayStudyFormAdmin, self).clean()

        if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')


class AssayStudySupportingDataInlineFormSet(BaseInlineFormSet):
    """Form for Study Supporting Data (as part of an inline)"""
    class Meta(object):
        model = AssayStudySupportingData
        exclude = ('',)

AssayStudySupportingDataFormSetFactory = inlineformset_factory(
    AssayStudy,
    AssayStudySupportingData,
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
    formset=AssayStudyAssayInlineFormSet,
    extra=1,
    exclude=[]
)


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

        sections_with_times = (
            'compound',
            'cell',
            'setting'
        )

        for time_unit in TIME_CONVERSIONS.keys():
            for current_section in sections_with_times:
                # Create fields for Days, Hours, Minutes
                self.fields[current_section + '_addition_time_' + time_unit] = forms.FloatField(initial=0, required=False)
                self.fields[current_section + '_duration_' + time_unit] = forms.FloatField(initial=0, required=False)
                # self.fields['addition_time_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
                # self.fields['duration_' + time_unit + '_increment'] = forms.FloatField(initial=0, required=False)
                # Change style
                self.fields[current_section + '_addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
                self.fields[current_section + '_duration_' + time_unit].widget.attrs['style'] = 'width:50px;'
                # self.fields['addition_time_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'
                # self.fields['duration_' + time_unit + '_increment'].widget.attrs['style'] = 'width:50px;'

        # Set CSS class to receipt date to use date picker
        self.fields['compound_receipt_date'].widget.attrs['class'] = 'datepicker-input'
        self.fields['item_setup_date'].widget.attrs['class'] = 'datepicker-input'

        # Set the widgets for some additional fields
        self.fields['item_name'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_scientist'].widget = forms.Textarea(attrs={'rows': 1})
        self.fields['item_notes'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['item_variance_from_organ_model_protocol'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['item_notebook_page'].widget.attrs['style'] = 'width:50px;'
        self.fields['cell_cell_sample'].widget.attrs['style'] = 'width:50px;'
        self.fields['cell_passage'].widget.attrs['style'] = 'width:50px;'

    ### ADDITIONAL MATRIX FIELDS (unsaved)
    number_of_items = forms.IntegerField(required=False)

    ### ITEM FIELD HELPERS
    action = forms.ChoiceField(choices=(
        ('', 'Please Select an Action'),
        ('add_name', 'Add Names/IDs*'),
        ('add_test_type', 'Add Test Type*'),
        ('add_date', 'Add Setup Date*'),
        ('add_device', 'Add Device/Organ Model Information*'),
        ('add_settings', 'Add Settings'),
        ('add_compounds', 'Add Compounds'),
        ('add_cells', 'Add Cells'),
        ('add_notes', 'Add Notes/Notebook Information'),
        # ADD BACK LATER
        # ('copy', 'Copy Contents'),
        # TODO TODO TODO TENTATIVE
        # ('clear', 'Clear Contents'),
        ('delete', 'Delete Selected'),
    ), required=False)

    # The item_ isn't just to be annoying, I want to avoid conflicts with other fields
    ### ADDING ITEM FIELDS
    item_name = forms.CharField(required=False)

    item_setup_date = forms.DateField(required=False)

    item_test_type = forms.ChoiceField(required=False, choices=TEST_TYPE_CHOICES)

    item_scientist = forms.CharField(required=False)
    item_notebook = forms.CharField(required=False)
    item_notebook_page = forms.CharField(required=False)
    item_notes = forms.CharField(required=False)

    ### ADDING SETUP FIELDS
    item_device = forms.ModelChoiceField(queryset=Microdevice.objects.all().order_by('name'), required=False)
    item_organ_model = forms.ModelChoiceField(queryset=OrganModel.objects.all().order_by('name'), required=False)
    item_organ_model_protocol = forms.ModelChoiceField(queryset=OrganModelProtocol.objects.all().order_by('version'), required=False)
    item_variance_from_organ_model_protocol = forms.CharField(required=False)

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
        queryset=PhysicalUnits.objects.filter(availability__contains='cell'),
        required=False
    )

    cell_passage = forms.CharField(required=False)

    cell_addition_location = forms.ModelChoiceField(queryset=AssaySampleLocation.objects.all().order_by('name'), required=False)

    ### ?ADDING SETUP SETTINGS
    setting_setting = forms.ModelChoiceField(queryset=AssaySetting.objects.all().order_by('name'), required=False)
    setting_unit = forms.ModelChoiceField(queryset=PhysicalUnits.objects.all().order_by('base_unit','scale_factor'), required=False)

    setting_value = forms.CharField(required=False)

    setting_addition_location = forms.ModelChoiceField(queryset=AssaySampleLocation.objects.all().order_by('name'),
                                                        required=False)

    ### ADDING COMPOUNDS
    compound_compound = forms.ModelChoiceField(queryset=Compound.objects.all().order_by('name'), required=False)
    # Notice the special exception for %
    compound_concentration_unit = forms.ModelChoiceField(
        queryset=(PhysicalUnits.objects.filter(
            unit_type__unit_type='Concentration'
        ).order_by(
            'base_unit',
            'scale_factor'
        ) | PhysicalUnits.objects.filter(unit='%')),
        required=False, initial=4
    )
    compound_concentration = forms.FloatField(required=False)

    compound_addition_location = forms.ModelChoiceField(queryset=AssaySampleLocation.objects.all().order_by('name'),
                                                       required=False)

    ### INCREMENTER
    compound_concentration_increment = forms.FloatField(required=False, initial=1)
    compound_concentration_increment_type = forms.ChoiceField(choices=(
        ('/', 'Divide'),
        ('*', 'Multiply'),
        ('+', 'Add'),
        ('-', 'Subtract')
    ), required=False)
    compound_concentration_increment_direction = forms.ChoiceField(choices=(
        ('lrd', 'Left to Right and Down'),
        ('rlu', 'Right to Left and Up')
    ), required=False)

    # Text field (un-saved) for supplier
    compound_supplier_text = forms.CharField(required=False, initial='')
    # Text field (un-saved) for lot
    compound_lot_text = forms.CharField(required=False, initial='')
    # Receipt date
    compound_receipt_date = forms.DateField(required=False)

    # FORCE UNIQUENESS CHECK
    def clean(self):
        super(AssayMatrixForm, self).clean()

        if AssayMatrix.objects.filter(
                study=self.instance.study,
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

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupCompoundFormSet, self)._construct_form(i, **kwargs)

        # Text field (un-saved) for supplier
        form.fields['supplier_text'] = forms.CharField(initial='N/A')
        # Text field (un-saved) for lot
        form.fields['lot_text'] = forms.CharField(initial='N/A')
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
                instance = forms.ModelForm.save(form, commit=False)

                if instance and instance.id and commit:
                    instance.delete()
            # ValueError here indicates that the instance couldn't even validate and so should be ignored
            except ValueError:
                pass

        # Forms to save
        for form in forms_data:
            instance = forms.ModelForm.save(form, commit=False)

            matrix_item = instance.matrix_item

            current_data = form.cleaned_data

            compound_id = int(current_data.get('compound'))
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
                if commit:
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
                if commit:
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

            # If instance, apply initial values
            if form.instance.compound_instance_id:
                current_compound_instance = compound_instances_dic.get(form.instance.compound_instance_id)

                form.fields['compound'].initial = current_compound_instance.compound
                form.fields['supplier_text'].initial = current_compound_instance.supplier.name
                form.fields['lot_text'].initial = current_compound_instance.lot
                form.fields['receipt_date'].initial = current_compound_instance.receipt_date

            # Set CSS class to receipt date to use date picker
            form.fields['receipt_date'].widget.attrs['class'] = 'datepicker-input'

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
            matrix_item=matrix_item
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
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
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
                    created_by=matrix_item.created_by,
                    created_on=matrix_item.created_on,
                    modified_by=matrix_item.modified_by,
                    modified_on=matrix_item.modified_on
                )
                if commit:
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
        self.fields['cell_sample'].widget.attrs['style'] = 'width:50px;'
        self.fields['passage'].widget.attrs['style'] = 'width:50px;'

        self.fields['density_unit'].queryset = PhysicalUnits.objects.filter(availability__contains='cell')


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


class AssaySetupSettingForm(ModelFormSplitTime):
    class Meta(object):
        model = AssaySetupCell
        exclude = tracking

        # widgets = {
        #     'matrix_item': forms.TextInput(),
        #     'setting': forms.TextInput(),
        #     'unit': forms.TextInput(),
        #     'addition_location': forms.TextInput(),
        # }


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

    def _construct_form(self, i, **kwargs):
        form = super(AssaySetupSettingFormSet, self)._construct_form(i, **kwargs)
        for time_unit in TIME_CONVERSIONS.keys():
            # Create fields for Days, Hours, Minutes
            form.fields['addition_time_' + time_unit] = forms.FloatField(initial=0)
            form.fields['duration_' + time_unit] = forms.FloatField(initial=0)
            # Change style
            form.fields['addition_time_' + time_unit].widget.attrs['style'] = 'width:50px;'
            form.fields['duration_' + time_unit].widget.attrs['style'] = 'width:50px;'

        if form.instance.addition_time:
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

        if form.instance.duration:
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


class AssayMatrixItemFullForm(SignOffMixin, forms.ModelForm):
    """Frontend form for Items"""
    class Meta(object):
        model = AssayMatrixItem
        widgets = {
            'concentration': forms.NumberInput(attrs={'style': 'width:50px;'}),
            'notebook_page': forms.NumberInput(attrs={'style': 'width:50px;'}),
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
                study=self.instance.study,
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
        """Checks to make sure duration is valid"""
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


class AssayStudySignOffForm(SignOffMixin, forms.ModelForm):
    class Meta(object):
        model = AssayStudy
        fields = ['signed_off', 'signed_off_notes']
        widgets = {
            'signed_off_notes': forms.Textarea(attrs={'cols': 50, 'rows': 2}),
        }


class AssayStudyStakeholderSignOffForm(SignOffMixin, forms.ModelForm):
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


class AssayStudyDataUploadForm(forms.ModelForm):
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

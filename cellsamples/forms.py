from django import forms
from .models import CellSample, CellType, CellSubtype
from mps.forms import SignOffMixin

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')
# Excluding restricted is likewise useful
restricted = ('restricted',)


class CellSampleForm(SignOffMixin, forms.ModelForm):
    """Form for Cell Samples"""
    def __init__(self, groups, *args, **kwargs):
        """Init the CellSample Form

        Parameters:
        groups -- a queryset of groups (allows us to avoid N+1 problem)
        """
        super(CellSampleForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = groups
        self.fields['cell_type'].queryset = CellType.objects.all().prefetch_related('organ')
        self.fields['cell_subtype'].queryset = CellSubtype.objects.all().prefetch_related('cell_type')

    class Meta(object):
        model = CellSample
        exclude = tracking + restricted
        widgets = {
            'isolation_method': forms.Textarea(attrs={'rows': 3}),
            'isolation_notes': forms.Textarea(attrs={'rows': 3}),
            'patient_condition': forms.Textarea(attrs={'rows': 3}),
        }


class CellTypeForm(SignOffMixin, forms.ModelForm):
    """Form for Cell Types"""
    class Meta(object):
        model = CellType
        exclude = tracking
        widgets = {
            'cell_type': forms.Textarea(attrs={'rows': 1}),
        }


class CellSubtypeForm(SignOffMixin, forms.ModelForm):
    """Form for Cell Subtypes"""
    def __init__(self, *args, **kwargs):
        super(CellSubtypeForm, self).__init__(*args, **kwargs)
        self.fields['cell_type'].queryset = CellType.objects.all().prefetch_related('organ')

    class Meta(object):
        model = CellSubtype
        exclude = tracking
        widgets = {
            'cell_subtype': forms.Textarea(attrs={'rows': 1}),
        }

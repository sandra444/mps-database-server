from django import forms
from .models import CellSample, CellType, CellSubtype

# These are all of the tracking fields
tracking = ('created_by', 'created_on', 'modified_on', 'modified_by', 'signed_off_by', 'signed_off_date')
# Excluding restricted is likewise useful
restricted = ('restricted',)

class CellSampleForm(forms.ModelForm):

    class Meta(object):
        model = CellSample
        exclude = tracking + restricted


class CellTypeForm(forms.ModelForm):

    class Meta(object):
        model = CellType
        exclude = tracking


class CellSubtypeForm(forms.ModelForm):

    class Meta(object):
        model = CellSubtype
        exclude = tracking

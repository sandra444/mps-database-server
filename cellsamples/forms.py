from django import forms
from .models import CellSample, CellType, CellSubtype


class CellSampleForm(forms.ModelForm):

    class Meta(object):
        model = CellSample
        exclude = ('restricted',)


class CellTypeForm(forms.ModelForm):

    class Meta(object):
        model = CellType
        exclude = ('',)


class CellSubtypeForm(forms.ModelForm):

    class Meta(object):
        model = CellSubtype
        exclude = ('',)

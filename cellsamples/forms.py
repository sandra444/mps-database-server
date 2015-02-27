from django import forms
from .models import CellSample, CellType

class CellSampleForm(forms.ModelForm):

    class Meta(object):
        model = CellSample
        exclude = ('restricted',)


class CellTypeForm(forms.ModelForm):

    class Meta(object):
        model = CellType
        exclude = ('',)

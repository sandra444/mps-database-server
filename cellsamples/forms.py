from django import forms
from .models import CellSample

class CellSampleForm(forms.ModelForm):

    class Meta(object):
        model = CellSample
        exclude = ('restricted',)

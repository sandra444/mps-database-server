from django import forms
from .models import Compound

class CompoundForm(forms.ModelForm):

    class Meta(object):
        model = Compound
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'smiles': forms.Textarea(attrs={'size':50, 'rows': 3}),
            'inchikey': forms.Textarea(attrs={'size':50, 'rows': 3}),
            'molecular_formula': forms.Textarea(attrs={'size':50, 'rows': 3}),
            'ro5_violations': forms.TextInput(attrs={'size':2}),
        }

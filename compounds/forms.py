from django import forms
from .models import *
from django.forms.models import BaseInlineFormSet


class CompoundForm(forms.ModelForm):

    class Meta(object):
        model = Compound
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'tags': forms.Textarea(attrs={'rows': 1}),
            'smiles': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'inchikey': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'molecular_formula': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'ro5_violations': forms.TextInput(attrs={'size': 2}),
        }
        exclude = ('',)

    # Deal with nonsense
    def clean(self):
        super(forms.ModelForm, self).clean()

        chemblid = self.cleaned_data.get('chemblid', '')
        inchikey = self.cleaned_data.get('inchikey', '')
        pubchemid = self.cleaned_data.get('pubchemid', '')

        if chemblid and Compound.objects.filter(chemblid=chemblid).exists():
            raise forms.ValidationError('A compound with the given ChEMBL ID already exists')
        if inchikey and Compound.objects.filter(inchikey=inchikey).exists():
            raise forms.ValidationError('A compound with the given InChI Key already exists')
        if pubchemid and Compound.objects.filter(pubchemid=pubchemid).exists():
            raise forms.ValidationError('A compound with the given PubChem ID already exists')

        return self.cleaned_data


class CompoundSummaryInlineFormset(BaseInlineFormSet):
    class Meta(object):
        model = CompoundSummary
        exclude = ('',)


class CompoundPropertyInlineFormset(BaseInlineFormSet):
    class Meta(object):
        model = CompoundProperty
        exclude = ('',)

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

            'clearance': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'absorption': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'pk_metabolism': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'preclinical': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'clinical': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'post_marketing': forms.Textarea(attrs={'size': 50, 'rows': 3}),
        }
        exclude = ('',)

    # Deal with nonsense
    def clean(self):
        super(forms.ModelForm, self).clean()

        chemblid = self.cleaned_data.get('chemblid', '')
        inchikey = self.cleaned_data.get('inchikey', '')
        pubchemid = self.cleaned_data.get('pubchemid', '')
        drugbank_id = self.cleaned_data.get('drugbank_id', '')

        # If this instance does not have a primary key, then it is new and this is NOT an update
        if not self.instance.pk:
            if chemblid and Compound.objects.filter(chemblid=chemblid).exists():
                raise forms.ValidationError('A compound with the given ChEMBL ID already exists')
            if inchikey and Compound.objects.filter(inchikey=inchikey).exists():
                raise forms.ValidationError('A compound with the given InChI Key already exists')
            if pubchemid and Compound.objects.filter(pubchemid=pubchemid).exists():
                raise forms.ValidationError('A compound with the given PubChem ID already exists')
            if drugbank_id and Compound.objects.filter(drugbank_id=drugbank_id).exists():
                raise forms.ValidationError('A compound with the given DrugBank ID already exists')

        return self.cleaned_data


class CompoundSummaryInlineFormset(BaseInlineFormSet):
    class Meta(object):
        model = CompoundSummary
        exclude = ('',)


class CompoundPropertyInlineFormset(BaseInlineFormSet):
    class Meta(object):
        model = CompoundProperty
        exclude = ('',)


class CompoundTargetInlineFormset(BaseInlineFormSet):
    class Meta(object):
        model = CompoundTarget
        exclude = ('',)


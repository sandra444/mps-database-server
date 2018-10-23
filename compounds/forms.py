from django import forms
from .models import (
    Compound,
    CompoundSummary,
    CompoundProperty,
    CompoundTarget
)
from django.forms.models import BaseInlineFormSet
from mps.forms import BootstrapForm
from django.forms.models import inlineformset_factory


class CompoundForm(BootstrapForm):
    """Form for Compounds"""
    class Meta(object):
        model = Compound
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'tags': forms.Textarea(attrs={'rows': 1}),
            'smiles': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'inchikey': forms.Textarea(attrs={'size': 50, 'rows': 1}),
            'molecular_formula': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'ro5_violations': forms.TextInput(attrs={'size': 2}),
            'drug_class': forms.Textarea(attrs={'rows': 1}),

            'clearance': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'absorption': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'pk_metabolism': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'preclinical': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'clinical': forms.Textarea(attrs={'size': 50, 'rows': 3}),
            'post_marketing': forms.Textarea(attrs={'size': 50, 'rows': 3}),
        }
        exclude = (
            'created_by',
            'created_on',
            'modified_on',
            'modified_by',
            'signed_off_by',
            'signed_off_date',
            'last_update'
        )

    # Deal with nonsense
    def clean(self):
        """Clean Compound Form

        Ensures that chemblid, inchikey, and pubchemid, and drugbank_id are unique
        """
        super(CompoundForm, self).clean()

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


# SUBJECT TO DEPRECATION
class CompoundSummaryInlineFormset(BaseInlineFormSet):
    """Form for Summary inlines"""
    class Meta(object):
        model = CompoundSummary
        exclude = ('',)


# SUBJECT TO DEPRECATION
class CompoundPropertyInlineFormset(BaseInlineFormSet):
    """Form for property inlines"""
    class Meta(object):
        model = CompoundProperty
        exclude = ('',)


class CompoundTargetForm(BootstrapForm):
    """Form for Target inlines"""
    class Meta(object):
        model = CompoundTarget
        exclude = ('',)


class CompoundTargetInlineFormset(BaseInlineFormSet):
    """Formset for Target inlines"""
    class Meta(object):
        model = CompoundTarget
        exclude = ('',)

CompoundTargetFormset = inlineformset_factory(
    Compound,
    CompoundTarget,
    form=CompoundTargetForm,
    formset=CompoundTargetInlineFormset,
    extra=1,
    exclude=[],
    widgets={
        'name': forms.Textarea(attrs={'size': 25, 'rows': 1}),
        'uniprot_id': forms.TextInput(attrs={'size': 10}),
        'pharmacological_action': forms.TextInput(attrs={'size': 7}),
        'organism': forms.TextInput(attrs={'size': 7}),
        'type': forms.TextInput(attrs={'size': 11}),
    }
)

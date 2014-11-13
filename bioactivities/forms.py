from django import forms
from bioactivities.models import *
from compounds.models import Compound


class AssayForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        model = Assay
        widgets = {
            'chemblid': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'assay_type': forms.Textarea(attrs={'rows': 1}),
            'organism': forms.Textarea(attrs={'rows': 1}),
            'strain': forms.Textarea(attrs={'rows': 1}),
            'journal': forms.Textarea(attrs={'rows': 1}),
        }


class TargetsForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        model = Target
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'synonyms': forms.Textarea(attrs={'rows': 3}),
            'chemblid': forms.Textarea(attrs={'rows': 1}),
            'gene_names': forms.Textarea(attrs={'rows': 1}),
            'organism': forms.Textarea(attrs={'rows': 1}),
            'uniprot_accession': forms.Textarea(attrs={'rows': 1}),
            'target_type': forms.Textarea(attrs={'rows': 1}),
        }

class FilterForm(forms.Form):
    # bioactivities = forms.ModelMultipleChoiceField(
    #     queryset=BioactivityType.objects.all(), # not optional, use .all() if unsure
    #     widget=forms.CheckboxSelectMultiple,
    # )
    # target = forms.ModelMultipleChoiceField(
    #     queryset=Target.objects.all(), # not optional, use .all() if unsure
    #     widget=forms.CheckboxSelectMultiple,
    # )
    compounds = forms.ModelMultipleChoiceField(
        queryset=Compound.objects.all(), # not optional, use .all() if unsure
        widget=forms.CheckboxSelectMultiple,
    )

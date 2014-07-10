from django import forms
from bioactivities.models import Assay


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


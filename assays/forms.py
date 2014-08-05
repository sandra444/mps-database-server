from django import forms


class AssayResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }


class AssayRunForm(forms.ModelForm):

    class Meta(object):
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows':1}),
            'name': forms.Textarea(attrs={'rows':1}),
            'description': forms.Textarea(attrs={'rows':3}),
        }

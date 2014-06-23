from django import forms


class AssayResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 10}),
        }

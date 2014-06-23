from django import forms


class TestResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'test_time': forms.TextInput(attrs={'size': 3}),
            'percent_min': forms.TextInput(attrs={'size': 3}),
            'percent_max': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 5}),
        }


class FindingResultForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'finding_time': forms.TextInput(attrs={'size': 3}),
            'percent_min': forms.TextInput(attrs={'size': 3}),
            'percent_max': forms.TextInput(attrs={'size': 3}),
            'value': forms.TextInput(attrs={'size': 5})
        }

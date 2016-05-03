from django import forms


class DrugTrialForm(forms.ModelForm):

    class Meta(object):
        widgets = {
                'description': forms.Textarea(attrs={'cols': 70, 'rows': 10}),
                'condition': forms.Textarea(attrs={'cols': 70, 'rows': 10}),
        }


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


class FindingForm(forms.ModelForm):

    class Meta(object):
        widgets = {
            'finding_name': forms.Textarea(attrs={'size': 100, 'rows': 1, 'cols': 100}),
            'description': forms.Textarea(attrs={'size': 400, 'rows': 4, 'cols': 100}),
        }

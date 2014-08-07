from django import forms


class ResourceForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'resource_name': forms.Textarea(attrs={'rows': 1}),
            'resource_website': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ResourceTypeForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'resource_type_name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ResourceSubtypeForm(forms.ModelForm):
    """Size the text input boxes"""

    class Meta(object):
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

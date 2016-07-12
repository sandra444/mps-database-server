from django import forms


class ResourceForm(forms.ModelForm):
    """Form for Resources"""
    class Meta(object):
        widgets = {
            'resource_name': forms.Textarea(attrs={'rows': 1}),
            'resource_website': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ResourceTypeForm(forms.ModelForm):
    """Form for Resource Types"""
    class Meta(object):
        widgets = {
            'resource_type_name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ResourceSubtypeForm(forms.ModelForm):
    """Form for Resource Subtypes"""
    class Meta(object):
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class DefinitionForm(forms.ModelForm):
    """Form for Definitions"""
    class Meta(object):
        widgets = {
            'term': forms.Textarea(attrs={'rows': 1}),
            'definition': forms.Textarea(attrs={'rows': 5}),
        }

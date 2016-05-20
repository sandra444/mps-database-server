from django import forms
from captcha.fields import CaptchaField
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User


class SearchForm(forms.Form):
    app = forms.CharField(max_length=50)
    compound = forms.CharField(max_length=100, required=False)
    target = forms.CharField(max_length=100, required=False)
    name = forms.CharField(max_length=100, required=False)
    pubchem = forms.BooleanField(required=False)
    exclude_targetless = forms.BooleanField(required=False)
    exclude_organismless = forms.BooleanField(required=False)
    search_term = forms.CharField(max_length=500, required=False)

    def clean(self):
        super(SearchForm, self).clean()

        app = self.cleaned_data.get('app', '')
        compound = self.cleaned_data.get('compound', '')
        target = self.cleaned_data.get('target', '')
        name = self.cleaned_data.get('name', '')

        if app == "Bioactivities" and not any([compound, target, name]):
            raise forms.ValidationError(
                'You must have at least one search term'
            )

        return self.cleaned_data


# Add captcha to registration form
class CaptchaRegistrationForm(RegistrationFormUniqueEmail):
    captcha = CaptchaField()


# Add captcha to reset form
class CaptchaResetForm(PasswordResetForm):
    captcha = CaptchaField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")

        return email

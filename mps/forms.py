from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from captcha.fields import CaptchaField

class SearchForm(forms.Form):
    app = forms.CharField(max_length=50)
    search_term  = forms.CharField(max_length=500)

# class MyRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     captcha = CaptchaField()
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2', 'captcha')
#
#     def save(self, commit=True):
#         user = super(MyRegistrationForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         # user.set_password(self.cleaned_data['password1'])
#
#         if commit:
#             user.save()
#
#         return user

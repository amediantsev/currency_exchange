import random

from django import forms
from django.conf import settings

from account import models
from account.tasks import send_email_async


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = models.User
        fields = ('email', 'username', 'password', 'password2', 'phone')

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors:
            if cleaned_data['password'] != cleaned_data['password2']:
                raise forms.ValidationError('Password do not match')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False
        user.save()

        activation_code = user.activation_codes.create()
        activation_code.send_activation_code()
        return user


# class SignUpSMSForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())
#     password2 = forms.CharField(widget=forms.PasswordInput())
#     phone = forms.CharField(max_length=20)
#
#     class Meta:
#         model = models.User
#         fields = ('username', 'email', 'phone', 'password', 'password2')
#
#     def clean(self):
#         cleaned_data = super().clean()
#         if not self.errors:
#             if cleaned_data['password'] != cleaned_data['password2']:
#                 raise forms.ValidationError('Password do not match')
#         return cleaned_data
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])
#         user.is_active = False
#
#         data = self.cleaned_data
#         email_code = random.randrange(100000, 999999)
#         models.ConfirmationKey.objects.create(user_email=data['email'], key=email_code)
#         subject = 'Confirmation of registration'
#         message = 'Hello, buddy, it\'s your one-time code: ' + str(email_code) + '\nEnter it in the form'
#         email_from = settings.EMAIL_HOST_USER
#         recipient_list = [data['email']]
#         send_email_async.delay(subject, message, email_from, recipient_list)
#
#         super().save(commit)


# class ConfirmationForm(forms.Form):
#
#     Code = forms.IntegerField(label='Enter your code here, please: ')

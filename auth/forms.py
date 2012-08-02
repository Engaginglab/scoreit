from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class SignUpForm(forms.Form):
    username = forms.CharField(label=_('User name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    password = forms.CharField(widget=forms.PasswordInput,
        label=_('Password'), required=True)
    # password_repeat = forms.CharField(widget=forms.PasswordInput,
    #     label=_('Repeat Password'), required=True)

    first_name = forms.CharField(label=_('First Name'), required=True)
    last_name = forms.CharField(label=_('Last Name'), required=True)

    def clean_username(self):
        data = self.cleaned_data['username']
        try:
            User.objects.get(username=data)
        except User.DoesNotExist:
            return data
        raise forms.ValidationError(_('This username is already taken.'))

    def clean_email(self):
        data = self.cleaned_data['email']
        try:
            User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise forms.ValidationError(
            _('A user with this email is already registered.'))

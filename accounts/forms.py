from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        label="Email", max_length=254, required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': _("email_placeholder"), 'autocomplete': 'true'
        })
    )


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=150, label=_("email_label"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': _("email_placeholder"),'autocomplete': 'true'
        })
    )
    password = forms.CharField(
        label=_("password_label"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': _("password_placeholder"),'autocomplete': 'true'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _("password_placeholder")})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _("password2_placeholder")})

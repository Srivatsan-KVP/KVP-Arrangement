from django import forms

class LoginForm(forms.Form):
    login_username = forms.CharField(max_length=32)
    login_password = forms.CharField(widget=forms.PasswordInput())

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput())
    password = forms.CharField(label='Enter your password', widget=forms.PasswordInput())

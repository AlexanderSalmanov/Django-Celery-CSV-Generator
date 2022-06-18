from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.conf import settings

from . import forms

# Create your views here.

User = settings.AUTH_USER_MODEL

class LoginView(generic.FormView):
    template_name = 'accounts/login.html'
    form_class = forms.LoginForm
    success_url = reverse_lazy('hello')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            return redirect('hello')
        return super(LoginView, self).form_invalid(form)

class SignUp(generic.CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('hello')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)
            return redirect('hello')
        return super().form_valid(form)

from django.http import HttpResponse
from django.shortcuts import render
from account.forms import UserCreationFormReboot
from django.urls import reverse_lazy
from django.views import generic


class SignUp(generic.CreateView):
    form_class = UserCreationFormReboot
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

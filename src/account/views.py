from django.urls import reverse_lazy
from django.views import generic

from account.forms import UserCreationFormReboot


class SignUp(generic.CreateView):
    form_class = UserCreationFormReboot
    success_url = reverse_lazy('login')

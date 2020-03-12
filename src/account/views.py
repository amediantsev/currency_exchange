from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from account.forms import UserCreationFormReboot
from account.models import User , Contact
from account.tasks import send_email_async
from currency_exchange import settings_local, settings


class SignUp(generic.CreateView):
    form_class = UserCreationFormReboot
    success_url = reverse_lazy('login')


class MyProfile(generic.UpdateView):
    template_name = 'my_profile.html'
    queryset = User.objects.filter(is_active=True)
    fields = ('email', )
    success_url = reverse_lazy('index')


class ContactUs(generic.CreateView):
    template_name = 'my_profile.html'
    queryset = Contact.objects.all()
    fields = ('email', 'title', 'body')
    success_url = reverse_lazy('index')
    model = Contact



    def form_valid(self, form):
        subject = self.object.title
        message = self.object.body
        email_from = self.object.email
        recipient_list = [settings.EMAIL_HOST_USER]
        send_email_async.delay(subject=subject, message=message, email_from=email_from, recipient_list=recipient_list)
        return super().form_valid(form)

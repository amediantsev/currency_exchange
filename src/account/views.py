from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from account.forms import SignUpForm #, SignUpSMSForm
from account.models import User, Contact, ActivationCode
from account.tasks import send_email_async
from currency_exchange import settings


class SignUp(generic.CreateView):
    template_name = 'signup.html'
    queryset = User.objects.all()
    form_class = SignUpForm
    success_url = reverse_lazy('login')


class MyProfile(generic.UpdateView):
    template_name = 'my_profile.html'
    queryset = User.objects.filter(is_active=True)
    fields = ('email', )
    success_url = reverse_lazy('index')

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(id=self.request.user.id)


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


class Activate(generic.View):
    def get(self, request, activation_code):
        ac = get_object_or_404(ActivationCode.objects.select_related('user'),
                               code=activation_code, is_activated=False)

        if ac.is_expired:
            return Http404

        ac.is_activated = True
        ac.save(update_fields=['is_activated'])
        user = ac.user
        user.is_active = True
        user.save(update_fields=['is_active'])
        return redirect('index')


# class SignUpSMS(generic.CreateView):
#     template_name = 'signup.html'
#     queryset = User.objects.all()
#     form_class = SignUpSMSForm
#     success_url = reverse_lazy('confirmation')


# class SMS_Activate(generic.View):
#
#     def get(self, request, activation_code):
#         ac = get_object_or_404(ActivationCode.objects.select_related('user'),
#                                code=activation_code, is_activated=False)
#
#         if ac.is_expired:
#             return Http404
#
#         ac.is_activated = True
#         ac.save(update_fields=['is_activated'])
#         user = ac.user
#         user.is_active = True
#         user.save(update_fields=['is_active'])
#         return redirect('index')

import urllib
import json
import requests

from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from account.forms import SignUpForm, ActivateForm, SignUpSMSForm
from account.models import User, Contact, ActivationCode, SmsCode
from account.tasks import send_email_async, send_tel_message
    

# class AjaxFormMixin(FormView):

    # def form_valid(self, form):
    #     form.save()
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     errors_dict = json.dumps(dict([(k, [e for e in v]) for k, v in form.errors.items()]))
    #     return HttpResponseBadRequest(json.dumps(errors_dict))


class SignUpIndex(generic.TemplateView):
    template_name = 'signup-index.html'


class SignUp(generic.CreateView):
    template_name = 'signup.html'
    queryset = User.objects.all()
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['GOOGLE_RECAPTCHA_SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        return context

    def form_valid(self, form):

        # get the token submitted in the form
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(url, data=data)

        # verify the token submitted with the form is valid
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if not result['success']:
            messages.add_message(self.request, messages.ERROR, 'Invalid Captcha. Please, try again')
            return super().form_invalid(form)

        return super().form_valid(form)


class SignUpSMS(SignUp):
    form_class = SignUpSMSForm
    success_url = reverse_lazy('account:sms-activate')

    def get_success_url(self):
        return super().get_success_url()


class MyProfile(generic.UpdateView):
    template_name = 'my_profile.html'
    queryset = User.objects.filter(is_active=True)
    success_url = reverse_lazy('index')
    fields = ('email', 'first_name', 'last_name', 'phone', 'avatar')
    model = User

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(id=self.request.user.id)


class ContactUs(generic.CreateView):
    template_name = 'contact-us.html'
    queryset = Contact.objects.all()
    fields = ('title', 'body')
    success_url = reverse_lazy('index')
    model = Contact

    def form_valid(self, form):
        subject = f'From {self.request.user.email}: ' + form.cleaned_data.get('title')
        message = form.cleaned_data.get('body') + \
        '\n\n' + \
        '*' * 100 + \
        f'\n\nWas sent from user {self.request.user} with email {self.request.user.email}'
        
        email_from = settings.EMAIL_HOST_USER
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

        send_tel_message(user=user)

        return redirect('index')


class SMSActivate(generic.FormView):
    form_class = ActivateForm
    template_name = 'sms-activate.html'

    # def dispatch(self, request, *args, **kwargs):
    #     super().dispatch()

    def post(self, request):
        user_id = request.session['user_id']
        sms_code = request.POST['sms_code']

        ac = get_object_or_404(
            SmsCode.objects.select_related('user'),
            code=sms_code,
            user_id=user_id,
            is_activated=False,
        )

        if ac.is_expired:
            raise Http404

        ac.is_activated = True
        ac.save(update_fields=['is_activated'])

        user = ac.user
        user.is_active = True
        user.save(update_fields=['is_active'])

        send_tel_message(user=user)
        
        return redirect('index')

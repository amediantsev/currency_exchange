from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from account.forms import SignUpForm, ActivateForm, SignUpSMSForm
from account.models import User, Contact, ActivationCode, SmsCode
from account.tasks import send_email_async
from currency_exchange import settings


class SignUpIndex(generic.TemplateView):
    template_name = 'signup-index.html'


class SignUp(generic.CreateView):
    template_name = 'signup.html'
    queryset = User.objects.all()
    form_class = SignUpForm
    success_url = reverse_lazy('login')


class SignUpSMS(SignUp):
    form_class = SignUpSMSForm
    success_url = reverse_lazy('account:sms-activate')

    def get_success_url(self):
        self.request.session['user_id'] = self.object.id
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
        return redirect('index')

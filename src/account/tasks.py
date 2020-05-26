import requests
import os

from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.conf import settings

from twilio.rest import Client


@shared_task
def send_email_async(subject, message, email_from, recipient_list):
    send_mail(subject, message, email_from, recipient_list)


@shared_task
def send_activation_code_async(email_to, code):
    path = reverse_lazy('account:activate', args=(code, ))
    send_mail('Your activation code',
              f'134.122.114.146{path}',
              'testtestapp454545@gmail.com',
              [email_to],
              fail_silently=False
              )


@shared_task()
def send_sms_code_async(phone, code):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    client.messages.create(
        body=f'Your sms code: {code}',
        from_=settings.MY_PHONE_NUMBER,
        to=phone
    )

    return 'successed!'


@shared_task
def send_tel_message(user):
	bot_api_key = os.environ['TELEGRAM_BOT_API_KEY']
	channel_name = '@CurrencyExchangeBotHillel2'
	message = f'User {user.username} was successfully activated account'

	url = f'https://api.telegram.org/bot{bot_api_key}/sendMessage?chat_id={channel_name}&text={message}'

	params = {
		'chat_id': channel_name,
		'text': message

	}

	print(requests.get(url, params=params).json())

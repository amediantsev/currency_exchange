import requests
import os

from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse


@shared_task
def send_email_async(subject, message, email_from, recipient_list):
    send_mail(subject, message, email_from, recipient_list)


@shared_task
def send_activation_code_async(email_to, code):
    path = reverse('account:activate', args=(code, ))
    send_mail('Your activation code',
              f'127.0.0.1:8000{path}',
              'testtestapp454545@gmail.com',
              [email_to],
              fail_silently=False
              )


@shared_task()
def send_sms_code_async(phone, code):
    print(phone, code)


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

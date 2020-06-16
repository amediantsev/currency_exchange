from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext
from twilio.rest import Client

from account.tasks import send_activation_code_async, send_sms_code_async
import currency.model_choices as mch_currency


def generate_sms_code():
    import random
    return random.randint(1000, 32000)


def avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    f = str(uuid4())
    filename = f'{f}.{ext}'
    return '/'.join(['avatar', str(instance.id), filename])


class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_path,
                               null=True,
                               blank=True,
                               default=None)
    phone = models.CharField(max_length=20)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        gettext('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': gettext("A user with that username already exists."),
            'required': gettext("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        }
    )


class Contact(models.Model):
    email = models.EmailField()
    title = models.CharField(max_length=256)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class ActivationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_codes')
    created = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(default=uuid4, editable=False, unique=True)
    is_activated = models.BooleanField(default=False)

    @property
    def is_expired(self):
        now = timezone.now()
        diff = now - self.created
        return diff.days > 7

    def send_activation_code(self):
        send_activation_code_async(self.user.email, self.code)


class SmsCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_codes')
    created = models.DateTimeField(auto_now_add=True)
    code = models.PositiveSmallIntegerField(default=generate_sms_code)
    is_activated = models.BooleanField(default=False)

    @property
    def is_expired(self):
        now = timezone.now()
        diff = now - self.created
        return diff.days > 7

    def send_sms_code(self):
        send_sms_code_async.delay(
            phone=self.user.phone,
            code = self.code
            )


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors')
    source = models.PositiveSmallIntegerField(choices=mch_currency.SOURCE_CHOICES)
    text = models.TextField(max_length=2000)

    def __str__(self):
        presentation = f'{self.get_source_display()} (by {self.author}): {self.text}'
        if len(self.text) > 20:
            return f'{self.get_source_display()} (by {self.author}): {self.text[0:30]}...'
        return presentation


import account.signals

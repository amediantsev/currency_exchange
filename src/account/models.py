from django.utils import timezone
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser

from account.tasks import send_activation_code_async


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








import account.signals

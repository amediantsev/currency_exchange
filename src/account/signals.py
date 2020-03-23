import os, shutil

from django.db.models.signals import pre_save
from django.dispatch import receiver

from account.models import User
from currency_exchange.settings import MEDIA_ROOT

@receiver(pre_save, sender=User)
def pre_save_User(sender, instance, **kwargs):
    shutil.rmtree(os.path.join(MEDIA_ROOT, 'avatar', str(instance.id)))

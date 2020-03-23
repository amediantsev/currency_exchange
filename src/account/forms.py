from django.contrib.auth.forms import UserCreationForm
from account import models

class UserCreationFormReboot(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.User

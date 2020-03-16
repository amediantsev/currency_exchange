from django.db import models
from django.utils import timezone

from currency import model_choices as mch

class Rate(models.Model):
    created = models.DateTimeField(default=timezone.now)
    currency = models.PositiveSmallIntegerField(choices=mch.CURRENCY_CHOICES)
    buy = models.DecimalField(max_digits=4, decimal_places=2)
    sale = models.DecimalField(max_digits=4, decimal_places=2)
    source = models.PositiveSmallIntegerField(choices=mch.SOURCE_CHOICES)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.get_source_display()} ' \
               f'{self.created.year}-{self.created.month}-{self.created.day} ' \
               f'{self.created.hour}:{self.created.minute} ' \
               f'{self.get_currency_display()} {self.buy} {self.sale}'

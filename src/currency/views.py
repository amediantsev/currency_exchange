import csv

from django.http import HttpResponse
from django.views import generic

from currency.models import Rate

class LastRates(generic.ListView):
    template_name = 'last-rates.html'
    model = Rate
    queryset = Rate.objects.all()
    ordering = '-created'
    paginate_by = 20


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qkngi6q!7y74@lht)x2ivvzcd%^s@g0@_j$^78%$#nft828#dj'
class RateCSV(generic.View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Dispisition'] = 'attachment; filename"rates.csv"'
        writer = csv.writer(response)
        headers = [
            'id',
            'created',
            'currency',
            'buy',
            'sale',
            'source'
        ]
        writer.writerow(headers)
        for rate in Rate.objects.all():
            writer.writerow(map(str, [
                rate.id,
                rate.created,
                rate.get_currency_display(),
                rate.buy,
                rate.sale,
                rate.get_source_display(),
            ]))
        return response

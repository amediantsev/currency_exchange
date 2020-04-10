import csv
from urllib.parse import urlencode

from django.core.cache import cache
from django.http import HttpResponse
from django.views import generic
from django_filters.views import FilterView

from currency.filters import RateFilter
from currency.models import Rate
from currency import model_choices as mch
from currency.utils import generate_rate_cache_key
from currency_exchange.settings import CACHE_RATES_TIMEOUT


class LastRates(FilterView):
    filterset_class = RateFilter
    template_name = 'last-rates.html'
    model = Rate
    queryset = Rate.objects.all()
    ordering = '-created'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        query_params = dict(self.request.GET.items())
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = urlencode(query_params)

        return context


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


class LatestRates(generic.TemplateView):
    template_name = 'latest-rates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['rates'] = Rate.objects.filter(source=mch.SR_PRIVAT, currency=mch.CURR_USD).last()

        cache_key_base = 'latest-rates-{}-{}'


        rates=[]
        for bank in mch.SOURCE_CHOICES:
            source = bank[0]
            for curr in mch.CURRENCY_CHOICES:
                currency = curr[0]
                cache_key = generate_rate_cache_key(source, currency)

                rate = cache.get(cache_key)
                if rate is None:
                    rate = Rate.objects.filter(source=source, currency=currency).order_by('created').last()
                    if rate:
                        rate_dict = {
                            'currency': rate.currency,
                            'source': rate.source,
                            'sale': rate.sale,
                            'buy': rate.sale,
                            'created': rate.created
                        }
                        rates.append(rate_dict)
                        cache.set(cache_key, rate_dict, CACHE_RATES_TIMEOUT)
                else:
                    rates.append(rate)

        context['rates'] = rates
        return context

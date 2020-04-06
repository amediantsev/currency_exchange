import csv
from urllib.parse import urlencode

from django.http import HttpResponse
from django.views import generic
from django_filters.views import FilterView

from currency.filters import RateFilter
from currency.models import Rate

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

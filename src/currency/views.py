import csv
from urllib.parse import urlencode

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django_filters.views import FilterView

from account.models import Comment
from currency.filters import RateFilter
from currency.forms import CommentForm
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
        # context['rates'] = Rate.objects.filter(source=mch.SR_PRIVAT, currency=mch.CURR_USD).last()

        # cache_key_base = 'latest-rates-{}-{}'


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


class Exchangers(generic.FormView):
    template_name = 'exchangers.html'
    queryset = Comment.objects.all()
    success_url = reverse_lazy('account:exchangers')
    model = Comment
    form_class = CommentForm

    def get_context_data(self, *args, **kwargs):        
        context = super().get_context_data()
        
        rates_privat = []
        for curr in mch.CURRENCY_CHOICES:
            rates_privat.append(Rate.objects.filter(source=mch.SR_PRIVAT, currency=curr[0]).last())

        rates_mono = []
        for curr in mch.CURRENCY_CHOICES:
            rates_mono.append(Rate.objects.filter(source=mch.SR_MONO, currency=curr[0]).last())

        rates_vkurse = []
        for curr in mch.CURRENCY_CHOICES:
            rates_vkurse.append(Rate.objects.filter(source=mch.SR_VKURSE, currency=curr[0]).last())

        rates_otp = []
        for curr in (mch.CURRENCY_CHOICES[0], mch.CURRENCY_CHOICES[1]):
            rates_otp.append(Rate.objects.filter(source=mch.SR_OTP, currency=curr[0]).last())

        rates_pumb = []
        for curr in mch.CURRENCY_CHOICES:
            rates_pumb.append(Rate.objects.filter(source=mch.SR_PUMB, currency=curr[0]).last())

        rates_oshchad = []
        for curr in mch.CURRENCY_CHOICES:
            rates_oshchad.append(Rate.objects.filter(source=mch.SR_OSHCHAD, currency=curr[0]).last())

        context['rates_privat'] = rates_privat
        context['rates_mono'] = rates_mono
        context['rates_vkurse'] = rates_vkurse
        context['rates_otp'] = rates_otp
        context['rates_pumb'] = rates_pumb
        context['rates_oshchad'] = rates_oshchad

        form_comments_kwargs = [
            {"context": context, "bank_name": "privat", "choice_id": mch.SR_PRIVAT},
            {"context": context, "bank_name": "mono", "choice_id": mch.SR_MONO},
            {"context": context, "bank_name": "otp", "choice_id": mch.SR_OTP},
            {"context": context, "bank_name": "pumb", "choice_id": mch.SR_PUMB},
            {"context": context, "bank_name": "oshchad", "choice_id": mch.SR_OSHCHAD}
        ]

        for kwargs_dict in form_comments_kwargs:
            form_comments(**kwargs_dict)

        return context


def comment_creation(request, pk):
    Comment.objects.create(
        author=request.user,
        text=request.POST['text'],
        source=pk
    )
    return redirect('currency:exchangers')


def form_comments(context, bank_name, choice_id, *args, **kwargs):
    try:
        context[f"last_comment_{bank_name}"] = Comment.objects.filter(source=choice_id).last()
    except:
        context[choice_id] = 'No comments about this bank'

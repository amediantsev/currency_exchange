from decimal import Decimal
import requests

from celery import shared_task
from bs4 import BeautifulSoup

from currency.models import Rate
from currency import model_choices as mch


def _privat():
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    response = requests.get(url)
    r_json = response.json()

    for rate in r_json:
        if rate['ccy'] in {'USD', 'EUR'}:
            currency = mch.CURR_USD if rate['ccy'] == 'USD' else mch.CURR_EUR
            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(rate['buy']),
                'sale': Decimal(rate['sale']),
                'source': mch.SR_PRIVAT
            }

            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_PRIVAT).last()

            if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
                new_rate.save()

def _mono():
    url = 'https://api.monobank.ua/bank/currency'
    response = requests.get(url)
    r_json = response.json()

    for rate in r_json:
        if (rate['currencyCodeA'] in {840, 978}) and (rate['currencyCodeB'] == 980):
            currency = mch.CURR_USD if rate['currencyCodeA'] == 840 else mch.CURR_EUR
            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(str(round(float(rate['rateBuy']), 2))),
                'sale': Decimal(str(round(float(rate['rateBuy']), 2))),
                'source': mch.SR_MONO
            }
            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_MONO).last()
            if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
                new_rate.save()

def _vkurse():
    url = 'http://vkurse.dp.ua/course.json'
    response = requests.get(url)
    r_json = response.json()

    for curr in r_json:
        if curr in {'Dollar', 'Euro'}:
            if curr == 'Dollar':
                currency = mch.CURR_USD
            else:
                currency = mch.CURR_EUR

            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(r_json[curr]['buy']),
                'sale': Decimal(r_json[curr]['sale']),
                'source': mch.SR_VKURSE
            }
            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_VKURSE).last()
            if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
                new_rate.save()

def _otp():
    url = 'https://www.otpbank.com.ua/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    currency_block = soup.find('tbody', class_='currency-list__body')
    currency_block = currency_block.select("tbody tr")
    for tr_tag in currency_block:
        curr = tr_tag.find('td', class_='currency-list__type').text
        if curr in {'USD', 'EUR'}:
            if curr == 'USD':
                currency = mch.CURR_USD
            else:
                currency = mch.CURR_EUR

            values = tr_tag.findAll('td', class_='currency-list__value')

            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(values[0].text),
                'sale': Decimal(values[1].text),
                'source': mch.SR_OTP
            }
            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_OTP).last()
            if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
                new_rate.save()

def _pumb():
    url = 'https://www.pumb.ua/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    currency_block = soup.find('div', class_='exchange-rate')
    currency_block = currency_block.select("table tr")
    currencies_blocks = [currency_block[0], currency_block[1]]
    for block in currencies_blocks:
        if 'USD' in block.text:
            currency = mch.CURR_USD
        else:
            currency = mch.CURR_EUR

        a = 0
        buy = ''
        sale = ''
        for block in currencies_blocks:                         # походу это уродливый код и вообще костыль
            for i in block:                                     # потом постараюсь оптимизировать
                if a == 10:                                     # у этих тегов просто нету классов,
                    buy = i.text                                # они между собой отличаются только записями
                elif a == 12:
                    sale = i.text
                a += 1

        rate_kwargs = {
            'currency': currency,
            'buy': Decimal(buy),
            'sale': Decimal(sale),
            'source': mch.SR_PUMB
        }
        new_rate = Rate(**rate_kwargs)
        last_rate = Rate.objects.filter(currency=currency, source=mch.SR_PUMB).last()
        if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
            new_rate.save()

def _oshchad():
    url = 'https://www.oschadbank.ua/ua'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    currs = {'USD', 'EUR'}
    for i in currs:
        if i == 'USD':
            currency = mch.CURR_USD
            buy = soup.find('strong', class_='buy-USD').text.strip()
            sale = soup.find('strong', class_='sell-USD').text.strip()
        else:
            currency = mch.CURR_EUR
            buy = soup.find('strong', class_='buy-EUR').text.strip()
            sale = soup.find('strong', class_='sell-EUR').text.strip()

        rate_kwargs = {
            'currency': currency,
            'buy': Decimal(buy),
            'sale': Decimal(sale),
            'source': mch.SR_OSHCHAD
        }
        new_rate = Rate(**rate_kwargs)
        last_rate = Rate.objects.filter(currency=currency, source=mch.SR_OSHCHAD).last()
        if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
            new_rate.save()


@shared_task(bind=True)
def parse_rates(self):
    _privat()
    _mono()
    _vkurse()
    _otp()
    _pumb()
    _oshchad()

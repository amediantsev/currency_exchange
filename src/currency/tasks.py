from decimal import Decimal
import requests

from django.utils import timezone
from celery import shared_task
from bs4 import BeautifulSoup
from pandas import date_range

from currency.models import Rate
from currency import model_choices as mch


def save_rate(last_rate, new_rate):
    if last_rate is None or (new_rate.buy != last_rate.buy or new_rate.sale != last_rate.sale):
        new_rate.save()

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
            save_rate(last_rate, new_rate)

def _mono():
    url = 'https://api.monobank.ua/bank/currency'
    response = requests.get(url)
    r_json = response.json()

    for rate in r_json:
        if (rate['currencyCodeA'] in {840, 978}) and (rate['currencyCodeB'] == 980):
            currency = mch.CURR_USD if rate['currencyCodeA'] == 840 else mch.CURR_EUR
            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(str(round(rate['rateBuy'], 2))),
                'sale': Decimal(str(round(rate['rateSell'], 2))),
                'source': mch.SR_MONO
            }
            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_MONO).last()
            save_rate(last_rate, new_rate)

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

            buy = r_json[curr]['buy'].replace(',', '.')
            sale = r_json[curr]['sale'].replace(',', '.')

            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(buy),
                'sale': Decimal(sale),
                'source': mch.SR_VKURSE
            }

            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_VKURSE).last()
            save_rate(last_rate, new_rate)

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
            save_rate(last_rate, new_rate)

def _pumb():
    url = 'https://www.pumb.ua/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    currency_block = soup.find('div', class_='exchange-rate')
    currency_block = currency_block.select("table tr")
    target_blocks = [currency_block[1], currency_block[2]]

    for block in target_blocks:
        if block.text.strip().split('\n')[0] == 'USD':
            currency = mch.CURR_USD
        else:
            currency = mch.CURR_EUR

        block = block.find_all('td')
        sale = block[1].text
        buy = block[2].text

        rate_kwargs = {
            'currency': currency,
            'buy': Decimal(buy),
            'sale': Decimal(sale),
            'source': mch.SR_PUMB
        }

        new_rate = Rate(**rate_kwargs)
        last_rate = Rate.objects.filter(currency=currency, source=mch.SR_PUMB).last()
        save_rate(last_rate, new_rate)

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
        save_rate(last_rate, new_rate)


@shared_task(bind=True)
def parse_rates(self):
    _privat()
    _mono()
    _vkurse()
    _otp()
    _pumb()
    _oshchad()


@shared_task(bind=True)
def parse_archive_rates(self):
    end_date = timezone.now().date()
    five_years = timezone.timedelta(days=(365*5 + 2)) # 2016 and 2020 - leap years
    daterange = date_range(end_date - five_years, end_date)
    for date in daterange:
        response = requests.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date.day}.{date.month}.{date.year}')
        r_json = response.json()
        if Rate.objects.filter(created=date) == 0:
            for rate in r_json['exchangeRate']:
                if rate['currency'] == 'USD':
                    Rate.objects.create(
                        created=str(date.date()),
                        currency=mch.CURR_USD,
                        buy = rate['purchaseRate'],
                        sale = rate['saleRate'],
                        source = mch.SR_PRIVAT
                    )
                if rate['currency'] == 'EUR':
                    Rate.objects.create(
                        created=str(date.date()),
                        currency=mch.CURR_EUR,
                        buy=rate['purchaseRate'],
                        sale=rate['saleRate'],
                        source=mch.SR_PRIVAT
                    )

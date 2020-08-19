from decimal import Decimal
import requests

from django.utils import timezone
from celery import shared_task
from bs4 import BeautifulSoup as bs
from pandas import date_range

from currency.models import Rate
from currency import model_choices as mch
from currency.utils import save_rate


def _privat():
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    response = requests.get(url)
    r_json = response.json()

    for rate in r_json:
        if rate['ccy'] in {'USD', 'EUR', 'RUR'}:
            if rate['ccy'] == 'USD':
                currency = mch.CURR_USD
            elif rate['ccy'] == 'EUR':
                currency = mch.CURR_EUR
            else:
                currency = mch.CURR_RUB

            rate_kwargs = {
                'currency': currency,
                'buy': Decimal(rate['buy'][:6]),
                'sale': Decimal(rate['sale'][:6]),
                'source': mch.SR_PRIVAT
            }

            new_rate = Rate(**rate_kwargs)
            last_rate = Rate.objects.filter(currency=currency, source=mch.SR_PRIVAT).last()
            save_rate(last_rate, new_rate)


def _mono():
    url = 'https://api.monobank.ua/bank/currency'
    response = requests.get(url)
    r_json = response.json()

    if r_json != {'errorDescription': 'Too many requests'}:
        for rate in r_json:
            if (rate['currencyCodeA'] in {840, 978, 643}) and (rate['currencyCodeB'] == 980):
                if rate['currencyCodeA'] == 840:
                    currency = mch.CURR_USD
                elif rate['currencyCodeA'] == 978:
                    currency = mch.CURR_EUR
                elif rate['currencyCodeA'] == 643:
                    currency = mch.CURR_RUB

                rate_kwargs = {
                    'currency': currency,
                    'buy': Decimal(str(round(rate['rateBuy'], 3))),
                    'sale': Decimal(str(round(rate['rateSell'], 3))),
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
            if curr == 'Dollar':
                currency = mch.CURR_USD
            elif curr == 'Euro':
                currency = mch.CURR_EUR
            else:
                currency = mch.CURR_RUB

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
    soup = bs(response.content, 'html.parser')
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
    soup = bs(response.content, 'html.parser')
    currency_block = soup.find('div', class_='exchange-rate')
    currency_block = currency_block.select("table tr")
    target_blocks = [currency_block[1], currency_block[2], currency_block[3]]

    for block in target_blocks:
        if block.text.strip().split('\n')[0] == 'USD':
            currency = mch.CURR_USD
        elif block.text.strip().split('\n')[0] == 'EUR':
            currency = mch.CURR_EUR
        else:
            currency = mch.CURR_RUB

        block = block.find_all('td')
        buy = block[1].text
        sale = block[2].text

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
    response = requests.get(url, verify=False)
    soup = bs(response.content, 'html.parser')
    currs = {'USD', 'EUR', 'RUB'}

    for i in currs:
        if i == 'USD':
            currency = mch.CURR_USD
            buy = soup.find('strong', class_='buy-USD').text.strip()
            sale = soup.find('strong', class_='sell-USD').text.strip()
        elif i == 'EUR':
            currency = mch.CURR_EUR
            buy = soup.find('strong', class_='buy-EUR').text.strip()
            sale = soup.find('strong', class_='sell-EUR').text.strip()
        else:
            currency = mch.CURR_RUB
            buy = soup.find('strong', class_='buy-RUB').text.strip()
            sale = soup.find('strong', class_='sell-RUB').text.strip()

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
    start_date = end_date - five_years
    daterange = date_range(start_date, end_date)
    for date in daterange:
        response = requests.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date.day}.{date.month}.{date.year}')
        r_json = response.json()
        if len(Rate.objects.filter(created=date)) == 0:
            for rate in r_json['exchangeRate']:
                if rate['currency'] == 'USD':
                    Rate.objects.create(
                        created=str(date.date()),
                        currency=mch.CURR_USD,
                        buy = rate['purchaseRate'],
                        sale = rate['saleRate'],
                        source = mch.SR_PRIVAT
                    )
                elif rate['currency'] == 'EUR':
                    Rate.objects.create(
                        created=str(date.date()),
                        currency=mch.CURR_EUR,
                        buy=rate['purchaseRate'],
                        sale=rate['saleRate'],
                        source=mch.SR_PRIVAT
                    )
                elif rate['currency'] == 'RUR':
                    Rate.objects.create(
                        created=str(date.date()),
                        currency=mch.CURR_RUB,
                        buy=rate['purchaseRate'],
                        sale=rate['saleRate'],
                        source=mch.SR_PRIVAT
                    )
 
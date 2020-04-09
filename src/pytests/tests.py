from uuid import uuid4
import pytest

from django.urls import reverse
from django.core import mail

from account.models import Contact
from account.tasks import send_activation_code_async
from currency.models import Rate
from currency import tasks


class Response:
    pass

def test_sanity():
    assert 200 == 200

def test_index_page(client):
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 200

def test_get_rates_api_not_auth(client):
    url = reverse('api-currency:rates')
    response = client.get(url)
    assert response.status_code == 401
    resp_j = response.json()
    assert len(resp_j) == 1
    assert resp_j['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_rates_api_auth(api_client, user):
    url = reverse('api-currency:rates')
    response = api_client.get(url)
    assert response.status_code == 401

    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_get_put_delete_rate_api(api_client, user):

    # GET List

    url = reverse('api-currency:rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200

    # POST method

    response = api_client.post(
        url,
        data={
            'sale': '11.11',
            'buy': '11.11',
            'source': '1',
            'currency': '1',
            format: 'json'
        }
    )
    assert response.status_code == 201

    # GET method

    id = str(Rate.objects.last().id)
    url_id = url + id + '/'
    response = api_client.get(url_id)
    assert response.status_code == 200

    # PUT method

    response = api_client.put(
        url_id,
        data={
            'sale': '22.22',
            'buy': '22.22',
            'source': '2',
            'currency': '2',
            format: 'json'
        }
    )
    assert response.status_code == 200

    # DELETE method

    response = api_client.delete(url_id)
    assert response.status_code == 204


@pytest.mark.django_db
def test_get_rates_api(api_client, user):
    url = reverse('api-currency:rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_contact_api_not_auth(client):
    url = reverse('api-currency:contacts')
    response = client.get(url)
    assert response.status_code == 401
    resp_j = response.json()
    assert len(resp_j) == 1
    assert resp_j['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_contacts_api_auth(api_client, user):
    url = reverse('api-currency:contacts')
    response = api_client.get(url)
    assert response.status_code == 401

    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_get_put_delete_contact_api(api_client, user):
    url = reverse('api-currency:contacts')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200

    # POST method

    response = api_client.post(
        url,
        data={
            'title': 'it\'s title of message',
            'body': 'it\'s body of message',
            format: 'json'
        }
    )
    assert response.status_code == 201

    # GET method

    id = str(Contact.objects.last().id)
    url_id = url + id + '/'
    response = api_client.get(url_id)
    assert response.status_code == 200

    # PUT method

    response = api_client.put(
        url_id,
        data={
            'title': 'it\'s NEW title of message',
            'body': 'it\'s NEW body of message',
            format: 'json'
        }
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_send_email(mocker):
    emails = mail.outbox

    send_activation_code_async(1, str(uuid4()))

    emails = mail.outbox
    assert len(mail.outbox) == 1

    email = mail.outbox[0]


@pytest.mark.django_db
def test_contactus(client, user):
    contact_url = reverse('account:contact-us')

    response = client.get(contact_url)
    assert response.status_code == 200

    login_url = reverse('login')
    response = client.get(login_url)
    assert response.status_code == 200

    response = client.post(
        login_url,
        data={'username': user.username, 'password': user.raw_password, format: 'json'},
    )
    assert response.status_code == 302

    response = client.get(contact_url)
    assert response.status_code == 200

    response = client.post(
        login_url,
        data={'title': 'it\'s title of message', 'body': 'it\'s body of mail', format: 'json'},
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_privat(mocker):

    def mock():
        response = Response()
        response.json = lambda: [
            {
                'ccy': 'USD',
                'base_ccy': 'UAH',
                'buy': '27.05000',
                'sale': '27.50000'
            },
            {
                'ccy': 'EUR',
                'base_ccy': 'UAH',
                'buy': '29.30000',
                'sale': '30.05000'
            },
            {
                'ccy': 'RUR',
                'base_ccy': 'UAH',
                'buy': '0.32500',
                'sale': '0.37500'
            },
        ]

        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    tasks._privat()


@pytest.mark.django_db
def test_task_mono(mocker):

    def mock():
        response = Response()
        response.json = lambda: [
            {
                'currencyCodeA': 840,
                'currencyCodeB': 980,
                'date': 1586439005,
                'rateBuy': 27.25,
                'rateSell': 27.4725
            },
            {
                'currencyCodeA': 978,
                'currencyCodeB': 980,
                'date': 1586439005,
                'rateBuy': 29.5,
                'rateSell': 30.03
            },
            {
                'currencyCodeA': 643,
                'currencyCodeB': 980,
                'date': 1586439605,
                'rateBuy': 0.325,
                'rateSell': 0.375
            },
        ]

        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    tasks._mono()


@pytest.mark.django_db
def test_task_mono(mocker):

    def mock():
        response = Response()
        response.json = lambda: {
             'Dollar': {'buy': '27.38', 'sale': '27.48'},
             'Euro': {'buy': '29.50', 'sale': '29,90'},
             'Rub': {'buy': '0.346', 'sale': '0.360'},

        }
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    tasks._vkurse()

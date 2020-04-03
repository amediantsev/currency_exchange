from uuid import uuid4
import pytest

from django.urls import reverse
from django.core import mail

from account.tasks import send_activation_code_async
from currency.tasks import _privat


class Response:
    pass

def test_sanity():
    assert 200 == 200

def test_index_page(client):
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 200

def test_get_rates_not_auth(client):
    url = reverse('api-currency:rates')
    response = client.get(url)
    assert response.status_code == 401
    resp_j = response.json()
    assert len(resp_j) == 1
    assert resp_j['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_rates_auth(api_client, user):
    url = reverse('api-currency:rates')
    response = api_client.get(url)
    assert response.status_code == 401

    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.skip
@pytest.mark.django_db
def test_get_rates(api_client, user):
    url = reverse('api-currency:rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


# @pytest.mark.django_db
# def test_task(mocker):
#
#     def mock():
#         response = Response()
#         response.json = lambda: [{'ccy': 'USD'}]
#         return response
#
#     requests_get_patcher = mocker.patch('requests.get')
#     requests_get_patcher.return_value = mock()
#     _privat()


@pytest.mark.django_db
def test_send_email(mocker):
    emails = mail.outbox
    print('EMAILS:', emails)

    send_activation_code_async(1, str(uuid4()))

    emails = mail.outbox
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    print(email.__dict__)

from rest_framework import generics

from currency.api.serializers import *
from currency.api.filters import *
from currency_exchange.settings import EMAIL_HOST_USER


class RatesView(generics.ListCreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RateFilter


class RateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class ContactsView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ContactFilter

    def get_queryset(self):
        super().get_queryset()
        self.queryset = Contact.objects.filter(email=self.request.user.email)
        return self.queryset


class ContactView(generics.RetrieveUpdateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        super().get_queryset()
        self.queryset = Contact.objects.filter(email=self.request.user.email)
        return self.queryset

#  filters - https://django-filter.readthedocs.io/en/master/
'''
1.
http://127.0.0.1:8000/api/v1/currency/rates/?created__lt=10/10/2019
'created' - exact, lt, lte, gt, gte + BONUS range
'currency', - exact
'source', - exact
2. account.model.Contact - /contacts/ - GET, POST
                           /contacts/<id>/ - GET, PUT
                           list only auth users (request.user)
                           send email after create (/contacts/id/ POST)

3. BONUS
ADD TESTS for API
self.client.get('api/v1/currency/rates/') -> json
self.client.post('api/v1/currency/rates/', data={}) -> json['id']
self.client.get('api/v1/currency/rates/json['id']') -> status_code == 200
'''

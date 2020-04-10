from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from currency.api.serializers import *
from currency.api.filters import *


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RatesView(generics.ListCreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RateFilter
    pagination_class = StandardResultsSetPagination


class RateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class ContactsView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ContactFilter
    pagination_class = StandardResultsSetPagination

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

from rest_framework import generics

from currency.api.serializers import *
from currency.api.filters import *


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

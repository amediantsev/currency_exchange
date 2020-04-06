from django_filters import rest_framework as filters

from account.models import Contact
from currency.models import Rate


class RateFilter(filters.FilterSet):
    created = filters.DateFilter(field_name="created", lookup_expr="date")
    created_lt = filters.DateFilter(field_name="created", lookup_expr="date__lt")
    created_lte = filters.DateFilter(field_name="created", lookup_expr="date__lte")
    created_gt = filters.DateFilter(field_name="created", lookup_expr="date__gt")
    created_gte = filters.DateFilter(field_name="created", lookup_expr="date__gte")

    class Meta:
        model = Rate
        fields = ['source', 'currency']


class ContactFilter(filters.FilterSet):
    created = filters.DateFilter(field_name="created", lookup_expr="date")
    created_lt = filters.DateFilter(field_name="created", lookup_expr="date__lt")
    created_lte = filters.DateFilter(field_name="created", lookup_expr="date__lte")
    created_gt = filters.DateFilter(field_name="created", lookup_expr="date__gt")
    created_gte = filters.DateFilter(field_name="created", lookup_expr="date__gte")

    class Meta:
        model = Contact
        fields = ['title', 'body']

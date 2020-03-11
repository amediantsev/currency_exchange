from django.views.generic import ListView

from currency.models import Rate

class LastRates(ListView):
    template_name = 'last-rates.html'
    model = Rate
    queryset = Rate.objects.all()
    ordering = '-created'
    paginate_by = 20

from django.core.management.base import BaseCommand

from currency.tasks import parse_archive_rates


class Command(BaseCommand):
    help = 'Parse the archive of the exchange rate of the PrivatBank' \
           'over the past few years and insert these into the database'

    def handle(self, *args, **options):
        parse_archive_rates.delay()

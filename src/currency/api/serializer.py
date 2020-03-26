from rest_framework import serializers

from currency.models import Rate


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('id', 'created', 'buy', 'sale', )
        extra_kwargs = {
            'currency': {'write_only': True},
            'source': {'write_only': True},
        }

from rest_framework import serializers

from account.models import Contact
from currency.models import Rate
from currency_exchange.settings import EMAIL_HOST_USER
from account.tasks import send_email_async


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = (
            'id',
            'created',
            'get_currency_display',
            'currency',
            'buy',
            'sale',
            'get_source_display',
            'source',
        )
        extra_kwargs = {
            'currency': {'write_only': True},
            'source': {'write_only': True},
        }


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = (
            'id',
            'created',
            'title',
            'body',
        )


    def create(self, validated_data):
        self.validated_data['email'] = self.context['request'].user.email
        email_from = self.validated_data['email']
        message = self.validated_data['body']
        subject = self.validated_data['title']
        recipient_list = [EMAIL_HOST_USER]
        send_email_async.delay(subject, message, email_from, recipient_list)

        return super().create(self.validated_data)

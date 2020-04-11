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
        username = self.context['request'].user.username
        user_fn_ln = self.context['request'].user.first_name + ' ' + self.context['request'].user.last_name
        user_email = self.context['request'].user.email

        self.validated_data['email'] = user_email

        subject = f'From {user_email}: ' + self.validated_data['title']
        message = self.validated_data['body'] + \
        '\n\n' + \
        '*' * 100 + \
        f'\n\nWas sent from {user_fn_ln} ({username}) with email {user_email}'

        email_from = EMAIL_HOST_USER 
        recipient_list = [EMAIL_HOST_USER]
        
        send_email_async.delay(subject, message, email_from, recipient_list)

        return super().create(self.validated_data)

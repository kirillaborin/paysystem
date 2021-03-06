from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import Bill, Transaction


class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        instance = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return instance

    class Meta:
        model = User
        fields = ('pk', 'username', 'password')


class BillSerializer(ModelSerializer):
    currency_code = serializers.ReadOnlyField(source='currency.code')
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Bill
        fields = ('pk', 'owner', 'currency_code', 'amount')


class TransactionSerializer(ModelSerializer):
    sender = serializers.ReadOnlyField(source='source_bill.owner.username')
    recipient = serializers.ReadOnlyField(source='dest_bill.owner.username')
    source_amount = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = (
            'pk',
            'source_bill',
            'dest_bill',
            'source_amount',
            'dest_amount',
            'sender',
            'recipient',
            'created_at',
            'type'
        )

    def validate(self, data):
        if data['source_bill'].owner != self.context['request'].user:
            raise serializers.ValidationError({
                'source_bill': 'it\'s not your bill'
            })

        if data['source_bill'] == data['dest_bill']:
            raise serializers.ValidationError(
                "You need different source and dest bills"
            )

        if data['dest_amount'] <= 0:
            raise serializers.ValidationError({
                'dest_amount': 'only positive value'
            })

        return data

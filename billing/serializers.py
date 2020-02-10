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

    class Meta:
        model = Bill
        fields = ('pk', 'owner', 'currency', 'amount')


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

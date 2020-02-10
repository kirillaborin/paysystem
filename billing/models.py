from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F


def convert_currency(cur_from, cur_to, amount):
    return amount / settings.CONVERT_RATES.get(
        (cur_from, cur_to), 1
    )


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.code.upper()


class Bill(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator('0')]
    )

    class Meta:
        unique_together = ['currency', 'owner']

        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte='0'),
                name='bill_balance_non_negative'
            )
        ]

    def __str__(self):
        return '%s: %s %s' % (
            self.owner.username, self.amount, self.currency.code)


class TransactionBase(models.Model):

    class Type(models.IntegerChoices):
        TRANSFER = 0
        FEE = 1

    source_bill = models.ForeignKey(
        Bill,
        related_name='transactions_in',
        on_delete=models.PROTECT
    )
    dest_bill = models.ForeignKey(
        Bill,
        related_name='transactions_out',
        on_delete=models.PROTECT
    )
    type = models.SmallIntegerField(
        choices=Type.choices,
        default=Type.TRANSFER
    )
    source_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    dest_amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'billing_transaction'

    def __str__(self):
        return '%s to %s %s %s' % (
            self.type,
            self.dest_bill.owner,
            self.dest_amount,
            self.dest_bill.currency
        )


class TransactionManager(models.Manager):
    """
    управляет логикой переводов между счетами
    """
    @transaction.atomic()
    def create(self, **kwargs):
        """
        создает перевод, при необходимости комиссию
        + обновляет балансы счетов
        """
        source_amount = dest_amount = kwargs['dest_amount']
        source_bill = kwargs['source_bill']
        dest_bill = kwargs['dest_bill']

        if source_bill.currency.pk != dest_bill.currency.pk:
            # нужна конвертация
            source_amount = convert_currency(
                source_bill.currency.code,
                dest_bill.currency.code,
                dest_amount
            )

        transfer = TransactionBase.objects.create(
            source_bill=source_bill,
            dest_bill=dest_bill,
            type=self.model.Type.TRANSFER,
            source_amount=source_amount,
            dest_amount=dest_amount
        )

        source_bill.amount = F('amount') - source_amount
        source_bill.save()
        dest_bill.amount = F('amount') + dest_amount
        dest_bill.save()

        if source_bill.owner.pk != dest_bill.owner.pk:
            # платим комиссию в пользу системы
            self.pay_system_fee(source_bill, source_amount)

        return transfer

    def pay_system_fee(self, source_bill, source_amount):
        """
        платим комиссию системному
        аккаунту в той же валюте
        """
        system_bill = Bill.objects.get(
            owner__username='system',
            currency=source_bill.currency
        )
        fee_amount = source_amount * settings.TRANSFER_RATE
        TransactionBase.objects.create(
            source_bill=source_bill,
            dest_bill=system_bill,
            type=self.model.Type.FEE,
            source_amount=fee_amount,
            dest_amount=fee_amount
        )


class Transaction(TransactionBase):
    objects = TransactionManager()

    class Meta:
        proxy = True

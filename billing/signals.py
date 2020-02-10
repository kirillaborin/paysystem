#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Currency, Bill


@receiver(post_save, sender=User)
def create_bills_with_gift(sender, instance, created, **kwargs):
    """
    создает счета, на долларовый +100$ подарок
    """
    if created:
        for currency in Currency.objects.all():
            amount = Decimal('100' if currency.code == 'usd' else '0')
            Bill.objects.create(
                currency=currency,
                amount=amount,
                owner=instance
            )

from django import template

from myhpi.vouchers import models

register = template.Library()


@register.filter
def first(voucher_allocation):
    return voucher_allocation.vouchers.fisrt()


@register.filter
def other(voucher_allocation):
    return voucher_allocation.vouchers.exclude(pk=voucher_allocation.vouchers.first().pk)


@register.filter
def is_angel(user):
    return models.is_angel(user)

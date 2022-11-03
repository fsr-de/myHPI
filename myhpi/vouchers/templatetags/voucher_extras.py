from django import template

from myhpi.vouchers import models

register = template.Library()


@register.filter
def is_angel(user):
    return models.is_angel(user)

import json
import random
import string
from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models, transaction, IntegrityError
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.models import BasePage


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    voucher_count = models.IntegerField(default=2)
    regular_ticket_id = models.IntegerField()
    angel_ticket_id = models.IntegerField()

    def __str__(self):
        return self.title


class Voucher(models.Model):
    ANGEL_TYPE = "A"
    REGULAR_TYPE = "R"
    TYPE_CHOICES = [
        (ANGEL_TYPE, _("Angel")),
        (REGULAR_TYPE, _("Regular"))
    ]

    code = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=REGULAR_TYPE)
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        return f"Voucher {self.code}"


class VoucherAllocation(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    vouchers = models.ManyToManyField(Voucher)

    def __str__(self):
        return f"Voucher allocation for {self.user} @ {self.event}"


class VoucherObtainPage(BasePage):
    body = CustomMarkdownField()
    event = models.OneToOneField(Event, on_delete=models.CASCADE)

    parent_page_types = [
        "core.RootPage",
    ]
    subpage_types = []
    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("event"),
    ]

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            if VoucherAllocation.objects.filter(user=request.user, event=self.event).exists():
                messages.error(request, _("You already have a voucher for this event."))
            else:
                is_angel = False  # TODO: get from engelsystem
                voucher_data = []
                vouchers = []
                if is_angel:
                    voucher = Voucher(code=''.join(random.choice(string.ascii_uppercase) for i in range(16)))
                    voucher_data.append({
                        "code": voucher.code,
                        "max_usages": 1,
                        "item": self.event.angel_ticket_id,
                        "tag": "angel",
                        "comment": f"created for {request.user.email} at {datetime.now()}",
                    })
                    vouchers.append(voucher)
                for i in range(self.event.voucher_count - len(voucher_data)):
                    voucher = Voucher(code=''.join(random.choice(string.ascii_uppercase) for i in range(16)))
                    voucher_data.append({
                      "code": voucher.code,
                      "max_usages": 1,
                      "item": self.event.regular_ticket_id,
                      "tag": "regular",
                      "comment": f"created for {request.user.email} at {datetime.now()}",
                    })
                    vouchers.append(voucher)
                result = requests.post(
                    url=f"{settings.PRETIX_BASE_URL}/api/v1/organizers/verde/events/{self.event.slug}/vouchers/batch_create/",
                    headers={"Authorization": f"Token {settings.PRETIX_API_TOKEN}"},
                    json=voucher_data
                )
                if result.status_code != 201:
                    messages.error(request, _("An error occurred while creating your vouchers."))
                    print(result.content)
                else:
                    try:
                        with transaction.atomic():
                            allocation = VoucherAllocation.objects.create(user=request.user, event=self.event)
                            for voucher in vouchers:
                                voucher.save()
                                allocation.vouchers.add(voucher)
                            allocation.save()
                            messages.success(request, _("Your vouchers have been created."))
                    except IntegrityError as e:
                        print(e)
                        messages.error(request, _("An error occurred while creating your vouchers."))
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try:
            context["voucher_allocation"] = VoucherAllocation.objects.get(user=request.user)
        except VoucherAllocation.DoesNotExist:
            pass
        return context

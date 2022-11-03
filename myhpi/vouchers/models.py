import random
import string
from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.models import BasePage


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    additional_voucher_count = models.IntegerField(default=1)
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
        return self.code

    def redemption_url(self):
        event = None
        if self.voucherallocation_set.exists():
            event = self.voucherallocation_set.first().event
        elif self.own_voucher is not None:
            event = self.own_voucher.event
        return f"{settings.PRETIX_BASE_URL}/verde/{event.slug}/redeem?voucher={self.code}" if event else None

    def submit_to_pretix(self, event, user):
        voucher_data = {
            "code": self.code,
            "max_usages": 1,
            "item": event.angel_ticket_id if self.type == self.ANGEL_TYPE else event.regular_ticket_id,
            "tag": "angel" if self.type == self.ANGEL_TYPE else "regular",
            "comment": f"created for {user.email} at {datetime.now()}",
            "show_hidden_items": True,
        }
        return requests.post(
            url=f"{settings.PRETIX_BASE_URL}/api/v1/organizers/verde/events/{event.slug}/vouchers/",
            headers={"Authorization": f"Token {settings.PRETIX_API_TOKEN}"},
            data=voucher_data
        )


class VoucherAllocation(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    own_voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name="own_voucher", null=True, blank=True)
    additional_vouchers = models.ManyToManyField(Voucher)

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

    @method_decorator(login_required, name='dispatch')
    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            if "generate_own" in request.POST or "generate_angel" in request.POST:
                if "generate_own" in request.POST and is_angel(request.user) or "generate_angel" in request.POST and not is_angel(request.user):
                    messages.error(request, "You are not allowed to generate this type of voucher.")
                if (allocation := VoucherAllocation.objects.filter(user=request.user, event=self.event)).exists() and allocation.first().own_voucher is not None:
                    messages.error(request, _("You already have an own voucher."))
                else:
                    voucher = Voucher(type=Voucher.ANGEL_TYPE if is_angel(request.user) else Voucher.REGULAR_TYPE, code=''.join(random.choice(string.ascii_uppercase) for i in range(16)))
                    result = voucher.submit_to_pretix(self.event, request.user)
                    if result.status_code != 201:
                        messages.error(request, _("An error occurred while creating your voucher."))
                    else:
                        voucher.save()
                        if not allocation.exists():
                            allocation = VoucherAllocation(user=request.user, event=self.event)
                        else:
                            allocation = allocation.first()
                        allocation.own_voucher = voucher
                        allocation.save()
                        messages.success(request, _("Your voucher has been created."))
            elif "generate_additional" in request.POST:
                if (allocation := VoucherAllocation.objects.filter(user=request.user, event=self.event)).exists() and allocation.first().additional_vouchers.count() >= self.event.additional_voucher_count:
                    messages.error(request, _("You cannot create additional vouchers."))
                else:
                    voucher = Voucher(code=''.join(random.choice(string.ascii_uppercase) for i in range(16)))
                    result = voucher.submit_to_pretix(self.event, request.user)
                    if result.status_code != 201:
                        messages.error(request, _("An error occurred while creating your voucher."))
                    else:
                        voucher.save()
                        if not allocation.exists():
                            allocation = VoucherAllocation(user=request.user, event=self.event)
                            allocation.save()
                        else:
                            allocation = allocation.first()
                        allocation.additional_vouchers.add(Voucher.objects.get(code=voucher.code))
                        allocation.save()
                        messages.success(request, _("Your voucher has been created."))
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try:
            context["voucher_allocation"] = VoucherAllocation.objects.get(user=request.user)
        except VoucherAllocation.DoesNotExist:
            pass
        return context


def is_angel(user):
    return True  # TODO: get from Engelsystem

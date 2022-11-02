import random
import string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.models import BasePage


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

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
                allocation = VoucherAllocation.objects.create(user=request.user, event=self.event)
                for i in range(2):
                    voucher = Voucher(code=''.join(random.choice(string.ascii_uppercase) for i in range(16)))
                    voucher.save()
                    allocation.vouchers.add(voucher)
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try:
            context["voucher_allocation"] = VoucherAllocation.objects.get(user=request.user)
        except VoucherAllocation.DoesNotExist:
            pass
        return context

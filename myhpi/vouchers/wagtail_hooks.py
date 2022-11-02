from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from myhpi.vouchers.models import Event


class EventAdmin(ModelAdmin):
    model = Event
    add_to_settings_menu = True


modeladmin_register(EventAdmin)

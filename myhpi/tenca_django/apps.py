from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TencaDjangoConfig(AppConfig):
    name = "myhpi.tenca_django"
    verbose_name = _("Mailing Lists")

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from myhpi.core.models import (
    AbbreviationExplanation,
    InformationPage,
    Minutes,
    MinutesLabel,
    MinutesList,
)


class MinutesLabelAdmin(ModelAdmin):
    model = MinutesLabel
    add_to_settings_menu = True


class AbbreviationExplanationAdmin(ModelAdmin):
    model = AbbreviationExplanation
    add_to_settings_menu = True


modeladmin_register(MinutesLabelAdmin)
modeladmin_register(AbbreviationExplanationAdmin)


@hooks.register("before_serve_page")
def check_view_permissions(page, request, serve_args, serve_kwargs):
    if isinstance(page, (Minutes, MinutesList, InformationPage)):
        target_groups = request.user.groups.all()
        if request.user.is_superuser:
            return
        if getattr(request.user, "_ip_range_group_name", None):
            target_groups = Group.objects.filter(
                Q(name=request.user._ip_range_group_name) | Q(id__in=request.user.groups.all())
            )
        is_matching_group = any(group in page.visible_for.all() for group in target_groups)
        if not (is_matching_group or page.is_public):
            raise PermissionDenied


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("css/myHPI_admin.css"))


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    return format_html('<script src="{}"></script>', static("js/admin/easymde_custom.js"))

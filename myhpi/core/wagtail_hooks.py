from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from myhpi.core.models import AbbreviationExplanation, Minutes, MinutesLabel


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
    if isinstance(page, Minutes):
        target_groups = request.user.groups.all()
        if getattr(request.user, "_ip_range_group_name", None):
            target_groups = Group.objects.filter(
                Q(name=request.user._ip_range_group_name) | Q(id__in=request.user.groups.all())
            )
        if not any(group in page.visible_for.all() for group in target_groups):
            raise PermissionDenied


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("css/myHPI_admin.css"))

from itertools import chain

from django.core.exceptions import PermissionDenied
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks

from myhpi.core.models import InformationPage, Minutes, MinutesList


@hooks.register("before_serve_page")
def check_view_permissions(page, request, serve_args, serve_kwargs):
    if isinstance(page, (Minutes, MinutesList, InformationPage)):
        page.specific.check_can_view(request)


@hooks.register("before_serve_document")
def check_document_permissions(document, request):
    can_view = False
    for page in chain(document.informationpage_set.all(), document.minutes_set.all()):
        try:
            check_view_permissions(page, request, (), {})
            can_view = True
            break
        except PermissionDenied:
            continue
    if not can_view:
        raise PermissionDenied


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("css/myHPI_admin.css"))


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    return format_html(
        '<script src="{}"></script><script src="{}"></script><script src="{}"></script>',
        static("js/admin/easymde_custom.js"),
        static("wagtailimages/js/image-chooser-modal.js"),
        static("wagtailadmin/js/page-chooser-modal.js"),
    )

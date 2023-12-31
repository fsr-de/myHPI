import os

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from myhpi.search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("select2/", include("django_select2.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path(
        ".well-known/security.txt",
        RedirectView.as_view(url=os.path.join(settings.STATIC_URL, "security.txt")),
    ),
    path("", include("myhpi.core.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_MAILING_LISTS:
    urlpatterns += i18n_patterns(
        path("lists/", include("myhpi.tenca_django.urls")),
        # This is done manually, but shouldn't. It's all due to the ominous "problems with trailing slashes"
        path(
            "lists",
            RedirectView.as_view(url=reverse_lazy("tenca_django:tenca_dashboard")),
            name="tenca_index",
        ),
    )

urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
)

if settings.ENABLE_MAILING_LISTS:
    urlpatterns += i18n_patterns(
        path("lists/", include("myhpi.tenca_django.urls")),
        # This is done manually, but shouldn't. It's all due to the ominous "problems with trailing slashes"
        path(
            "lists",
            RedirectView.as_view(url=reverse_lazy("tenca_django:tenca_dashboard")),
            name="tenca_index",
        ),
    )

urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
)

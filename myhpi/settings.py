import os
import sys
from email.utils import getaddresses

import tenca
from django.contrib.messages import constants
from environ import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(interpolate=True)
# for syntax see https://django-environ.readthedocs.io/en/latest/
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
DJANGO_DEBUG = env.bool("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SITE_URL = env.str("SITE_URL")
if SITE_URL.endswith("/"):
    SITE_URL = SITE_URL[:-1]

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_REFERRER_POLICY = "same-origin"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django_bootstrap_icons",
    "django_select2",
    "modelcluster",
    "mozilla_django_oidc",
    "taggit",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.contrib.modeladmin",
    "wagtail",
    "wagtail_localize",
    "wagtail_localize.locales",
    "wagtailmarkdown",
    "myhpi.core",
    "myhpi.polls",
    "myhpi.search",
    "static_precompiler",
    "django_prometheus",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "myhpi.core.auth.MyHPIOIDCAB",
]

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_SCOPES = "openid email profile"
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 3600  # renew auth after 1 hour

OIDC_RP_CLIENT_ID = env.str("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env.str("OIDC_RP_CLIENT_SECRET")

OIDC_REALM = "myhpi-testing" if DEBUG else "fsr"
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    f"https://auth.myhpi.de/realms/{OIDC_REALM}/protocol/openid-connect/auth"
)
OIDC_OP_TOKEN_ENDPOINT = f"https://auth.myhpi.de/realms/{OIDC_REALM}/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = (
    f"https://auth.myhpi.de/realms/{OIDC_REALM}/protocol/openid-connect/userinfo"
)
OIDC_OP_JWKS_ENDPOINT = f"https://auth.myhpi.de/realms/{OIDC_REALM}/protocol/openid-connect/certs"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "myhpi.core.middleware.IPRangeUserMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

if DJANGO_DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "myhpi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "myhpi/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "myhpi.core.context.base_context",
            ],
        },
    },
]

WSGI_APPLICATION = "myhpi.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": env.str("POSTGRES_HOST"),
            "PORT": env.str("POSTGRES_PORT"),
            "USER": env.str("POSTGRES_USER"),
            "PASSWORD": env.str("POSTGRES_PASSWORD"),
            "NAME": "myhpi",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "de"

TIME_ZONE = "UTC"

USE_I18N = True
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", "English"),
    ("de", "German"),
]
WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "wagtail_localize.machine_translators.deepl.DeepLTranslator",
    "OPTIONS": {"AUTH_KEY": env.str("DEEPL_API_KEY", "")},
}

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "myhpi", "locale"),
]

# SCSS Precompiler
# To learn more see: https://django-static-precompiler.readthedocs.io/en/stable/index.html

STATIC_PRECOMPILER_COMPILERS = (
    (
        "static_precompiler.compilers.libsass.SCSS",
        {
            "precision": 8,
        },
    ),
)

STATIC_PRECOMPILER_FINDER_LIST_FILES = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "static_precompiler.finders.StaticPrecompilerFinder",
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_URL = env.str("STATIC_URL")
STATIC_ROOT = env.str("STATIC_ROOT")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "myhpi", "static"),)

MEDIA_ROOT = env.str("MEDIA_ROOT")
MEDIA_URL = env.str("MEDIA_URL")

# Wagtail settings

WAGTAIL_SITE_NAME = "myHPI"
WAGTAILDOCS_SERVE_METHOD = "serve_view"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = SITE_URL

ANONYMOUS_IP_RANGE_GROUPS = {
    env.str("ANONYMOUS_IP_RANGE"): env.str("ANONYMOUS_IP_RANGE_GROUP_NAME")
}

# django.contrib.messages
MESSAGE_TAGS = {
    constants.DEBUG: "alert-info",
    constants.INFO: "alert-info",
    constants.SUCCESS: "alert-success",
    constants.WARNING: "alert-warning",
    constants.ERROR: "alert-danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
INTERNAL_IPS = env.str("INTERNAL_IPS")

WAGTAILMARKDOWN = {
    "allowed_tags": ["abbr"],
    "allowed_attributes": {"abbr": ["title"]},
    "extensions": ["toc", "abbr"],
}

ENABLE_MAILING_LISTS = env.bool("ENABLE_MAILING_LISTS", False)

# The mailing lists library (Tenca) has a django-like settings module.
# This code will read in all correctly prefixed settings from the
# current module, e.g. `TENCA_API_USER` -> `tenca.settings.API_USER`
if ENABLE_MAILING_LISTS:
    import tenca.settings

    TENCA_API_HOST = env.str("TENCA_API_HOST")
    TENCA_API_PORT = env.int("TENCA_API_PORT")
    TENCA_API_SCHEME = env.str("TENCA_API_SCHEME")
    TENCA_ADMIN_USER = env.str("TENCA_ADMIN_USER")
    TENCA_ADMIN_PASS = env.str("TENCA_ADMIN_PASS")
    TENCA_LIST_HASH_ID_SALT = env.str("TENCA_LIST_HASH_ID_SALT")
    TENCA_WEB_UI_HOSTNAME = env.str("TENCA_WEB_UI_HOSTNAME")
    TENCA_DISABLE_GOODBYE_MESSAGES = env.bool("TENCA_DISABLE_GOODBYE_MESSAGES")
    TENCA_HASH_STORAGE_CLASS = env.str("TENCA_HASH_STORAGE_CLASS")

    tenca.settings.load_from_module(sys.modules[__name__])

    INSTALLED_APPS += ["myhpi.tenca_django"]
    MIDDLEWARE += ["myhpi.tenca_django.middleware.TencaNoConnectionMiddleware"]

INSTITUTION_EMAIL_REPLACEMENTS = [
    ("hpi.uni-potsdam.de", "hpi.de"),
    ("student.hpi.uni-potsdam.de", "student.hpi.de"),
]

ALUMNI_EMAIL_REPLACEMENTS = [
    ("hpi.de", "student.hpi.de"),
    ("hpi.uni-potsdam.de", "student.hpi.uni-potsdam.de"),
]

# mail configuration
EMAIL_CONFIG = env.email_url("EMAIL_URL")
vars().update(EMAIL_CONFIG)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env.str("SERVER_EMAIL")
ADMINS = getaddresses(env.list("ADMINS"))

# Set this to view /metrics with X-API-KEY header
METRICS_API_KEY = env.str("METRICS_API_KEY", default=None)

# logging

LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(levelname)s %(asctime)s %(name)s %(module)s %(message)s"},
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "backupCount": 10,
            "maxBytes": 5242880,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["mail_admins", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["mail_admins", "console"],
    },
}

BS_ICONS_CACHE = os.path.join(STATIC_ROOT, "icon_cache")

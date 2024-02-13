from myhpi.settings import *  # NOQA, otherwise it will be removed by autoflake in the pre-commit hook

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
WAGTAIL_APPEND_SLASH = False

METRICS_API_KEY = "TEST_KEY"

LANGUAGE_CODE = "en"

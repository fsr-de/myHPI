from django.urls import path

from myhpi.core.views import metrics_view

urlpatterns = [path("metrics", metrics_view, name="prometheus-django-metrics")]

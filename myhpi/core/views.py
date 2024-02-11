# Create your views here.
import prometheus_client
from django.conf import settings
from django.http import HttpResponse


def metrics_view(request):
    provided_key = request.headers.get("X-API-KEY")
    if provided_key and provided_key == settings.METRICS_API_KEY:
        metrics_page = prometheus_client.generate_latest(prometheus_client.REGISTRY)
        return HttpResponse(metrics_page, content_type=prometheus_client.CONTENT_TYPE_LATEST)
    else:
        return HttpResponse("Unauthorized", status=401)

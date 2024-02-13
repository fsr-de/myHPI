from ipaddress import ip_address, ip_network

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class IPRangeUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        try:
            self.ip_ranges = {
                ip_network(k): v for k, v in settings.ANONYMOUS_IP_RANGE_GROUPS.items()
            }
        except ValueError as e:
            raise ImproperlyConfigured from e

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        address = ip_address(get_client_ip(request))
        request.user.ip_range_group_name = []
        for ip_range, group_name in self.ip_ranges.items():
            if address in ip_range:
                # user is in this IP range
                request.user.ip_range_group_name = group_name
                break

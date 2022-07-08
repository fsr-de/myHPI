from django.contrib.auth.models import Group
from django.db.models import Q


def get_user_groups(user):
    if getattr(user, "_ip_range_group_name", False):
        # join user groups together with the groups they have based on their IP address
        return Group.objects.filter(Q(name=user._ip_range_group_name) | Q(id__in=user.groups.all()))
    else:
        # use the users groups only
        return user.groups.all()

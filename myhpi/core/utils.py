from django.contrib.auth.models import Group
from django.db.models import Q

from myhpi import settings


def get_user_groups(user):
    if getattr(user, "_ip_range_group_name", False):
        # join user groups together with the groups they have based on their IP address
        return Group.objects.filter(Q(name=user._ip_range_group_name) | Q(id__in=user.groups.all()))
    else:
        # use the users groups only
        return user.groups.all()


# taken from https://github.com/fsr-de/1327/blob/master/_1327/main/utils.py
def email_belongs_to_domain(email, domain):
    return email.rpartition("@")[2] == domain


def replace_email_domain(email, original_domain, new_domain):
    return email[: -len(original_domain)] + new_domain


def toggle_institution(email):
    for original_domain, new_domain in settings.INSTITUTION_EMAIL_REPLACEMENTS:
        if email_belongs_to_domain(email, original_domain):
            yield replace_email_domain(email, original_domain, new_domain)
        elif email_belongs_to_domain(email, new_domain):
            yield replace_email_domain(email, new_domain, original_domain)


def alternative_emails(email):
    yield from toggle_institution(email)
    for current_domain, alumni_domain in settings.ALUMNI_EMAIL_REPLACEMENTS:
        if email_belongs_to_domain(email, current_domain):
            alumni_mail = replace_email_domain(email, current_domain, alumni_domain)
            yield alumni_mail
            yield from toggle_institution(alumni_mail)

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Group


def mail_replacement(email):
    return email.replace("uni-potsdam.", "")


class MyHPIOIDCAB(OIDCAuthenticationBackend):

    def create_user(self, claims):
        email = mail_replacement(claims.get('email'))
        first_name = claims.get('given_name', '')
        last_name = claims.get('family_name', '')
        username = claims.get('sub')

        user = self.UserModel.objects.create_user(username, email=email, first_name=first_name, last_name=last_name)

        try:
            hpi = Group.objects.get(name="HPI")
            user.groups.add(hpi)
        except Group.DoesNotExist:
            pass

        if "student" in email:
            try:
                student = Group.objects.get(name="Student")
                user.groups.add(student)
            except Group.DoesNotExist:
                pass

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = mail_replacement(claims.get('email'))

        user.save()

        return user

    def filter_users_by_claims(self, claims):
        """Return all users matching the specified username."""
        username = claims.get('sub')
        if not username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username__iexact=username)

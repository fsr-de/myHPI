from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


def mail_replacement(email):
    return f"{email.split('@')[0]}@{email.split('@')[1].replace('uni-potsdam.', '')}"


class MyHPIOIDCAB(OIDCAuthenticationBackend):
    def _update_groups(self, user, claims):
        return

    def create_user(self, claims):
        email = mail_replacement(claims.get("email"))
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        username = claims.get("sub")

        user = self.UserModel.objects.create_user(
            username, email=email, first_name=first_name, last_name=last_name
        )
        self._update_groups(user, claims)
        return user

    def update_user(self, user, claims):
        user.email = claims.get("email")
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        self._update_groups(user, claims)
        user.save()

        return user

    def filter_users_by_claims(self, claims):
        """Return all users matching the specified username."""
        username = claims.get("sub")
        if not username:
            return self.UserModel.objects.none()
        users = self.UserModel.objects.filter(username__iexact=username)
        if not users.exists():
            users = self.UserModel.objects.filter(
                email__iexact=mail_replacement(claims.get("email"))
            )
        return users

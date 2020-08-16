from passlib.hash import bcrypt

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from pta_export.core.models import User as OCPTAUser


class UserModelEmailBackend(ModelBackend):
    """
    Authentication backend for login with email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = get_user_model().objects.get(email__iexact=username, is_active=True)
            if check_password(password, user.password) and self.user_can_authenticate(user):
                return user
        except get_user_model().DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None


class OCPTABackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        DjangoUser = get_user_model()

        try:
            ocpta_user = OCPTAUser.objects.get(afkorting=username)
        except OCPTAUser.DoesNotExist:
            return None

        # check password
        if not bcrypt.verify(password, ocpta_user.password):
            return None

        defaults = {
            "email": ocpta_user.email,
            "is_active": bool(ocpta_user.actief),
            "first_name": ocpta_user.naam[:255],
            "is_staff": True,
        }

        try:
            django_user = DjangoUser.objects.get(username=username)
            for field, value in defaults.items():
                setattr(django_user, field, value)

        except DjangoUser.DoesNotExist:
            django_user = DjangoUser.objects.create_user(username=username, **defaults)
            django_user.set_unusable_password()
        django_user.save()

        if self.user_can_authenticate(django_user):
            return django_user

        return None

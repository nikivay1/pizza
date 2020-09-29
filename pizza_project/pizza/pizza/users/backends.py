from django.contrib.auth.backends import ModelBackend
from .models import AppUser


class SmsCodeBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, user_id, check_can_auth):
        return self.get_user(user_id, check_can_auth)

    def get_user(self, user_id, check_can_auth=True):
        try:
            user = AppUser._default_manager.get(pk=user_id)
        except AppUser.DoesNotExist:
            return None
        if check_can_auth:
            return user if self.user_can_authenticate(user) else None
        return user

from django.db.models import Q
from django.contrib.auth.backends import AllowAllUsersModelBackend

from authentication.models import CustomUser


class AuthBackend(AllowAllUsersModelBackend):
    def create_user(self, username, email, password) -> CustomUser or str:
        user = CustomUser.objects.create_user(username=username,
                                              email=email,
                                              password=password)
        return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by searching the username or email field
            user = CustomUser.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

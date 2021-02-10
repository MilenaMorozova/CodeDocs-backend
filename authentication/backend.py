from django.db.models import Q
from django.contrib.auth.backends import AllowAllUsersModelBackend
from django.db.utils import IntegrityError

from authentication.models import CustomUser
from .exceptions import UserAlreadyExistException, NotUniqueFieldException, UserDoesNotExistException


class AuthBackend(AllowAllUsersModelBackend):
    def create_user(self, username, email, password) -> CustomUser:
        try:
            user = CustomUser.objects.create_user(username=username,
                                                  email=email,
                                                  password=password)
            return user
        except IntegrityError:
            raise UserAlreadyExistException()

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by searching the username or email field
            user = CustomUser.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            raise UserDoesNotExistException()
            # return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            # raise UserDoesNotExistException()
            return None

    def is_correct_username(self, username):
        if CustomUser.objects.filter(username=username).exists():
            raise NotUniqueFieldException('username')
        return True

    def is_correct_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise NotUniqueFieldException('email')
        return True

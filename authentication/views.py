from django.http import HttpResponse

from authentication.backend import AuthBackend
from .helper import catch_view_exception
from .auth_logger import auth_logger
from .exceptions import AuthenticationException

auth_backend = AuthBackend()


@catch_view_exception(('username'), auth_logger)
def check_username_for_uniqueness(username, **kwargs):
    try:
        auth_backend.is_correct_username(username)
        return HttpResponse(200)
    except AuthenticationException as e:
        return HttpResponse(content=e.message, status=e.response_status)


@catch_view_exception(('email'), auth_logger)
def check_email_for_uniqueness(email, **kwargs):
    try:
        auth_backend.is_correct_username(email)
        return HttpResponse(200)
    except AuthenticationException as e:
        return HttpResponse(content=e.message, status=e.response_status)


@catch_view_exception(('username', 'email', 'password'), auth_logger)
def sign_up(username, email, password, **kwargs):
    try:
        auth_backend.create_user(username=username,
                                 email=email,
                                 password=password)

        return HttpResponse(status=201)
    except AuthenticationException as e:
        return HttpResponse(content=e.message, status=e.response_status)

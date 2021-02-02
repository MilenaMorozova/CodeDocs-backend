from django.http import HttpResponse, HttpResponseBadRequest

from authentication.backend import AuthBackend
from .helper import catch_view_exception
from .auth_logger import auth_logger
from .exceptions import AuthenticationException

auth_backend = AuthBackend()


@catch_view_exception(('username', 'email', 'password'), auth_logger)
def sign_up(username, email, password):
    try:
        auth_backend.create_user(username=username,
                                email=email,
                                password=password)

        return HttpResponse(status=201)
    except AuthenticationException as e:
        return HttpResponse(content=e.message, status=e.response_status)

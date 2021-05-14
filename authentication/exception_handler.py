from smtplib import SMTPException
import datetime

from rest_framework.views import exception_handler
from django.http import HttpResponse
from rest_framework import status

from authentication.models import CustomUser


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    elif isinstance(exc, SMTPException):
        if context['request'].stream.path == '/auth/users/':
            CustomUser.objects.filter(username=context['request'].data['username'],
                                      email=context['request'].data['email']).all().delete()

        response = HttpResponse(content=' '. join(['This email', *exc.args[0], 'is invalid']),
                                status=status.HTTP_400_BAD_REQUEST)

    else:
        response = HttpResponse(content=f"{str(exc)}\n problem in server, "
                                        "please report the error to 'msmorozova_3@edu.hse.ru' "
                                        "and specify the date: " + str(datetime.datetime.now()),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

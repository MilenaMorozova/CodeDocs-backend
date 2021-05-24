import traceback
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
from rest_framework import status


def catch_view_exception(required_request_fields: tuple or list, logger):
    def decorator(func):
        def wrap(request):

            # check necessary fields in request
            for field in required_request_fields:
                try:
                    request.data[field]
                except KeyError:
                    logger.error(f"{field} is empty field")
                    return HttpResponseBadRequest(f"{field} not given")

            # catch server exceptions
            try:
                return func(request)
            except Exception as ex:
                logger.error(f"UNKNOWN EXCEPTION {func.__name__} {ex} {traceback.format_exc()}")
                return HttpResponse("problem in server, please report the error to 'msmorozova_3@edu.hse.ru' "
                                    "and specify the date: " + str(datetime.datetime.now()),
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrap
    return decorator

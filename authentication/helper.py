import traceback
from django.http import HttpResponse, HttpResponseBadRequest
import datetime


def catch_view_exception(required_request_fields: tuple or list, logger):
    def decorator(func):
        def wrap(request):
            # check type of request
            if request.method not in ['GET', 'POST']:
                logger.error(f"bad type_request = {request.method}")
                return HttpResponseBadRequest("Bad request type")

            # check necessary fields in request
            request_dict = getattr(request, request.method).dict()
            for field in required_request_fields:
                try:
                    request_dict[field]
                except KeyError:
                    logger.error(f"{field} is empty field")
                    return HttpResponseBadRequest(f"{field} not given")

            # catch server exceptions
            try:
                return func(**request_dict)
            except Exception as ex:
                logger.error(f"{func.__name__} {ex} {traceback.format_exc()}")
                return HttpResponse("problem in server, please report the error to 'ismashtakov@edu.hse.ru' "
                                    "and specify the date: " + str(datetime.datetime.now()), status=500)
        return wrap
    return decorator

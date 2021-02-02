import traceback
from django.http import HttpResponse
import datetime

from authentication.exceptions import BadRequestTypeException, FieldNotGivenException


def catch_view_exception(required_request_fields: tuple, logger):
    def decorator(func):
        def wrap(request):
            # check type of request
            if request.method not in ['GET', 'POST']:
                logger.error(f"bad type_request = {request.method}")
                raise BadRequestTypeException()

            # check necessary fields in request
            request_dict = getattr(request, request.method).dict()
            for field in required_request_fields:
                try:
                    request_dict[field]
                except KeyError:
                    logger.error(f"{field} is empty field")
                    raise FieldNotGivenException(field)

            # catch server exceptions
            try:
                return func(**request_dict)
            except Exception as ex:
                logger.error(f"{func.__name__} {ex} {traceback.format_exc()}")
                return HttpResponse("problem in server, please report the error to 'ismashtakov@edu.hse.ru' "
                                    "and specify the date: " + str(datetime.datetime.now()), status=500)
        return wrap
    return decorator

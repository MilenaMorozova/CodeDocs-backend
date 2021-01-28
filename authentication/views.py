from django.http import HttpResponse, HttpResponseBadRequest

from authentication.backend import AuthBackend

auth_backend = AuthBackend()

# TODO check availability all necessary fields
# TODO create logger
def sign_up(request):
    try:
        auth_backend.create_user(username=request.GET['username'],
                                email=request.GET['email'],
                                password=request.GET['password'])
        return HttpResponse(status=201)
    except Exception as e:
        return HttpResponseBadRequest(str(e))

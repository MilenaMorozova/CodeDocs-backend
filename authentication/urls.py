from django.urls import path

from .views import sign_up, check_username, check_email

urlpatterns = [
    path('sign_up', sign_up),
    path('check_username', check_username),
    path('check_email', check_email)
]

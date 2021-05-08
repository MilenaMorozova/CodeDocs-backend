from django.urls import path

from .consumers import FileEditorConsumer

websocket_urlpatterns = [
    path('files/<encode_file>/<access_token>/', FileEditorConsumer.as_asgi()),
]

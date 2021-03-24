from django.urls import path

from .consumers import FileEditorConsumer

websocket_urlpatterns = [
    path('files/<int:file_id>/<access_token>/', FileEditorConsumer.as_asgi()),
]

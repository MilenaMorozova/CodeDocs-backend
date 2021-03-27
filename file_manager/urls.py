from django.urls import path
from .views import (
    create_file, delete_file, my_files
)


urlpatterns = [
    path('create_file/', create_file),
    path('delete_file/', delete_file),
    path('my', my_files)
]

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from helpers.helper import catch_view_exception
from helpers.logger import create_logger
from .file_manager_backend import FileManager
from .exceptions import FileManageException
from .serializers import (
    UserFilesSerializer, FileSerializer
)

file_manager_logger = create_logger('file_manager_logger')


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@catch_view_exception(('name', 'programming_language'), file_manager_logger)
def create_file(request):
    file = FileManager.create_file(request.data['name'],
                                   request.data['programming_language'],
                                   request.user)
    serializer = FileSerializer(file)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@catch_view_exception(['file_id'], file_manager_logger)
def delete_file(request):
    try:
        FileManager.delete_file(request.data['file_id'],
                                request.user)
        return HttpResponse(status=status.HTTP_200_OK)
    except FileManageException as e:
        return HttpResponse(content=e.message, status=e.response_status)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@catch_view_exception([], file_manager_logger)
def my_files(request):
    files = FileManager.get_user_files(request.user)
    serializer = UserFilesSerializer(files, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

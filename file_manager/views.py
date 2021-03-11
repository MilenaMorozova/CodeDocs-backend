from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from helpers.helper import catch_view_exception
from helpers.logger import create_logger
from .file_manager import FileManager
from .exceptions import FileManageException

file_manager_logger = create_logger('file_manager_logger')


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@catch_view_exception(('filename', 'programming_language'), file_manager_logger)
def create_file(request):
    FileManager.create_file(request.data['filename'],
                            request.data['programming_language'],
                            request.user)
    return HttpResponse(status=status.HTTP_200_OK)


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

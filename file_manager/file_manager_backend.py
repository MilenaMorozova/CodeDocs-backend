from .models import File, UserFiles, Access

from .exceptions import (
    NoRequiredFileAccess, FileDoesNotExistException
)
from .operations import Insert, Delete


class FileManager:
    @staticmethod
    def create_file(name, programming_language, user):
        file = File.objects.create(name=name,
                                   programming_language=programming_language)
        UserFiles.objects.create(file=file,
                                 user=user,
                                 access=Access.OWNER)
        return file

    @staticmethod
    def delete_file(file_id, user):
        try:
            file = File.objects.get(pk=file_id)

            if not file.user_files.filter(user=user, access=Access.OWNER).exists():
                raise NoRequiredFileAccess('OWNER')

            file.delete()
        except File.DoesNotExist:
            raise FileDoesNotExistException()

    @staticmethod
    def get_user_files(user):
        return UserFiles.objects.filter(user=user).all()

    @staticmethod
    def generate_link(file_id):
        try:
            file = File.objects.get(id=file_id)
            return f"/file/{file.encode()}"
        except File.DoesNotExist:
            raise FileDoesNotExistException()

    @staticmethod
    def leave_file(file_id, user):
        try:
            access_to_file = UserFiles.objects.get(file__id=file_id, user=user)
            if access_to_file.access == Access.OWNER:
                raise NoRequiredFileAccess('VIEWER OR EDITOR')
            access_to_file.delete()

        except UserFiles.DoesNotExist:
            raise NoRequiredFileAccess('ANY')

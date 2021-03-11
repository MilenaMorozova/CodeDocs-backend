from .models import File, UserFiles

from .exceptions import (
    NoRequiredFileAccess, FileDoesNotExistException
)


class FileManager:
    @staticmethod
    def create_file(filename, programming_language, user):
        file = File.objects.create(name=filename,
                                   programming_language=programming_language)
        UserFiles.objects.create(file=file,
                                 user=user,
                                 access=UserFiles.Access.OWNER)

    @staticmethod
    def delete_file(file_id, user):
        try:
            file = File.objects.get(pk=file_id)

            if not file.user_files.filter(user=user, access=UserFiles.Access.OWNER).exists():
                raise NoRequiredFileAccess('OWNER')

            file.delete()
        except File.DoesNotExist:
            raise FileDoesNotExistException()

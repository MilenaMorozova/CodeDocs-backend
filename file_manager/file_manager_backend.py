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
    def edit_file(file_id, operation, position, text, revision):
        file = File.objects.get(pk=file_id)
        current_operation = Insert(position, text) if operation == 'Ins' else Delete(position, text)

    @staticmethod
    def add_to_file_content(file_id, where, text):
        file = File.objects.get(pk=file_id)

        file.content = file.content[:where] + text + file.content[where:]
        file.save()

    @staticmethod
    def delete_from_file_content(file_id, where, count):
        file = File.objects.get(pk=file_id)

        file.content = file.content[:where] + file.content[where + count:]
        file.save()

    @staticmethod
    def replace_in_file_content(file_id, where, count, text):
        FileManager.delete_from_file_content(file_id, where, count)
        FileManager.add_to_file_content(file_id, where, text)

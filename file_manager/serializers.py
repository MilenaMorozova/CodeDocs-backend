from rest_framework import serializers

from file_manager.models import File, UserFiles


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ('created', 'users', 'content')


class UserFilesSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)

    class Meta:
        model = UserFiles
        exclude = ('id', 'user')

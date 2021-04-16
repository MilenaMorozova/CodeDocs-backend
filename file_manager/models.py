from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import base64
import json

from .exceptions import (
    FileDoesNotExistException, UnableToDecodeFileException
)


class Access(models.IntegerChoices):
    VIEWER = 0
    EDITOR = 1
    OWNER = 2


class File(models.Model):
    class ProgrammingLanguage(models.TextChoices):
        PYTHON = "python"
        JS = "js"

    name = models.CharField(max_length=248)
    programming_language = models.CharField(choices=ProgrammingLanguage.choices, max_length=50)
    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField(get_user_model(),
                                   through='UserFiles',
                                   related_name='files')

    link_access = models.IntegerField(default=Access.VIEWER, choices=Access.choices)
    last_revision = models.IntegerField(default=0)

    def encode(self):
        return str(base64.b64encode(bytes(json.dumps({"file_id": self.pk}), encoding='UTF-8')), encoding='UTF-8')

    @staticmethod
    def decode(data: str):
        try:
            b_data = bytes(data, encoding='UTF-8')
            decode_data = base64.b64decode(b_data)
            file_id = json.loads(decode_data, encoding='UTF-8')['file_id']
            return File.objects.get(pk=file_id)
        except File.DoesNotExist:
            raise FileDoesNotExistException()
        except Exception:
            raise UnableToDecodeFileException()


class UserFiles(models.Model):

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='user_files')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_files')
    access = models.IntegerField(choices=Access.choices)


class Operations(models.Model):
    class Type(models.IntegerChoices):
        NEU = 0
        INSERT = 1
        DELETE = 2

    type = models.IntegerField(choices=Type.choices)
    position = models.IntegerField()
    text = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='operations')
    revision = models.IntegerField()
    channel_name = models.TextField()

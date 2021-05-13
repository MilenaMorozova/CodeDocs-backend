import base64
import json

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connections

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


def CASCADE_WITH_DELETING_FILES_WHERE_USER_IS_OWNER(collector, field, sub_objs, using):
    # delete from UserFiles
    collector.collect(
        sub_objs, source=field.remote_field.model, source_attr=field.name,
        nullable=field.null, fail_on_restricted=False,
    )
    if field.null and not connections[using].features.can_defer_constraint_checks:
        collector.add_field_update(field, None, sub_objs)

    # delete from File
    user_files = sub_objs.filter(access=Access.OWNER).all()
    files_for_deleting = File.objects.filter(user_files__in=user_files)

    collector.collect(
        files_for_deleting, source=field.remote_field.model, source_attr=field.name,
        nullable=field.null, fail_on_restricted=False,
    )


class UserFiles(models.Model):

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='user_files')
    user = models.ForeignKey(get_user_model(),
                             on_delete=CASCADE_WITH_DELETING_FILES_WHERE_USER_IS_OWNER,
                             related_name='user_files')
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

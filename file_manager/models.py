from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


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


class UserFiles(models.Model):
    class Access(models.IntegerChoices):
        VIEWER = 0
        EDITOR = 1
        OWNER = 2

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='user_files')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_files')
    access = models.IntegerField(choices=Access.choices)


class Operations(models.Model):
    class TypeOperation(models.IntegerChoices):
        INSERT = 0
        DELETE = 1

    type = models.IntegerField(choices=TypeOperation.choices)
    position = models.IntegerField()
    text = models.TextField()
    revision = models.IntegerField()

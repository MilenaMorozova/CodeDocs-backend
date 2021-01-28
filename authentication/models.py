from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from .account_colors import random_color


class CustomAccountManager(BaseUserManager):
    def create_user(self, username, email, password):
        user = self.model(username=username,
                          email=email,
                          password=password,
                          account_color=random_color())
        user.save(using=self._db)
        return user

    def create_superuser(self):
        pass

    def get_by_natural_key(self, username):
        print(username)
        return self.get(username=username)


class CustomUser(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(unique=True, max_length=128)
    account_color = models.CharField(max_length=7)
    is_confirmed = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'

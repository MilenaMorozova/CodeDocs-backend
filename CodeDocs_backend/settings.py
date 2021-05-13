"""
Django settings for CodeDocs_backend project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd6cspfpj##7p%v25--_qqz*%nr!84)r5p*p1v@0rgl#^ys!i!@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['26.124.121.68',
                 '26.158.8.9',
                 'localhost',
                 '127.0.0.1',
                 '26.124.121.68']

DOMAIN = '26.124.121.68:3000'
SITE_NAME = 'code_docs'

CHANNEL_LAYERS = {
    "default": {
        # "BACKEND": "channels.layers.InMemoryChannelLayer",  # local-development
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication.apps.AuthenticationConfig',
    'file_manager.apps.FileManagerConfig',

    'rest_framework.authtoken',
    'rest_framework',
    'djoser',
    'corsheaders',
    'channels',
    'channels_presence',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

CSRF_COOKIE_SECURE = True

CORS_ORIGIN_WHITELIST = (
    'http://26.158.8.9:8000',
    'http://localhost:8000',
)

ROOT_URLCONF = 'CodeDocs_backend.urls'
AUTH_USER_MODEL = 'authentication.CustomUser'
ASGI_APPLICATION = "CodeDocs_backend.asgi.application"

# email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_HOST_USER = os.getenv('CODE_DOCS_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('CODE_DOCS_EMAIL_PASSWORD')
EMAIL_USE_TLS = True
SERVER_EMAIL = os.getenv('CODE_DOCS_EMAIL')
DEFAULT_FROM_EMAIL = os.getenv('CODE_DOCS_EMAIL')

REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
  ),
  'EXCEPTION_HANDLER': 'authentication.exception_handler.custom_exception_handler'
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(weeks=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(weeks=24),
    'ROTATE_REFRESH_TOKENS': True,
}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'username/reset/confirm/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': 'activate?uid={uid}&token={token}',
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'SERIALIZERS': {
        'user_create': 'authentication.serializers.UserRegistrationSerializer',
        'user': 'authentication.serializers.UserSerializer',
        'current_user': 'authentication.serializers.UserSerializer'
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CodeDocs_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#                     'level': 'DEBUG',
#                     'handlers': ['console', ],
#         },
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'code_docs',
        'USER': os.getenv('CODE_DOCS_DB_USERNAME'),
        'PASSWORD': os.getenv('CODE_DOCS_DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
               'NAME': 'auto_tests',
           }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

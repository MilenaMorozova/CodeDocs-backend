from unittest.mock import patch

from django.test import Client, TestCase
from rest_framework import status

from authentication.backend import AuthBackend


class TestLogger:
    def error(self, error):
        pass


def create_test_logger(*args): return TestLogger()


class CheckUsername(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    # @patch('helpers.logger.create_logger', 'create_test_logger')
    def test_username_is_unique(self):
        response = self.client.post('/auth/check_username/', {'username': 'Igor Mashtakov'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_username_already_exist(self):
        auth_backend = AuthBackend()
        auth_backend.create_user(username='Igor Mashtakov',
                                 email='masht@mail.ru',
                                 password='12345')
        response = self.client.post('/auth/check_username/', {'username': 'Igor Mashtakov'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.content, b'This username is already in use')


@patch('helpers.logger.create_logger', 'create_test_logger')
class CheckEmail(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_email_is_unique(self):
        response = self.client.post('/auth/check_email/', {'email': 'masht@mail.ru'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_already_exist(self):
        auth_backend = AuthBackend()
        auth_backend.create_user(username='Igor Mashtakov',
                                 email='masht@mail.ru',
                                 password='12345')
        response = self.client.post('/auth/check_email/', {'email': 'masht@mail.ru'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.content, b'This email is already in use')

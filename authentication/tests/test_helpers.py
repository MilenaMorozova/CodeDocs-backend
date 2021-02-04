from django.test import TestCase, RequestFactory

from ..helper import catch_view_exception
from helpers.logger import create_logger


test_logger = create_logger('test_helper')


@catch_view_exception(('username', 'email'), test_logger)
def test_view(username, email, **kwargs):
    if not username:
        raise Exception()
    return 1


class HelperTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_bad_type_request_put(self):
        request = self.factory.put('/tests/helper')
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Bad request type')

    def test_no_username_in_params(self):
        request = self.factory.get('/tests/helper', {'email': 'masht@mail.ru'})
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'username not given')

    def test_unnecessary_param(self):
        request = self.factory.get('/tests/helper', {'username': 'Igor',
                                                      'email': 'masht@mail.ru',
                                                      'password': '12345'})
        response = test_view(request)
        self.assertEqual(response, 1)

    def test_another_exception(self):
        request = self.factory.get('/tests/helper', {'username': '',
                                                     'email': 'masht@mail.ru'})
        response = test_view(request)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(b'problem in server' in response.content)

    def test_ok(self):
        request = self.factory.get('/tests/helper', {'username': 'Igor',
                                                     'email': 'masht@mail.ru'})
        response = test_view(request)
        self.assertEqual(response, 1)

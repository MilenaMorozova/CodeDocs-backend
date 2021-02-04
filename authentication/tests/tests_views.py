from django.test import Client, TestCase


class SignUp(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_create_new_user(self):
        response = self.client.get('/authentication/sign_up', {'username': 'Igor Mashtakov',
                                                               'email': 'masht@mail.ru',
                                                               'password': '12345'})
        self.assertEqual(response.status_code, 201)

    def test_user_already_exist(self):
        _ = self.client.get('/authentication/sign_up', {'username': 'Igor Mashtakov',
                                                        'email': 'masht@mail.ru',
                                                        'password': '12345'})
        response = self.client.get('/authentication/sign_up', {'username': 'Igor Mashtakov',
                                                               'email': 'masht@mail.ru',
                                                               'password': '12345'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'This user already exist')

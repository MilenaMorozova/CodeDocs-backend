from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import CustomUser
from file_manager.models import UserFiles, File, Access
from file_manager.exceptions import FileDoesNotExistException


class CreateFileTestCase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                    email='111@mail.ru',
                                                    password='12345')

        self.client.force_authenticate(user=self.user)

    def test_authorized_user_create_file(self):
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        response = self.client.post('/file/create_file/', file_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(File.objects.filter(**file_params).exists())

        file = File.objects.get(**file_params)
        self.assertTrue(UserFiles.objects.filter(user=self.user, file=file, access=Access.OWNER))

    def test_authorized_user_filename_not_given(self):
        response = self.client.post('/file/create_file/', {'programming_language': "python"})
        self.assertContains(response, "name not given", status_code=status.HTTP_400_BAD_REQUEST)

    def test_authorized_user_pl_not_given(self):
        response = self.client.post('/file/create_file/', {'name': "test_file2"})
        self.assertContains(response, "programming_language not given", status_code=status.HTTP_400_BAD_REQUEST)


class MyFileTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                    email='111@mail.ru',
                                                    password='12345')

        self.client.force_authenticate(user=self.user)

    def test_no_files(self):
        response = self.client.get('/file/my')
        self.assertContains(response, "[]")

    def test_files_exist(self):
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        _ = self.client.post('/file/create_file/', file_params).content
        response = self.client.get('/file/my')
        self.assertContains(response, b'[{"file": {"id": 1, "name": "file_1", "programming_language": "python"}, '
                                      b'"access": 2}]')
        # self.assertContains(response, b'[{"file": ' + file_data + b', "access": 2}]')


class DeleteFileTestsCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                    email='111@mail.ru',
                                                    password='12345')

        self.client.force_authenticate(user=self.user)

    def tearDown(self) -> None:
        File.objects.all().delete()

    def test_no_file_id(self):
        response = self.client.post('/file/delete_file/')
        self.assertContains(response, "file_id not given", status_code=status.HTTP_400_BAD_REQUEST)

    def test_no_such_file(self):
        response = self.client.post('/file/delete_file/', {'file_id': 1})
        self.assertContains(response, "Such file does not exist", status_code=status.HTTP_404_NOT_FOUND)

    def test_file_exist(self):
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        _ = self.client.post('/file/create_file/', file_params)

        response = self.client.post('/file/delete_file/', {'file_id': self.user.files.get().pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_owner(self):
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        _ = self.client.post('/file/create_file/', file_params)

        another_user = CustomUser.objects.create_user(username='Michael Scolfield',
                                                      email='121@mail.ru',
                                                      password='origami')

        self.client.force_authenticate(user=another_user)

        response = self.client.post('/file/delete_file/', {'file_id': self.user.files.get().pk})
        self.assertContains(response, "You must be OWNER that to do this", status_code=status.HTTP_406_NOT_ACCEPTABLE)


class GenerateLinkTestCase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                    email='111@mail.ru',
                                                    password='12345')

        self.client.force_authenticate(user=self.user)

    def tearDown(self) -> None:
        File.objects.all().delete()

    def test_no_file_id(self):
        response = self.client.post('/file/open_file/')
        self.assertContains(response, "file_id not given", status_code=status.HTTP_400_BAD_REQUEST)

    def test_file_no_exist(self):
        response = self.client.post('/file/open_file/', {'file_id': 45})
        e = FileDoesNotExistException()
        self.assertContains(response, e.message, status_code=e.response_status)

    def test_file_exist(self):
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        _ = self.client.post('/file/create_file/', file_params)

        response = self.client.post('/file/open_file/', {'file_id': self.user.files.get().pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        encode_content = str(response.content, encoding='UTF-8').split('/')[-1]
        file = File.decode(encode_content)
        self.assertEqual(file.pk, self.user.files.get().pk)

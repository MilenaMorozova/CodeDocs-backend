from channels.testing import WebsocketCommunicator
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
# from unittest import TestCase
# import pytest

from CodeDocs_backend.asgi import application
from authentication.models import CustomUser
from file_manager.models import File
from file_manager.file_manager_backend import FileManager
from asgiref.sync import sync_to_async, async_to_sync


class MockJWTTokenUserAuthentication:
    @staticmethod
    def get_validated_token(*args):
        return 1

    @staticmethod
    def get_user(*args):
        try:
            return CustomUser.objects.get()
        except Exception as e:
            print(e)


class FileEditorConsumerTestCase(TestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                   email='111@mail.ru',
                                                   password='12345')
        self.file = FileManager.create_file(name="file_1", programming_language="python", user=self.user)
        client = APIClient()
        client.force_authenticate(user=self.user)
        file_params = {'name': "file_1",
                       'programming_language': "python"}
        _ = client.post('/file/create_file/', file_params)
        self.file = self.user.files.get()

        self.token_patcher = patch('rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token',
                             MockJWTTokenUserAuthentication.get_validated_token)
        self.token_patcher.start()

        self.user_patcher = patch(
            'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication.get_user',
            MockJWTTokenUserAuthentication.get_user)
        self.user_patcher.start()

        print('setUp')

    def tearDown(self) -> None:
        File.objects.all().delete()
        CustomUser.objects.all().delete()

        self.token_patcher.stop()
        self.user_patcher.stop()

    @pytest.mark.asyncio
    async def test_connection(self):
        # self.assertTrue(True)
        print(await sync_to_async(CustomUser.objects.count)())
        communicator = WebsocketCommunicator(application.application_mapping["websocket"], f"/files/123/1278/")
        await communicator.connect()
        answer = await communicator.output_queue.get()
        print(1)
        # self.assertEqual(answer, {'type': 'websocket.close', 'code': 4401})

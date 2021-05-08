from unittest.mock import patch
import base64
import json

from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from channels_presence.models import Presence
from asgiref.sync import sync_to_async

from CodeDocs_backend.asgi import application
from authentication.models import CustomUser
from file_manager.models import File, UserFiles, Access, Operations
from file_manager.file_manager_backend import FileManager
from authentication.serializers import UserSerializer
from file_manager.serializers import (
    FileSerializer, UserWithAccessSerializer, OperationSerializer
)


class MockJWTTokenUserAuthentication:
    @staticmethod
    def get_validated_token(*args):
        return 1

    @staticmethod
    def get_user(*args):
        try:
            return CustomUser.objects.last()
        except Exception as e:
            print(e)


class FileEditorConsumerTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(username='Igor Mashtakov',
                                                   email='111@mail.ru',
                                                   password='12345')
        self.file = FileManager.create_file(name="file_1", programming_language="python", owner=self.user)
        self.file = self.user.files.get()

        self.token_patcher = patch('rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token',
                                   MockJWTTokenUserAuthentication.get_validated_token)
        self.token_patcher.start()

        self.user_patcher = patch('rest_framework_simplejwt.authentication.JWTTokenUserAuthentication.get_user',
                                  MockJWTTokenUserAuthentication.get_user)
        self.user_patcher.start()

    def tearDown(self) -> None:
        File.objects.all().delete()
        CustomUser.objects.all().delete()

        self.token_patcher.stop()
        self.user_patcher.stop()

    async def test_connection__unable_to_decode_file(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"], "/files/123/1278/")
        await communicator.connect()

        answer = await communicator.output_queue.get()
        self.assertEqual(answer, {'type': 'websocket.close', 'code': 4400})

    async def test_connection__file_does_not_exist(self):
        file_id_bytes = bytes(json.dumps({"file_id": self.file.pk + 1}), encoding='UTF-8')
        encode_file_id = str(base64.b64encode(file_id_bytes), encoding='UTF-8')

        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{encode_file_id}/1278/")
        await communicator.connect()

        answer = await communicator.output_queue.get()
        self.assertEqual(answer, {'type': 'websocket.close', 'code': 4404})

    async def test_connection__user_have_not_access_to_file(self):
        new_user = await sync_to_async(CustomUser.objects.create_user)(username='Michael',
                                                                       email='1@mail.ru',
                                                                       password='1345')

        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        channel_name_answer = await communicator.output_queue.get()
        self.assertEqual(channel_name_answer['type'], 'websocket.send')
        self.assertIn('"type": "channel_name", "channel_name"', channel_name_answer['text'])

        new_user_answer = await communicator.output_queue.get()
        self.assertEqual(new_user_answer['type'], 'websocket.send')

        default_access = (await sync_to_async(File.objects.get)(id=self.file.pk)).link_access

        answer = json.loads(new_user_answer['text'])
        right_answer = {'type': 'new_user',
                        'user': {
                            'user': UserSerializer(new_user).data,
                            'access': default_access
                        }}
        self.assertDictEqual(answer, right_answer)

        access_to_file = (await sync_to_async(UserFiles.objects.get)(user=new_user, file=self.file)).access
        self.assertEqual(default_access, access_to_file)

    async def test_connection__one_connection(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        channel_name_answer = await communicator.output_queue.get()
        self.assertEqual(channel_name_answer['type'], 'websocket.send')
        self.assertIn('"type": "channel_name", "channel_name"', channel_name_answer['text'])

        new_user_answer = await communicator.output_queue.get()
        self.assertEqual(new_user_answer['type'], 'websocket.send')

        answer = json.loads(new_user_answer['text'])
        right_answer = {'type': 'new_user',
                        'user': {
                            'user': UserSerializer(self.user).data,
                            'access': Access.OWNER
                        }}
        self.assertDictEqual(answer, right_answer)

    async def test_connection__two_connections_from_one_user(self):
        encode_file_id = self.file.encode()

        # the first connection
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{encode_file_id}/1278/")
        await communicator.connect()
        channel_name_answer = await communicator.output_queue.get()
        self.assertEqual(channel_name_answer['type'], 'websocket.send')
        self.assertIn('"type": "channel_name", "channel_name"', channel_name_answer['text'])

        new_user_answer = await communicator.output_queue.get()
        self.assertEqual(new_user_answer['type'], 'websocket.send')

        answer = json.loads(new_user_answer['text'])
        right_answer = {'type': 'new_user',
                        'user': {
                            'user': UserSerializer(self.user).data,
                            'access': Access.OWNER
                        }}
        self.assertDictEqual(answer, right_answer)

        # the second connection
        communicator2 = WebsocketCommunicator(application.application_mapping["websocket"],
                                              f"/files/{encode_file_id}/1278/")
        await communicator2.connect()

        channel_name_answer2 = await communicator2.output_queue.get()
        self.assertEqual(channel_name_answer2['type'], 'websocket.send')
        self.assertIn('"type": "channel_name", "channel_name"', channel_name_answer2['text'])

        self.assertTrue(await communicator2.receive_nothing(1))

        self.assertEqual(2, await sync_to_async(Presence.objects.count)())  # number of connections

    async def test_file_info(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        await communicator.send_json_to({'type': 'file_info'})
        file_info_answer = await communicator.output_queue.get()
        self.assertEqual(file_info_answer['type'], 'websocket.send')

        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'file_info',
                             'file': FileSerializer(self.file).data}
        self.assertDictEqual(file_answer, right_file_answer)

    async def test_active_users__one_user(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        await communicator.send_json_to({'type': 'active_users'})

        active_users_answer = await communicator.output_queue.get()
        self.assertEqual(active_users_answer['type'], 'websocket.send')

        users_answer = json.loads(active_users_answer['text'])

        def access_to_file():
            users_with_access = UserFiles.objects.filter(user=self.user, file=self.file).all()
            return UserWithAccessSerializer(users_with_access, many=True).data

        right_users_answer = {'type': 'active_users',
                              'users': await sync_to_async(access_to_file)()}
        self.assertDictEqual(users_answer, right_users_answer)

    async def test_active_users__users(self):
        # the first user connect
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        users_data = [{'username': 'Michael', 'email': '1@mail.ru', 'password': '1345'},
                      {'username': 'Shon', 'email': 'd@merfi.com', 'password': 'surgeon'}]

        # connect other users
        for user_data in users_data:
            _ = await sync_to_async(CustomUser.objects.create_user)(**user_data)

            communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                                 f"/files/{self.file.encode()}/1278/")
            await communicator.connect()

            _ = await communicator.output_queue.get()
            _ = await communicator.output_queue.get()

        await communicator.send_json_to({'type': 'active_users'})
        answer = await communicator.output_queue.get()

        self.assertEqual(answer['type'], 'websocket.send')
        self.assertIn('{"type": "active_users"', answer['text'])

        def check_users_in_answer():
            users = UserFiles.objects.all()
            for user in users:
                self.assertIn(f'{json.dumps(UserWithAccessSerializer(user).data)}', answer['text'])

        await sync_to_async(check_users_in_answer)()

    async def test_active_users__two_connections_from_one_user(self):
        # the first connection
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        # the second connection
        communicator2 = WebsocketCommunicator(application.application_mapping["websocket"],
                                              f"/files/{self.file.encode()}/1278/")
        await communicator2.connect()

        _ = await communicator2.output_queue.get()  # channel_name

        # active users
        await communicator.send_json_to({'type': 'active_users'})
        active_users_answer = await communicator.output_queue.get()
        self.assertEqual(active_users_answer['type'], 'websocket.send')

        users_answer = json.loads(active_users_answer['text'])

        def access_to_file():
            users_with_access = UserFiles.objects.filter(user=self.user, file=self.file).all()
            return UserWithAccessSerializer(users_with_access, many=True).data

        right_users_answer = {'type': 'active_users',
                              'users': await sync_to_async(access_to_file)()}
        self.assertDictEqual(users_answer, right_users_answer)

        self.assertEqual(2, await sync_to_async(Presence.objects.count)())  # number of connections

    async def test_all_users__one_user(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        await communicator.send_json_to({'type': 'all_users'})
        all_users_answer = await communicator.output_queue.get()
        self.assertEqual(all_users_answer['type'], 'websocket.send')

        users_answer = json.loads(all_users_answer['text'])

        def access_to_file():
            users_with_access = UserFiles.objects.filter(user=self.user, file=self.file).all()
            return UserWithAccessSerializer(users_with_access, many=True).data

        right_users_answer = {'type': 'all_users',
                              'users': await sync_to_async(access_to_file)()}
        self.assertDictEqual(users_answer, right_users_answer)

    async def test_all_users__two_connections_from_one_user(self):
        # the first connection
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        # the second connection
        communicator2 = WebsocketCommunicator(application.application_mapping["websocket"],
                                              f"/files/{self.file.encode()}/1278/")
        await communicator2.connect()

        _ = await communicator2.output_queue.get()  # channel_name

        # active users
        await communicator.send_json_to({'type': 'all_users'})
        all_users_answer = await communicator.output_queue.get()
        self.assertEqual(all_users_answer['type'], 'websocket.send')

        users_answer = json.loads(all_users_answer['text'])

        def access_to_file():
            users_with_access = UserFiles.objects.filter(user=self.user, file=self.file).all()
            return UserWithAccessSerializer(users_with_access, many=True).data

        right_users_answer = {'type': 'all_users',
                              'users': await sync_to_async(access_to_file)()}
        self.assertDictEqual(users_answer, right_users_answer)

        self.assertEqual(2, await sync_to_async(Presence.objects.count)())  # number of connections

    async def test_all_users__several_users(self):
        # the first user connect
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        users_data = [{'username': 'Michael', 'email': '1@mail.ru', 'password': '1345'},
                      {'username': 'Shon', 'email': 'd@merfi.com', 'password': 'surgeon'}]

        # connect other users
        for user_data in users_data:
            _ = await sync_to_async(CustomUser.objects.create_user)(**user_data)

        await communicator.send_json_to({'type': 'all_users'})
        answer = await communicator.output_queue.get()

        self.assertEqual(answer['type'], 'websocket.send')
        self.assertIn('{"type": "all_users"', answer['text'])

        def check_users_in_answer():
            users = UserFiles.objects.all()
            for user in users:
                self.assertIn(f'{json.dumps(UserWithAccessSerializer(user).data)}', answer['text'])

        await sync_to_async(check_users_in_answer)()

    async def test_change_file_config__change_filename(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        new_name = 'another_file_1'
        await communicator.send_json_to({'type': 'change_file_config',
                                         'config': {
                                             'name': new_name
                                         }})
        self.file.name = new_name

        file_info_answer = await communicator.output_queue.get()
        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'change_file_config',
                             'file': FileSerializer(self.file).data}
        self.assertDictEqual(file_answer, right_file_answer)

    async def test_change_file_config__change_filename_and_pl(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        new_file_config = {'name': 'another_file_1',
                           'programming_language': 'js'}

        await communicator.send_json_to({'type': 'change_file_config',
                                         'config': new_file_config})

        self.file.name = new_file_config['name']
        self.file.programming_language = new_file_config['programming_language']

        file_info_answer = await communicator.output_queue.get()
        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'change_file_config',
                             'file': FileSerializer(self.file).data}
        self.assertDictEqual(file_answer, right_file_answer)

    async def test_change_file_config__change_to_the_same_config(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        new_file_config = {'name': self.file.name,
                           'programming_language': self.file.programming_language}

        await communicator.send_json_to({'type': 'change_file_config',
                                         'config': new_file_config})
        file_info_answer = await communicator.output_queue.get()

        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'change_file_config',
                             'file': FileSerializer(self.file).data}
        self.assertDictEqual(file_answer, right_file_answer)

    async def test_change_file_config__change_nothing(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        await communicator.send_json_to({'type': 'change_file_config',
                                         'config': {}})
        file_info_answer = await communicator.output_queue.get()

        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'change_file_config',
                             'file': FileSerializer(self.file).data}
        self.assertDictEqual(file_answer, right_file_answer)

    async def test_change_link_access(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        new_access = Access.EDITOR
        await communicator.send_json_to({'type': 'change_link_access',
                                         'new_access': new_access})

        file_info_answer = await communicator.output_queue.get()

        file_answer = json.loads(file_info_answer['text'])
        right_file_answer = {'type': 'change_link_access',
                             'new_access': new_access}
        self.assertDictEqual(file_answer, right_file_answer)

        await sync_to_async(self.file.refresh_from_db)()
        self.assertEqual(self.file.link_access, new_access)

    async def test_change_user_access__cannot_change_user_access(self):
        # the first user connect
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        # the second user connect
        _ = await sync_to_async(CustomUser.objects.create_user)(username='Michael Scofield',
                                                                email='1@mail.ru',
                                                                password='15')
        another_communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                                     f"/files/{self.file.encode()}/1278/")
        await another_communicator.connect()

        _ = await another_communicator.output_queue.get()  # channel_name
        _ = await another_communicator.output_queue.get()  # new_user

        # the second user try to change the first user access
        await another_communicator.send_json_to({'type': 'change_user_access',
                                                 'new_access': Access.EDITOR,
                                                 'another_user_id': self.user.pk})

        change_user_access_answer = await another_communicator.output_queue.get()
        change_access_answer = json.loads(change_user_access_answer['text'])
        right_change_access_answer = {'type': 'error',
                                      'code': 4403}
        self.assertDictEqual(change_access_answer, right_change_access_answer)

    async def test_change_user_access__cannot_change_to_this_access(self):
        def change_access():
            access_to_file = UserFiles.objects.get(user=self.user, file=self.file)
            access_to_file.access = Access.VIEWER
            access_to_file.save()

        await sync_to_async(change_access)()
        # the first user connect
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        # the second user connect
        _ = await sync_to_async(CustomUser.objects.create_user)(username='Michael Scofield',
                                                                email='1@mail.ru',
                                                                password='15')
        another_communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                                     f"/files/{self.file.encode()}/1278/")
        await another_communicator.connect()

        _ = await another_communicator.output_queue.get()  # channel_name
        _ = await another_communicator.output_queue.get()  # new_user

        # the second user try to change the first user access
        await another_communicator.send_json_to({'type': 'change_user_access',
                                                 'new_access': Access.EDITOR,
                                                 'another_user_id': self.user.pk})

        change_user_access_answer = await another_communicator.output_queue.get()
        change_access_answer = json.loads(change_user_access_answer['text'])
        right_change_access_answer = {'type': 'error',
                                      'code': 4406}
        self.assertDictEqual(change_access_answer, right_change_access_answer)

    async def test_change_user_access__oks(self):
        # the first user connect
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        # the second user connect
        another_user = await sync_to_async(CustomUser.objects.create_user)(username='Michael Scofield',
                                                                           email='1@mail.ru',
                                                                           password='15')
        another_communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                                     f"/files/{self.file.encode()}/1278/")
        await another_communicator.connect()

        _ = await another_communicator.output_queue.get()  # channel_name
        _ = await another_communicator.output_queue.get()  # new_user

        await communicator.send_json_to({'type': 'change_user_access',
                                         'new_access': Access.EDITOR,
                                         'another_user_id': another_user.pk})

        change_user_access_answer = await another_communicator.output_queue.get()
        change_access_answer = json.loads(change_user_access_answer['text'])

        def another_user_with_access():
            user_with_access = UserFiles.objects.get(user=another_user, file=self.file)
            return UserWithAccessSerializer(user_with_access).data
        right_change_access_answer = {'type': 'change_user_access',
                                      'user': await sync_to_async(another_user_with_access)()}
        self.assertDictEqual(change_access_answer, right_change_access_answer)

    async def test_apply_operation__one_operation(self):
        communicator = WebsocketCommunicator(application.application_mapping["websocket"],
                                             f"/files/{self.file.encode()}/1278/")
        await communicator.connect()

        _ = await communicator.output_queue.get()  # channel_name
        _ = await communicator.output_queue.get()  # new_user

        operation = {'type': Operations.Type.INSERT,
                     'position': 0,
                     'text': "Hello!"}
        await communicator.send_json_to({'type': 'apply_operation',
                                         'revision': 0,
                                         'operation': operation})

        apply_operation_answer = await communicator.output_queue.get()

        def check_operation():
            prev_revision = self.file.last_revision
            self.file.refresh_from_db()
            self.assertEqual(prev_revision + 1, self.file.last_revision)
            self.assertEqual(self.file.content, operation['text'])

            self.assertTrue(Operations.objects.filter(**operation, revision=self.file.last_revision).exists())

            operation_answer = json.loads(apply_operation_answer['text'])

            db_operation = Operations.objects.last()
            right_operation_answer = {'type': 'apply_operation',
                                      'operation': OperationSerializer(db_operation).data}
            self.assertDictEqual(operation_answer, right_operation_answer)

        await sync_to_async(check_operation)()

    # async def test_apply_operation__several_operations(self):
    #     # the first connect
    #     communicator = WebsocketCommunicator(application.application_mapping["websocket"],
    #                                          f"/files/{self.file.encode()}/1278/")
    #     await communicator.connect()
    #
    #     _ = await communicator.output_queue.get()  # channel_name
    #     _ = await communicator.output_queue.get()  # new_user
    #
    #     # the second_connect
    #     _ = await sync_to_async(CustomUser.objects.create_user)(username='Michael Scofield',
    #                                                             email='1@mail.ru',
    #                                                             password='15')
    #     another_communicator = WebsocketCommunicator(application.application_mapping["websocket"],
    #                                                  f"/files/{self.file.encode()}/1278/")
    #     await another_communicator.connect()
    #
    #     _ = await another_communicator.output_queue.get()  # channel_name
    #     _ = await another_communicator.output_queue.get()  # new_user
    #
    #     operation1 = {'type': Operations.Type.INSERT,
    #                  'position': 0,
    #                  'text': "Hello!"}
    #     operation2 = {'type': Operations.Type.INSERT,
    #                  'position': 5,
    #                  'text': " World!"}
    #     operation3 = {'type': Operations.Type.DELETE,
    #                  'position': 0,
    #                  'text': "He"}
    #     operation4 = {'type': Operations.Type.NEU,
    #                   'position': None,
    #                   'text': None}
    #
    #     await communicator.send_json_to({'type': 'apply_operation',
    #                                      'revision': 0,
    #                                      'operation': operation1})
    #     _ = await communicator.output_queue.get()
    #     await communicator.send_json_to({'type': 'apply_operation',
    #                                      'revision': 1,
    #                                      'operation': operation4})
    #     _ = await communicator.output_queue.get()
    #     await another_communicator.send_json_to({'type': 'apply_operation',
    #                                              'revision': 2,
    #                                              'operation': operation3})
    #     _ = await another_communicator.output_queue.get()
    #     await communicator.send_json_to({'type': 'apply_operation',
    #                                      'revision': 3,
    #                                      'operation': operation2})
    #
    #     _ = await communicator.output_queue.get()
    #
    #     def check_operation():
    #         self.file.refresh_from_db()
    #         self.assertEqual(self.file.last_revision, 4)
    #         self.assertEqual(self.file.content, "llo World!")
    #
    #         self.assertTrue(Operations.objects.count(), 4)
    #
    #     await sync_to_async(check_operation)()

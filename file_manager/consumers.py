from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from channels_presence.models import Room, Presence
from channels_presence.decorators import (
    remove_presence, touch_presence
)
from rest_framework_simplejwt.exceptions import InvalidToken
from channels.exceptions import StopConsumer
from rest_framework import status

from authentication.models import CustomUser
from .models import File, UserFiles, Operations
from .serializers import (
    UserWithAccessSerializer, FileSerializer, OperationSerializer
)
from authentication.serializers import UserSerializer
from .exceptions import FileManageException
from .operation_factory import OperationFactory as factory


class FileEditorConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = None
        self.room_group_name = None
        self.room = None
        self.access = None

    def connect(self):
        self.accept()

        # get current user
        try:
            jwt = JWTTokenUserAuthentication()
            validated_token = jwt.get_validated_token(self.scope['url_route']['kwargs']['access_token'])
            print("CONNECT", CustomUser.objects.count())
            token_user = jwt.get_user(validated_token)
            self.scope['user'] = CustomUser.objects.get(pk=token_user.pk)
        except InvalidToken as e:
            self.close_connect(e.status_code)

        if not self.scope['user'].is_authenticated:
            self.close_connect(status.HTTP_401_UNAUTHORIZED)

        # decode file
        try:
            self.file = File.decode(self.scope['url_route']['kwargs']['encode_file'])
        except FileManageException as e:
            self.close_connect(e.response_status)

        self.room_group_name = f"file_{self.file.pk}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                                                    self.channel_name)
        self.room = Room.objects.add(self.room_group_name, self.channel_name, self.scope["user"])

        # check access to file
        try:
            access_to_file = UserFiles.objects.get(user=self.scope['user'], file=self.file)
        except UserFiles.DoesNotExist:
            access_to_file = UserFiles.objects.create(user=self.scope['user'],
                                                      file=self.file,
                                                      access=self.file.link_access)
        self.access = access_to_file.access

        self.send_json({'type': 'channel_name',
                        'channel_name': self.channel_name})

        if Presence.objects.filter(user=self.scope['user'], room=self.room).count() == 1:
            user_serializer = UserWithAccessSerializer(access_to_file)
            self.send_to_group({'type': 'new_user',
                                'user': user_serializer.data})

    def close_connect(self, http_code):
        self.close(4000 + http_code)
        raise StopConsumer()

    def send_content(self, content):
        self.send_json(content['content'])

    def send_to_group(self, content):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {'type': 'send_content',
                                   'content': content})

    @touch_presence
    def receive_json(self, content, **kwargs):
        getattr(self, content['type'])(content)

    def file_info(self, event):
        file_serializer = FileSerializer(self.file)
        self.send_json({**event,
                        'file': file_serializer.data})

    def active_users(self, event):
        users = self.room.get_users()
        users_with_accesses = UserFiles.objects.filter(user__in=users, file=self.file).all()
        serializer = UserWithAccessSerializer(users_with_accesses, many=True)
        self.send_json({**event,
                        'users': serializer.data})

    def all_users(self, event):
        all_users = UserFiles.objects.filter(file=self.file).all()
        serializer = UserWithAccessSerializer(all_users, many=True)
        self.send_json({**event,
                        'users': serializer.data})

    def change_file_config(self, event):
        for field in event['config']:
            setattr(self.file, field, event['config'][field])

        self.file.save()

        file_serializer = FileSerializer(self.file)
        self.send_to_group({'type': event['type'],
                            'file': file_serializer.data})

    def change_link_access(self, event):
        self.file.link_access = event['new_access']
        self.file.save()
        self.send_to_group(event)

    def change_user_access(self, event):
        user = UserFiles.objects.get(user__id=event['another_user_id'], file=self.file)

        if self.access < user.access:
            self.send_json({'type': 'error',
                            'code': 4000 + status.HTTP_403_FORBIDDEN})
        elif self.access < event['new_access']:
            self.send_json({'type': 'error',
                            'code': 4000 + status.HTTP_406_NOT_ACCEPTABLE})
        else:
            user.access = event['new_access']
            user.save()

            user_serializer = UserWithAccessSerializer(user)
            self.send_to_group({'type': event['type'],
                                'user': user_serializer.data})

    def apply_operation(self, event):
        bd_operations = Operations.objects.filter(revision__gt=event['revision'],
                                                  file=self.file).order_by('revision').all()
        operations = [factory.create(operation.type, operation.position, operation.text) for operation in bd_operations]

        # operation transformation
        current_operation = factory.create(event['operation']['type'],
                                           event['operation']['position'],
                                           event['operation']['text'])
        for operation in operations:
            current_operation /= operation

        # update file content
        self.file.content = current_operation.execute(self.file.content)
        self.file.last_revision += 1
        self.file.save()

        current_operation_query = Operations.objects.create(**current_operation.info(),
                                                      revision=self.file.last_revision,
                                                      file=self.file,
                                                      channel_name=self.channel_name)

        operation_serializer = OperationSerializer(current_operation_query)
        self.send_to_group({'type': event['type'],
                            'operation': operation_serializer.data})

    def operation_history(self, event):
        operations_query = Operations.objects.filter(revision__gt=event['revision']).order_by('revision').all()

        operation_serializer = OperationSerializer(operations_query, many=True)
        self.send_json({'type': event['type'],
                        'operations': operation_serializer.data})

    @remove_presence
    def disconnect(self, code):
        # leave room
        if not Presence.objects.filter(user=self.scope['user'], room=self.room).exists():
            user_serializer = UserSerializer(self.scope['user'])
            self.send_to_group({'type': 'delete_user',
                                'user': user_serializer.data})
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name,
                                                        self.channel_name)

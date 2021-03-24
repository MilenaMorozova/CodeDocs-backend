from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from authentication.models import CustomUser


class FileEditorConsumer(JsonWebsocketConsumer):

    def connect(self):
        jwt = JWTTokenUserAuthentication()
        validated_token = jwt.get_validated_token(self.scope['url_route']['kwargs']['access_token'])
        user = jwt.get_user(validated_token)
        self.scope['user'] = CustomUser.objects.get(pk=user.pk)

        if not user.is_authenticated:
            self.close()

        self.room_name = self.scope['url_route']['kwargs']['file_id']
        self.room_group_name = f"file_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                                                    self.channel_name)

        self.accept()

    def receive_json(self, content, **kwargs):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': "It's OK!"
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        self.send_json({
            'message': message + "RTYRTYR"
        })

    def disconnect(self, code):
        # leave room
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name,
                                                        self.channel_name)

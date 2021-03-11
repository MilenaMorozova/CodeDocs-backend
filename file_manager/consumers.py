from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        pass

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        pass

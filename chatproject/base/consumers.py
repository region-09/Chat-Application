import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import auth

class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        print("connection!")
        room = self.scope['url_route']['kwargs']['room']
        await self.channel_layer.group_add(room, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        room = self.scope['url_route']['kwargs']['room']
        await self.channel_layer.group_discard(room, self.channel_name)

    # IMPORTANT 'send.message' is for function in line 27 "send_message" we replace by "."
    async def receive(self, text_data):
        room = self.scope['url_route']['kwargs']['room']
        message = json.loads(text_data)['message']
        await self.channel_layer.group_send(
            room,
            {
                'sender': self.scope['user'].username,
                'type': 'send.message',
                'message': message,
            }
        )

    async def send_message(self, event):
        # Send the received message to the WebSocket
        message = event['message']
        user = self.scope['user'].username
        sender = event['sender']
        if sender != user:
            await self.send(text_data=json.dumps(
                {'sender': sender, 'message': message}))
        else:
            pass
    
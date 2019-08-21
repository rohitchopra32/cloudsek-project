from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class SendFileStatus(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'task_result'
        print(self.room_group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['task_id']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'result',
                'result': message
            }
        )

    def result(self, event):
        result = event['result']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'result': result
        }))

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import DenyConnection
import json

from .models import Application, ACTIVE_STATUSES


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.app_slug = self.scope['url_route']['kwargs']['app_slug']
        self.tier = self.scope['url_route']['kwargs']['tier']
        self.group_name = 'maintenance_{}_{}'.format(self.app_slug, self.tier)

        try:
            application = Application.objects.get(slug=self.app_slug, tier=self.tier)
        except Application.DoesNotExist:
            raise DenyConnection

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

        # Signal right away if a maintenance event is active
        active =  application.maintenance_events.filter(status__in=ACTIVE_STATUSES)
        if active:
            self.send(text_data=json.dumps({
                'message': 'a maintenance message is active!',
                'active': True,
            }))


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'maintenance_msg',
                'message': text_data_json['message'],
                'active': text_data_json.get('active', False)
            }
        )

    # Receive message from group
    def maintenance_msg(self, event):
        self.send(text_data=json.dumps({
            'message': event['message'],
            'active': event['active']
        }))

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import DenyConnection

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
            # There should only be one active at a time,
            # but don't be strict here
            self.send(text_data=json.dumps(active[0].get_details_for_ws()))


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )


    def receive(self, text_data):
        '''
        Handle message sent by a connected WebSocket
        (This is only used for by the "send test message" UI.)
        '''
        text_data_json = json.loads(text_data)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'maintenance_msg',
                'active': text_data_json.get('active', False),
                'status': text_data_json.get('status', None),
                'details': text_data_json.get('details', None),
            }
        )


    def maintenance_msg(self, event):
        '''
        Forward messages broadcasted to the group on to the WebSocket
        '''
        self.send(text_data=json.dumps(event))

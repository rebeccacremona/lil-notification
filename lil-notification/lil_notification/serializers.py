from rest_framework import serializers

from .models import Application, MaintenanceEvent


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = [
            'id',
            'slug',
            'tier'
        ]


class MaintenanceEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaintenanceEvent
        fields = [
            'id',
            'status',
            'scheduled_start',
            'scheduled_end',
            'started',
            'ended',
            'reason'
        ]


class MaintenanceEventWithApplicationSerializer(MaintenanceEventSerializer):

    class Meta(MaintenanceEventSerializer.Meta):
        fields = list(MaintenanceEventSerializer.Meta.fields) + ['application']
        depth = 1

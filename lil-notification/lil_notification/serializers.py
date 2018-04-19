from rest_framework import serializers

from .models import Application, MaintenanceEvent


class BaseSerializer(serializers.ModelSerializer):
    """ Base serializer from which all of our serializers inherit. """

    def update(self, instance, validated_data):
        """
            When updating, requiring that our serializers provide a whitelist of fields that can be updated.
            This is a safety check that avoids implementation errors where users can update fields that should only be set on create.
        """
        assert hasattr(self.Meta, 'allowed_update_fields'), "Serializers that are used for update must set Meta.allowed_update_fields"
        if set(validated_data.keys()) - set(self.Meta.allowed_update_fields):
            raise serializers.ValidationError('Only updates on these fields are allowed: %s' % ', '.join(self.Meta.allowed_update_fields))
        return super(BaseSerializer, self).update(instance, validated_data)


class ApplicationSerializer(BaseSerializer):

    class Meta:
        model = Application
        fields = [
            'id',
            'slug',
            'tier'
        ]


class MaintenanceEventSerializer(BaseSerializer):

    class Meta:
        model = MaintenanceEvent
        fields = [
            'id',
            'application',
            'status',
            'scheduled_start',
            'scheduled_end',
            'started',
            'ended',
            'reason'
        ]
        allowed_update_fields = [
            'status',
            'scheduled_start',
            'scheduled_end',
            'started',
            'ended',
            'reason'
        ]
        depth = 1


    def validate(self, attrs):
        """ Hack to avoid duplicating validation set up on the model."""
        # http://www.django-rest-framework.org/topics/3.0-announcement/#differences-between-modelserializer-validation-and-modelform
        instance = MaintenanceEvent(**attrs)
        instance.full_clean()
        return attrs


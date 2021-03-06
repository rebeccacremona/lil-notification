from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from simple_history.models import HistoricalRecords

from rest_framework.authtoken.models import Token

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.functional import cached_property


import logging
logger = logging.getLogger(__name__)


ACTIVE_STATUSES = [
    'imminent',
    'in_progress'
]


class Application(models.Model):
    # required fields
    slug = models.SlugField()
    tier = models.CharField(max_length=50)

    class Meta:
        unique_together = ('slug', 'tier')

    def __str__(self):
        return self.name

    @cached_property
    def name(self):
        return "{} {}".format(self.slug, self.tier)


class MaintenanceEvent(models.Model):
    # required fields
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='maintenance_events'
    )
    status = models.CharField(
        max_length=50,
        default='imminent',
        choices=(
            ('imminent', 'imminent'),
            ('in_progress', 'in_progress'),
            ('completed', 'completed'),
            ('canceled', 'canceled'),
        )
    )
    # optional fields
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    ended = models.DateTimeField(blank=True, null=True)
    reason =  models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    # Django methods

    def __str__(self):
        return "{}: {}, {}".format(self.id, self.application.name, self.status)

    def clean(self):
        super(MaintenanceEvent, self).clean()
        if MaintenanceEvent.invalid_active_status_for_pk(self.id, self.status):
            raise ValidationError(
                'There is already an active maintenance event for {}.'.format(
                    self.application.name
                )
            )


    # Custom methods

    @classmethod
    def invalid_active_status_for_pk(cls, pk, status):
        # We should be able to update the statuses of active events,
        # but if a different active event already exists, we
        # should not be able to create another one.
        already_active = cls.objects.filter(status__in=ACTIVE_STATUSES)
        return already_active.count() > 1 or (
            already_active and \
            already_active.get().id != pk and \
            (status in ACTIVE_STATUSES or not status)
        )

    def is_active(self):
        return self.status in ACTIVE_STATUSES

    def get_details_for_ws(self):
        return {
            'active': self.is_active(),
            'status': self.status,
            'scheduled_start': self.scheduled_start.strftime('%c %Z') if self.scheduled_start else None,
            'scheduled_end': self.scheduled_end.strftime('%c %Z') if self.scheduled_end else None,
        }


@receiver(post_save, sender=MaintenanceEvent)
def notify_groups(sender, instance=None, created=False, **kwargs):
    if instance:
        logger.info('Notifying {} about MaintenanceEvent {}'.format(instance.application.name, instance))
        group = 'maintenance_{}_{}'.format(instance.application.slug, instance.application.tier)
        data = {'type': 'maintenance_msg'}
        data.update(instance.get_details_for_ws())
        async_to_sync(get_channel_layer().group_send)(group, data)
        logger.info('Notified {} about MaintenanceEvent {}'.format(instance.application.name, instance))


@receiver(pre_delete, sender=MaintenanceEvent)
def notify_groups_on_relevant_delete(sender, instance=None, **kwargs):
    if instance:
        logger.info('Pending deletion of MaintenanceEvent {}'.format(instance))
        if instance.is_active():
            instance.status = 'canceled'
            instance.save()


# Create API tokens for new users
# via http://www.django-rest-framework.org/api-guide/authentication/#by-using-signals
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(
            user=instance
        )

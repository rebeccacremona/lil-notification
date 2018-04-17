from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property


ACTIVE_STATUSES = [
    'imminent',
    'in_progress'
]


class Application(models.Model):
    # required fields
    slug = models.SlugField()
    tier = models.CharField(max_length=50)
    # optional fields
    full_name = models.CharField(max_length=50, blank=True, null=True)

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
            ('imminent', 'Pending: notify users downtime is imminent.'),
            ('in_progress', 'In Progress: maintenance underway.'),
            ('completed', 'Completed: maintenance completed.'),
            ('canceled', 'Canceled: maintenance event did not take place.'),
        )
    )
    # optional fields
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    ended = models.DateTimeField(blank=True, null=True)
    reason =  models.TextField(blank=True, null=True)


    # Django methods

    def __str__(self):
        return "MaintenanceEvent {}: {}".format(self.id, self.status)


    def clean(self):
        super(MaintenanceEvent, self).clean()
        # We should be able to update the statuses of active events,
        # but if a different active event already exists, we
        # should not be able to create another one.
        already_active = self.__class__.objects.filter(status__in=ACTIVE_STATUSES)
        if already_active and \
           (already_active.count() > 1 or already_active.get() != self):
            raise ValidationError(
                'There is already an active maintenance event for {}.'.format(
                    self.application.name
                )
            )


    # Custom methods

    def is_active(self):
        return self.status in ACTIVE_STATUSES


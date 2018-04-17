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
        if self.__class__.objects.filter(status__in=ACTIVE_STATUSES):
            raise ValidationError(
                'There is already an active maintenance event for {}.'.format(
                    self.application.name
                )
            )


    # Custom methods

    def is_active(self):
        return self.status in ACTIVE_STATUSES


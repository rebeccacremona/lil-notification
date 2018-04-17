import logging
from django.core.exceptions import ValidationError

import pytest

from .models import Application, MaintenanceEvent, ACTIVE_STATUSES

# Fixtures

@pytest.fixture()
@pytest.mark.django_db
def application():
    a = Application(
        slug='perma',
        tier='prod'
    )
    a.save()
    return a


@pytest.fixture()
def unsaved_event_for_app(application):
    class Factory(object):
        def get(self):
            return MaintenanceEvent(application=application)
    return Factory()


# Tests

@pytest.mark.django_db
def test_application_validation():
    slug = 'perma'
    other_slug = 'h2o'
    tier = 'prod'
    other_tier = 'stage'
    a = Application(slug=slug, tier=tier)
    a.full_clean()
    a.save()

    b = Application(slug=slug, tier=tier)
    with pytest.raises(ValidationError) as excinfo:
        b.full_clean()
    assert 'Application with this Slug and Tier already exists.' in str(excinfo)
    b.tier = other_tier
    b.save()

    c = Application(slug=other_slug, tier=tier)
    c.full_clean()
    c.save()


@pytest.mark.django_db
def test_application_str(application):
    assert application.name == str(application)


@pytest.mark.django_db
def test_only_one_active_event(unsaved_event_for_app):
    for status in ACTIVE_STATUSES:
        e1 = unsaved_event_for_app.get()
        e1.status = status
        e1.full_clean()
        e1.save()

        e2 = unsaved_event_for_app.get()
        for status in ACTIVE_STATUSES:
            with pytest.raises(ValidationError) as excinfo:
                e2.status = status
                e2.full_clean()
            assert 'There is already an active maintenance event for {}'.format(e1.application.name) in str(excinfo)

        # clean up for next iteration
        # also proves 'canceled' events don't cause validation to fail
        e1.status = 'canceled'
        e1.save()


@pytest.mark.django_db
def test_new_event_after_completed_event(unsaved_event_for_app):
    e1 = unsaved_event_for_app.get()
    e1.status = 'completed'
    e1.full_clean()
    e1.save()

    e2 = unsaved_event_for_app.get()
    e2.full_clean()
    e2.save()

    assert e1.application is e2.application


@pytest.mark.django_db
def test_can_update_own_status(unsaved_event_for_app):
    e = unsaved_event_for_app.get()
    e.full_clean()
    e.save()
    e.refresh_from_db()
    assert e.status == 'imminent'

    e.status = 'in_progress'
    e.full_clean()
    e.save()
    e.refresh_from_db()
    assert e.status == 'in_progress'


@pytest.mark.django_db
def test_group_notified_on_save(caplog, unsaved_event_for_app):
    caplog.set_level(logging.INFO)
    e = unsaved_event_for_app.get()
    e.full_clean()
    e.save()

    assert len(caplog.records) == 2
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert record.name == 'lil_notification.models'
    assert "Notifying perma prod about MaintenanceEvent" in caplog.records[0].msg
    assert "Notified perma prod about MaintenanceEvent" in caplog.records[1].msg

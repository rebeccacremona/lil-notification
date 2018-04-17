import json

from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe

from .models import Application, MaintenanceEvent


def maintenance_monitor(request, app, tier):
    get_object_or_404(Application, slug=app, tier=tier)
    return render(request, 'maintenance_monitor.html', {
        'app': app,
        'app_json': mark_safe(json.dumps(app)),
        'tier': tier,
        'tier_json': mark_safe(json.dumps(tier))
    })



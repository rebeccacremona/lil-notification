from simple_history.admin import SimpleHistoryAdmin

from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Application, MaintenanceEvent

# remove built-ins
admin.site.unregister(Group)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'tier')
    list_filter = ('slug', 'tier')
    exclude = ['full_name']

@admin.register(MaintenanceEvent)
class MaintenanceEventAdmin(SimpleHistoryAdmin):
    list_display = ('get_app', 'get_tier', 'status', 'scheduled_start','scheduled_end','started','ended')
    list_filter = ('application__slug', 'application__tier', 'status', 'scheduled_start','scheduled_end','started','ended')
    search_fields = ('application__slug', 'application__tier', 'status', )

    def get_app(self, obj):
        return obj.application.slug
    get_app.short_description = 'App'
    get_app.admin_order_field = 'application__slug'

    def get_tier(self, obj):
        return obj.application.tier
    get_tier.short_description = 'Tier'
    get_tier.admin_order_field = 'application__tier'



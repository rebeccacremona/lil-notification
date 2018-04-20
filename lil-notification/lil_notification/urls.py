from rest_framework.routers import APIRootView

from django.urls import path, re_path

from . import views

# list views that should appear in the HTML version of the API root
root_view = APIRootView.as_view(api_root_dict={
    'applications': 'applications',
    'maintenance_events': 'maintenance_events'
})


urlpatterns = [
    # url(r'^$', views.index, name='index')
    path('api/', root_view),
    path('api/applications/', views.ApplicationListView.as_view(), name='applications'),
    path('api/applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='applications_detail'),
    re_path(r'^api/(?P<parent_type>applications)/(?P<parent_id>[0-9]+)/maintenance-events/?$', views.ApplicationMaintenanceEventListView.as_view(), name='applications_events'),
    path('api/maintenance-events/', views.MaintenanceEventListView.as_view(), name='maintenance_events'),
    path('api/maintenance-events/<int:pk>/', views.MaintenanceEventDetailView.as_view(), name='maintenance_events_detail'),
    path('<app>/<tier>', views.maintenance_monitor, name='maintenance_monitor')
]

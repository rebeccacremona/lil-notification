from django.urls import path

from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    path('<app>/<tier>', views.maintenance_monitor, name='maintenance_monitor')
]

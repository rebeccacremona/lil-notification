import json

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe

from .models import Application, MaintenanceEvent
from .serializers import ApplicationSerializer, MaintenanceEventSerializer


###
# Proof-of-Concept GUI
###

def maintenance_monitor(request, app, tier):
    get_object_or_404(Application, slug=app, tier=tier)
    return render(request, 'maintenance_monitor.html', {
        'app': app,
        'app_json': mark_safe(json.dumps(app)),
        'tier': tier,
        'tier_json': mark_safe(json.dumps(tier))
    })


###
# API
###


### BASE VIEW ###
# all via https://github.com/harvard-lil/perma/blob/develop/perma_web/api/views.py#

class BaseView(APIView):
    permission_classes = (IsAdminUser,)  # by default all users must be authenticated
    serializer_class = None  # overridden for each subclass

    # configure filtering of list endpoints by query string
    filter_backends = (
        DjangoFilterBackend,  # subclasses can be filtered by keyword if filter_class is set
        SearchFilter,         # subclasses can be filtered by q= if search_fields is set
        OrderingFilter        # subclasses can be ordered by order_by= if ordering_fields is set
    )
    ordering_fields = ()      # lock down order_by fields -- security risk if unlimited


    ### helpers ###

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.
        Copied from GenericAPIView
        """
        try:
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)
            return queryset
        except DjangoValidationError as e:
            raise ValidationError(e.error_dict)

    def get_object_for_user(self, user, queryset):
        """
            Get single object from queryset, making sure that returned object is accessible_to(user).
        """
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404
        # if not obj.accessible_to(user):
        #     raise PermissionDenied()
        return obj

    def get_object_for_user_by_pk(self, user, pk):
        """
            Get single object by primary key, based on our serializer_class.
        """
        ModelClass = self.serializer_class.Meta.model
        return self.get_object_for_user(user, ModelClass.objects.filter(pk=pk))


    ### basic views ###

    def simple_list(self, request, queryset):
        """
            Paginate and return a list of objects from given queryset.
        """
        queryset = self.filter_queryset(queryset)
        paginator = LimitOffsetPagination()
        items = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(items, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def simple_get(self, request, pk=None, obj=None):
        """
            Return single serialized object based on either primary key or object already loaded.
        """
        if not obj:
            obj = self.get_object_for_user_by_pk(request.user, pk)
        serializer = self.serializer_class(obj, context={"request": request})
        return Response(serializer.data)

    def simple_create(self, data, save_kwargs={}):
        """
            Validate and save new object.
        """
        serializer = self.serializer_class(data=data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save(**save_kwargs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def simple_update(self, obj, data):
        """
            Validate and update given fields on object.
        """
        serializer = self.serializer_class(obj, data=data, partial=True, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise ValidationError(serializer.errors)

    def simple_delete(self, obj):
        """
            Delete object.
        """
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


### ACTUAL VIEWS ###


# /applications/
class ApplicationListView(BaseView):
    serializer_class = ApplicationSerializer

    def get(self, request, format=None):
        """ List applications. """
        queryset = Application.objects.all()
        return self.simple_list(request, queryset)


# /applications/:id/
class ApplicationDetailView(BaseView):
    serializer_class = ApplicationSerializer

    def get(self, request, pk, format=None):
        """ Single application details. """
        return self.simple_get(request, pk)


# /applications/:id/maintenance-events/
class ApplicationMaintenanceEventListView(BaseView):
    serializer_class = MaintenanceEventSerializer
    ordering_fields = ('scheduled_start', 'scheduled_end', 'started', 'ended')
    search_fields = ('reason')

    def get(self, request, pk, format=None):
        """ List maintenance events for app. """
        queryset = MaintenanceEvent.objects.filter(
            application=self.get_object_for_user_by_pk(request.user, pk).id
        )
        return self.simple_list(request, queryset)

    def post(self, request, pk, format=None):
        """
        Create new maintenance event for app.
        """
        # Get application id from route, not from request data.
        data = request.data.copy()
        data['application'] = self.get_object_for_user_by_pk(request.user, pk).id
        return self.simple_create(data)


# /maintenance-events/
class MaintenanceEventListView(BaseView):
    serializer_class = MaintenanceEventSerializer
    ordering_fields = ('scheduled_start', 'scheduled_end', 'started', 'ended')
    search_fields = ('reason')

    def get(self, request, format=None):
        """ List maintenance events. """
        queryset = MaintenanceEvent.objects.all()
        return self.simple_list(request, queryset)


# /maintenance-events/:id/
class MaintenanceEventDetailView(BaseView):
    serializer_class = MaintenanceEventSerializer

    def get(self, request, pk, format=None):
        """ Single application details. """
        return self.simple_get(request, pk)

    def patch(self, request, pk, format=None):
        """ Update  maintenance event. """
        # Get application id from route, not from request data.
        data = request.data.copy()
        data['application'] = self.get_object_for_user_by_pk(request.user, pk).id
        return self.simple_create(data)

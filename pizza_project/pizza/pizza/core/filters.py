from rest_framework import generics, filters
import django_filters
from . import models


class AvailableStreetFilter(filters.FilterSet):

    name = django_filters.CharFilter(name='keywords', lookup_expr='icontains')

    class Meta:
        model = models.AvailableStreet
        fields = ('id', 'name')

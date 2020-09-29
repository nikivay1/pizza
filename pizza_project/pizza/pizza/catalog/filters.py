from rest_framework import generics, filters
import django_filters
from . import models


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ProductFilter(filters.FilterSet):

    category = NumberInFilter(name='category', lookup_expr='in')

    class Meta:
        model = models.Product
        fields = ['category']

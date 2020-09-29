from rest_framework import generics, filters

from catalog.filters import ProductFilter
from .. import serializers
from .. import models
from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationC(PageNumberPagination):
    page_size = 6


class ProductListView(generics.ListAPIView):

    serializer_class = serializers.ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProductFilter
    pagination_class = PageNumberPaginationC

    def get_queryset(self):
        return self.request.geo_location.products.filter(
            is_active=True,
            action_id=None,
            prices__is_active=True
        ).distinct().order_by('category_id', 'position')


class ProductActionListView(generics.ListAPIView):

    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        return self.request.geo_location.products.filter(
            action__isnull=False,
            is_active=True,
            prices__is_active=True
        ).distinct()[:3]

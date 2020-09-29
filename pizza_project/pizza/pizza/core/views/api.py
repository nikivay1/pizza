from django.utils import timezone
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from ..models import Action, AvailableStreet, Location
from ..serializers import LimitOffsetSerializer, ActionListSerializer, AvailableStreetSerializer, LocationSerializer
from ..filters import AvailableStreetFilter


class ActionsListView(APIView):

    serializer_class = LimitOffsetSerializer

    def get(self, request):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)

        limit = serializer.validated_data['limit']
        offset = serializer.validated_data['offset']

        current_time = timezone.now()
        actions_list = Action.objects.all()[offset:offset + limit]
        actual_list = Action.objects.filter(active_from__lte=current_time, active_until__gte=current_time)[:3]
        expired_list = Action.objects.filter(active_until__lt=current_time)[:3]

        data = {'actual': ActionListSerializer(actions_list, many=True).data}

        if offset == 0:
            data.update({
                'actual_list': ActionListSerializer(actual_list, many=True).data,
                'expired_list': ActionListSerializer(expired_list, many=True).data
            })
        return Response(data)


class PageNumber(PageNumberPagination):
    page_size = 20


class AvailableStreetListView(ListAPIView):

    pagination_class = PageNumber
    serializer_class = AvailableStreetSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AvailableStreetFilter

    def get_queryset(self):
        return AvailableStreet.objects.filter(location_id=self.request.geo_location.id)


class LocationListView(ListAPIView):

    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer

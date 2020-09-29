from rest_framework import serializers
from .models import Action, AvailableStreet, Location


class LimitOffsetSerializer(serializers.Serializer):

    limit = serializers.IntegerField(min_value=1)
    offset = serializers.IntegerField(min_value=0)


class ActionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Action
        fields = ('id', 'active_from', 'active_until', 'title', 'text', 'picture', 'is_expired')


class AvailableStreetSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvailableStreet
        fields = ('id', 'name')


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('id', 'name')

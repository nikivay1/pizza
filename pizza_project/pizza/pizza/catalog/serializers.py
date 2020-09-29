from rest_framework import serializers
from . import models


class ImageSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        request = self.context['request']
        file_url = request.build_absolute_uri(instance.image.url)
        return file_url

    class Meta:
        model = models.Image


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductPrice
        fields = ('id', 'price', 'name')


class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Action
        fields = ('id', 'name', 'icon', 'color')


class ProductSerializer(serializers.ModelSerializer):

    action = ActionSerializer()
    category_name = serializers.SerializerMethodField()
    category_icon = serializers.SerializerMethodField()
    images = ImageSerializer(many=True)
    prices = serializers.SerializerMethodField(read_only=True)
    old_price = serializers.SerializerMethodField()

    def get_prices(self, obj):
        return PriceSerializer(
            obj.prices.filter(is_active=True),
            many=True
        ).data

    def get_old_price(self, obj):
        if obj.old_price:
            return str(obj.old_price)
        return 0

    def get_category_name(self, obj):
        return obj.category.name

    def get_category_icon(self, obj):
        return obj.category.icon.url

    class Meta:
        model = models.Product
        fields = (
            'id',
            'name',
            'action',
            'category',
            'category_name',
            'category_icon',
            'images',
            'prices',
            'ingredients',
            'old_price'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ('id', 'name')

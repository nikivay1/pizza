from django.utils.translation import ugettext_lazy as _
from users.validators import validate_phone_number as validate_international_phonenumber
from rest_framework import serializers

from users.serializers import UserSerializer
from . import models
from catalog import models as catalog_models
from core import models as core_models


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = catalog_models.ProductPrice
        fields = ('id', 'price', 'name', 'short_name')


class ShortArenaSerializer(serializers.Serializer):

    arena = serializers.CharField()
    tribune = serializers.IntegerField()
    row_number = serializers.IntegerField()
    col_number = serializers.IntegerField()


class ShortAddressSerializer(serializers.Serializer):

    street = serializers.CharField()
    house = serializers.CharField()
    landmark = serializers.CharField(required=False, allow_blank=True)


class AddressSerializer(serializers.ModelSerializer):

    comment = serializers.CharField(write_only=True, allow_blank=True, required=False)
    payment_type = serializers.ChoiceField(write_only=True, choices=models.Order.PAYMENT_TYPE)
    phone = serializers.CharField(validators=[validate_international_phonenumber])
    username = serializers.CharField()

    def validate(self, attrs):
        if attrs['delivery_type'] == models.Address.DELIVERY_TYPE_CHOICES.DELIVERY:
            if attrs['address_type'] == models.Address.TYPE_CHOICES.ADDRESS:
                serializer = ShortAddressSerializer
            else:
                if not self.context['request'].geo_location.config.arena_allowed:
                    raise serializers.ValidationError({'address_type': _("Incorrect address type")})
                serializer = ShortArenaSerializer
            serializer(data=attrs.copy()).is_valid(raise_exception=True)
        return attrs

    class Meta:
        model = models.Address
        fields = (
            'id',
            'username', 'phone', 'delivery_type',
            'address_type', 'street', 'house',
            'row_number', 'col_number', 'tribune',
            'landmark', 'comment', 'arena',
            'payment_type'
        )


class OrderSerializer(serializers.ModelSerializer):

    address = AddressSerializer()

    class Meta:
        model = models.Order
        fields = ('id', 'status', 'address', 'payment_type')


class OrderCreateSerializer(serializers.ModelSerializer):

    address = AddressSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    payment_type = serializers.CharField(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'status', 'address', 'payment_type')


class ShortProductSerializer(serializers.ModelSerializer):

    is_favorite = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        # user = self.parent.context['request'].user
        # if user.is_authenticated():
        #     return catalog_models.FavoriteProduct.objects.filter(product_id=obj.id, user_id=user.id).exists()
        return False

    def get_price(self, obj):
        return PriceSerializer(obj.prices.first()).data

    def get_icon(self, obj):
        image = obj.get_primary_image()
        return image['special'].url

    class Meta:
        model = catalog_models.Product
        fields = ('id', 'name', 'is_favorite', 'icon', 'price')


class CartItemCreateSerializer(serializers.ModelSerializer):

    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = models.CartItem
        fields = ('product', 'price', 'amount')


class CartItemSerializer(serializers.ModelSerializer):

    product_url = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product = ShortProductSerializer(read_only=True)
    price = PriceSerializer()

    def get_product_url(self, obj):
        image = obj.product.get_primary_image()
        return image['cart'].url

    def get_product_name(self, obj):
        return str(obj.product)

    class Meta:
        model = models.CartItem
        fields = ('id', 'price', 'amount', 'product', 'product_url', 'product_name')


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True)
    specials = serializers.SerializerMethodField(read_only=True)
    order = OrderSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    arena_allowed = serializers.SerializerMethodField(read_only=True)
    empty_location = serializers.SerializerMethodField(read_only=True)

    def get_empty_location(self, obj):
        return self.context['request'].empty_location

    def get_arena_allowed(self, obj):
        return self.context['request'].geo_location.config.arena_allowed

    def get_user(self, obj):
        user = self.context['request'].user
        if user.is_authenticated():
            return UserSerializer(user).data
        return None

    def get_specials(self, obj):
        current_product_ids = obj.items.values_list('price__product_id', flat=True)
        special_ids = set(obj.items.values_list('price__product__specials__id', flat=True))
        return ShortProductSerializer(
            catalog_models.Product.objects.filter(
                id__in=special_ids,
                prices__is_active=True,
                is_active=True
            ).exclude(
                id__in=current_product_ids
            ).distinct()[:20], many=True
        ).data

    class Meta:
        model = models.Cart
        fields = (
            'id', 'token', 'items', 'specials', 'order',
            'user', 'arena_allowed', 'empty_location'
        )


class CartItemCounterSerializer(serializers.ModelSerializer):

    def validate_amount(self, validated_value):
        if validated_value < 1:
            raise serializers.ValidationError(_("must be greater 0"))
        return validated_value

    class Meta:
        model = models.CartItem
        fields = ('id', 'amount')


class ExtOrderSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField(read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    def get_items(self, obj):
        return CartItemSerializer(obj.cart.items.all(), many=True).data

    class Meta:
        model = models.Order
        fields = ('id', 'status', 'items', 'number', 'created_at', 'url')

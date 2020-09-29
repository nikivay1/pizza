from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from importlib import import_module

from django.utils.translation import ugettext_lazy as _
from .validators import validate_phone_number as validate_international_phonenumber
from rest_framework import serializers
from users.models import AppUser, PhoneVerification


class AuthSerializer(serializers.Serializer):

    username = serializers.CharField(validators=[validate_international_phonenumber])
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppUser
        fields = ('id', 'first_name', 'last_name', 'email', 'phone')


class UserRegistrationSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(validators=[validate_international_phonenumber])

    class Meta:
        model = AppUser
        fields = ('first_name', 'phone')


class SMSCodeSerializer(serializers.Serializer):

    code = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            return PhoneVerification.objects.get(
                session=self.context['request'].session.session_key,
                token=attrs['token'],
                sms_code=attrs['code']
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError("incorrect sms")


class PasswordRecoverSerializer(serializers.Serializer):

    phone = serializers.CharField(validators=[validate_international_phonenumber])

    def validate(self, attrs):
        try:
            return AppUser.objects.get(phone=attrs['phone'], is_active=True)
        except AppUser.DoesNotExist:
            return AnonymousUser


class ProfileDataSerializer(serializers.ModelSerializer):

    cache = {}

    orders = serializers.SerializerMethodField()

    def get_orders(self, obj):
        serializer = self.cache.get('order_serializer', None)

        if serializer is None:
            self.cache['order_serializer'] = import_module('cart.serializers').ExtOrderSerializer

        return self.cache['order_serializer'](obj.orders.exclude(status='CANCELED'), many=True).data

    class Meta:
        model = AppUser
        fields = ('id', 'orders', 'first_name', 'phone', 'email')


class ProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppUser
        fields = ('id', 'first_name', 'email')


class PasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=False)
    password1 = serializers.CharField(min_length=4, required=False)
    password2 = serializers.CharField(min_length=4, required=False)

    def validate(self, attrs):

        old, new1, new2 = attrs.get('old_password', '').strip(), \
                          attrs.get('password1', '').strip(), \
                          attrs.get('password2', '').strip()

        if not (old or new1 or new2):
            return False

        if not (old and new1 and new2):
            raise serializers.ValidationError(_("passwords field is empty"))

        user = authenticate(username=self.context['request'].user.phone, password=old)

        if not user:
            raise serializers.ValidationError(_("old password didn't match"))

        if new1 != new2:
            raise serializers.ValidationError(_("password was not matched"))

        return new1

from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import APIException as BaseAPIException
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from core import utils
from .. import serializers
from .. import models
from ..utils import get_current_cart


class APIException(BaseAPIException):

    def __init__(self, *args, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs):
        super(APIException, self).__init__(*args, **kwargs)
        self.status_code = status_code


class CartMixin(object):

    def get_cart(self):
        cart = get_current_cart(self.request)
        self.cart = cart or models.Cart()
        return self.cart


class CartDetailView(CartMixin, generics.RetrieveAPIView):

    serializer_class = serializers.CartSerializer
    queryset = models.Cart.objects.filter()

    def get_object(self):
        return self.get_cart()


class AddProductView(CartMixin, generics.CreateAPIView):

    serializer_class = serializers.CartItemCreateSerializer

    def perform_create(self, serializer):
        cart = self.get_cart()

        user_id = None
        if self.request.user.is_authenticated():
            user_id = self.request.user.id

        if cart._state.adding:
            cart.user_id = user_id
            cart.save()

        if not cart._state.adding and not cart.user:
            cart.user_id = user_id
            cart.save()

        item = cart.items.filter(price=serializer.validated_data['price']).first()

        try:
            order = cart.order
        except models.Order.DoesNotExist:
            pass
        else:
            if order.sb_form_url and not order.is_paid():
                order.sb_form_url = ''
                order.sb_remote_id = ''
                order.sb_internal_id = ''
                order.save()

        if item:
            item.amount += 1
            item.save()
            serializer.instance = item
        else:
            serializer.save(cart=cart)

    def post(self, request, *args, **kwargs):
        response = super(AddProductView, self).post(request, *args, **kwargs)
        response.set_cookie('cart', self.cart.token, expires=timezone.now() + timezone.timedelta(days=10))
        return response


class ItemCartUpdateView(CartMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = serializers.CartItemCounterSerializer

    def perform_update(self, serializer):
        cart = self.cart
        try:
            order = cart.order
        except models.Order.DoesNotExist:
            pass
        else:
            if order.sb_form_url and not order.is_paid():
                order.sb_form_url = ''
                order.sb_remote_id = ''
                order.sb_internal_id = ''
                order.save()
        serializer.save()

    def get_queryset(self):
        return self.get_cart().items.all()


class OrderCreateView(CartMixin, generics.CreateAPIView):

    serializer_class = serializers.OrderCreateSerializer
    queryset = models.Order.objects.all()

    def perform_create(self, serializer):
        cart = self.get_cart()
        config = self.request.geo_location.config
        if cart.get_total_price() < config.min_order_sum:
            raise APIException(
                _("Min order price is") + ' ' + str(config.min_order_sum),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        order = cart.get_order()

        if order:
            self.serializer_class(data=serializer.validated_data, instance=order)

        user_id = None

        if self.request.user.is_authenticated():
            user_id = self.request.user.id

        serializer.save(cart=cart, user_id=user_id)


class AddressUpdateView(CartMixin, generics.UpdateAPIView):

    serializer_class = serializers.AddressSerializer

    def get_object(self):
        return self.get_cart().order.address

    def put(self, request, *args, **kwargs):
        if not request.geo_location.config.is_worked():
            return Response({'detail': _("Delivery don't work now")}, status=status.HTTP_403_FORBIDDEN)
        return super(AddressUpdateView, self).put(request, *args, **kwargs)

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.save(location=self.request.geo_location)
        self.order = instance.order
        if self.order.get_total_price() < instance.location.config.min_order_sum:
            return Response({
                'message': _("Min order price is") + ' ' + str(instance.location.config.min_order_sum) + ' ' + _('rub')
            }, status=status.HTTP_400_BAD_REQUEST)
        payment_type = serializer.validated_data['payment_type']
        self.order.status = models.Order.STATUS_CHOICES.WAIT

        if payment_type == models.Order.PAYMENT_TYPE.ON_DELIVERY:
            self.order.started_at = timezone.now()
            self.order.expired_at = timezone.timedelta(minutes=self.order.address.location.config.order_timeout) + self.order.started_at
            self.order.status = models.Order.STATUS_CHOICES.WAIT
            self.redirect_url = self.order.get_absolute_url()
            self.order.send_notification()
        else:
            if self.order.sb_form_url:
                self.redirect_url = self.order.sb_form_url
                return
            else:
                self.order.set_internal_id()
                order_id, form_url = utils.create_sb_order(self.order, self.request)

                if order_id and form_url:
                    self.order.online_status = models.Order.TRANSACTION_STATUS.REGISTERED
                    self.order.sb_remote_id = order_id
                    self.order.sb_form_url = form_url
                    self.order.save()

                    self.redirect_url = self.order.sb_form_url
                else:
                    raise serializers.serializers.ValidationError("Incorrect request")

            if self.order.sb_started_at is None:
                self.order.sb_started_at = timezone.now()

        self.order.payment_type = payment_type
        self.order.comment = serializer.validated_data.get('comment', '')

        if self.request.user.is_authenticated():
            self.order.user = self.request.user

        self.order.save()

    def update(self, request, *args, **kwargs):
        super(AddressUpdateView, self).update(request, *args, **kwargs)
        return Response(self.redirect_url)


class CleanCartView(CartMixin, APIView):

    def post(self, request):
        cart = self.get_cart()
        if not cart._state.adding:
            cart.items.all().delete()
        return Response()


class OrderPaymentLinkView(generics.RetrieveAPIView):

    def get_queryset(self):
        return models.Order.objects.filter()

    @transaction.atomic
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().select_for_update().get(pk=self.kwargs['pk'])

        if instance.created_at < (timezone.now() - timezone.timedelta(days=2)):
            return Response({
                'message': _("order was created more that 2 days ago, you cann't to pay it")
            }, status=status.HTTP_403_FORBIDDEN)

        status_code, form_url = utils.get_or_create_sb_link(instance, request)

        if status_code == 1:
            message = _("Order already paid")
        elif status_code == 0:
            message = _("Order link was created")
        else:
            message = _("Error on create order link")

        return Response({
            'message': message,
            'form_url': form_url
        })

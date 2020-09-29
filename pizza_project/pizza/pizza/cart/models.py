import uuid
import hashlib

import telegram

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

from core.models import TimeStampedModel
from core import utils


class Cart(TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        verbose_name=_("user"),
        related_name='carts'
    )

    token = models.CharField(
        _("token"),
        max_length=512,
        default=utils.generate_token,
        editable=False
    )

    def get_order(self):
        try:
            return self.order
        except:
            pass

    def get_total_price(self):
        return sum(
            [item.price.price * item.amount for item in self.items.all()]
        )

    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")


class CartItem(models.Model):

    cart = models.ForeignKey(
        'Cart',
        related_name='items',
        verbose_name=_("cart")
    )

    price = models.ForeignKey(
        'catalog.ProductPrice',
        verbose_name=_("price")
    )

    amount = models.IntegerField(
        _("amount"),
        default=1
    )

    def __str__(self):
        return '{price} x {amount}'.format(
            price=self.price.get_display_str(),
            amount=self.amount
        )

    @property
    def product(self):
        return self.price.product

    class Meta:
        verbose_name = _("cart item")
        verbose_name_plural = _("cart items")


class Order(TimeStampedModel):

    STATUS_CHOICES = Choices(
        ('NEW', _("new")),
        ('WAIT', _("wait")),
        ('FAILED', _("failed")),
        ('CONFIRMED', _("confirmed")),
        ('PROGRESS', _("progress")),
        ('DELIVERY', _("delivery")),
        ('CANCELED', _("canceled")),
        ('DONE', _("done"))
    )

    PAYMENT_TYPE = Choices(
        ('ON_DELIVERY', _("on delivery")),
        ('ONLINE', _("online")),
    )

    TRANSACTION_STATUS = Choices(
        (None, 'NONE', _("null")),
        (0, 'REGISTERED', _("registered and didn't paid")),
        (1, 'HOLD', _("amount was hold")),
        (2, 'SUCCESS', _("success")),
        (3, 'AUTH_CANCELLED', _("auth cancelled")),
        (4, 'RETURNED', _("amount returned")),
        (5, 'INITIAL_BY_EMITENT', _("initialized by emitent")),
        (6, 'AUTH_REJECTED', _("auth rejected"))
    )

    payment_type = models.CharField(
        _("payment type"),
        max_length=16,
        default=PAYMENT_TYPE.ON_DELIVERY,
        choices=PAYMENT_TYPE
    )

    online_status = models.IntegerField(
        _("payment status"),
        null=True,
        default=TRANSACTION_STATUS.NONE,
        choices=TRANSACTION_STATUS
    )

    sb_internal_id = models.CharField(
        _("internal order id"),
        default='',
        max_length=512,
        editable=False,
        blank=True
    )

    sb_remote_id = models.CharField(
        _("sb order id"),
        default='',
        max_length=128,
        editable=False,
        blank=True
    )

    sb_form_url = models.CharField(
        _("sb form url"),
        default='',
        max_length=2048,
        blank=True,
        editable=False
    )

    number = models.PositiveIntegerField(
        _("number"),
        db_index=True,
        unique=True,
        editable=False
    )

    cart = models.OneToOneField(
        'Cart',
        verbose_name=_("cart"),
        related_name='order',
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        related_name='orders',
        null=True,
        blank=True
    )

    status = models.CharField(
        _("status"),
        default=STATUS_CHOICES.NEW,
        choices=STATUS_CHOICES,
        max_length=32
    )

    address = models.OneToOneField(
        'Address',
        null=True,
        default=None
    )

    comment = models.TextField(
        _("comment"),
        default="",
        blank=True
    )

    sb_started_at = models.DateTimeField(
        _("sb created at"),
        default=None,
        null=True
    )

    started_at = models.DateTimeField(
        _("started at"),
        default=None,
        null=True,
        blank=True
    )

    expired_at = models.DateTimeField(
        _("expired at"),
        default=None,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{user}, status: {status}, address: {address}.'.format(
            user=self.user or 'anonymous',
            status=self.get_status_display(),
            address=self.address
        )

    def get_pay_link(self):
        if self.payment_type == self.PAYMENT_TYPE.ONLINE:
            if self.online_status == self.TRANSACTION_STATUS.REGISTERED:
                return self.sb_form_url

    def is_paid(self):
        return self.online_status == self.TRANSACTION_STATUS.SUCCESS

    @transaction.atomic
    def set_number(self):
        current_number = Order.objects.select_for_update()\
                             .aggregate(max_number=models.Max('number'))['max_number'] or 100
        self.number = current_number + 1

    def set_internal_id(self):
        self.sb_internal_id = uuid.uuid4().hex

    def has_errors(self):
        return self.payment_type == self.PAYMENT_TYPE.ONLINE and \
               self.online_status != self.TRANSACTION_STATUS.SUCCESS

    def is_wait(self):
        return self.online_status in [
            self.TRANSACTION_STATUS.REGISTERED,
            self.TRANSACTION_STATUS.INITIAL_BY_EMITENT
        ]

    def is_ready(self):
        return self.status in [
            self.STATUS_CHOICES.DONE,
            self.STATUS_CHOICES.CANCELED
        ]

    def get_seconds(self):
        if self.expired_at:
            return self.expired_at - self.started_at
        return 0

    def get_hash(self):
        params = '{id}:{number}:{created_at}'.format(
            id=self.id, number=self.number, created_at=self.created_at.timestamp()
        ).encode()
        return hashlib.sha256(params).hexdigest()

    def get_absolute_url(self):
        return reverse('order-detail', kwargs={'number': self.number, 'hash': self.get_hash()})

    def get_total_price(self):
        return self.cart.get_total_price()
    get_total_price.short_description = _("total price")

    def save(self, *args, **kwargs):
        if self._state.adding:
            save_kwargs = {}
            if self.cart.user:
                save_kwargs = {
                    'username': self.cart.user.first_name,
                    'phone': self.cart.user.phone,
                }
            self.address = Address.objects.create(**save_kwargs)
            self.set_number()
            self.set_internal_id()
        super(Order, self).save(*args, **kwargs)

    def send_notification(self):
        from users.tasks import send_order_notifications
        config = self.address.location.config

        send_order_notifications.delay(
            config.notification_phone_is_enabled,
            str(config.order_phone_notification_number),
            config.notification_telegram_is_enabled,
            str(config.order_telegram_notification_channel),
            self.id
        )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("order")
        verbose_name_plural = _("orders")


class Address(models.Model):

    DELIVERY_TYPE_CHOICES = Choices(
        ('DELIVERY', _("delivery")),
        ('PICKUP', _("pickup"))
    )

    TYPE_CHOICES = Choices(
        ('ADDRESS', _("address")),
        ('ARENA', _("arena"))
    )

    username = models.CharField(_("username"), max_length=512, default="")
    phone = PhoneNumberField(_("phone"), null=True, default=None)
    delivery_type = models.CharField(_("delivery type"), max_length=12, default=DELIVERY_TYPE_CHOICES.DELIVERY,
                                     choices=DELIVERY_TYPE_CHOICES)
    address_type = models.CharField(_("type"), max_length=12, default=TYPE_CHOICES.ADDRESS, choices=TYPE_CHOICES)

    location = models.ForeignKey('core.Location', verbose_name=_("Location"), default=None, null=True, blank=True)

    street = models.CharField(_("street"), max_length=1024, default="", blank=True)
    house = models.CharField(_("house"), max_length=512, default="", blank=True)
    landmark = models.CharField(_("landmark"), max_length=1024, default="", blank=True)

    arena = models.CharField(_("arena"), max_length=1024, default="", blank=True)
    tribune = models.PositiveIntegerField(_("tribune"), default=0)
    row_number = models.PositiveIntegerField(_("row number"), default=0)
    col_number = models.PositiveIntegerField(_("col number"), default=0)

    def __str__(self):
        return self.get_delivery_type_display()

    def display_html(self):
        main_part = """<div style='border: 1px solid silver; padding: 10px;margin-top: 10px;'>
        <p><b>Контакт: </b><i>{username}</i></p>
        <p><b>Телефон: </b><i>{phone}</i></p>
        <p><b>Тип доставки: </b><i>{delivery_type}</i></p>""".format(
            username=self.username,
            phone=self.phone,
            delivery_type=self.get_delivery_type_display()
        )
        pattern1 = """
        {main_part}
        <p><b>Стадион: </b><i>{arena}</i></p>
        <p><b>Трибуна: </b><i>{tribune}</i></p>
        <p><b>Ряд: </b><i>{row_number}</i></p>
        <p><b>Место: </b><i>{col_number}</i></p>
        </div>
        """
        pattern2 = """
        {main_part}
        <p><b>Улица: </b><i>{street}</i></p>
        <p><b>Дом: </b><i>{house}</i></p>
        <p><b>Ориентир: </b><i>{landmark}</i></p>
        </div>
        """

        if self.delivery_type == self.DELIVERY_TYPE_CHOICES.DELIVERY:
            if self.address_type == self.TYPE_CHOICES.ADDRESS:
                return pattern2.format(
                    street=self.street,
                    house=self.house,
                    landmark=self.landmark,
                    main_part=main_part
                )
            else:
                return pattern1.format(
                    arena=self.arena,
                    tribune=self.tribune,
                    row_number=self.row_number,
                    col_number=self.col_number,
                    main_part=main_part
                )
        return main_part

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("address")

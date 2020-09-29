import uuid

import base64
import hashlib
from django.urls import reverse
from importlib import import_module

import phonenumbers
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group as BaseGroup
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

from core.models import TimeStampedModel, SMSTemplate
from core.utils import generate_key, generate_number_code
from users.tasks import send_email_message, send_tpl_sms_message


def bind_unauthorized_cart_to_user(request=None, user=None, **kwargs):
    Cart = import_module('cart.models').Cart
    cart_token = request.COOKIES.get('cart', None)
    if Cart.objects.filter(token=cart_token).exists():
        Cart.objects.filter(user=user, order__isnull=True).delete()
        Cart.objects.filter(token=cart_token).update(user=user)


user_logged_in.connect(bind_unauthorized_cart_to_user)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not phone:
            raise ValueError('The given phone must be set')
        phone = phonenumbers.parse(phone, 'RU')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        _("id"),
        default=uuid.uuid4,
        primary_key=True
    )

    phone = PhoneNumberField(
        _("phone"),
        unique=True
    )

    first_name = models.CharField(
        _('first name'),
        max_length=30,
        blank=True
    )

    last_name = models.CharField(
        _('last name'),
        max_length=30,
        blank=True
    )

    surname = models.CharField(
        _("surname"),
        max_length=64,
        default=""
    )

    email = models.EmailField(
        _('email address'),
        blank=True
    )

    email_confirmed = models.BooleanField(
        _("email confirmed"),
        default=False
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    location = models.ForeignKey(
        'core.Location',
        verbose_name=_("Location"),
        default=None,
        related_name='users',
        null=True
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    manage_location = models.ForeignKey(
        'core.Location',
        verbose_name=_("Manage location"),
        related_name='managers',
        default=None,
        null=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'surname'
    ]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name()

    def is_manager(self):
        return self.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()

    def get_email_confirm_url(self):
        if self.email_confirmed:
            return
        pattern = '{id}:{email}:{hash}'.format(
            id=self.id,
            email=self.email,
            hash=self.get_email_hash()
        ).encode()
        token = base64.b64encode(pattern).decode()
        return '{url}?token={token}'.format(
            url=reverse('email-confirm'),
            token=token
        )

    def get_email_hash(self):
        raw_str = '{id}:{email}:{date_joined}'.format(
            id=self.id,
            email=self.email,
            date_joined=self.date_joined.time()
        ).encode()
        return hashlib.sha256(raw_str).hexdigest()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{} {} {}'.format(self.first_name, self.last_name, self.surname)
        return full_name.strip()

    def clean(self):
        super(AppUser, self).clean()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_email_message#.apply_async(args=[subject, message, from_email, [self.email], **kwargs])

    def sms_user(self, message):
        """
        Sends an email to this User.
        """
        send_tpl_sms_message.delay(str(self.phone), message, raw=True)

    def sms_tpl_user(self, tpl_name, context):
        """
        Sends an email to this User.
        """
        task_args = [
            str(self.phone),
            tpl_name,
            context
        ]
        send_tpl_sms_message.apply_async(args=task_args)

    def set_password(self, raw_password):
        """
        Расширение метода установки пароля с записью в базу каждой попытки.
        
        :param raw_password: str Новый пароль
        :return: 
        """

        super(AppUser, self).set_password(raw_password)
        if not self._state.adding:
            self.passwords.create(password=self.password)

    def set_light_password(self):
        """
        Установка простого числового пароля для отправки по смс.
        
        :return: int Новый пароль
        """

        raw_password = generate_number_code(length=8)
        self.set_password(raw_password)
        return raw_password

    def can_change_password(self):
        """
        Проверка возможности смены пароля.
        Если пользователь очень часто запрашивает смену пароля, необходимо заблокировать попыткию
        Блокировка будет произведена на определенный timeout устанавливаемый в settings.
        
        :return: bool
        """

        current_time = timezone.now() - timezone.timedelta(seconds=settings.PASSWORD_CHANGE_TIMEOUTS)
        return self.passwords.filter(
            created_at__gte=current_time
        ).count() < settings.PASSWORD_CHANGE_ATTEMPTS


class PasswordUser(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), related_name='passwords')
    password = models.TextField(_("password hash"), default="")

    class Meta:
        verbose_name = _("user password")
        verbose_name_plural = _("user passwords")


class PhoneVerification(models.Model):

    STATUS_CHOICES = Choices(
        (1, 'WAIT', _("wait")),
        (2, 'VERIFIED', _("confirmed")),
        (3, 'ACCEPTED', u"использован"),
        (4, 'CANCELLED', u"отменен")
    )

    MAX_SMS_CODE_ATTEMPTS = 3
    SMS_CODE_LIVE_TIMEOUT = 60 * 3
    MAX_ATTEMPTS = 3
    ATTEMPTS_TIMEOUT = 60 * 3

    session = models.CharField(_("session key"), max_length=512, editable=False)
    phone = PhoneNumberField(_("phone"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    status = models.SmallIntegerField(_("status"), default=STATUS_CHOICES.WAIT, choices=STATUS_CHOICES, editable=False)
    token = models.CharField(_("token"), max_length=512, default=generate_key, db_index=True)
    sms_code = models.CharField(_("sms code"), max_length=16, default=generate_number_code)
    sms_code_attempts = models.IntegerField(_("failed attempts"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @classmethod
    def get_by_token(cls, session, key):
        return cls.objects.filter(session=session, token=key).last()

    @classmethod
    def handle_sms_code_failed(cls, session_key, key):
        instance = cls.get_by_token(session=session_key, key=key)
        result = instance, True
        if instance and instance.status == cls.STATUS_CHOICES.WAIT:
            instance.sms_code_attempts += 1
            instance.save(update_fields=['sms_code_attempts'])
            if instance.sms_code_attempts >= cls.MAX_SMS_CODE_ATTEMPTS:
                instance.cancel()
            result = (instance, instance.sms_code_attempts >= cls.MAX_SMS_CODE_ATTEMPTS)
        return result

    def cancel(self):
        self.status = self.STATUS_CHOICES.CANCELLED
        self.save(update_fields=['status'])

    def sms_code_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(seconds=self.SMS_CODE_LIVE_TIMEOUT)

    def send_sms_code(self):
        ctx = {'sms_code': self.sms_code}
        send_tpl_sms_message.delay(
            str(self.phone),
            'verification',
            ctx
        )

    @classmethod
    def attempts(cls, timeout=None, max_attempts=None, **query_params):
        timeout = timeout or cls.ATTEMPTS_TIMEOUT
        max_attempts = max_attempts or cls.MAX_ATTEMPTS
        dt_time = timezone.now() - timezone.timedelta(seconds=timeout)
        current_attempts = cls.objects.filter(created_at__gte=dt_time, **query_params).aggregate(
            count=models.Count('*')
        )['count']

        return max_attempts - current_attempts

    @classmethod
    def cancel_wait_records(cls, auth_token):
        cls.objects.filter(auth_token=auth_token, status=cls.STATUS_CHOICES.WAIT) \
            .update(status=cls.STATUS_CHOICES.CANCELLED)

    def mark_as_verified(self):
        self.token = generate_key(length=20)
        self.status = self.STATUS_CHOICES.VERIFIED
        self.save()

    class Meta:
        unique_together = (
            'status',
            'token',
        )
        verbose_name = u'подтверждение номера телефона'
        verbose_name_plural = u'подтверждения номеров телефонов'


class Group(BaseGroup):

    class Meta:
        proxy = True
        verbose_name = _("group")
        verbose_name_plural = _("groups")

Group._meta.get_field('name').choices = (
            (settings.MANAGER_GROUP_NAME, _("Managers")),
        )

import json
import uuid

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from parler.models import TranslatableModel, TranslatedFields
from core.utils import upload_path_handler


class BaseUUIDModel(models.Model):

    id = models.UUIDField(_("id"), default=uuid.uuid4, primary_key=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class Location(TimeStampedModel):

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=512,
        default=''
    )

    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class SiteConfiguration(TranslatableModel):

    location = models.OneToOneField(
        'core.Location',
        verbose_name=_("Location"),
        related_name='config',
        null=True
    )
    title = models.CharField(_("header title"), max_length=1024, blank=True, default="")
    min_order_sum = models.PositiveIntegerField(_("min order sumw"), default=0)
    translations = TranslatedFields(
        address=models.CharField(_("address"), max_length=1024, blank=True, default=""),
        address_comment=models.CharField(_("address comment"), max_length=1024, default="", blank=True),
        schedule=models.CharField(_("schedule"), max_length=1024, default="", blank=True),
        bottom_right_banner_text=models.TextField(_("Bottom banner's text"), default='')
    )

    phone = models.CharField(_("phone"), max_length=512, blank=True, default="")

    notification_phone_is_enabled = models.BooleanField(_("phone notification is enabled"), default=True)
    notification_telegram_is_enabled = models.BooleanField(_("telegram notifications is enabled"), default=True)

    order_phone_notification_number = models.CharField(_("phone notification"), max_length=16, default='', blank=True)
    order_telegram_notification_channel = models.CharField(_("telegram notification"), max_length=16, default='', blank=True)

    email = models.EmailField(_("email"), blank=True, default="")
    order_timeout = models.PositiveIntegerField(_("order minutes"), default=0, help_text=_("order creation time"))
    metric_code = models.TextField(_("yandex/google metric"), default='', blank=True,
                                   help_text=_("yandex/google metric"))
    arena_allowed = models.BooleanField(_("delivery to arena is allowed"), default=False)

    work_day_started_at = models.TimeField(_("work day started at"), default='09:00')
    work_day_ended_at = models.TimeField(_("work day ended at"), default='23:00')

    yandex_delivery_area = models.TextField(
        verbose_name=_("Yandex delivery area"),
        default=''
    )

    yandex_map_coordinates = JSONField(
        verbose_name=_("Yandex map coordinates"),
        default=[43.410262, 39.9695]
    )

    bottom_right_banner_image = models.ImageField(
        verbose_name=_("Bottom banner's image"),
        default=None,
        blank=True,
        null=True
    )

    bottom_right_banner_icon = models.ImageField(
        verbose_name=_("Bottom banner's icon"),
        default=None,
        blank=True,
        null=True
    )

    def clean(self):
        if not isinstance(self.yandex_map_coordinates, list):
            raise ValidationError({'yandex_map_coordinates': "Укажите координаты в формате: '[x, y]'"})
        elif len(self.yandex_map_coordinates) != 2:
            raise ValidationError({'yandex_map_coordinates': "Укажите две координаты в формате: '[x, y]'"})

    def __str__(self):
        if self.location:
            return self.location.name
        return '-'

    class Meta:
        verbose_name = _("site config")
        verbose_name_plural = _("sites config")

    def is_worked(self):
        current_time = timezone.make_naive(timezone.now()).time()
        return self.work_day_started_at < current_time < self.work_day_ended_at

    def to_json(self):

        return json.dumps({
            'title': self.title,
            'order_timeout': self.order_timeout,
            'address': self.address,
            'address_comment': self.address_comment,
            'schedule': self.schedule,
            'phone': str(self.phone),
            'email': self.email,
            'min_order_sum': self.min_order_sum,
            'delivery_is_available': self.is_worked(),
            'y_map_coord': self.yandex_map_coordinates or [43.410262, 39.9695],
            'y_map_area': self.yandex_delivery_area
        })


class SocialLink(models.Model):

    IMAGE_PATH = 'social'

    name = models.CharField(_("name"), max_length=512, default="")
    icon = models.ImageField(_("icon"), upload_to=upload_path_handler)
    icon_alt = models.CharField(_("icon alt"), max_length=1024, default="", blank=True)
    url = models.CharField(_("http link"), max_length=1024)
    position = models.PositiveIntegerField(_("position"), default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']
        verbose_name = _("social link")
        verbose_name_plural = _("social links")


class SMSTemplate(models.Model):

    slug = models.SlugField(_("slug name"), unique=True)
    text = models.TextField(_("text"), default="")

    @classmethod
    def get_slag(cls, slug):
        return cls.objects.filter(slug=slug).first()

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = _("sms template")
        verbose_name_plural = _("sms templates")


class SliderImage(models.Model):

    IMAGE_PATH = 'slider/'

    config = models.ForeignKey(SiteConfiguration, verbose_name=_("config"), related_name='slider_images')
    image = models.ImageField(_("image"), upload_to=upload_path_handler)
    position = models.PositiveIntegerField(_("ordering"), default=0)

    class Meta:
        ordering = ('position',)
        verbose_name = _("slider image")
        verbose_name_plural = _("slider images")


class Action(TimeStampedModel, TranslatableModel):

    active_from = models.DateTimeField(
        _("active from"),
        default=None,
        null=True,
        blank=True
    )

    active_until = models.DateTimeField(
        _("active until"),
        default=None,
        null=True,
        blank=True
    )
    translations = TranslatedFields(
        title=models.CharField(
            _("title"),
            max_length=1024,
            default=""
        ),
        text=models.TextField(
            _("text"),
            default=""
        )
    )

    picture = ThumbnailerImageField(
       _("picture")
    )

    def is_expired(self):
        return timezone.now() > self.active_until

    is_expired.boolean = True
    is_expired.short_description = _("Expired")

    def __str__(self):
        try:
            return '{}'.format(self.title)
        except:
            return '-'

    class Meta:
        ordering = ['-active_from']
        verbose_name = _("action")
        verbose_name_plural = _("actions")


class AvailableStreet(TimeStampedModel, TranslatableModel):

    location = models.ForeignKey(
        'core.Location',
        verbose_name=_("location"),
        default=None,
        null=True
    )

    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_("street name"),
            max_length=2014,
            default=''
        )
    )

    keywords = models.TextField(
        _("keywords"),
        default=''
    )

    def __str__(self):
        try:
            return self.name
        except:
            return '-'

    class Meta:
        verbose_name = _("available street")
        verbose_name_plural = _("available streets")

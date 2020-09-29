from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from parler.models import TranslatableModel, TranslatedFields

from core.models import BaseUUIDModel, TimeStampedModel
from core.utils import upload_path_handler


class Category(TimeStampedModel, TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(
            _("name"),
            max_length=512,
            default=""
        )
    )

    icon = ThumbnailerImageField(
        _("icon"),
        null=True
    )

    position = models.PositiveIntegerField(
        _("position"),
        default=0
    )

    show_on_top_menu = models.BooleanField(
        _("show on top menu"),
        default=True
    )

    show_on_bottom_menu = models.BooleanField(
        _("show on bottom menu"),
        default=True
    )

    images = GenericRelation('Image', related_query_name='categories')

    def __str__(self):
        try:
            return self.name
        except:
            return '-'

    class Meta:
        ordering = ['position']
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")


class Action(TranslatableModel):

    IMAGE_PATH = 'actions'

    translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=32, default="")
    )

    icon = models.FileField(_("icon"), upload_to=upload_path_handler)
    color = models.CharField(_("color hex"), max_length=8, default="", help_text=_("example: #651fff"))

    def __str__(self):
        try:
            return self.name
        except:
            return '-'

    class Meta:
        verbose_name = _("action")
        verbose_name_plural = _("actions")


class Product(TimeStampedModel, TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(
            _("name"),
            max_length=512,
            default=""
        ),
        ingredients=models.CharField(
            _("ingredients"),
            max_length=1024,
            default=""
        )
    )

    location = models.ForeignKey(
        'core.Location',
        verbose_name=_("Location"),
        related_name='products',
        default=None,
        null=True
    )
    action = models.ForeignKey(
        'Action',
        verbose_name=_("action"),
        related_name='products',
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        'Category',
        related_name='products',
        verbose_name=_("category")
    )

    is_active = models.BooleanField(
        _("active"),
        default=False
    )

    old_price = models.DecimalField(
        _("old price"),
        decimal_places=2,
        max_digits=20,
        default=0
    )

    specials = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name=_("specials")
    )

    position = models.PositiveIntegerField(
        _("position"),
        default=0
    )

    images = GenericRelation('Image', related_query_name='products')

    def get_primary_image(self):
        image = self.images.first()
        if image is None:
            return
        return image.image

    def clean(self):
        if self.action:
            if Product.objects.filter(action__isnull=False, location=self.location).exclude(id=self.id).count() >= 3:
                raise ValidationError({'action': _("You can add 3 products for actions")})

    class Meta:
        ordering = ['position',]
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        try:
            return self.name
        except:
            return '-'


class ProductPrice(TimeStampedModel, TranslatableModel):

    product = models.ForeignKey(
        'Product',
        verbose_name=_("product"),
        related_name='prices'
    )

    translations = TranslatedFields(
        name=models.CharField(
            _("name"),
            max_length=512,
            blank=True,
            default=""
        ),
        short_name=models.CharField(
            _("short name"),
            max_length=512,
            default="",
            blank=True,
            help_text=_("would be used in specials")
        )
    )

    price = models.DecimalField(
        _("price"),
        default=0,
        max_digits=20,
        decimal_places=2
    )

    position = models.PositiveIntegerField(
        _("position"),
        default=0
    )

    is_active = models.BooleanField(
        _("active"),
        default=False
    )

    def __str__(self):
        try:
            return '{name} {price} rub.'.format(name=self.name, price=self.price)
        except:
            return '- {} rub.'.format(self.price)

    def get_display_str(self):
        return '{product} {price}'.format(
            product=self.product,
            price=self
        )

    class Meta:
        ordering = ['position']
        verbose_name = _("price")
        verbose_name_plural = _("prices")


class Image(TimeStampedModel):

    IMAGE_PATH = 'images'

    object_id = models.IntegerField(
        _("object id")
    )

    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        verbose_name=_("object name")
    )

    image = ThumbnailerImageField(
        _("image"),
        upload_to=upload_path_handler
    )

    position = models.PositiveIntegerField(
        _("position"),
        default=0
    )

    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")


class FavoriteProduct(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user")
    )

    product = models.ForeignKey(
        'Product',
        verbose_name=_("product")
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("favorite")
        verbose_name_plural = _("favorite")
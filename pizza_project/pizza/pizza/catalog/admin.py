from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from .models import Category, Product, ProductPrice, Image, Action


class ImageInline(GenericTabularInline):
    model = Image
    fields = ('image', 'get_preview')
    extra = 0
    readonly_fields = ('get_preview',)

    def get_preview(self, obj):
        return '<img src="{url}"/>'.format(url=obj.image['preview'].url)
    get_preview.allow_tags = True
    get_preview.short_description = _("Preview")


class ProductImageInline(ImageInline):

    min_num = 1
    max_num = 1


class CategoryAdmin(SortableAdminMixin, TranslatableAdmin):

    list_display = ('name',)


class ExtendedSortableTabular(SortableInlineAdminMixin):

    def template(self):
        return 'adminsortable2/stacked.html'


class ProductPriceInline(ExtendedSortableTabular, TranslatableTabularInline):

    model = ProductPrice
    min_num = 1
    extra = 0


class ProductAdmin(SortableAdminMixin, TranslatableAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('location', 'category', 'is_active', 'action')
    inlines = [
        ProductPriceInline,
        ProductImageInline
    ]


class ActionAdmin(TranslatableAdmin):

    list_display = ('name', 'icon')
    list_display_links = list_display


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Action, ActionAdmin)

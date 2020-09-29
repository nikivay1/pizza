from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from parler.admin import TranslatableAdmin
from adminsortable2.admin import SortableInlineAdminMixin
from jet.admin import CompactInline
from . import models


class SocialLinkAdmin(SortableInlineAdminMixin, admin.StackedInline):
    model = models.SocialLink
    extra = 0


class SMSTemplateAdmin(CompactInline):
    model = models.SMSTemplate
    extra = 0


class SliderImageAdmin(SortableInlineAdminMixin, admin.StackedInline):
    model = models.SliderImage
    extra = 0


class ConfigAdmin(TranslatableAdmin):

    fieldsets = (
        ("General", {
            'fields': (
                'location',
                'title',
                ('address', 'address_comment'),
                'schedule',
                ('email', 'phone'),
                ('bottom_right_banner_image', 'bottom_right_banner_icon'),
                'bottom_right_banner_text'
            )
        }),
        ("Yandex maps/metrics", {
            'fields': (
                'yandex_delivery_area',
                'yandex_map_coordinates',
                'metric_code'
            )
        }),
        ("Order settings", {
            'fields': (
                'min_order_sum',
                ('order_timeout', 'arena_allowed'),
                ('work_day_started_at', 'work_day_ended_at')
            )
        }),
        ("Order notifications", {
            'fields': (
                'notification_phone_is_enabled', 'order_phone_notification_number',
                'notification_telegram_is_enabled', 'order_telegram_notification_channel'
            )
        }),
    )
    inlines = [
        SliderImageAdmin
    ]


class ActionAdmin(TranslatableAdmin):

    list_display = ('id', 'title', 'active_from', 'active_until', 'is_expired')
    list_display_links = list_display


class LocationAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'is_active')
    list_display_links = list_display


admin.site.site_title = _("PIZZA RALLY")
admin.site.site_header = _("PIZZA RALLY")
# admin.site.index_title = _("Pizza raily")

admin.site.register(models.SiteConfiguration, ConfigAdmin)
admin.site.register(models.Action, ActionAdmin)
admin.site.register(models.AvailableStreet, TranslatableAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.SocialLink)
admin.site.register(models.SMSTemplate)

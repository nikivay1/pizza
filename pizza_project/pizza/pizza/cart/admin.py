from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .models import Cart, Order, CartItem, Address


class OrderAdmin(admin.ModelAdmin):

    list_display = ('get_number', 'get_location', 'user', 'status', 'get_total_price')
    readonly_fields = (
        'get_number', 'get_address', 'get_started_at', 'comment', 'user', 'get_expired_at',
        'online_status', 'payment_type', 'sb_remote_id', 'sb_internal_id', 'get_order_details',
        'get_total_price'
    )
    search_fields = ('number', 'address__username', 'number', 'sb_internal_id', 'sb_remote_id')
    list_filter = ('status', 'address__delivery_type', 'address__location')
    fieldsets = (
        (_("primary"), {
            'fields': (
                'get_number', 'payment_type', 'status',
                ('get_started_at', 'get_expired_at'), 'user', 'comment'
            )
        }),
        (_("payment"), {
            'fields': ('online_status', 'sb_internal_id', 'sb_remote_id')
        }),
        (_("delivery/address and cart"), {
            'fields': (
                'get_total_price', 'payment_type', 'comment', 'get_address',
                'get_order_details'
            )
        }),
    )

    def get_queryset(self, request):
        current_user = request.user
        queryset = super(OrderAdmin, self).get_queryset(request)
        if current_user.is_superuser:
            return queryset
        return queryset.filter(address__location_id=current_user.manage_location_id)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return 'status', 'address__delivery_type', 'address__location'
        return 'status', 'address__delivery_type'

    def get_started_at(self, obj):
        if obj.started_at:
            started_at = timezone.make_naive(obj.started_at).strftime('%Y-%m-%d %H:%M')
            return '<span style="color: red; font-weight: 700;">{started_at}</span>'.format(started_at=started_at)
        return '-'
    get_started_at.allow_tags = True
    get_started_at.short_description = _("started at")

    def get_expired_at(self, obj):
        if obj.started_at:
            expired = obj.get_seconds()
            return '<span style="color: red; font-weight: 700;">{expired}</span>'.format(expired=expired)
        return '-'
    get_expired_at.allow_tags = True
    get_expired_at.short_description = _("expired at")

    def get_number(self, obj):
        return '<span style="font-size: 18px; color: green;">#{}</span>'.format(obj.number)
    get_number.allow_tags = True
    get_number.short_description = _("number")

    def get_address(self, obj):
        return obj.address.display_html()
    get_address.allow_tags = True
    get_address.short_description = _("address")

    def get_location(self, obj):
        if obj.address.location:
            return obj.address.location.name
        return '-'
    get_location.allow_tags = True
    get_location.short_description = _("Location")

    def get_order_details(self, obj):
        items = []
        for item in obj.cart.items.all():
            items.append(
                '<li>{item}</li>'.format(item=item)
            )
        return '<ul style="font-weight: bold;font-size: 20px;">{li_items}</ul>'.format(li_items=''.join(items))
    get_order_details.allow_tags = True
    get_order_details.short_description = _("cart")


class CartItemInline(admin.TabularInline):

    model = CartItem
    extra = 0
    max_num = 0
    min_num = 0
    readonly_fields = ('cart', 'product', 'price', 'amount')


class CartAdmin(admin.ModelAdmin):

    list_display = ('id', 'token', 'user', 'created_at')
    list_display_links = list_display

    inlines = [
        CartItemInline
    ]


admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Address)

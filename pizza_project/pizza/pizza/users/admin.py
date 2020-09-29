from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from .models import AppUser, PhoneVerification, Group, BaseGroup


class PhoneVerificationAdmin(admin.ModelAdmin):

    list_display = ('phone', 'user', 'status', 'created_at')
    list_display_links = list_display


class UserAdmin(BaseUserAdmin):

    list_display = ('phone', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('phone', 'first_name', 'last_name', 'email')
    list_filter = BaseUserAdmin.list_filter + ('groups__name',)
    ordering = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if obj and obj.is_manager():
            fieldsets += (
                _("Location"), {
                    'fields': ('manage_location',)
                }
            ),
        return fieldsets


admin.site.unregister(BaseGroup)
admin.site.register(Group, GroupAdmin)
admin.site.register(AppUser, UserAdmin)
admin.site.register(PhoneVerification, PhoneVerificationAdmin)
